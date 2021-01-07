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

MOVES_PROMPT = ','.join([ f"{name} ({idx})" for idx, name in enumerate(MOVES_STR)])


async def main():
    print("Client up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    future_trial_finished = asyncio.get_running_loop().create_future()
    async def human_player(actor_session):
        nonlocal future_trial_finished
        observation = None

        actor_session.start()

        async for event in actor_session.event_loop():
            if "observation" in event:
                if not observation:
                    print(f"👊 / ✋ / ✌️ game starts!")
                    observation = event["observation"]
                else:
                    observation = event["observation"]
                    print(f"🤖 plays {MOVES_STR[observation.them.last_round_move]}")
                    if observation.me.last_round_win:
                        print(f"🧑 wins the round - 🧑 {observation.me.score} / 🤖 {observation.them.score}")
                    elif observation.them.last_round_win:
                        print(f"🤖 wins the round - 🧑 {observation.me.score} / 🤖 {observation.them.score}")
                    else:
                        print(f"it's a draw - 🧑 {observation.me.score} / 🤖 {observation.them.score}")

                print(f"\n---\n")
                move_idx = int(input(f'Your turn: {MOVES_PROMPT} ? '))
                next_action = Action(move=MOVES[move_idx])
                actor_session.do_action(next_action)
                print(f"🧑 plays {MOVES_STR[next_action.move]}")

        print(f"Trial over: 🧑 {observation.me.score} / 🤖 {observation.them.score}")
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
