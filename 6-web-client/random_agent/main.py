# Copyright 2020 Artificial Intelligence Redefined <dev+cogment@ai-r.com>
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

import cogment
import cog_settings

import asyncio
import random

from data_pb2 import Action, ROCK, PAPER, SCISSORS

MOVES = [ROCK, PAPER, SCISSORS]
MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

async def random_player(actor_session):
    actor_session.start()
    print(f"[Agent '{actor_session.name}'] trial {actor_session.get_trial_id()} starts!")

    async for event in actor_session.event_loop():
        if "observation" in event:
            next_action = Action(move=random.choice(MOVES))
            print(f"[Agent '{actor_session.name}'] will play {MOVES_STR[next_action.move]}")
            actor_session.do_action(next_action)
            print(f"[Agent '{actor_session.name}'] played")


async def main():
    print("Agent service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    context.register_actor(
        impl=random_player,
        impl_name="random",
        actor_classes=["player"])

    await context.serve_all_registered(cogment.ServedEndpoint(port=9000))

if __name__ == '__main__':
    asyncio.run(main())
