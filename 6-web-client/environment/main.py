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
from data_pb2 import Observation, PlayerState, ROCK, PAPER, SCISSORS

import cogment

import asyncio

MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

DEFEATS = {
    ROCK: PAPER,
    SCISSORS: ROCK,
    PAPER: SCISSORS
}


async def environment(environment_session):
    target_game_score = 2
    state = {
        "games_count": 0,
        "p1": {
            "won_games_count": 0,
            "current_game_score": 0
        },
        "p2": {
            "won_games_count": 0,
            "current_game_score": 0
        },
    }
    print("environment starting")
    [p1, p2] = environment_session.get_active_actors()
    p1_state = PlayerState(won_last=False, last_move=None)
    p2_state = PlayerState(won_last=False, last_move=None)
    environment_session.start([
        (p1.actor_name, Observation(me=p1_state, them=p2_state)),
        (p2.actor_name, Observation(me=p2_state, them=p1_state)),
    ])

    async for event in environment_session.event_loop():
        if event.actions:
            [p1_action, p2_action] = [recv_action.action for recv_action in event.actions]

            # Compute who wins, if the two players had the same move, nobody wins
            p1_state = PlayerState(
                won_last=p1_action.move == DEFEATS[p2_action.move],
                last_move=p1_action.move
            )
            p2_state = PlayerState(
                won_last=p2_action.move == DEFEATS[p1_action.move],
                last_move=p2_action.move
            )
            if p1_state.won_last:
                state["p1"]["current_game_score"] += 1
            elif p2_state.won_last:
                state["p2"]["current_game_score"] += 1

            # Generate and send observations
            observations = [
                (p1.actor_name, Observation(me=p1_state, them=p2_state)),
                (p2.actor_name, Observation(me=p2_state, them=p1_state)),
            ]

            # Update the game scores
            if state["p1"]["current_game_score"] >= target_game_score:
                state["games_count"] += 1
                state["p1"]["current_game_score"] = 0
                state["p2"]["current_game_score"] = 0
                state["p1"]["won_games_count"] += 1

                environment_session.add_reward(value=1, confidence=1, to=[p1.actor_name])
                environment_session.add_reward(value=-1, confidence=1, to=[p2.actor_name])

                print(f"{p1.actor_name} won game #{state['games_count']}")
            elif state["p2"]["current_game_score"] >= target_game_score:
                state["games_count"] += 1
                state["p1"]["current_game_score"] = 0
                state["p2"]["current_game_score"] = 0
                state["p2"]["won_games_count"] += 1

                environment_session.add_reward(value=-1, confidence=1, to=[p1.actor_name])
                environment_session.add_reward(value=1, confidence=1, to=[p2.actor_name])

                print(f"{p2.actor_name} won game #{state['games_count']}")

            if event.type == cogment.EventType.ACTIVE and state["games_count"]<5:
                # The trial is active
                environment_session.produce_observations(observations)
            else:
                # The trial termination has been requested
                environment_session.end(observations)

        for message in event.messages:
            print(f"environment received a message from '{message.sender_name}': - '{message.payload}'")

    print("environment end")
    print(f"\t * {state['games_count']} games played")
    print(f"\t * {p1.actor_name} won {state['p1']['won_games_count']} games")
    print(f"\t * {p2.actor_name} won {state['p2']['won_games_count']} games")

async def main():
    print("Environment service starting...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=9000))

if __name__ == '__main__':
    asyncio.run(main())
