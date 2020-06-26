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
        metavar=("USER", "PASSWORD"),
        help="Basic authentication credentials to use.",
    )
    help_text_user_file: str = (
        "File is expected to be a text file consisting of lines of individual JSON "
        "objects that will be supplied to Revolori one by one. Each line represents "
        "one user."
    )
    revolori_parser.add_argument(
        "--list-users",
        "-l",
        metavar="PATH",
        help=f"List the users contained in the given file. {help_text_user_file}",
    )
    revolori_parser.add_argument(
        "--create-users",
        "-c",
        metavar="PATH",
        help=f"Create users supplied in the given file. {help_text_user_file}",
    )
    revolori_parser.add_argument(
        "--delete-users",
        "-d",
        metavar="PATH",
        help=f"Create users supplied in the given file. {help_text_user_file}",
    )

    args = parser.parse_args()

    if args.mode == JIRA_PARSER_NAME:
        setup_jira(jira_url=args.jira_url, login=args.login)
    elif args.mode == REVOLORI_PARSER_NAME:
        setup_revolori(
            revolori_url=args.revo_url,
            auth=args.revo_auth,
            list_users_file=args.list_users,
            create_users_file=args.create_users,
            delete_users_file=args.delete_users,
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
    revolori_url: str,
    auth: List[str] = None,
    list_users_file: str = None,
    create_users_file: str = None,
    delete_users_file: str = None,
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

    if list_users_file:
        _revo_list_users(revolori_url, req_auth, list_users_file)

    if create_users_file:
        _revo_create_users(revolori_url, req_auth, create_users_file)

    if delete_users_file:
        _revo_delete_users(revolori_url, req_auth, delete_users_file)


def _revo_parse_users_file(users_file: str) -> List[str]:
    """
    Parses the given file and returns parsed lines if it is a valid Revolori users file.
    Asks for permission to continue, exits if not given.
    Also exits if the file is malformed.
    """

    if not os.path.isfile(users_file):
        exit_with_error(f"Passed path does not point to a file: {users_file}")

    # Read file and make sure each line is valid JSON
    with open(users_file, "r") as uf:
        users_file_content: List[str] = uf.read().split("\n")

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
        f"{users_file}.\nDo you want to continue? [Y/n] "
    )

    if yn.lower() not in "yj":
        print("Cancelled.")
        sys.exit(0)

    return all_jsons


def _revo_send_requests(
    method: str,
    revolori_url: str,
    path: str,
    req_auth,
    request_params: List[Tuple[str, str]],
) -> None:
    """
    Send all given payloads with `method` to `revolori_url/path`.
    Authentication can optionally be supplied as `req_auth`.
    Exits if at least one request fails.

    : request_params : List of (path, payload) tuples for each request.
    """

    errors: List[Tuple[int, str]] = []
    with requests.Session() as session:
        session.auth = req_auth
        session.headers.update({"Content-Type": "application/json; charset=UTF-8"})
        for req_path, payload in request_params:
            payload_utf8 = payload.encode("utf-8")
            url: str = apiu.path.join(revolori_url, REVOLORI_USER_API_PATH, req_path)
            r = session.request(method=method, url=url, data=payload_utf8)

            if r.status_code == 200:
                continue
            # If the request was badly formatted, it might be an isolated incident
            elif r.status_code == 400:
                errors.append((r.status_code, payload))
            elif r.status_code == 401:
                exit_with_error(
                    f"Revolori returned 401 (Unauthorized); did you supply authentication?"
                )
            else:
                exit_with_error(
                    f"Revolori returned {r.status_code} ({r.reason}) "
                    f"when requesting {method} {full_path} with: {payload}"
                )

    if errors:
        print(f"{len(errors)} requests failed:")
        print("  Code | Request payload (first 75 characters)")
        for err in errors:
            print(f"  {err[0]}  | {err[1][:75]}...")
        sys.exit(1)

    return


def _revo_list_users(revolori_url: str, req_auth, create_users_file: str) -> None:
    """ List all users contained in the given file. """
    print("===== [LIST USERS MODE] =====\n")

    # Parse and check the given users file.
    user_jsons: List[str] = _revo_parse_users_file(create_users_file)

    # Print the users one by one
    for uj in user_jsons:
        print(json.dumps(json.loads(uj), indent="  ", ensure_ascii=False))

    print("\nAll users listed successfully")


def _revo_create_users(revolori_url: str, req_auth, create_users_file: str) -> None:
    """ Create users in Revolori that are specified in the given file. """
    print("===== [CREATE USERS MODE] =====")

    # Parse and check the given users file.
    user_jsons: List[str] = _revo_parse_users_file(create_users_file)

    # Call Revolori line by line and create users, printing the errors
    request_params: List[Tuple[str, str]] = list(
        zip([""] * len(user_jsons), user_jsons)
    )
    _revo_send_requests(
        method="POST",
        revolori_url=revolori_url,
        path=REVOLORI_USER_API_PATH,
        req_auth=req_auth,
        request_params=request_params,
    )

    print("Users created successfully")


def _revo_get_user_ids(user_jsons: List[str]) -> List[str]:
    """ Parse the given user JSONs and return each user's Revolori ID. """
    user_ids: List[str] = []
    for uj in user_jsons:
        uj_parsed = json.loads(uj)
        user_ids.append(uj_parsed["email"])
    return user_ids


def _revo_delete_users(revolori_url: str, req_auth, delete_users_file: str) -> None:
    """ Delete users in Revolori that are specified in the given file. """
    print("===== [DELETE USERS MODE] =====")

    # Parse and check the given users file.
    user_jsons: List[str] = _revo_parse_users_file(delete_users_file)
    user_ids: List[str] = _revo_get_user_ids(user_jsons)

    # Call Revolori line by line and delete users, printing the errors
    request_params: List[Tuple[str, str]] = list(zip(user_ids, [""] * len(user_ids)))
    _revo_send_requests(
        method="DELETE",
        revolori_url=revolori_url,
        path=REVOLORI_USER_API_PATH,
        req_auth=req_auth,
        request_params=request_params,
    )

    print("Users deleted successfully")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
