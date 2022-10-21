#!/usr/bin/env bash

set -euo pipefail

HTTP_USER=$REVOLORI_HTTP_AUTH_USER
HTTP_PASSWD=$REVOLORI_HTTP_AUTH_PASSWD
REVOLORI_URL=http://$REVOLORI_HOST:$REVOLORI_PORT

# when adding users: please do not use whitespace inbetween the json, since this is a bash array
users=(
    '{"firstName":"Max","lastName":"Mustermann","password":"passwd","email":"mm@example.com","secondaryIDs":{"slack":["mm1","mm2"]}}'

    '{"firstName":"Maria","lastName":"Molewsko","password":"passwd","email":"maria@molewsko.com","secondaryIDs":{"gitlab":["mariamolewsko","maria1299"]}}'
)

DUMMY_DATA_COUNT=512
dummy_data=(
    'maria@molewsko.com'
    'mm@example.com'
)

setup-user() {
    local user=$1
    echo -e  "setting up user:\n$user"
    status=$(curl -u $HTTP_USER:$HTTP_PASSWD -X POST -v --silent --header "Content-Type: application/json" --data "$user" $REVOLORI_URL/user 2>&1 | grep "< HTTP/1.1" | awk '{printf $3}')
    if [[ $status != "201" ]]; then
        echo "error: Could not create user due to http status: $status"
        exit 1;
    fi
    echo ""
}

add-dummy-data() {
    local user=$1
    local date_end=$(date --date="yesterday" -I)
    local date_start=$(date --date="today - 21 days" -I)
    echo -e "Adding $DUMMY_DATA_COUNT dummy accesses for last three weeks to user: '$user'"
    # FIX: once new /generate endpoint has been provided
    status=$(curl -u $OVERSEER_ADMIN:$OVERSEER_ADMIN_PASSWD --verbose -X POST "http://$OVERSEER_HOST:$OVERSEER_PORT/generate?owner_rid=$user&date_start=$date_start&date_end=$date_end&number_of_entries=$DUMMY_DATA_COUNT" 2>&1 | grep "< HTTP/1.1" | awk '{printf $3}')
    if [[ $status != "200" ]]; then
        echo "error: Could not create user due to http status: $status"
        exit 1;
    fi
    echo ""
}

>&2 echo -e "\e[31m\nWARN: This is a development version of the system. DO NOT USE IN PRACTICE!\e[0m\n"

echo "> Setup users"
for user in "${users[@]}"; do
    setup-user $user
done
echo -e "> Done\n"

echo "> Add dummy access data in overseer"
for user in "${dummy_data[@]}"; do
    add-dummy-data $user
done
echo "> Done"
