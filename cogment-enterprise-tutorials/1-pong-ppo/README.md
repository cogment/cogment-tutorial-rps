# PPO Implementation with Cogment Enterprise

This folder contains an implementation of the Proximal Policy Optimization (PPO) algorithm using the Cogment framework for the classic Pong environment

## Setup

### Local

#### Prerequisites

- Python 3.9
- Cogment Enterprise Python SDK 0.4.0 (at the moment this needs to be retrieved from AIR as an archive file `cogment-enterprise-0.4.0.tar.gz`)

#### Installation

Run the following:

```shell
$ ./install.sh
```

This will create a virtual env in `./.venv` and install Cogment and the python dependencies in it, accept the Atari license and run Cogment code generation.

Alternatively these steps can be followed manually

- Install Cogment by following [these instructions](https://cogment.ai/docs/reference/cli#installation-script-compatible-with-linux-and-macos)
- Install Python dependencies
  ```shell
  pip install -r requirements.txt ./cogment-enterprise-0.4.0.tar.gz
  ```
- Activate Pong Atari environment
  ```shell
  AutoROM --accept-license
  ```
- Generate cogment settings
  ```shell
  python -m cogment.generate --spec=cogment.yaml --output=cog_settings.py
  ```

#### Run

> Do not forget to run that in the desired environment. In particular if you used the install script run `source .venv/bin/activate`

```shell
cogment launch -qq ./launch.yaml
```

## Docker

- Build docker. Note that it is required to have access to `cogment-enterprise.tar.gz`
  ```shell
  docker build -f Dockerfile -t ppo_bench:latest .
  ```
- Run docker
  ```shell
  docker run --rm -it ppo_bench:lastest
  ```
