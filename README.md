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

If you chose to use the dockerized versin, creating a `cogment` alias makes it way easier. You can run the folliwng to define the alias in your running shell, you can add it to your `.bashrc`, `.zshrc` or similar to keep the alias around.

```
alias cogment='docker run --rm -v$(pwd):/cogment -v/var/run/docker.sock:/var/run/docker.sock cogment/cli:v1.0.0-alpha1'
```

> ⚠️ Take care to use simple quotes to create your alias, i.e. use `alias cogment='...'` for it to work properly.

## Usage

Generate protobufs, cog_settings and build the project:

```
cogment run generate
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
