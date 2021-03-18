# Revolori API Reference

Revolori is the provider of APIs for user management and authentication.

- [User Management](#user-management)
  - POST /user
  - GET /user
  - GET /user/:id
  - PUT /user/:id
  - DELETE /user/:id
- [User Authentication](#user-authentication)
  - POST /login
  - DELETE /login
  - GET /refresh
- [ID Mapping](#id-mapping)
  - GET /id
- [Utility](#utility)
  - GET /health

## User Management

The user routes are secured with [basic authentication](https://en.wikipedia.org/wiki/Basic_access_authentication). Thus, an HTTP request requires an authorization header that looks as follows:

**Key:** *Authorization* | **Value:** *Basic AUTH_NAME:AUTH_PASSWORD*

The environment variables AUTH_NAME and AUTH_Password can be defined in the environment file.  Please refer to the [README](README.md) in the Revolori git repository for more information on the environment file.

### POST /user

- **Description:** Signup a new user.
- **Accepts:** application/json
- **Authentication:** Basic
- **Body Parameters**
  - `firstName` (String): First name of the new user.
  - `lastName` (String): Last name of the new user.
  - `password` (String): Password of the new user.
  - `email` (String):Email address of the new user.
  - `secondaryIDs`: Arbitrary amount of additional IDs of the new user in the format "tool":[ "id1", "id2", ...].
- **Returned Content:** -
- **Returned Status Codes**
  - `200: OK`
  - `400: Bad Request`
  - `500: Internal Server Error`

**Exemplary Request Body:**

```json
{
    "firstName": "Some",
    "lastName": "User",
    "password": "somePassword",
    "email": "someEmail@example.com",
    "secondaryIDs":{
        "slack": ["slackID", "slackID2"],
        "gitlab": ["gitlabID", "gitlabID2"],
        "other": ["someID"]
    }
}
```

### GET /user

- **Description:** Get the data of all available users.
- **Accepts:** No specific headers required.
- **Authentication:** Basic
- **Returned Content**
  - List of users in JSON format.
  - If no user exists, an empty list is returned.
- **Returned Status Codes**
    `200: OK`
    `400: Bad Request`
    `500: Internal Server Error`

**Exemplare Response Body:**

```json
[
    {
        "firstName": "Max",
        "lastName": "Musterman",
        "email": "admin@it.de",
        "secondaryIDs": {
            "gitlab": [
                "admin_gitlab",
                "admin_gitlab2"
            ],
            "other": [
                "admin_other",
                "admin_other2"
            ],
            "slack": [
                "admin_slack",
                "admin_slack2"
            ]
        }
    },
    {
        "firstName": "Test",
        "lastName": "User",
        "email": "user@example.com",
        "secondaryIDs": {
            "slack": [
                "normal_slack",
                "normal_slack2"
            ],
            "test": [
                "normal_test"
            ]
        }
    }
]
```

### GET /user/:id

- **Description:** Get the data of the user with the specified id.
- **Accepts:** No specific headers required.
- **Authentication:** Basic
- **URL Parameters**
  - `:id` (string): ID of the desired user.
- **Returned Content:** Requested user in JSON format.
- **Returned Status Codes**
    `200: OK`
    `400: Bad Request`
    `500: Internal Server Error`

**Exemplare Response Body:**

```json
{
    "firstName": "Max",
    "lastName": "Musterman",
    "email": "admin@it.de",
    "secondaryIDs": {
        "gitlab": [
            "admin_gitlab",
            "admin_gitlab2"
        ],
        "other": [
            "admin_other",
            "admin_other2"
        ],
        "slack": [
            "admin_slack",
            "admin_slack2"
        ]
    }
}
```

### PUT /user/:id

- **Description:**  Update an available user.
- **Accepts:** application/json
- **Authentication:** Basic
- **URL Parameters:**
  - :id (string): id of the user to update.
- **Body Parameters**
  - `firstName` (String): First name of the new user.
  - `lastName` (String): Last name of the new user.
  - `password` (String): Password of the new user.
  - `email` (String): Email address of the new user. The email needs to match with the :id URL parameter and can't be changed.
  - `secondaryIDs`: Arbitrary amount of additional IDs of the new user in the format "tool":[ "id1", "id2", ...].
- **Returned Content:** -
- **Returned Status Codes**
  - `200: OK`
  - `400: Bad Request`
  - `500: Internal Server Error`

**Exemplary Request Body:**

```json
{
    "firstName": "User3",
    "lastName": "DifferentName",
    "password": "SomeOtherPassword",
    "email": "oneID@example.com",
    "secondaryIDs": {
        "slack": ["third_user"],
        "test": ["third_user"]
    }
}
```

### DELETE /user/:id

- **Description:**  Delete an available user.
- **Authentication:** Basic
- **URL Parameters:**
  - `:id` (string): id of the user to delete.
- **Returned Content:** -
- **Returned Status Codes**
  - `200: OK`
  - `500: Internal Server Error`


## User Authentication
### POST /login

- **Description:** Login of an existing user.
- **Authentication:** -
- **Accepts:** application/json
- **Body Parameters**
  - `email` (String): Email address of the user.
  - `password` (String): Password of the user.
- **Returned Content**
  - JWT authentication token in JSON Format.
  - Sets an HTTP-only cookie that includes a refresh token that can be used to refresh the authentication token.
- **Returned Status Codes**
  - `200: OK`
  - `400: Bad Request`
  - `500: Internal Server Error`

**Exemplary Request Body:**

```json
{
  "email": "someEmail@example.com",
  "password": "somePassword"
}
```

**Exemplary Response Body:**

```json
{
"token":"SomeBase64EncodedJWT"
}
```


### DELETE /login

- **Description:**  Log-out a user. This removes the cookie with that holds the refresh token and removes the entry related to the token from the whitelist.
  - In case a query parameter `all=true` is added to the request, all whitelist entries of the user that sends the request are deleted.  The query parameter can be omitted if a user only wants to logout from the current session and wants to keep other session, e.g. on different devices, alive.
  - Note that only the cookie with the refresh token and whitelist entries are deleted. The removal of the authentication token is up to the client.
- **Accepts:** No specific headers required.
- **Authentication:** -
- **Query Parameters**
  - `all=true`: remove all available whitelist entries of a user.
- **Returned Content:** -
- **Returned Status Codes**
  - `200: OK`

### GET /refresh

- **Description:**  Refreshes the authentication token.
- **Accepts:** No specific headers required.
- **Authentication:** Cookie with a valid refresh token
- **Returned Content:** JWT authentication token in JSON Format.
- **Returned Status Codes**
  - `200: OK`
  - `400: Bad Request`
  - `500: Internal Server Error`

**Exemplary Response Body:**

```json
{
"token":"SomeBase64EncodedJWT"
}
```

## ID Mapping
### GET /id

- **Description:**  Matches users' secondary IDs to their primary IDs.
- **Accepts:** application/json
- **Authentication:** -
- **Body Parameters**
  - key-value pairs of type `string:[string]`
  - The key describes the tool and the list of strings contains the secondary IDs for the specified tool.
- **Returned Content:** Mapping of transmitted secondary IDs to primary IDs for each provided tool.
- **Returned Status Codes**
  - `200: OK`
  - `400: Bad Request`
  - `500: Internal Server Error`

**Exemplary Request Body:**

```json
{
    "email": ["some_user@example.com"],
    "gitlab": ["another_user"],
    "slack": ["admin_slack", "some_user"]
}
```

**Exemplary Response Body:**

```json
{
    "email": {
        "some_user@example.com": "some_user@example.com"
    },
    "slack": {
        "admin_slack": "admin@example.com",
        "some_user": "some_user@example.com"
    },
    "gitlab": {
        "another_user": "another_user@example.com"
    }
}
```

## Utility
### GET /health

- **Description:** Check if Revolori is running.
- **Accepts:** No specific headers required.
- **Authentication:** -
- **Parameters**: -
- **Returned Content:** -
- **Returned Status Codes**
  - `200: OK`


