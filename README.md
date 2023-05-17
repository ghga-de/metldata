
[![tests](https://github.com/ghga-de/metldata/actions/workflows/unit_and_int_tests.yaml/badge.svg)](https://github.com/ghga-de/metldata/actions/workflows/unit_and_int_tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/ghga-de/metldata/badge.svg?branch=main)](https://coveralls.io/github/ghga-de/metldata?branch=main)

# Metldata

metldata - A framework for handling metadata based on ETL, CQRS, and event sourcing.

## Description

<!-- Please provide a short overview of the features of this service.-->

TBD.


## Installation
We recommend using the provided Docker container.

A pre-build version is available at [docker hub](https://hub.docker.com/repository/docker/ghga/metldata):
```bash
docker pull ghga/metldata:0.1.0
```

Or you can build the container yourself from the [`./Dockerfile`](./Dockerfile):
```bash
# Execute in the repo's root dir:
docker build -t ghga/metldata:0.1.0 .
```

For production-ready deployment, we recommend using Kubernetes, however,
for simple use cases, you could execute the service using docker
on a single server:
```bash
# The entrypoint is preconfigured:
docker run -p 8080:8080 ghga/metldata:0.1.0 --help
```

If you prefer not to use containers, you may install the service from source:
```bash
# Execute in the repo's root dir:
pip install .

# To run the service:
metldata --help
```

## Configuration
### Parameters

The service requires the following configuration parameters:
- **`source_event_topic`** *(string)*: Name of the topic to which source events are published. Default: `source_events`.

- **`source_event_type`** *(string)*: Name of the event type for source events. Default: `source_event`.

- **`metadata_model_path`** *(string)*: The path to the metadata model defined in LinkML.

- **`submission_store_dir`** *(string)*: The directory where the submission JSONs will be stored.

- **`accession_store_path`** *(string)*: A file for storing the already registered accessions.

- **`prefix_mapping`** *(object)*: Specifies the ID prefix (values) per resource type (keys). Can contain additional properties.

  - **Additional Properties** *(string)*

- **`suffix_length`** *(integer)*: Length of the numeric ID suffix. Default: `8`.


### Usage:

A template YAML for configurating the service can be found at
[`./example-config.yaml`](./example-config.yaml).
Please adapt it, rename it to `.metldata.yaml`, and place it into one of the following locations:
- in the current working directory were you are execute the service (on unix: `./.metldata.yaml`)
- in your home directory (on unix: `~/.metldata.yaml`)

The config yaml will be automatically parsed by the service.

**Important: If you are using containers, the locations refer to paths within the container.**

All parameters mentioned in the [`./example-config.yaml`](./example-config.yaml)
could also be set using environment variables or file secrets.

For naming the environment variables, just prefix the parameter name with `metldata_`,
e.g. for the `host` set an environment variable named `metldata_host`
(you may use both upper or lower cases, however, it is standard to define all env
variables in upper cases).

To using file secrets please refer to the
[corresponding section](https://pydantic-docs.helpmanual.io/usage/settings/#secret-support)
of the pydantic documentation.



## Architecture and Design:
<!-- Please provide an overview of the architecture and design of the code base.
Mention anything that deviates from the standard triple hexagonal architecture and
the corresponding structure. -->

TBD.


## Development
For setting up the development environment, we rely on the
[devcontainer feature](https://code.visualstudio.com/docs/remote/containers) of vscode
in combination with Docker Compose.

To use it, you have to have Docker Compose as well as vscode with its "Remote - Containers"
extension (`ms-vscode-remote.remote-containers`) installed.
Then open this repository in vscode and run the command
`Remote-Containers: Reopen in Container` from the vscode "Command Palette".

This will give you a full-fledged, pre-configured development environment including:
- infrastructural dependencies of the service (databases, etc.)
- all relevant vscode extensions pre-installed
- pre-configured linting and auto-formating
- a pre-configured debugger
- automatic license-header insertion

Moreover, inside the devcontainer, a convenience commands `dev_install` is available.
It installs the service with all development dependencies, installs pre-commit.

The installation is performed automatically when you build the devcontainer. However,
if you update dependencies in the [`./setup.cfg`](./setup.cfg) or the
[`./requirements-dev.txt`](./requirements-dev.txt), please run it again.

## License
This repository is free to use and modify according to the
[Apache 2.0 License](./LICENSE).

## Readme Generation
This readme is autogenerate, please see [`readme_generation.md`](./readme_generation.md)
for details.
