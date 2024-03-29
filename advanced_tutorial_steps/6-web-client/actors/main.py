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

MOVES = [ROCK, PAPER, SCISSORS]

PORT = os.getenv('RANDOM_AGENT_PORT')

async def random_agent(actor_session):
    actor_session.start()

    print(f"Random agent started on trial '{actor_session.get_trial_id()}'")

    async for event in actor_session.all_events():
        if event.observation:
            observation = event.observation
            print(f"'{actor_session.name}' received an observation: '{observation}'")
            if event.type == cogment.EventType.ACTIVE:
                action = PlayerAction(move=random.choice(MOVES))
                actor_session.do_action(action)
        for reward in event.rewards:
            print(f"'{actor_session.name}' received a reward for tick #{reward.tick_id}: {reward.value}")
        for message in event.messages:
            print(f"'{actor_session.name}' received a message from '{message.sender_name}': - '{message.payload}'")

DEFEATS = {
    ROCK: PAPER,
    SCISSORS: ROCK,
    PAPER: SCISSORS
}

async def heuristic_agent(actor_session):
    actor_session.start()

    print(f"Heuristic agent started on trial '{actor_session.get_trial_id()}'")

    async for event in actor_session.all_events():
        if event.observation:
            observation = event.observation
            print(f"'{actor_session.name}' received an observation: '{observation}'")
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
        for reward in event.rewards:
            print(f"'{actor_session.name}' received a reward for tick #{reward.tick_id}: {reward.value}")
        for message in event.messages:
            print(f"'{actor_session.name}' received a message from '{message.sender_name}': - '{message.payload}'")

async def main():
    print("Random & Heuristic agents actor service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")
    context.register_actor(
        impl=random_agent,
        impl_name="random_agent",
        actor_classes=["player",])

    context.register_actor(
        impl=heuristic_agent,
        impl_name="heuristic_agent",
        actor_classes=["player",])

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT), prometheus_port=None)

if __name__ == '__main__':
    asyncio.run(main())
