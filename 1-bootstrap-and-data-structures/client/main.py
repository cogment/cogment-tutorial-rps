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
from data_pb2 import TrialConfig

import cogment

import asyncio

async def main():
    print("Client starting...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    # Create a controller
    controller = context.get_controller(endpoint=cogment.Endpoint("orchestrator:9000"))

    # Start a new trial
    trial_id = await controller.start_trial(trial_config=TrialConfig())
    print(f"Trial '{trial_id}' started")

    # Let the trial play for a while
    await asyncio.sleep(10)

    # Termination the trial
    await controller.terminate_trial(trial_id)
    print(f"Trial '{trial_id}' terminated")

if __name__ == '__main__':
    asyncio.run(main())
