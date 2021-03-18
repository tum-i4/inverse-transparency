# Revolori

**Revolori** is an authentication provider for the Inverse Transparency Toolchain. For more
details on Inverse Transparency, see https://www.inversetransparenz.de/.

## Run Revolori in Development Mode
If you develop code for Revolori, you can follow this part of the tutorial to quickly run it on your local machine.
Note that using this option means that Vault stores data in-memory and thus the data is **not persisted** between session.

To run a local instance of **Revolori**, follow these steps:

#### Install Go
Please check out [https://golang.org/]() to get the current version of Go.

#### Install HashiCorp Vault
Please check out [https://learn.hashicorp.com/vault/getting-started/install]().

#### Run Revolori in Development Mode
There are two options to run Revolori in development:
Automatically starting and configuring Vault with the provided tool `start-revolori-dev`
or manually setting up Vault to then start Revolori.

##### Automatically start Vault and Revolori
The Revolori starter allows to easily start a Revolori development server. A shell script
executes all the required commands.

If you start the development server for the first time, crypto keys need to be generated.
You can generate keys and start Revolori by running the following command:
````shell script
$ ./start-revolori-dev true
````
If you already created the keys in a previous run, it is sufficient to run:
````shell script
$ ./start-revolori-dev
````
The repository contains a set of crypto keys to sign the different authentication tokens.
Those tokens are automatically imported into the Vault development server.
These keys should only be used for development purposes!

##### Manually Start and Initialize a HashiCorp Vault Development Server
Alternatively, the server can be started manually. You first need to start a Vault dev
server:
````shell script
$ vault server -dev -dev-listen-address 127.0.0.1:5430 -dev-root-token-id "default_token"
````
Open a different terminal to initialize Vault:
````shell script
$ export VAULT_ADDR='http://127.0.0.1:5430'
$ vault secrets enable -path=users kv
$ vault secrets enable -path=keys kv
$ vault secrets enable -path=whitelist kv
$ vault kv put keys/hmac key=@dev_keys/hmac
$ vault kv put keys/ecdsa key=@dev_keys/ecdsa_key
````

For more information about the Vault dev server, please see
[https://learn.hashicorp.com/vault/getting-started/dev-server]().

To now start Revolori, run the following command in the project directory to create
an executable and to run the server in development mode:
````shell script
$ go build
$ ./revolori -dev
````

## Deploy Revolori for Production
If you want to deploy Revolori on a server or your local machine, follow this tutorial.
Contrary to development mode, data **is persisted** between sessions.

Revolori uses HashiCorp Vault to securely store data. As a storage Backend to persist the data,
HashiCorp Consul is used. To start both Vault and Consul as well as Revolori itself, it
relies on [Docker](https://www.docker.com/) for an easy deployment of the whole toolchain.

Follow the below steps to deploy Revolori.

#### Install Docker and Docker Compose
Please follow the official documentation to install
[Docker Engine](https://docs.docker.com/engine/install/) and
[Docker Compose](https://docs.docker.com/compose/install/) on your machine.


#### Clone the Git Repository
Clone the repository that contains Revolori and switch to Revolori's root directory:
````shell script
$ git clone https://gitlab.lrz.de/pit/t5-inv-t-tools.git
$ cd t5-inv-t-tools/revolori-sso-provider
````

#### Adjust Environment Variables
Copy the `sample.env` file and rename it to `.env`. You can then adjust the environment
variables in the `.env` file to your preferences. Most importantly,
set the preferred path to store logs of Vault (`VAULT_LOGS`) and data of Consul (`CONSUL_DATA`).

**Note:** You do not have an access token for Vault yet. Set all other environment
variables and leave `VAULT_TOKEN` as is. Continue with the next steps where you will get an
access token.

#### Initial Setup of Vault
There are two ways to initialize Vault: an automatic process that is supported by a script
or a manual setup.

##### Automatic Initial Setup of Vault
The automatic setup utilizes a script that guides you through the steps for the Vault
initialization. A few manual steps such as entering unseal keys to unseal Vault are still
required while running the script.

You can start the Initialization of Vault with the following command:
````shell script
$ sudo ./init-revolori-prod http://127.0.0.1:5430
````
In case the local address of Vault in its container is different, replace the argument
passed to the script to the correct address.

Make sure to type in the correct unseal keys and login
token for Vault when prompted. Otherwise, the script will fail.

##### Manual Initial Setup of Vault
In this step, we will initially configure Vault.

First, Spin up the docker container.

````shell script
$ docker-compose up -d --build
````

You can now start a shell within the docker container of Vault:
````shell script
$ docker-compose exec vault sh
````

Now you need to initialize Vault. Therefore, set the `VAULT_ADDRESS` environment variable
to access Vault within the opened shell:
````shell script
$ export VAULT_ADDR="http://127.0.0.1:5430"
$ vault operator init
````
Replace the value of `VAULT_ADDR` with the previously set environment variable of the `.env` file in case
you changed it.

Vault operator init can only be called once on a new, empty Vault. Note down the unseal keys
and the root token. Please checkout the offical Vault documentation for more information
on tokens and unseal keys.

Now, you can unseal the Vault. Repeat the following command three times by using three
different unseal keys:
````shell script
$ vault operator unseal
````

To complete the Vault setup, you need to login with the root token, initialize the secrets
engines and create and update the crypto keys:
````shell script
$ vault login
$ vault secrets enable -path=users kv
$ vault secrets enable -path=keys kv
$ vault secrets enable -path=whitelist kv
$ vault kv put keys/hmac key=@/vault/keys/hmac
$ vault kv put keys/ecdsa key=@/vault/keys/ecdsa_key
````

Exit the shell of the container:
````shell script
$ exit
````

#### Restart the Revolori Container
During the automatic or manual initialization of Vault, you acquired a Vault root token.
Set the `VAULT_TOKEN` environment variable in the `.env` file to your Vault root token.

The generated public key ecdsa_key.pub is **required for Overseer**, so either copy it over or create a soft link with `ln -s`.

For extra security, you can now optionally delete the `dev_keys` folder that holds the created crypto keys because the keys are stored in your Vault.

Rebuild and restart the Revolori container:
 ````shell script
$ docker-compose up --detach --build revolori
 ````

## Update a Deployed Revolori Instance
Once Revolori is deployed, it can be updated to the newest version by pulling the changes
from the Git repository and restarting the docker container of Revolori:
 ````shell script
$ git pull
$ docker-compose up --detach --build revolori
 ````
