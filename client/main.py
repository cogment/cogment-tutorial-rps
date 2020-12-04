import cogment
import cog_settings

from data_pb2 import Action, ROCK, PAPER, SCISSORS, TrialConfig
import asyncio

MOVES = [ROCK, PAPER, SCISSORS]
MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

MOVES_PROMPT = ','.join([ f"{name} ({idx})" for idx, name in enumerate(MOVES_STR)])

async def human_player(actor_session):
    p1_score = None
    p2_score = None

    actor_session.start()

    async for event in actor_session.event_loop():
        if "observation" in event:
            observation = event["observation"]
            if not p1_score:
                print(f"Let's play 👊 / ✋ / ✌️!")
                p1_score=0
                p2_score=0
            if observation.p1_score > p1_score:
                print("🧑 won")
                p1_score = observation.p1_score
            elif observation.p2_score > p2_score:
                print("🤖 won")
                p2_score = observation.p2_score
            else:
                print("it's a draw")

            move_idx = int(input(f'Your turn: {MOVES_PROMPT} ? '))
            next_action = Action(move=MOVES[move_idx])
            await actor_session.do_action(next_action)
            print(f"You played {MOVES_STR[next_action.move]}")

    print(f"Trial over: 🧑 {p1_score} / 🤖 {p2_score}")


async def main():
    print("Client up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    # context.register_actor(
    #     impl=human_player,
    #     impl_name="human_player",
    #     actor_classes=["player"])

    # Create and join a new trial
    trial_id = None
    async def trial_controler(control_session):
        nonlocal trial_id
        print(f"Trial '{control_session.get_trial_id()}' starts")
        trial_id = control_session.get_trial_id()
        # TODO Investigate if we actually need that
        await asyncio.sleep(10)
        print(f"Trial '{control_session.get_trial_id()}' terminating")
        await control_session.terminate_trial()

    await context.start_trial(endpoint="orchestrator:9000", impl=trial_controler, trial_config=TrialConfig())

if __name__ == '__main__':
    asyncio.run(main())
