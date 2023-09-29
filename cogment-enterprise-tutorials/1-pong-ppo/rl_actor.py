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
import functools
import os

import cogment
import torch
import numpy as np

import cog_settings
from data_pb2 import Action
import model as bench_model
from environment import PONG_OBSERVATION_SHAPE


log = logging.getLogger(__name__)


def tensor_from_observation(observation):
    # Reshape observersion to match CNN input shape (see model.py)
    return torch.unsqueeze(torch.tensor(np.frombuffer(observation.value, dtype=np.uint8), dtype=torch.float32).reshape(tuple(PONG_OBSERVATION_SHAPE)).permute((2, 0, 1)), dim=0)

def action_from_tensor(action_tensor):
    return Action(value=action_tensor.cpu().numpy()[0])

async def rl_actor(model_registry, session):
    model_name = session.config.model_name

    latest_model = await model_registry.track_latest_model(model_name, bench_model.deserialize_eval_model, 30)
    await latest_model.wait_for_available()

    session.start()
    logging.info(f"Trial [{session.get_trial_id()}] started")

    step_count = 0
    async for event in session.all_events():
        if event.observation:
            obs_tensor = tensor_from_observation(event.observation.observation)
            if event.type != cogment.EventType.ACTIVE:
                continue
            step_count += 1

            model, model_iteration_info = await latest_model.get()
            with torch.no_grad():
                dist = model.network.get_action(obs_tensor.to(model.device))
                action = action_from_tensor(dist.sample())

            session.do_action(action)

    logging.info(f"Trial [{session.get_trial_id()}] ended: \n\t- [{step_count}] steps taken, \n\t- last model iteration used [{model_iteration_info.iteration}]")


async def main():
    context = cogment.Context(cog_settings=cog_settings, user_id="pong")
    model_registry = await context.get_model_registry_v2()

    actor_func = functools.partial(rl_actor, model_registry)
    context.register_actor(actor_func, "appo", ["player"])

    await context.serve_all_registered(
        directory_registration_host=os.getenv("DIRECTORY_REGISTRATION_HOST", "localhost")
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
