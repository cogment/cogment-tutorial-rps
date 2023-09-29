# Cogment Tutorials

[Cogment](https://cogment.ai) is an innovative open source AI platform designed to leverage the advent of AI to benefit humankind through human-AI collaboration developed by [AI Redefined](https://ai-r.com). Cogment enables AI researchers and engineers to build, train and operate AI agents in simulated or real environments shared with humans. For the full user documentation visit <https://docs.cogment.ai>

This repository includes sources for the different core Cogment tutorials.

## "Rock Paper Scissors" (RPS) tutorial

The RPS tutorial uses the simple game "Rock Paper Scissors" as the context for creating a simple Cogment application from scratch. Detailed instructions are available at [docs.cogment.ai](https://docs.cogment.ai/cogment/tutorial/introduction/).

- [Step 1: Bootstrap the RPS project and define observation & action space data structures](./1-bootstrap-and-data-structures)
- [Step 2: Implement a first actor and environment](./2-random-player)
- [Step 3: Send & receive rewards](./3-rewards)
- [Step 4: Add a second actor implementation based on a heuristic](./4-heuristic-player)
- [Step 5: Add a human player in the loop](./5-human-player)
- [Step 6: Implement a web client for the human player](./6-web-client)
- [Step 7: Add a player trained with Reinforcement Learning using DQN](./7-dqn-player)

### Dependencies

The tutorial requires a Unix environment, it has been tested on Macos, Ubuntu and Windows WSL2, the following need to be available:

- a working installation of **Cogment**,
- a Python (>=3.7) setup with virtualenv,
- a Node.JS (>=14) setup (for step 6).

### Usage

From each of the step's directory you can run the following.

Run the code generation phase and build the project using

```
./run.sh build
```

Then launch the environment, agents and orchestrator services:

```
./run.sh services_start
```

For steps 1-5 & 7, in a separate terminal, trigger a trial with:

```
./run.sh client_start
```

For step 6, in a separate terminal, launch the web client using:

```
./run.sh web_client_start
```

It should open your web browser to <http://localhost:8000> (if not open it manually)

## Cogment enterprise tutorial

Cogment Enterprise is the enterprise version of Cogment, it consists of proprietary modules on top of Cogment open source.

- [Pong PPO: reference implementation of a distributed decentralized execution / centralized training reinforcement training loop using Petting Zoo's Pong environment](./cogment-enterprise-tutorials/1-pong-ppo/)

## Developers

### Release process

People having mainteners rights of the repository can follow these steps to release a version **MAJOR.MINOR.PATCH**. The versioning scheme follows [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

1. Run `./scripts/create_release_branch.sh MAJOR.MINOR.PATCH` to create the release branch and update the version of the package,
2. On the release branch, check and update the changelog if needed, update internal dependencies, and make sure everything's fine on CI,
3. Run `./scripts/tag_release.sh MAJOR.MINOR.PATCH` to create the specific version section in the changelog, merge the release branch in `main`, create the release tag and update the `develop` branch with those.

Updating the mirror repositories, is handled directly by the CI.
