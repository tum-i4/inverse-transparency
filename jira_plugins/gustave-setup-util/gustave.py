#!.venv/bin/python3
""" gustave sets up Jira and Revolori
Name inspired by: M. Gustave, the concierge in "The Grand Budapest Hotel" """

import argparse
import json
import json.decoder
import os
import sys
from typing import List, Optional, Tuple

import apiu.path
import requests
import requests.auth
import requests.exceptions

VERSION = "0.1"
JIRA_API_PATH = "rest/api/2/user"
REVOLORI_HEALTH_API_PATH = "health"
REVOLORI_USER_API_PATH = "user"


def main():
    JIRA_PARSER_NAME = "jira"
    REVOLORI_PARSER_NAME = "revo"

    parser = argparse.ArgumentParser(prog="gustave")
    parser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + str(VERSION)
    )
    subparsers = parser.add_subparsers(title="modes", dest="mode")

    # Jira setup functionality
    jira_parser = subparsers.add_parser(JIRA_PARSER_NAME, help="Set up Jira")
    jira_parser.add_argument(
        "jira_url", help="The URL of the Jira instance, e.g. localhost:2929/jira"
    )
    jira_parser.add_argument(
        "--login",
        default="admin:admin",
        help="Optionally specify the login to use, formatted as user:password "
        "(default: admin:admin)",
    )

    # Revolori setup functionality
    revolori_parser = subparsers.add_parser("revo", help="Set up Revolori SSO")
    revolori_default_url: str = "https://revolori.sse.in.tum.de"
    revolori_parser.add_argument(
        "--url",
        "-u",
        dest="revo_url",
        default=revolori_default_url,
        help=f"The URL of the Revolori instance; default: {revolori_default_url}",
    )
    revolori_parser.add_argument(
        "--auth",
        "-a",
        dest="revo_auth",
        nargs=2,
        help="Basic authentication credentials to use. Expects user and password.",
    )
    revolori_parser.add_argument(
        "--create-users",
        "-c",
        metavar="PATH",
        help="Create users supplied in the given file. File is expected to be a text "
        "file consisting of lines of individual JSON objects that will be supplied to "
        "Revolori one by one. Each line represents one user.",
    )

    args = parser.parse_args()

    if args.mode == JIRA_PARSER_NAME:
        setup_jira(jira_url=args.jira_url, login=args.login)
    elif args.mode == REVOLORI_PARSER_NAME:
        setup_revolori(
            revolori_url=args.revo_url,
            auth=args.revo_auth,
            create_users_file=args.create_users,
        )
    else:
        parser.print_usage()
        sys.exit(2)


def exit_with_error(msg: str, code: int = 1):
    """ Print the given message and exit the program. """
    print(f"Error: {msg}")
    sys.exit(code)


def setup_jira(jira_url: str, login: str):
    if not jira_url.startswith("http"):
        jira_url = f"http://{jira_url}"

    full_api_url = apiu.path.join(jira_url, JIRA_API_PATH)

    try:
        user, password = login.split(":")
    except ValueError:
        exit_with_error(f'Couldn\'t split login at ":": {login}')

    # 0. Check connectivity
    try:
        requests.get(jira_url)
    except requests.exceptions.ConnectionError:
        exit_with_error(f"Jira not reachable at {jira_url}")

    print(f"Jira successfully contacted at {jira_url}")

    # 1. Create user "inv_api_user"
    iau_username: str = "inv_api_user"
    print(f'Creating user "{iau_username}"...')
    if (
        requests.get(full_api_url, params={"username": iau_username})
    ).status_code == 200:
        print(f"User exists already")
    else:
        response: requests.Response = requests.post(
            full_api_url,
            json={
                "name": iau_username,
                "password": "iau_pwd_9#",
                "emailAddress": "no_email@nooooemail.xyz",
            },
        )

        if response.status_code != 200:
            print(f'API error: [{response.status_code}] "{response.text}"')


def setup_revolori(
    revolori_url: str, auth: List[str] = None, create_users_file: str = None
):
    """
    Sets up Revolori. Currently supports creating users.

    : create_users_file : A file consisting of users to be created, with each line
        representing one JSON payload for Revolori.
    """

    try:
        requests.get(apiu.path.join(revolori_url, REVOLORI_HEALTH_API_PATH))
    except requests.exceptions.ConnectionError:
        exit_with_error(f"Revolori not reachable at {revolori_url}")

    print("Connection to Revolori established.")

    req_auth: Optional[requests.auth.HTTPBasicAuth] = None
    if auth:
        u, p = auth
        req_auth = requests.auth.HTTPBasicAuth(u, p)

    if create_users_file:
        _revo_create_users(revolori_url, req_auth, create_users_file)


def _revo_create_users(revolori_url: str, req_auth, create_users_file: str):
    """ Create users in Revolori that are specified in the given file. """
    print("===== [CREATE USERS MODE] =====")

    if not os.path.isfile(create_users_file):
        exit_with_error(f"Passed path does not point to a file: {create_users_file}")

    # Read file and make sure each line is valid JSON
    with open(create_users_file, "r") as users_file:
        users_file_content: List[str] = users_file.read().split("\n")

    all_jsons: List[str] = []
    for i, uf_line in enumerate(users_file_content):
        # Skip empty lines and comments
        if uf_line == "" or uf_line.strip().startswith("//"):
            continue
        else:
            try:
                json.loads(uf_line)
                all_jsons.append(uf_line)
            except json.decoder.JSONDecodeError as e:
                exit_with_error(
                    f'Could not parse line {i+1}: "{uf_line}". '
                    f"JSON decoder failed with: {str(e)}"
                )

    yn: str = input(
        f"Successfully parsed {len(all_jsons)} users from input file "
        "{create_users_file}.\nDo you want to continue? [Y/n] "
    )

    if yn.lower() not in "yj":
        print("Cancelled.")
        sys.exit(0)

    # Call Revolori line by line and create users, collecting the errors
    errors: List[Tuple[int, str]] = []
    for j in all_jsons:
        r = requests.post(
            apiu.path.join(revolori_url, REVOLORI_USER_API_PATH), auth=req_auth, data=j
        )
        if r.status_code == 200:
            continue
        # If the request was badly formatted, it might be an isolated incident
        elif r.status_code == 400:
            errors.append((r.status_code, j))
        elif r.status_code == 401:
            exit_with_error(
                f"Revolori returned 401 (Unauthorized); did you supply authentication?"
            )
        else:
            exit_with_error(
                f"Revolori returned {r.status_code} ({r.reason}) "
                f'when trying to create "{j}"'
            )

    # Print a resulting message summarizing the errors
    if errors:
        print(f"{len(errors)} requests failed:")
        print("  Code | Request payload (first 75 characters)")
        for err in errors:
            print(f"  {err[0]}  | {err[1][:75]}...")
        sys.exit(1)

    print("Users created successfully")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
