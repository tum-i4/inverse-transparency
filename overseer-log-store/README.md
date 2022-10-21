# Overseer Log Store
## Installation
Overseer requires Python 3.8.
Pipenv is recommended for installing Overseer.

```bash
$ mkdir .venv
$ pipenv install
```

## Configuration
Overseer reads its configuration from environment variables.
See `sample.env` for guidance.

You can set the variables freely, the only thing to keep in mind is that you will need
the public key of Revolori that is created during its setup.

## Running Overseer using Docker
Create a `.env` file according to the template `sample.env`.

Copy the public key from Revolori setup to the location of `$JWT_PUBLIC_KEY` set in `.env`:
```bash
$ set -a && source .env
$ cp ../revolori-sso-provider/dev_keys/ecdsa_key.pub $JWT_PUBLIC_KEY
```

To start the services:
```bash
$ docker-compose up -d --build
```

To stop the services:
```bash
$ docker-compose down
```

## Development

Migrating the database:
```bash
$ ./migrate-db
```

Running the dev server:
```bash
$ ./dev-server
```

Creating new database migrations:
```bash
$ ./create-db-revision "Add X column to table Y"
```
 - Migrations are auto generated from the live database.
 - Optionally, delete the database and run the `migrate-db` script to make sure that the live schema hasn't been altered.
**The automatically generated migration script will be useless if the database schema has been altered since the last migration.**
 - [Migrations scripts cannot be automatically generated for all schema changes.](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)


## Testing

### Unit tests
Make sure to set up the environmental variables. Then run:
```bash
$ python -m pytest ./overseer
```

### System tests
These tests are designed to test a deployed system. Run:
```bash
$ pytest ./system_test [-P PROTOCOL] -E OVERSEER_ENDPOINT [-T TIMEOUT]
```
Parameters:
- OVERSEER_ENDPOINT: the server endpoint root of the to-be-tested Overseer
- PROTOCOL: the connection protocol (default: `https`)
- TIMEOUT: how long to wait for a response from the server (default: 3)
