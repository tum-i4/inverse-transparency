# base image
FROM vault:latest

# add the config file
COPY ./config/vault-config.json /vault/config/vault-config.json

# add start dev script
COPY ./vault-init .

ENV VAULT_TOKEN root

# run vault
CMD vault server -config=/vault/config/vault-config.json
