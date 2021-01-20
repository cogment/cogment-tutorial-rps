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
    state = {
        "rounds_count": 0,
        "p1": {
            "won_rounds_count": 0
        },
        "p2": {
            "won_rounds_count": 0
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
        if "actions" in event or "final_actions" in event:
            is_final = "final_actions" in event
            [p1_action, p2_action] = event["actions"] if "actions" in event else event["final_actions"]
            print(f"{p1.actor_name} played {MOVES_STR[p1_action.move]}")
            print(f"{p2.actor_name} played {MOVES_STR[p2_action.move]}")

            # Compute who wins, if the two players had the same move, nobody wins
            p1_state = PlayerState(
                won_last=p1_action.move == DEFEATS[p2_action.move],
                last_move=p1_action.move
            )
            p2_state = PlayerState(
                won_last=p2_action.move == DEFEATS[p1_action.move],
                last_move=p2_action.move
            )
            state["rounds_count"] += 1
            if p1_state.won_last:
                state["p1"]["won_rounds_count"] += 1
                print(f"{p1.actor_name} wins!")
            elif p2_state.won_last:
                state["p2"]["won_rounds_count"] += 1
                print(f"{p2.actor_name} wins!")
            else:
                print(f"draw.")

            # Generate and send observations
            observations = [
                (p1.actor_name, Observation(me=p1_state, them=p2_state)),
                (p2.actor_name, Observation(me=p2_state, them=p1_state)),
            ]
            if is_final:
                environment_session.end(observations)
            else:
                environment_session.produce_observations(observations)
        if "message" in event:
            (sender, message) = event["message"]
            print(f"environment received a message from '{sender}': - '{message}'")

    print("environment end")
    print(f"\t * {state['rounds_count']} rounds played")
    print(f"\t * {p1.actor_name} won {state['p1']['won_rounds_count']} rounds")
    print(f"\t * {p2.actor_name} won {state['p2']['won_rounds_count']} rounds")
    print(f"\t * {state['rounds_count'] - state['p1']['won_rounds_count'] - state['p2']['won_rounds_count']} draws")

async def main():
    print("Environment service starting...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=environment)

    await context.serve_all_registered(port=9000)

if __name__ == '__main__':
    asyncio.run(main())
