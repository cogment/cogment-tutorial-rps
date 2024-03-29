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

import cog_settings
from data_pb2 import PlayerAction, ROCK, PAPER, SCISSORS

import cogment

import asyncio
import os
import random

PORT = int(os.getenv('RANDOM_AGENT_PORT'))
MOVES = [ROCK, PAPER, SCISSORS]

async def random_agent(actor_session):
    actor_session.start()

    async for event in actor_session.all_events():
        if event.observation:
            observation = event.observation
            if event.type == cogment.EventType.ACTIVE:
                action = PlayerAction(move=random.choice(MOVES))
                actor_session.do_action(action)

DEFEATS = {
    ROCK: PAPER,
    SCISSORS: ROCK,
    PAPER: SCISSORS
}

async def heuristic_agent(actor_session):
    actor_session.start()

    async for event in actor_session.all_events():
        if event.observation:
            observation = event.observation
            if event.type == cogment.EventType.ACTIVE:
                if observation.observation.me.won_last:
                    # I won the last round, let's play the same thing
                    actor_session.do_action(PlayerAction(move=observation.observation.me.last_move))
                elif observation.observation.them.won_last:
                    # I lost the last round, let's play what would have won
                    actor_session.do_action(PlayerAction(move=DEFEATS[observation.observation.them.last_move]))
                else:
                    # last round was a draw, let's play randomly
                    actor_session.do_action(PlayerAction(move=random.choice(MOVES)))

async def rock_agent(actor_session):
    actor_session.start()
    async for event in actor_session.all_events():
        if event.observation:
            if event.type == cogment.EventType.ACTIVE:
                actor_session.do_action(PlayerAction(move=ROCK))

async def main():
    print(f"Random & Heuristic agents service starting on port {PORT}...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")
    context.register_actor(
        impl=random_agent,
        impl_name="random_agent",
        actor_classes=["player",])

    context.register_actor(
        impl=heuristic_agent,
        impl_name="heuristic_agent",
        actor_classes=["player",])

    context.register_actor(
        impl=rock_agent,
        impl_name="rock_agent",
        actor_classes=["player",])

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT), prometheus_port=None)

if __name__ == '__main__':
    asyncio.run(main())
