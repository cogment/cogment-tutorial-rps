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


########################################
# Imports
########################################

import cog_settings
from data_pb2 import Observation

import cogment

import asyncio
import os

import logging

logging.basicConfig(level=logging.INFO)

# new in step 3
from data_pb2 import PlayerState, ROCK, PAPER, SCISSORS

########################################
# Settings
########################################
PORT = int(os.getenv("ENVIRONMENT_PORT"))

# new in step 3
DEFEATS = {ROCK: PAPER, SCISSORS: ROCK, PAPER: SCISSORS}


########################################
# Environment Implementation Functions
########################################
async def rps_environment(environment_session: cogment.environment.EnvironmentSession):
    # initialization
    [p1, p2] = environment_session.get_active_actors()

    print(f"Start trial {environment_session.get_trial_id()}")

    # new in step 3
    if (
        environment_session.config is not None
        and environment_session.config.target_score >= 0
    ):
        target_score = environment_session.config.target_score
    else:
        target_score = 3

    # new in step 3
    state = {
        "rounds_count": 0,
        "p1": {"score": 0},
        "p2": {"score": 0},
    }

    # new in step 3
    p1_state = PlayerState(won_last=False, last_move=None)
    p2_state = PlayerState(won_last=False, last_move=None)

    environment_session.start(
        [  # register with the orchestrator that all data has been sent and the session can be started with an initial observation sent to all actors
            (p1.actor_name, Observation(me=p1_state, them=p2_state)),
            (p2.actor_name, Observation(me=p2_state, them=p1_state)),
        ]
    )

    # event loop
    async for event in environment_session.all_events():
        if event.actions:
            print(f"environment received the actions")
            # get actors actions
            [p1_action, p2_action] = [
                recv_action.action for recv_action in event.actions
            ]
            print(f"{p1.actor_name} did action {p1_action}")
            print(f"{p2.actor_name} did action {p2_action}")

            # Compute who wins, if the two players had the same move, nobody wins - new in step 3
            p1_state = PlayerState(
                won_last=p1_action.move == DEFEATS[p2_action.move],
                last_move=p1_action.move,
            )
            p2_state = PlayerState(
                won_last=p2_action.move == DEFEATS[p1_action.move],
                last_move=p2_action.move,
            )

            # keep track of winner/loser of each round - new in step 3
            state["rounds_count"] += 1
            if p1_state.won_last:
                state["p1"]["score"] += 1
                print(f"{p1.actor_name} wins!")
            elif p2_state.won_last:
                state["p2"]["score"] += 1
                print(f"{p2.actor_name} wins!")
            else:
                print(f"draw.")

            # produce observation of updated state (computed above) - changed in step 3
            observations = [
                (p1.actor_name, Observation(me=p1_state, them=p2_state)),
                (p2.actor_name, Observation(me=p2_state, them=p1_state)),
            ]

            # handle end of the game - changed in step 4
            if state["p1"]["score"] >= target_score:
                environment_session.add_reward(
                    value=1, confidence=1, to=[p1.actor_name]
                )  # new in step 4
                environment_session.add_reward(
                    value=-1, confidence=1, to=[p2.actor_name]
                )
                environment_session.end(observations)
            elif state["p2"]["score"] >= target_score:
                environment_session.add_reward(
                    value=-1, confidence=1, to=[p1.actor_name]
                )  # new in step 4
                environment_session.add_reward(
                    value=1, confidence=1, to=[p2.actor_name]
                )
                environment_session.end(observations)
            else:
                # target score is not reached, continue sending observations to actors
                environment_session.produce_observations(observations)

    # termination
    print(f"Trial {environment_session.get_trial_id()} ended:")
    print(f"\t * {state['rounds_count']} rounds played")
    print(f"\t * {p1.actor_name} won {state['p1']['score']} rounds")
    print(f"\t * {p2.actor_name} won {state['p2']['score']} rounds")
    print(
        f"\t * {state['rounds_count'] - state['p1']['score'] - state['p2']['score']} draws",
        flush=True,
    )


async def main():
    print(f"Environment service starting on port {PORT}...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=rps_environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT))


if __name__ == "__main__":
    asyncio.run(main())
