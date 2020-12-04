# Cogment "Rock Paper Scissors" demo

🚧

## Dependencies

This project relies on **v1.0.0-alpha1** of `cogment-orchestrator`, `cogment-cli` and `cogment-py-sdk` which haven't been released yet. Local version of those, from their respective `develop` branch, are expected to be available.

### `cogment-cli`

Make sure you retrieve the latest `develop` build

```
docker pull registry.gitlab.com/ai-r/cogment-cli:latest
```

Create a `cogment` alias that uses this dockerized version

```
alias cogment="docker run --rm -v$(pwd):/cogment -v/var/run/docker.sock:/var/run/docker.sock registry.gitlab.com/ai-r/cogment-cli:latest"
```

### `cogment-orchestrator`

Make sure you retrieve the latest `develop` build

```
docker pull registry.gitlab.com/ai-r/cogment-orchestrator:latest
```

### `cogment-py-sdk`

Build a local docker tag using the following in a locally checked out `cogment-py-sdk` directory.

```
docker build -t cogment/cogment-py-sdk:v1.0.0-alpha1 .
```

## Usage

Build the project:

```
cogment -v generate --python_dir=.
cogment run build
```

Launch the environment, agents and orchestrator:

```
cogment run start
```

Trigger a trial and play RPS:

```
cogment run play
```
