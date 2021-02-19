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

import cog_settings
from data_pb2 import PlayerAction, ROCK, PAPER, SCISSORS

import cogment

import asyncio
import random

MOVES = [ROCK, PAPER, SCISSORS]

async def random_agent(actor_session):
    actor_session.start()

    async for event in actor_session.event_loop():
        if "observation" in event:
            observation = event["observation"]
            print(f"'{actor_session.name}' received an observation: '{observation}'")
            action = PlayerAction(move=random.choice(MOVES))
            actor_session.do_action(action)
        if "reward" in event:
            reward = event["reward"]
            print(f"{actor_session.name} received a reward for tick #{reward.tick_id}: {reward.value}")
        if "message" in event:
            (sender, message) = event["message"]
            print(f"'{actor_session.name}' received a message from '{sender}': - '{message}'")
        if "final_data" in event:
            final_data = event["final_data"]
            for observation in final_data.observations:
                print(f"'{actor_session.name}' received a final observation: '{observation}'")
            for reward in final_data.rewards:
                print(f"{actor_session.name} received a final reward for tick #{reward.tick_id}: {reward.value}")
            for message in final_data.messages:
                (sender, message) = message
                print(f"'{actor_session.name}' received a final message from '{sender}': - '{message}'")

DEFEATS = {
    ROCK: PAPER,
    SCISSORS: ROCK,
    PAPER: SCISSORS
}

async def heuristic_agent(actor_session):
    actor_session.start()

    async for event in actor_session.event_loop():
        if "observation" in event:
            observation = event["observation"]
            print(f"'{actor_session.name}' received an observation: '{observation}'")
            if observation.me.won_last:
                # I won the last round, let's play the same thing
                actor_session.do_action(PlayerAction(move=observation.me.last_move))
            elif observation.them.won_last:
                # I lost the last round, let's play what would have won
                actor_session.do_action(PlayerAction(move=DEFEATS[observation.them.last_move]))
            else:
                # last round was a draw, let's play randomly
                actor_session.do_action(PlayerAction(move=random.choice(MOVES)))
        if "reward" in event:
            reward = event["reward"]
            print(f"'{actor_session.name}' received a reward for tick #{reward.tick_id}: {reward.value}")
        if "message" in event:
            (sender, message) = event["message"]
            print(f"'{actor_session.name}' received a message from '{sender}': - '{message}'")
        if "final_data" in event:
            final_data = event["final_data"]
            for observation in final_data.observations:
                print(f"'{actor_session.name}' received a final observation: '{observation}'")
            for reward in final_data.rewards:
                print(f"'{actor_session.name}' received a final reward for tick #{reward.tick_id}: {reward.value}")
            for message in final_data.messages:
                (sender, message) = event["message"]
                print(f"'{actor_session.name}' received a final message from '{sender}': - '{message}'")

async def main():
    print("Random & Heuristic agents service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")
    context.register_actor(
        impl=random_agent,
        impl_name="random_agent",
        actor_classes=["player",])

    context.register_actor(
        impl=heuristic_agent,
        impl_name="heuristic_agent",
        actor_classes=["player",])

    await context.serve_all_registered(cogment.ServedEndpoint(port=9000))

if __name__ == '__main__':
    asyncio.run(main())
