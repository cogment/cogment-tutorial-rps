# Cogment "Rock Paper Scissors" (RPS) tutorial

[Cogment](https://cogment.ai) is an innovative open source AI platform designed to leverage the advent of AI to benefit humankind through human-AI collaboration developed by [AI Redefined](https://ai-r.com). Cogment enables AI researchers and engineers to build, train and operate AI agents in simulated or real environments shared with humans. For the full user documentation visit <https://docs.cogment.ai>

This repository includes the sources of the different steps of the Cogment RPS tutorial, detailed instructions are available at [docs.cogment.ai](https://docs.cogment.ai/cogment/tutorial/introduction/).

## The steps

- [Step 1: Bootstrap the RPS project and define observation & action space data structures](./1-bootstrap-and-data-structures)
- [Step 2: Implement a first actor and environment](./2-random-player)
- [Step 3: Send & receive rewards](./3-rewards)
- [Step 4: Add a second actor implementation based on a heuristic](./4-heuristic-player)
- [Step 5: Add a human player in the loop](./5-human-player)
- [Step 6: Implement a web client for the human player](./6-web-client)
- [Step 7: Add a player trained with Reinforcement Learning using DQN](./7-dqn-player)

## Dependencies

The tutorial requires a working installation of the **Cogment cli** as well as a working **docker** implementation.

## Usage

From each of the step's directory you can run the following.

Run the code generation phase and build the project using

```
cogment run generate
cogment run build
```

Then launch the environment, agents and orchestrator services:

```
cogment run start
```

For steps 1-5 & 7, in a separate terminal, trigger a trial with:

```
cogment run client
```

For step 6, you simply have to open localhost:3000 to trigger a trial

NOTE:

For step 6, you will need Node.js installed onto your computer
