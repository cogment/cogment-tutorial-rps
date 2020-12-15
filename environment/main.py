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

from data_pb2 import Observation, ROCK, PAPER, SCISSORS
import asyncio

MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]
TARGET_SCORE = 3


async def environment(environment_session):
    p1_score = 0
    p2_score = 0

    environment_session.start([("*", Observation(p1_score=p1_score, p2_score=p2_score))])
    print(f"[Environment] trial {environment_session.get_trial_id()} starts!")

    async for event in environment_session.event_loop():
        if "actions" in event:
            [p1, p2] = environment_session.get_active_actors()
            [p1_move, p2_move] = [action.move for action in event["actions"]]

            print(f"Player 1 '{p1.actor_name}' played: {MOVES_STR[p1_move]}")
            print(f"Player 2 '{p2.actor_name}' played: {MOVES_STR[p2_move]}")

            if p1_move == p2_move:
                print('Draw!')
            elif ((p1_move == ROCK and p2_move == SCISSORS) or
                (p1_move == PAPER and p2_move == ROCK) or
                (p1_move == SCISSORS and p2_move == PAPER)):
                print(f"Player 1 '{p1.actor_name}' wins!")
                p1_score += 1
            else:
                print(f"Player 2 '{p2.actor_name}' wins!")
                p2_score +=1

            if p1_score >= TARGET_SCORE:
                print(f"Player 1 '{p1.actor_name}' wins the match!")
                environment_session.end(observations=[("*", Observation(p1_score=p1_score, p2_score=p2_score))])
            elif p2_score >= TARGET_SCORE:
                print(f"Player 2 '{p2.actor_name}' wins the match!")
                environment_session.end(observations=[("*", Observation(p1_score=p1_score, p2_score=p2_score))])
            else:
                environment_session.produce_observations([("*", Observation(p1_score=p1_score, p2_score=p2_score))])

    print(f"[Environment] trial {environment_session.get_trial_id()} over")

async def main():
    print("Environment service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    context.register_environment(impl=environment)

    await context.serve_all_registered(port=9000)

if __name__ == '__main__':
    asyncio.run(main())
