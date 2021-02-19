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

from data_pb2 import Observation, PlayerState, ROCK, PAPER, SCISSORS
import asyncio

MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

async def environment(environment_session):
    game_index = 0
    round_index = 0
    p1_state = PlayerState(current_game_score=0, last_round_win=False, last_round_move=None)
    p2_state = PlayerState(current_game_score=0, last_round_win=False, last_round_move=None)
    target_score = environment_session.config.target_score

    environment_session.start([
        ("player_1", Observation(game_index=game_index, round_index=round_index, me=p1_state, them=p2_state)),
        ("player_2", Observation(game_index=game_index, round_index=round_index, me=p2_state, them=p1_state))
    ])
    print(f"[Environment] trial {environment_session.get_trial_id()} starts, first player to reach {target_score} wins!")

    async for event in environment_session.event_loop():
        if "actions" in event:
            print(f"Game #{game_index + 1} / Round #{round_index + 1}")
            [p1, p2] = environment_session.get_active_actors()
            [p1_move, p2_move] = [action.move for action in event["actions"]]

            print(f"Player 1 '{p1.actor_name}' played: {MOVES_STR[p1_move]}")
            print(f"Player 2 '{p2.actor_name}' played: {MOVES_STR[p2_move]}")

            if p1_move == p2_move:
                print('Draw!')
                p1_state.last_round_win = False
                p2_state.last_round_win = False
            elif ((p1_move == ROCK and p2_move == SCISSORS) or
                (p1_move == PAPER and p2_move == ROCK) or
                (p1_move == SCISSORS and p2_move == PAPER)):
                print(f"Player 1 '{p1.actor_name}' wins!")
                p1_state.current_game_score += 1
                p1_state.last_round_win = True
                p2_state.last_round_win = False
            else:
                print(f"Player 2 '{p2.actor_name}' wins!")
                p2_state.current_game_score += 1
                p1_state.last_round_win = False
                p2_state.last_round_win = True

            p1_state.last_round_move = p1_move
            p2_state.last_round_move = p2_move

            if p1_state.current_game_score >= target_score:
                print(f"Player 1 '{p1.actor_name}' wins the game!")
                round_index = 0
                game_index +=1
            elif p2_state.current_game_score >= target_score:
                print(f"Player 2 '{p2.actor_name}' wins the game!")
                round_index = 0
                game_index +=1
            else:
                round_index +=1

            observations = [
                ("player_1", Observation(game_index=game_index, round_index=round_index, me=p1_state, them=p2_state)),
                ("player_2", Observation(game_index=game_index, round_index=round_index, me=p2_state, them=p1_state))
            ]

            if game_index>=environment_session.config.games_count:
                environment_session.end(observations=observations)
            else:
                environment_session.produce_observations(observations=observations)

            # Resetting the score whenever we start a new game
            if round_index == 0:
                p1_state.current_game_score = 0
                p2_state.current_game_score = 0

    print(f"[Environment] trial {environment_session.get_trial_id()} over")

async def main():
    print("Environment service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    context.register_environment(impl=environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=9000))

if __name__ == '__main__':
    asyncio.run(main())
