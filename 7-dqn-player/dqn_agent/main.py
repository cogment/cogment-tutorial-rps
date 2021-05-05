# Copyright 2021 Artificial Intelligence Redefined <dev+cogment@ai-r.com>
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

import cog_settings
from data_pb2 import PlayerAction, ROCK, PAPER, SCISSORS

import cogment
import numpy as np
import tensorflow as tf

import asyncio


# Parameters for DQN
batch_size = 50  # Size of batch taken from replay buffer
gamma = 0.99  # Discount factor for future rewards
optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
loss_function = tf.keras.losses.Huber()  # Using huber loss for stability
target_model_update_interval = (
    100  # How many samples between each update to the target model
)
epsilon_min = 0.05  # Minimum exploration rate
epsilon_max = 1.0  # Maximum exploration rate
epsilon_decay_per_tick = (
    epsilon_max - epsilon_min
) / 1000.0  # Reach the lowest exploration rate after 1000 ticks
max_replay_buffer_size = 100000

MOVES = [ROCK, PAPER, SCISSORS]
actions_count = len(MOVES)

# Create the deep Q-Network
def create_model():
    in_me_last_move = tf.keras.Input(name="obs_me_last_move", shape=(1))
    in_them_last_move = tf.keras.Input(name="obs_them_last_move", shape=(1))
    one_hot_move = tf.keras.layers.experimental.preprocessing.CategoryEncoding(
        name="one_hot_move", max_tokens=len(MOVES), output_mode="binary"
    )
    one_hot_me_last_move = one_hot_move(in_me_last_move)
    one_hot_them_last_move = one_hot_move(in_them_last_move)
    concat_ins = tf.keras.layers.concatenate(
        [one_hot_me_last_move, one_hot_them_last_move]
    )
    hidden_layer = tf.keras.layers.Dense(24, activation="relu")(concat_ins)
    outs = tf.keras.layers.Dense(actions_count, activation="linear")(hidden_layer)
    return tf.keras.Model(
        inputs=[in_me_last_move, in_them_last_move], outputs=outs, name="rps_dqn_policy"
    )


# Convert a Cogment observation to an input usable with the model
def model_ins_from_observations(observations):
    return {
        "obs_me_last_move": np.array([[o.snapshot.me.last_move] for o in observations]),
        "obs_them_last_move": np.array(
            [[o.snapshot.them.last_move] for o in observations]
        ),
    }


# Create the replay buffer datastructure
def create_replay_buffer():
    return {
        "obs_me_last_move": np.array([]),
        "obs_them_last_move": np.array([]),
        "action": np.array([]),
        "reward": np.array([]),
        "next_obs_me_last_move": np.array([]),
        "next_obs_them_last_move": np.array([]),
    }


# Bunch of global variables, it's generally a bad idea,
# It works here because we only have one instance of the dqn_agent service.
_model = create_model()
_target_model = create_model()
_epsilon = epsilon_max
_rb = create_replay_buffer()
_collected_samples_count = 0


def get_and_update_epsilon():
    global _epsilon
    current_epsilon = _epsilon
    _epsilon -= epsilon_decay_per_tick
    _epsilon = max(_epsilon, epsilon_min)
    return current_epsilon


def append_trial_replay_buffer(trial_rb):
    global _rb
    global _collected_samples_count

    trial_rb_size = len(trial_rb["obs_me_last_move"])

    for key in _rb.keys():
        # Append the trial data to the current vector
        _rb[key] = np.append(_rb[key], trial_rb[key])
        # Enfore the size limit by discarding older data
        if len(_rb[key]) > max_replay_buffer_size:
            _rb[key] = _rb[key][-max_replay_buffer_size:]

    _collected_samples_count += trial_rb_size
    rb_size = len(_rb["obs_me_last_move"])

    # Sanity check, all vectors in the replay buffer should have the same size
    for key in _rb.keys():
        assert rb_size == len(_rb[key])

    print(
        f"{trial_rb_size} new samples stored after a trial, now having {rb_size} samples over a total of {_collected_samples_count} collected samples."
    )


def train():
    global _model
    global _target_model

    rb_size = len(_rb["obs_me_last_move"])

    if rb_size >= batch_size:
        # Step 1 - Randomly select a batch
        batch_indices = np.random.choice(range(rb_size), size=batch_size)
        batch_rb = create_replay_buffer()
        for key in batch_rb.keys():
            batch_rb[key] = np.take(_rb[key], batch_indices)

        # Step 2 - Compute target q values
        ## Predict the expected reward for the next observation of each sample
        ## Use the target model for stability
        target_actions_q_values = _target_model(
            {
                "obs_me_last_move": batch_rb["next_obs_me_last_move"],
                "obs_them_last_move": batch_rb["next_obs_them_last_move"],
            }
        )

        ## target Q value = reward + discount factor * expected future reward
        target_q_values = batch_rb["reward"] + gamma * tf.reduce_max(
            target_actions_q_values, axis=1
        )

        # Step 3 - Compute estimated q values
        ## Create masks of the taken actions to later select relevant q values
        selected_actions_masks = tf.one_hot(batch_rb["action"], actions_count)

        with tf.GradientTape() as tape:
            ## Recompute q values for all the actions at each sample
            estimated_actions_q_values = _model(
                {
                    "obs_me_last_move": batch_rb["obs_me_last_move"],
                    "obs_them_last_move": batch_rb["obs_them_last_move"],
                }
            )

            ## Apply the masks to get the Q value for taken actions
            estimated_q_values = tf.reduce_sum(
                tf.multiply(estimated_actions_q_values, selected_actions_masks), axis=1
            )

            ## Compute loss between the target Q values and the estimated Q values
            loss = loss_function(target_q_values, estimated_q_values)
            print(f"loss={loss.numpy()}")

            ## Backpropagation!
            grads = tape.gradient(loss, _model.trainable_variables)
            optimizer.apply_gradients(zip(grads, _model.trainable_variables))

        # Update the target model
        if _collected_samples_count % target_model_update_interval == 0:
            _target_model.set_weights(_model.get_weights())


async def dqn_agent(actor_session):
    actor_session.start()

    trial_rb = create_replay_buffer()

    async for event in actor_session.event_loop():
        if event.observation:
            model_ins = model_ins_from_observations([event.observation])
            if event.type == cogment.EventType.ACTIVE:

                if np.random.rand(1)[0] < get_and_update_epsilon():
                    # Take random action
                    action = np.random.choice(actions_count)
                else:
                    model_outs = _model(model_ins, training=False)
                    action = tf.math.argmax(model_outs[0]).numpy()
                actor_session.do_action(PlayerAction(move=action))

                trial_rb["obs_me_last_move"] = np.append(
                    trial_rb["obs_me_last_move"], model_ins["obs_me_last_move"]
                )
                trial_rb["obs_them_last_move"] = np.append(
                    trial_rb["obs_them_last_move"], model_ins["obs_them_last_move"]
                )
                trial_rb["action"] = np.append(trial_rb["action"], [action])
                trial_rb["reward"] = np.append(trial_rb["reward"], [0.0])
            else:
                trial_rb["obs_me_last_move"] = np.append(
                    trial_rb["obs_me_last_move"], model_ins["obs_me_last_move"]
                )
                trial_rb["obs_them_last_move"] = np.append(
                    trial_rb["obs_them_last_move"], model_ins["obs_them_last_move"]
                )
        for reward in event.rewards:
            trial_rb["reward"][reward.tick_id] = reward.value

    # Shifting the observations to get the next observations
    trial_rb["next_obs_me_last_move"] = trial_rb["obs_me_last_move"][1:]
    trial_rb["next_obs_them_last_move"] = trial_rb["obs_them_last_move"][1:]
    # Dropping the last row, as it only contains the last observations
    trial_rb["obs_me_last_move"] = trial_rb["obs_me_last_move"][:-1]
    trial_rb["obs_them_last_move"] = trial_rb["obs_them_last_move"][:-1]
    append_trial_replay_buffer(trial_rb)
    train()


async def main():
    print("Deep Q Learning agents service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")
    context.register_actor(
        impl=dqn_agent,
        impl_name="dqn_agent",
        actor_classes=[
            "player",
        ],
    )

    await context.serve_all_registered(cogment.ServedEndpoint(port=9000))


if __name__ == "__main__":
    asyncio.run(main())
