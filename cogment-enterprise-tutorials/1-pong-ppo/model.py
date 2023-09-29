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

import io
from typing import Tuple, Union
from dataclasses import dataclass

import torch
import numpy as np
from torch.distributions.distribution import Distribution
from torch.distributions.categorical import Categorical

def initialize_layer(layer: torch.nn.Module, std: float = np.sqrt(2), bias_const: float = 0.0):
    """Layer initialization"""
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer

class PolicyValueNetwork(torch.nn.Module):
    """Policy and Value networks for Atari games"""

    def __init__(self, num_actions: int) -> None:
        super().__init__()
        self.num_actions = num_actions
        self.shared_network = torch.nn.Sequential(
            initialize_layer(torch.nn.Conv2d(6, 32, 8, stride=4)),
            torch.nn.ReLU(),
            initialize_layer(torch.nn.Conv2d(32, 64, 3, stride=2)),
            torch.nn.ReLU(),
            initialize_layer(torch.nn.Conv2d(64, 64, 3, stride=1)),
            torch.nn.ReLU(),
            torch.nn.Flatten(),
            initialize_layer(torch.nn.Linear(64 * 7 * 7, 512)),
            torch.nn.ReLU(),
        )
        self.actor = initialize_layer(torch.nn.Linear(512, num_actions), std=0.01)
        self.value = initialize_layer(torch.nn.Linear(512, 1), std=1)

    def get_value(self, observation: torch.Tensor) -> torch.Tensor:
        """Compute the value of being in a state"""
        observation_clone = observation.clone()
        observation_clone[:, [0, 1, 2, 3], :, :] /= 255.0
        return self.value(self.shared_network(observation_clone))

    def get_action(self, observation: torch.Tensor) -> Distribution:
        """Actions given observations"""
        observation_clone = observation.clone()

        observation_clone[:, [0, 1, 2, 3], :, :] /= 255.0
        action_logits = self.actor(self.shared_network(observation_clone))
        dist = Categorical(logits=action_logits)

        return dist

    def get_action_value(self, observation: torch.Tensor, action: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get value and log prob"""
        observation_clone = observation.clone()
        observation_clone[:, [0, 1, 2, 3], :, :] /= 255.0
        hidden = self.shared_network(observation_clone)

        # Log probs
        action_logits = self.actor(hidden)
        dist = Categorical(logits=action_logits)
        log_probs = dist.log_prob(action)

        # Value
        values = self.value(hidden)
        return values, log_probs, dist.entropy()


@dataclass
class Config:
    seed: int = 10
    num_epochs: int = 4
    num_iter: int = 500
    learning_rate: float = 0.00025
    batch_size: int = 128
    buffer_size: int = 10000
    update_freq: int = 128
    num_rollout_steps: int = 128
    max_training_steps: int = 20_000_000
    discount_factor: float = 0.99
    lambda_gae: float = 0.95
    device: str = "cuda"
    entropy_loss_coef: float = 0.01
    value_loss_coef: float = 0.5
    clipping_coef: float = 0.1
    grad_norm: float = 0.5
    num_actions: int = 6


class APPOModel:
    def __init__(self, network: Union[torch.nn.Module, None] = None) -> None:
        self.cfg = Config()
        if self.cfg.device == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        if network is None:
            self.network = PolicyValueNetwork(num_actions=self.cfg.num_actions)
        else:
            self.network = network
        self.network.to(self.device)
        self.network_optimizer = torch.optim.Adam(self.network.parameters(), lr=self.cfg.learning_rate, eps=1e-5)

    def update_parameters(
        self,
        observations: torch.Tensor,
        actions: torch.Tensor,
        advs: torch.Tensor,
        values: torch.Tensor,
        log_probs: torch.Tensor,
        num_epochs: int,
        num_updates: int = 0,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Update policy & value networks"""

        returns = advs + values
        num_obs = len(returns)
        global_idx = np.arange(num_obs)
        self.network.to(self.device)
        for i in range(num_epochs):
            np.random.seed(self.cfg.seed + i + num_updates)
            np.random.shuffle(global_idx)
            for i in range(0, num_obs, self.cfg.batch_size):
                # Get data in batch
                idx = global_idx[i : i + self.cfg.batch_size]
                if len(idx) < self.cfg.batch_size:
                    break

                # Minibatch of observations
                observation = observations[idx]
                action = actions[idx]
                return_ = returns[idx]
                adv = advs[idx].clone()
                old_value = values[idx]
                old_log_prob = log_probs[idx]

                # Normalize the advatanges between -1 and 1
                adv = (adv - adv.mean()) / (adv.std() + 1e-8)

                # Compute the value and values loss
                value, new_log_prob, entropy = self.network.get_action_value(
                    observation=observation, action=action.long().flatten()
                )
                value_loss_unclipped = (value - return_) ** 2
                value_clipped = old_value + torch.clamp(value - old_value, -self.cfg.clipping_coef, self.cfg.clipping_coef)
                value_loss_clipped = (value_clipped - return_) ** 2
                value_loss_max = torch.max(value_loss_unclipped, value_loss_clipped)
                value_loss = 0.5 * value_loss_max.mean()

                # Get action distribution & the log-likelihood
                ratio = torch.exp(new_log_prob.view(-1, 1) - old_log_prob)

                # Compute policy loss
                policy_loss_1 = -adv * ratio
                policy_loss_2 = -adv * torch.clamp(ratio, 1 - self.cfg.clipping_coef, 1 + self.cfg.clipping_coef)
                policy_loss = torch.max(policy_loss_1, policy_loss_2).mean()

                # Loss
                entropy_loss = entropy.mean()
                loss = policy_loss - self.cfg.entropy_loss_coef * entropy_loss + value_loss * self.cfg.value_loss_coef

                # Update value network
                self.network_optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.cfg.grad_norm)
                self.network_optimizer.step()

        return policy_loss, value_loss

    @staticmethod
    async def compute_average_reward(rewards: list) -> torch.Tensor:
        """Compute the average reward of the last 100 episode"""
        last_100_rewards = rewards[np.maximum(0, len(rewards) - 100) : len(rewards)]
        return torch.vstack(last_100_rewards).mean()

    def compute_gae(
        self,
        rewards: torch.Tensor,
        values: torch.Tensor,
        dones: torch.Tensor,
        next_value: torch.Tensor,
        gamma: float = 0.99,
        lambda_: float = 0.95,
    ):
        """Compute Generalized Advantage Estimation (GAE). See equations 11 & 12 in
        https://arxiv.org/pdf/1707.06347.pdf
        """
        advs = []
        with torch.no_grad():
            gae = 0.0
            # dones = torch.cat((dones, torch.zeros(1, 1).to(self._torch_device)), dim=0)
            for i in reversed(range(len(rewards))):
                delta = rewards[i] + gamma * next_value * (1 - dones[i]) - values[i]
                gae = delta + gamma * lambda_ * (1 - dones[i]) * gae
                advs.append(gae)
                next_value = values[i]
        advs.reverse()

        return advs

class APPODataBufferSample:
    """APPO replay buffer's sample"""

    def __init__(
        self,
        observation: torch.Tensor,
        action: torch.Tensor,
        adv: torch.Tensor,
        value: torch.Tensor,
        log_prob: torch.Tensor,
    ):
        self.observation = observation
        self.action = action
        self.adv = adv
        self.value = value
        self.log_prob = log_prob

    def size(self) -> int:
        """get sample size"""
        return self.observation.size(dim=0)

class APPODataBuffer:
    """Replay buffer for PPO"""

    observations: torch.Tensor
    actions: torch.Tensor
    advs: torch.Tensor
    values: torch.Tensor
    log_probs: torch.Tensor

    def __init__(
        self,
        capacity: int,
        observation_shape: tuple,
        action_shape: tuple,
        device: torch.device = torch.device("cpu"),
        seed: int = 0,
        dtype: torch.dtype = torch.float32,
    ):
        self.capacity = capacity
        self.observation_shape = observation_shape
        self.action_shape = action_shape
        self.dtype = dtype
        self.device = device
        self.seed = seed

        # Initialize data storage
        self.observations = torch.zeros((self.capacity, *self.observation_shape), dtype=self.dtype)
        self.actions = torch.zeros((self.capacity, *self.action_shape), dtype=self.dtype)
        self.advs = torch.zeros((self.capacity, 1), dtype=self.dtype)
        self.values = torch.zeros((self.capacity, 1), dtype=self.dtype)
        self.log_probs = torch.zeros((self.capacity, 1), dtype=self.dtype)
        self._ptr = 0
        self.num_total = 0
        self.count = 0

    def add(
        self,
        observation: torch.Tensor,
        action: torch.Tensor,
        adv: torch.Tensor,
        value: torch.Tensor,
        log_prob: torch.Tensor,
    ) -> None:
        self.observations[self._ptr] = observation
        self.actions[self._ptr] = action
        self.advs[self._ptr] = adv
        self.values[self._ptr] = value
        self.log_probs[self._ptr] = log_prob
        self._ptr = (self._ptr + 1) % self.capacity
        self.num_total += 1

    def add_multi_samples(
        self, trial_obs: list, trial_act: list, trial_adv: list, trial_val: list, trial_log_prob: list
    ) -> None:
        for obs, act, adv, val, log_prob in zip(trial_obs, trial_act, trial_adv, trial_val, trial_log_prob):
            self.add(observation=obs, action=act, adv=adv, value=val, log_prob=log_prob)

        self.count += 1

    def sample(self, num) -> APPODataBufferSample:
        np.random.seed(self.seed + self.count)
        size = self.size()
        if size < num:
            indices = range(size)
        else:
            indices = np.random.choice(self.size(), size=num, replace=False)

        return APPODataBufferSample(
            observation=self.observations[indices].clone().to(self.device),
            action=self.actions[indices].clone().to(self.device),
            adv=self.advs[indices].clone().to(self.device),
            value=self.values[indices].clone().to(self.device),
            log_prob=self.log_probs[indices].clone().to(self.device),
        )

    def size(self):
        return self.num_total if self.num_total < self.capacity else self.capacity

class RolloutBuffer:
    """Rollout buffer for PPO"""

    def __init__(
        self,
        capacity: int,
        observation_shape: tuple,
        action_shape: tuple,
        observation_dtype: torch.dtype = torch.float32,
        action_dtype: torch.dtype = torch.float32,
        reward_dtype: torch.dtype = torch.float32,
    ) -> None:
        self.capacity = capacity
        self.observation_shape = observation_shape
        self.action_shape = action_shape
        self.observation_dtype = observation_dtype
        self.action_dtype = action_dtype
        self.reward_dtype = reward_dtype

        self.observations = torch.zeros((self.capacity, *self.observation_shape), dtype=self.observation_dtype)
        self.actions = torch.zeros((self.capacity, *self.action_shape), dtype=self.action_dtype)
        self.rewards = torch.zeros((self.capacity,), dtype=self.reward_dtype)
        self.dones = torch.zeros((self.capacity,), dtype=torch.float32)
        self.values = torch.zeros((self.capacity,), dtype=self.reward_dtype)
        self.log_probs = torch.zeros((self.capacity,), dtype=self.reward_dtype)

        self._ptr = 0
        self.num_total = 0

    def add(self, observation: torch.Tensor, action: torch.Tensor, reward: torch.Tensor, done: torch.Tensor, value: torch.Tensor,log_prob: torch.Tensor) -> None:
        """Add samples to rollout buffer"""
        if self.num_total < self.capacity:
            self.observations[self._ptr] = observation
            self.actions[self._ptr] = action
            self.rewards[self._ptr] = reward
            self.dones[self._ptr] = done
            self.values[self._ptr] = value
            self.log_probs[self._ptr] = log_prob
            self._ptr = (self._ptr + 1) % self.capacity
            self.num_total += 1

    def reset(self) -> None:
        """Reset the rollout"""
        self.observations = torch.zeros((self.capacity, *self.observation_shape), dtype=self.observation_dtype)
        self.actions = torch.zeros((self.capacity, *self.action_shape), dtype=self.action_dtype)
        self.rewards = torch.zeros((self.capacity,), dtype=self.reward_dtype)
        self.dones = torch.zeros((self.capacity,), dtype=torch.float32)
        self._ptr = 0
        self.num_total = 0

def serialize_model(model: APPOModel):
    model.network.to(torch.device("cpu"))
    stream = io.BytesIO()
    torch.save(model.network, stream)

    return stream.getvalue()


def deserialize_eval_model(serial_data):
    stream = io.BytesIO(serial_data)  # or stream.write(serial_data)
    network = torch.load(stream, map_location=torch.device("cpu"))
    network.eval()

    model = APPOModel(network)
    return model

def deserialize_training_model(serial_data):
    stream = io.BytesIO(serial_data)  # or stream.write(serial_data)
    network = torch.load(stream, map_location=torch.device("cpu"))
    network.train()

    model = APPOModel(network)
    return model


