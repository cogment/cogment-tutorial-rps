# Copyright 2021 Artificial Intelligence Redefined <dev+cogment@ai-r.com>
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
from data_pb2 import PlayerAction, ROCK, PAPER, SCISSORS, TrialConfig

import cogment

import asyncio

MOVES = [ROCK, PAPER, SCISSORS]
MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

MOVES_PROMPT = ', '.join([ f"{name} ({idx + 1})" for idx, name in enumerate(MOVES_STR)])

async def main():
    print("Client starting...")

    context = cogment.Context(cog_settings=cog_settings, user_id="rps")

    async def human_player(actor_session):
        round_index = 0

        actor_session.start()

        def print_observation(observation):
            print(f"🧑 played {MOVES_STR[observation.snapshot.me.last_move]}")
            print(f"🤖 played {MOVES_STR[observation.snapshot.them.last_move]}")
            if observation.snapshot.me.won_last:
                print(f" -> 🧑 wins round #{round_index + 1}")
            elif observation.snapshot.them.won_last:
                print(f" -> 🤖 wins the round #{round_index + 1}")
            else:
                print(f" -> round #{round_index + 1} is a draw")

        async for event in actor_session.event_loop():
            if event.observation:
                observation = event.observation

                if round_index > 0:
                    # The only time the observation is not relevant is on the first round of the first game
                    print_observation(observation)

                if event.type == cogment.EventType.ACTIVE:
                    # Only play when the trial is active
                    print(f"\n-- Round #{round_index + 1} --\n")
                    move = None
                    while move is None:
                        human_input = input(f"What's your move: {MOVES_PROMPT} ? ")
                        try:
                            move_idx = int(human_input) - 1
                            if 0 <= move_idx < len(MOVES):
                                move=MOVES[move_idx]
                            else:
                                print(f"⚠️ Invalid move index '{human_input}'")
                        except:
                            print(f"⚠️ Unrecognized input '{human_input}'")

                    next_action = PlayerAction(move=move)
                    actor_session.do_action(next_action)
                    print("\n")
                    round_index += 1

    context.register_actor(
        impl=human_player,
        impl_name="human",
        actor_classes=["player"])

    # Create a controller
    controller = context.get_controller(endpoint=cogment.Endpoint("orchestrator:9000"))

    # Start a new trial
    trial_id = await controller.start_trial(trial_config=TrialConfig())
    print(f"Trial '{trial_id}' started")

    # Let the human actor join the trial
    await context.join_trial(trial_id=trial_id, endpoint=cogment.Endpoint("orchestrator:9000"), impl_name="human")
    print(f"Human actor joined trial '{trial_id}'")

    # Wait for the trial to end by itself
    async for trial_info in controller.watch_trials(trial_state_filters=[cogment.TrialState.ENDED]):
        if trial_info.trial_id == trial_id:
            break

    print(f"Trial '{trial_id}' ended")

if __name__ == '__main__':
    asyncio.run(main())
