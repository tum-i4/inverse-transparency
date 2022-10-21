# Building and Running the application

## Building the Application

There are several environments to build the application:

| Environment | Location | Description |
| :---------- | :------- | :---------- |
| `dev` | `./dev` | Build location for the development environment. |
| `prod` | `not present yet` |  |

## Environments

A build environment can be seen as a contained space with its own settings and configurations for building the application. Mostly they suit a specific purpose like the `dev` environment for easy prototyping and development testing.

### File Hierarchy

Each environment consists of following directories and files:

```
./<env>
 |-.env
 |-README.md
 |-docker-compose.yaml
 |-prebuild.sh
 |-setup.sh
 |-secrets
 |  `-<service>
 |-data
 |  `-<service>
 `-configs
    `-<service>

<env>: Environment to be used.
<service>: Service directory (only present if service needs it). Can be vault, consul, revolori, overseer or clotilde.
```

| Name | Description |
| :--- | :---------- |
| `.env` | File that describes the whole environment. Automatically used by `docker-compose.yaml`. *Main configuration is done here!* |
| `README.md` | Environment's `README` that explains behavior and tips for the environment. *Always read this first*. |
| `docker-compose.yaml` | Used for building the application's docker images and to run them jointly. |
| `prebuild.sh` | Used for setting up the environment before building: E.g. creating keys. |
| `setup.sh` | Used for setting up the environment after building: E.g. making a demo users. |
| `secrets` | Directory containing each service's secrets (keys, tokens, etc.) if needed. |
| `data` | Directory containing each service's persistent data storage (SQL data bases, Consul DB, etc.) if needed. |
| `configs` | Directory containing each service's configuration files (such as for vault and consul). |

## Build Environment Variable

Besides all other variables defined in the `.env` file, the `BUILD_ENV` takes a special role, since it is needed for certain building scripts to build the correct environment (e.g. in clotilde, since it needs all environment variables be present during built time for security reasons).

### Run

To run a environment first go to it:

```
$ cd ./<env>
```

If there exists a `prebuild.sh` then run it before building:

```
$ ./prebuild.sh
```

Then build the services. (This step only has to be done once if the services' code remains unchanged).

```
$ docker-compose [ --env-file custom.env ] build
```

Then run it. The `-d` flag runs it as a daemon (in the background), so it is optional.

```
$ docker-compose up [ -d ]
```

If the environment provides a `setup.sh` use it for setting up the environment:
First set the environment on the machine:

```
$ set -a && source .env
```

Then set it up using:

```
$ ./setup.sh
```

To stop the environment, please always use `docker-compose`:
```
$ docker-compose down

```
## Development Environment

- location: `./dev`
- `BUILD_ENV=dev`

This environment is meant for development usage. It runs `revolori`'s dependency services `vault` in development mode and does not run `consul` at all for easier and faster setup.
It runs all services via docker containers on the `host` machine network. This allows for fast swapping between locally (non docker built) services and their container twins, allowing for easy manual integration testing by rebuilding/recompiling a service locally (outside of a docker container). Runs all services with their hosts set to `127.0.0.1`.

For further information check the `README` ([link](dev/README.md)) in `./dev`.
