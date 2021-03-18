FROM node:14.4

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

EXPOSE 5420

ENV HOST=0.0.0.0
ENV BASE_URL=host.docker.internal

ENTRYPOINT [ "npm", "start"]