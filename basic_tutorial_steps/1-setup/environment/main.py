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

########################################
# Imports
########################################

import cog_settings
from data_pb2 import Observation

import cogment

import asyncio
import os

import logging

logging.basicConfig(level=logging.INFO)

########################################
# Settings
########################################
PORT = int(os.getenv("ENVIRONMENT_PORT"))


########################################
# Environment Implementation Functions
########################################
async def rps_environment(environment_session):
    # initialization
    [p1, p2] = environment_session.get_active_actors()

    print(f"Start trial {environment_session.get_trial_id()}")

    # register with the orchestrator that all data has been sent and the session can be
    # started with an initial observation sent to all actors
    environment_session.start([("*", Observation())])

    # event loop
    async for event in environment_session.all_events():
        if event.actions:
            print(f"environment received the actions")

            # get actors actions (here empty)
            [p1_action, p2_action] = [
                recv_action.action for recv_action in event.actions
            ]

            print(f"{p1.actor_name} did action {p1_action}")
            print(f"{p2.actor_name} did action {p2_action}")

            # produce observation of state of the world (here empty)
            observation = Observation()

            # handle end of the game
            if event.type == cogment.EventType.ACTIVE:
                # The trial is active
                environment_session.produce_observations([("*", observation)])
            else:
                # The trial termination has been requested
                environment_session.end([("*", observation)])

    # termination
    print("environment end")


async def main():
    print(f"Environment service starting on port {PORT}...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=rps_environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT))


if __name__ == "__main__":
    asyncio.run(main())
