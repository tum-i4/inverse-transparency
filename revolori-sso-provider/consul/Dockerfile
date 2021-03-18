# base image
FROM consul:latest

# add the config file
COPY ./config/consul-config.json /consul/config/consul-config.json

# expose ports
EXPOSE 5431

# run consul
CMD consul agent -server -bind 0.0.0.0 -client 0.0.0.0 -bootstrap-expect 1 -config-file=/consul/config/consul-config.json

