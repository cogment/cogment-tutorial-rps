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

from data_pb2 import Action, ROCK, PAPER, SCISSORS, TrialConfig
import asyncio

MOVES = [ROCK, PAPER, SCISSORS]
MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

MOVES_PROMPT = ', '.join([ f"{name} ({idx + 1})" for idx, name in enumerate(MOVES_STR)])

def print_observation(observation):
    print(f"🧑 played {MOVES_STR[observation.me.last_round_move]}")
    print(f"🤖 played {MOVES_STR[observation.them.last_round_move]}")
    if observation.me.last_round_win:
        print(f" -> 🧑 wins the round - 🧑 {observation.me.current_game_score} / 🤖 {observation.them.current_game_score}")
    elif observation.them.last_round_win:
        print(f" -> 🤖 wins the round - 🧑 {observation.me.current_game_score} / 🤖 {observation.them.current_game_score}")
    else:
        print(f" -> it's a draw - 🧑 {observation.me.current_game_score} / 🤖 {observation.them.current_game_score}")

async def main():
    print("Client up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    future_trial_finished = asyncio.get_running_loop().create_future()
    async def human_player(actor_session):
        nonlocal future_trial_finished

        actor_session.start()

        async for event in actor_session.event_loop():
            if "observation" in event:
                observation = event["observation"]

                if observation.game_index > 0 or observation.round_index > 0:
                    # The only time the observation is not relevant is on the first round of the first game
                    print_observation(observation)

                if observation.round_index == 0:
                    if observation.game_index > 0:
                        print(f"\n** Game #{observation.game_index} over! - 🧑 {observation.me.current_game_score} / 🤖 {observation.them.current_game_score} **")
                    print(f"\n** Game #{observation.game_index + 1} starts! - 🧑 0 / 🤖 0 **")

                print(f"\n-- Round #{observation.round_index + 1} --\n")
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

                next_action = Action(move=move)
                actor_session.do_action(next_action)
                print("\n")
            if "final_data" in event:
                final_data = event["final_data"]

                assert len(final_data.observations) == 1
                assert len(final_data.messages) == 0

                print_observation(final_data.observations[0])

        future_trial_finished.set_result(True)

    context.register_actor(
        impl=human_player,
        impl_name="human",
        actor_classes=["player"])

    # Create and join a new trial
    future_trial_id = asyncio.get_running_loop().create_future()
    async def trial_controler(control_session):
        nonlocal future_trial_id
        print(f"Trial '{control_session.get_trial_id()}' starts")
        future_trial_id.set_result(control_session.get_trial_id())
        await future_trial_finished
        print(f"Trial '{control_session.get_trial_id()}' terminating")
        await control_session.terminate_trial()

    trial = asyncio.create_task(context.start_trial(endpoint="orchestrator:9000", impl=trial_controler, trial_config=TrialConfig()))
    trial_id = await future_trial_id
    # Join the trial as a human player
    await context.join_trial(trial_id=trial_id, endpoint="orchestrator:9000", impl_name="human")
    # Wait for the trial to be finished (well not really but didn't find a good way)
    # await asyncio.sleep(10)
    # future_trial_finished.set_result(True)
    await trial

if __name__ == '__main__':
    asyncio.run(main())
