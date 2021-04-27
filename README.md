# Cogment "Rock Paper Scissors" (RPS) tutorial

> ⚠️ 🚧 This is part of an upcoming release of cogment and still unstable.
>
> Current stable version can be found at <https://gitlab.com/cogment/cogment>

## Introduction

The Cogment framework is a high-efficiency, open source framework designed to enable the training of models in environments where humans and agents interact with the environment and each other continuously. It’s capable of distributed, multi-agent, multi-model training.

This repository includes the sources of the different steps of the Cogment RPS tutorial, detailed instructions are available at [docs.cogment.ai](https://docs.cogment.ai/).

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

For steps 1-5, in a separate terminal, trigger a trial with:

```
cogment run client
```

For step 6, you simply have to open localhost:3000 to trigger a trial

NOTE:

For step 6, you will need Node.js installed onto your computer
