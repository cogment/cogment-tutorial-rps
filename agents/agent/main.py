import cogment
import cog_settings

import asyncio
import random

from data_pb2 import Action, ROCK, PAPER, SCISSORS

MOVES = [ROCK, PAPER, SCISSORS]
MOVES_STR = ["👊 rock", "✋ paper", "✌️ scissors"]

async def random_player(actor_session):
    actor_session.start()
    print(f"[Agent '{actor_session.name}'] trial {actor_session.get_trial_id()} starts!")

    async for event in actor_session.event_loop():
        if "observation" in event:
            next_action = Action(move=random.choice(MOVES))
            print(f"[Agent '{actor_session.name}'] will play {MOVES_STR[next_action.move]}")
            actor_session.do_action(next_action)
            print(f"[Agent '{actor_session.name}'] played")


async def main():
    print("Agent service up and running.")

    context = cogment.Context(cog_settings=cog_settings, user_id='foo')

    context.register_actor(
        impl=random_player,
        impl_name="random",
        actor_classes=["player"])

    await context.serve_all_registered(port=9000)

if __name__ == '__main__':
    asyncio.run(main())
