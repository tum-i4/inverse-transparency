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

The app is now running at [localhost:5420](http://localhost:5420). If you edit a file in the src folder the page will reload to reflect your changes.

## Build and Run Production App

To build the app in production mode...

```shell
npm run build
```

...then start the production build of the app with

```shell
npm run start
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
