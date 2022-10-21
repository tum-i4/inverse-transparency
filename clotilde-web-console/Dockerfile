FROM node:14.4

WORKDIR /usr/src/app

COPY package*.json ./

ARG BUILD_ENV=prod

RUN npm install

COPY . .

# check which .env file to use based on environment variable
RUN ./make-build-env
RUN npm run build

ENV HOST=127.0.0.1
ENV PORT=5420
ENV BASE_URL=host.docker.internal

ENTRYPOINT [ "npm", "start"]
