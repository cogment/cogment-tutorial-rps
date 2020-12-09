# Cogment "Rock Paper Scissors" demo

🚧

## Dependencies

### `cogment-cli`

#### Binary version

Download the latest release from <https://github.com/cogment/cogment-cli/releases> and add the binary to your `$PATH` as `cogment` or add an alias.

#### Dockerized version

Retrieve the latest release

```
docker pull cogment/cli:v1.0.0-alpha1
```

Create a `cogment` alias that uses this dockerized version

```
alias cogment="docker run --rm -v$(pwd):/cogment -v/var/run/docker.sock:/var/run/docker.sock cogment/cli:v1.0.0-alpha1"
```

## Usage

Generate protobufs, cog_settings and build the project:

```
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
