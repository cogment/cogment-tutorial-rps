# Copyright 2021 AI Redefined Inc. <dev+cogment@ai-r.com>
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
from data_pb2 import EnvironmentConfig

import cogment

import asyncio
import datetime
import os

ORCHESTRATOR_ENDPOINT = f"grpc://{os.getenv('ORCHESTRATOR_HOST')}:{os.getenv('ORCHESTRATOR_PORT')}"
ENVIRONMENT_ENDPOINT = f"grpc://{os.getenv('ENVIRONMENT_HOST')}:{os.getenv('ENVIRONMENT_PORT')}"
RANDOM_AGENT_ENDPOINT = f"grpc://{os.getenv('RANDOM_AGENT_HOST')}:{os.getenv('RANDOM_AGENT_PORT')}"
DQN_AGENT_ENDPOINT = f"grpc://{os.getenv('DQN_AGENT_HOST')}:{os.getenv('DQN_AGENT_PORT')}"

async def main():
    print("Client starting...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    # Create a controller
    controller = context.get_controller(endpoint=cogment.Endpoint(ORCHESTRATOR_ENDPOINT))

    # Define 2 actors

    actor_1_params = cogment.ActorParameters(
        cog_settings,
        name="player_1",
        class_name="player",
        endpoint=DQN_AGENT_ENDPOINT,
        implementation="dqn_agent"
    )
    actor_2_params = cogment.ActorParameters(
        cog_settings,
        name="player_2",
        class_name="player",
        endpoint=RANDOM_AGENT_ENDPOINT,
        implementation="heuristic_agent"
    )

    # Configure the environment
    environment_config=EnvironmentConfig(
        target_score=5
    )

    # Assemble everything in the trial parameters
    trial_params=cogment.TrialParameters(
        cog_settings,
        environment_name="env",
        environment_endpoint=ENVIRONMENT_ENDPOINT,
        environment_config=environment_config,
        actors=[
            actor_1_params,
            actor_2_params,
        ]
    )

    # Listening for ended trials
    async def await_trial(trial_id):
        async for trial_info in controller.watch_trials(trial_state_filters=[cogment.TrialState.ENDED]):
            if trial_info.trial_id == trial_id:
                break

    # Start a trial campaign
    for i in range(1000):
        # Defining the trial id on the client side
        trial_id=f"rps-training#{i}-{datetime.datetime.now().isoformat()}"

        await_trial_task = asyncio.create_task(await_trial(trial_id))

        # Start a new trial using the trial params we just created
        trial_id = await controller.start_trial(trial_id_requested=trial_id, trial_params=trial_params)
        print(f"Trial '{trial_id}' ongoing")

        # Wait for the trial to end
        await await_trial_task

if __name__ == '__main__':
    asyncio.run(main())
