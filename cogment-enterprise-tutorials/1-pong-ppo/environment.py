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
import os

import numpy as np
import cogment
import gym as gymna
import supersuit as ss
from pettingzoo.atari import pong_v3

import cog_settings
from data_pb2 import Observation

PONG_OBSERVATION_SHAPE = [84, 84, 6]  # Observation in pong is an image
PONG_NB_PLAYERS = 2

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def atari_env_wrapper(env: gymna.Env) -> gymna.Env:
    """Wrapper for atari env"""
    env = ss.max_observation_v0(env, 2)
    env = ss.frame_skip_v0(env, 4)
    env = ss.clip_reward_v0(env, lower_bound=-1, upper_bound=1)
    env = ss.color_reduction_v0(env, mode="B")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.frame_stack_v1(env, 4)
    env = ss.agent_indicator_v0(env, type_only=False)

    return env

async def pong_environment(session):

    # Actor info
    actors = session.get_active_actors()
    actor_ids = [
        (actor_idx, actor.actor_name) for (actor_idx, actor) in enumerate(actors)
    ]
    (actor_idx, _) = actor_ids[0]
    player_names = []
    for actor in actors:
        player_names.append(actor.actor_name)

    # Pong environment
    env = pong_v3.env()
    env = atari_env_wrapper(env)

    # Reset the environment
    env.reset()
    observation, _, _, _ = env.last()

    # logging.info(f"obs env: {observation}")
    session.start([(player_names[0], Observation(value=observation.tobytes()))])

    async for event in session.all_events():
        if not event.actions:
            continue
        action_value = event.actions[actor_idx].action.value
        gym_action = np.array(action_value)

        env.step(gym_action)
        observation, reward, done, _ = env.last()

        session.add_reward(value=reward, confidence=1.0, to=player_names)
        if not done:
            session.produce_observations(
                [(player_names[0], Observation(value=observation.tobytes()))]
            )
        else:
            session.end(
                [(player_names[0], Observation(value=observation.tobytes()))]
            )
    env.close()


async def main():
    context = cogment.Context(cog_settings=cog_settings, user_id="pong")
    context.register_environment(pong_environment, "pong_environment")
    await context.serve_all_registered(
        directory_registration_host=os.getenv("DIRECTORY_REGISTRATION_HOST", "localhost")
    )


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(main())
