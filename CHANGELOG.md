# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

## v2.3.0 - 2023-09-29

### Added

- Separated content into `basic_tutorial_steps` and `advanced_tutorial_steps`
- Introduce reference implementation of a learning agent with cogment enterprise in `cogment-enterprise-tutorials`

### Changed

- Modified content of steps 1-4 of previous tutorials to present concepts in a different order.
- `run.sh` processes changed
  - install Cogment in virtual environment to reflect more up-to-date method for Cogment application implementation
  - changed `build` to `install`
- Upgrade Cogment js SDK to `2.0.8`

### Removed

- Implementing a learning agent with DQN -- does not use an up-to-date Cogment training loop.

## v2.2.0 - 2022-11-17

### Added

- Add a step 8 showcasing the directory.

### Changed

- Leveraging `cogment launch`
- Upgrade to React 18
- Use python built-in `venv` instead of `virtualenv`
- Upgrade to cogment python sdk 3.3.0

## v2.1.0 - 2022-04-12

### Added

- Add `./run.sh` scripts to start the services without relying on Docker.

### Changed

- Show the ability to provide `controller.start_trial` with `trial_params`.
- Requires cogment v2.2 and cogment-py-sdk v2.1.1

## v2.0.0 - 2022-01-17

- Updated to API v2.0

## v1.0.1 - 2021-09-27

### Changed

- Update to Cogment Orchestrator v1.0.3, Python SDK v1.2.0 and Javascript SDK v1.25.2.
- Update copyright notice to use the legal name of AI Redefined Inc.

## v1.0.0 - 2021-05-11

### Changed

- Naming changes to the DQN player tutorial to follow more closely convention of the algorithm.

## v1.0.0-beta3 - 2021-04-29

### Added

- New tutorial showing how to train an actor using reinforcement learning techniques

### Changed

- Update to the latest versions of the cogment modules

## v1.0.0-beta1 - 2021-04-08

## v1.0.0-alpha2 - 2021-04-06

### Changed

- Update to the latest versions of the cogment modules

## v1.0.0-alpha1 - 2021-03-30

- Initial public release.
