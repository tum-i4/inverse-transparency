# base image
FROM consul:latest

# add the config file
COPY ./config/consul-config.json /consul/config/consul-config.json

ENV HOST 127.0.0.1

# run consul
CMD consul agent -server -bind $HOST -client $HOST -bootstrap-expect 1 -config-file=/consul/config/consul-config.json

