# base image
FROM vault:latest

# add the config file
COPY ./config/vault-config.json /vault/config/vault-config.json

# expose port 5430
EXPOSE 5430

# run vault
CMD vault server -config=/vault/config/vault-config.json
