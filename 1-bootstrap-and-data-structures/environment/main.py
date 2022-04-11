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
from data_pb2 import Observation

import cogment

import asyncio
import os

PORT = os.getenv('ENVIRONMENT_PORT')

async def environment(environment_session):
    print(f"Start trial {environment_session.get_trial_id()}")

    # Start the trial and send an initial observation to all actors
    environment_session.start([("*", Observation())])

    async for event in environment_session.all_events():
        if event.actions:
            actions = event.actions
            print(f"environment received the actions")
            for actor, recv_action in zip(environment_session.get_active_actors(), actions):
                print(f" actor '{actor.actor_name}' did action '{recv_action.action}'")
            observation = Observation()
            if event.type == cogment.EventType.ACTIVE:
                # The trial is active
                environment_session.produce_observations([("*", observation)])
            else:
                # The trial termination has been requested
                environment_session.end([("*", observation)])
        for message in event.messages:
            print(f"environment received a message from '{message.sender_name}': - '{message.payload}'")

    print("environment end")

async def main():
    print(f"Environment service starting on port {PORT}...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT), prometheus_port=0)

if __name__ == '__main__':
    asyncio.run(main())
