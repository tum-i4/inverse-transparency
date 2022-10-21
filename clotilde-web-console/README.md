# Clotilde Web Console - Svelte App

## Getting Started

Create `.env` file with configuration for the app. See `sample.env` for an example configuration.

Install dependencies...

```shell
npm install
```

...then start dev server

```shell
npm run dev
```

The app is now running at [127.0.0.1:5420](http://127.0.0.1:5420). If you edit a file in the src folder, the page will reload to reflect your changes.

## Build and Run Production App

To build the app in production mode...

```shell
npm run build
```

...then start the production build of the app with

```shell
npm run start
```

### Deployment via nginx

To serve Clotilde via [nginx](https://www.nginx.com/):

#### Build Clotilde

1. Build as described above
2. Copy or link the resulting "public" folder to the web server root set in the nginx config

#### Configure nginx

In nginx.conf under the http section add a new server configuration:

```
server {
    listen 5420;
    server_name <SERVER_NAME>; # e.g. 127.0.0.1, or FQDN (domain)
    root <PATH_TO_BUILD>/public;

    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Linting

The project uses tslint. To run the linter on all source files...

```shell
npm run lint
```

## Adding Dependencies

When installing new dependencies always use `--save-dev` so Svelte compiles them correctly.

## Running in Docker Container

To run a production version of Clotilde using docker follow these steps.
From the project root directory:

* Set "BASE_URL" in .env file to `host.docker.internal`
* Build container: `docker build -t svelte/clotilde .`
* Run container: `docker run -p 5420:5420 svelte/clotilde`

# Production in Docker Container

To run the app in production in a docker container follow these steps:

First, create a `prod.env` according to `sample.env`, that includes the addresses at
which Clotilde can reach Overseer and Revolori.

Then build and run the application on the host server:

```
$ docker build inv-toolchain/clotilde .
$ docker run --rm -d --network host --name clotilde inv-toolchain/clotilde
```
