# Copyright 2023 AI Redefined Inc. <dev+cogment@ai-r.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
import time
import os

import torch
import numpy as np
import fire
import cogment
import cogment_enterprise.runner as ent_run

import cog_settings
import model as bench_model
from model import RolloutBuffer, APPODataBuffer, APPOModel
from environment import PONG_OBSERVATION_SHAPE, PONG_NB_PLAYERS
from data_pb2 import AgentConfig, EnvironmentConfig


ONE_HOUR = 3600
MODEL_STORE_TICK_MOD = 100
PLAYER_ACTOR_NAME = "pong_player"
MODEL_NAME = "tutorials_cnn"
total_trial_steps = 0


async def pre_trial_callback(info):
    actor0_config = AgentConfig()
    actor0_config.model_name = MODEL_NAME
    actor_configs = [actor0_config]

    env_config = EnvironmentConfig()
    env_config.id = 0

    params = cogment.TrialParameters(cog_settings)
    params.actors.append(cogment.ActorParameters(cog_settings, "player"))

    params.datalog_endpoint = "cogment://discover?type=datastore"
    params.environment_name = "pong_environment"
    params.environment_implementation = "pong_environment"
    params.actors[0].name = PLAYER_ACTOR_NAME
    params.actors[0].implementation = "appo"

    params.environment_config = env_config
    params.actors[0].config = actor_configs[0]


    return params


async def post_trial_callback(info):
    logging.debug(f"Trial [{info.trial_info.trial_id}] ended.")
    global total_trial_steps
    total_trial_steps += info.trial_info.tick_id


async def get_initial_model(registry):
    logging.debug(f"Preparing initial model [{MODEL_NAME}].")
    rl_model = None

    model_info = await registry.get_model_info(MODEL_NAME)
    if model_info is not None:
        serial_model = await registry.retrieve_model(MODEL_NAME)
        if serial_model is not None:
            logging.info(f"Starting from existing Model [{MODEL_NAME}]")
            rl_model = bench_model.deserialize_training_model(serial_model)

    if rl_model is None:
        logging.info(
            f"Model [{MODEL_NAME}] does not yet exist, creating first iteration..."
        )
        rl_model = APPOModel()
        serial_model = bench_model.serialize_model(rl_model)
        iteration_info = await registry.store_model(MODEL_NAME, serial_model)
        logging.info(
            f"Model [{MODEL_NAME}] initial version [{iteration_info.iteration}] saved (size [{iteration_info.size // 1024}]kb)"
        )
        await registry.update_model_info(MODEL_NAME, {"type": "appo"})

    logging.info(f"Training with model [{MODEL_NAME}]")
    logging.debug(
        f"Model state size [{PONG_OBSERVATION_SHAPE}] result size [{rl_model.network.num_actions}]"
    )

    return rl_model


# Note that we train all actors on the same model in this class.
# "All actors" = Only the actors that have been requested to the batch trainer.
class ModelTrainer:
    def __init__(self, model, datastore: str, dtype=torch.float32):
        self.step_index = 0
        self.update_index = 0
        self.rl_model = model
        self.dtype = dtype
        self.datastore = datastore

        # Data buffer
        self.data_buffer = APPODataBuffer(
            capacity=self.rl_model.cfg.buffer_size,
            observation_shape=PONG_OBSERVATION_SHAPE[::-1],
            action_shape=(1,),
            seed=0,
            device=self.rl_model.device
        )
        self.tot_num_updates = (
            self.rl_model.cfg.max_training_steps // self.rl_model.cfg.num_rollout_steps
        )
        self.total_reward = 0
        self.trial_rewards = []

    def _build_training_sample(self, actor_data, trial_done):
        obs = actor_data.observation
        action = actor_data.action

        # Reshape observersion to match CNN input shape (see model.py)
        obs = torch.tensor(np.frombuffer(obs.value, dtype=np.uint8), dtype=self.dtype)
        action = torch.tensor(action.value, dtype=self.dtype)
        obs = torch.unsqueeze(obs.reshape(PONG_OBSERVATION_SHAPE).permute((2, 0, 1)), dim=0)
        done = (
            torch.ones(1, dtype=self.dtype)
            if trial_done
            else torch.zeros(1, dtype=self.dtype)
        )
        reward = (
            torch.tensor(actor_data.reward, dtype=self.dtype)
            if actor_data.reward is not None
            else torch.tensor(0, dtype=self.dtype)
        )

        return (obs, action, reward, done)

    async def _training_step(self, update_index, registry):
        # Ramdonly select samples from data buffer
        data = self.data_buffer.sample(self.rl_model.cfg.num_rollout_steps)

        # Anneal leanring rate
        decaying_coef = 1.0 - (update_index - 1.0) / self.tot_num_updates
        curr_lr = decaying_coef * self.rl_model.cfg.learning_rate
        self.rl_model.network_optimizer.param_groups[0]["lr"] = curr_lr

        # Update parameters
        _, _ = self.rl_model.update_parameters(
            observations=data.observation,
            actions=data.action,
            advs=data.adv,
            values=data.value,
            log_probs=data.log_prob,
            num_epochs=self.rl_model.cfg.num_epochs,
            num_updates=update_index,
        )

        # Save model
        serial_model = bench_model.serialize_model(self.rl_model)
        if (update_index % MODEL_STORE_TICK_MOD) == 0:
            model_iteration_info = await registry.store_model(
                MODEL_NAME,
                serial_model,
                {"step_index": str(self.step_index)},
            )
        else:
            model_iteration_info = await registry.publish_model(MODEL_NAME, serial_model)

        return model_iteration_info

    async def _process_sample(self, trial_step_index, sample, rollout_buffer):
        trial_done = sample.trial_state == cogment.TrialState.ENDED
        for _, actor_data in sample.actors_data.items():
            (obs, action, reward, done) = self._build_training_sample(actor_data, trial_done)

            # Episodic rewards (step environment). In the case of pong petting zoo, the number of env. step
            # are the reward evaluating agent performance
            if trial_done:
                trial_reward = (trial_step_index + 1) / PONG_NB_PLAYERS
                sample_consumption_lag = time.time() - (sample.timestamp / 1_000_000_000)
                logging.info(f"Last sample from trial [{sample.trial_id}] consumed, ended with a reward of [{trial_reward}] | lag is [{sample_consumption_lag:.2f}s]")
                self.trial_rewards.append(torch.tensor(trial_reward, dtype=self.dtype))

            # Collect rollout data
            if (
                (trial_step_index + 1) % self.rl_model.cfg.num_rollout_steps > 0
            ) and not trial_done:
                with torch.no_grad():
                    value = self.rl_model.network.get_value(obs)
                    dist = self.rl_model.network.get_action(obs)
                    log_prob = dist.log_prob(action)

                # Add data to rollout buffer
                rollout_buffer.add(
                    observation=obs,
                    action=action,
                    reward=reward,
                    done=done,
                    value=value,
                    log_prob=log_prob,
                )
            elif rollout_buffer.num_total > 1:
                # Either the rollout buffer is full, or we reached the end of the trial
                curr_num_data = rollout_buffer.num_total + 1
                next_obs = torch.unsqueeze(
                    obs.reshape(PONG_OBSERVATION_SHAPE).permute((2, 0, 1)), dim=0
                )
                with torch.no_grad():
                    next_value = self.rl_model.network.get_value(next_obs)
                    next_value = next_value.squeeze(0).cpu()

                # Compute GAE for APPO
                dones_gae = (
                    rollout_buffer.dones[:curr_num_data].roll(-1).clone()
                )
                dones_gae[-1] = float(trial_done)

                advs = self.rl_model.compute_gae(
                    rewards=rollout_buffer.rewards[:curr_num_data],
                    values=rollout_buffer.values[:curr_num_data],
                    dones=dones_gae,
                    next_value=next_value,
                    gamma=self.rl_model.cfg.discount_factor,
                    lambda_=self.rl_model.cfg.lambda_gae,
                )

                # Add data to data buffer
                self.data_buffer.add_multi_samples(
                    trial_obs=rollout_buffer.observations[:curr_num_data],
                    trial_act=rollout_buffer.actions[:curr_num_data],
                    trial_adv=advs,
                    trial_log_prob=rollout_buffer.log_probs[:curr_num_data],
                    trial_val=rollout_buffer.values[:curr_num_data],
                )

                rollout_buffer.reset()

    def _is_model_update_required(self) -> bool:
        """Determine whether a model update is required."""

        # Check if there's enough data in the buffer for an update
        has_sufficient_data = self.data_buffer.size() >= self.rl_model.cfg.num_rollout_steps

        # Check if the current step is an appropriate time to update the model
        is_update_step = (self.step_index + 1) % self.rl_model.cfg.update_freq == 0

        return has_sufficient_data and is_update_step



    # Per-trial callback
    async def trial_callback(self, session):
        trial_step_index = 0

        rollout_buffer = RolloutBuffer(
            capacity=self.rl_model.cfg.num_rollout_steps,
            observation_shape=PONG_OBSERVATION_SHAPE[::-1],
            action_shape=(1,),
        )
        async for sample in session.all_samples():
            # Process raw sample and add it to the rollout buffer
            # When the buffer is full, add the full rollout to the data_buffer
            await self._process_sample(
                trial_step_index, sample, rollout_buffer
            )

            # Update the model if needed
            if self._is_model_update_required():
                self.update_index += 1
                update_index = self.update_index
                model_iteration_info = await self._training_step(update_index, session.model_registry)

                if update_index % 50 == 0:
                    avg_trial_rewards = torch.zeros(1, dtype=self.dtype)
                    if len(self.trial_rewards) > 0:
                        avg_trial_rewards = await self.rl_model.compute_average_reward(
                            self.trial_rewards
                        )

                    logging.info(
                        f"Step [{self.step_index}] | Model update [{update_index}] | Avg. trial reward [{avg_trial_rewards.item():.2f}] | Model iteration [{model_iteration_info.model_name}@{model_iteration_info.iteration}]"
                    )

            trial_step_index += 1
            self.step_index += 1



        await self.datastore.delete_trials([session.trial_id])


async def run_batch(nb_trials, nb_parallel_trials, wait_for_training):
    logging.debug("Starting enterprise batch with training")
    runner = ent_run.TrialRunner("pong", cog_settings)
    datastore = await runner.get_datastore()

    registry = await runner.get_model_registry()
    rl_model = await get_initial_model(registry)
    model_trainer = ModelTrainer(model=rl_model, datastore=datastore)

    start = time.time()
    batch = await runner.run_simple_batch(
        nb_trials, nb_parallel_trials, None, pre_trial_callback, post_trial_callback
    )
    trainer = await runner.run_simple_trial_training(
        batch, trial_callback=model_trainer.trial_callback, actor_names=[PLAYER_ACTOR_NAME]
    )
    trainer.set_nb_parallel_trials(10)

    logging.debug(f"Master waiting for trials to end...")
    batch_ended_normally = await batch.wait()
    trials_time = time.time() - start

    nb_ticks_per_sec = total_trial_steps / trials_time
    logging.info(
        f"Number of trial steps run [{total_trial_steps}], number of samples trained [{model_trainer.total_samples}]"
    )
    logging.info(
        f"Ran for {trials_time:.2f} sec : {nb_ticks_per_sec:.2f} steps/sec", flush=True
    )

    if wait_for_training:
        if not batch_ended_normally:
            logging.warning(f"The batch did not end normally")
        logging.debug(f"Waiting for training to finish...")
        await trainer.wait()
        logging.debug(f"Training finished.")

        end = time.time()
        training_time = end - start

        serial_model = bench_model.serialize_model(model_trainer.rl_model)
        iteration_info = await registry.store_model(
            MODEL_NAME, serial_model, {"batch_done": batch.id}
        )
        logging.info(
            f"Model [{MODEL_NAME}] final iteration [{iteration_info.iteration}] saved"
        )

        # This is not a very good metric as it averages computation while the trial is running and
        # computation alone (with full computer resources).
        logging.info(
            f"Trainer ran for [{training_time:.2f}] sec: [{model_trainer.total_samples / training_time:.2f}] samples/sec"
        )


def main(total_trials=1000, parallel_trials=10, wait_for_training=False):
    if total_trials <= 0 or parallel_trials <= 0:
        raise RuntimeError("Invalid parameters (must be > 0)")

    if total_trials < parallel_trials:
        raise RuntimeError(
            f"Number of trials [{total_trials}] must be >= number of parallel trials [{parallel_trials}]"
        )

    logging.basicConfig(level=logging.INFO)

    logging.debug(f"Args: [{total_trials}] [{parallel_trials}] [{wait_for_training}]")
    asyncio.run(run_batch(total_trials, parallel_trials, wait_for_training))


if __name__ == "__main__":
    fire.Fire(main)
