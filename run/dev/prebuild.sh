#!/usr/bin/env bash

set -euo pipefail

FILES=( ./secrets/overseer/issuer.pub ./secrets/vault/hmac ./secrets/vault/ecdsa_key ./secrets/vault/ecdsa_key.pub )

FILES_EXIST=1

# check if all files exists
for file in "${FILES[@]}"; do
    if [ -e $file ]; then
        echo "$file exists."
    else
        echo "$file does not exist."
        FILES_EXIST=0
    fi
done

if [ "x$FILES_EXIST" == "x1" ]; then
    echo "> All necessary files already exist. Exiting."
    exit 0
else
    echo "> Some keys are missing: Please proceed to create new keys."
fi

# create keys
mkdir -p ./secrets/vault
mkdir -p ./secrets/overseer
ssh-keygen -t ecdsa -b 384 -m pem -N "" -f ./secrets/vault/ecdsa_key
openssl rand -hex -base64 683 | tr -d '\n' > ./secrets/vault/hmac
cp ./secrets/vault/ecdsa_key.pub ./secrets/overseer/issuer.pub
