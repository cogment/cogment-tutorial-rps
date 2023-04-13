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
from data_pb2 import Observation, PlayerState, ROCK, PAPER, SCISSORS

import cogment

import asyncio
import os

PORT = os.getenv('ENVIRONMENT_PORT')

MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

DEFEATS = {
    ROCK: PAPER,
    SCISSORS: ROCK,
    PAPER: SCISSORS
}

async def environment(environment_session):
    # Default target score
    target_score = 3
    if environment_session.config is not None and environment_session.config.target_score >= 0:
        target_score = environment_session.config.target_score
    state = {
        "rounds_count": 0,
        "p1": {
            "score": 0
        },
        "p2": {
            "score": 0
        },
    }
    [p1, p2] = environment_session.get_active_actors()
    p1_state = PlayerState(won_last=False, last_move=None)
    p2_state = PlayerState(won_last=False, last_move=None)
    environment_session.start([
        (p1.actor_name, Observation(me=p1_state, them=p2_state)),
        (p2.actor_name, Observation(me=p2_state, them=p1_state)),
    ])

    async for event in environment_session.all_events():
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
            state["rounds_count"] += 1
            if p1_state.won_last:
                state["p1"]["score"] += 1
            elif p2_state.won_last:
                state["p2"]["score"] += 1

            # Generate and send observations
            observations = [
                (p1.actor_name, Observation(me=p1_state, them=p2_state)),
                (p2.actor_name, Observation(me=p2_state, them=p1_state)),
            ]

            # Handle end of game
            if state["p1"]["score"] >= target_score:
                environment_session.add_reward(value=1, confidence=1, to=[p1.actor_name])
                environment_session.add_reward(value=-1, confidence=1, to=[p2.actor_name])

                environment_session.end(observations)
            elif state["p2"]["score"] >= target_score:
                environment_session.add_reward(value=-1, confidence=1, to=[p1.actor_name])
                environment_session.add_reward(value=1, confidence=1, to=[p2.actor_name])

                environment_session.end(observations)
            else:
                environment_session.produce_observations(observations)

async def main():
    print(f"Environment service starting on port {PORT}...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    context.register_environment(impl=environment)

    await context.serve_all_registered(cogment.ServedEndpoint(port=PORT), prometheus_port=0)

if __name__ == '__main__':
    asyncio.run(main())
