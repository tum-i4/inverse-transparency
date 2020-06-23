#!.venv/bin/python3
""" gustave sets up Jira
Name inspired by: M. Gustave, the concierge in "The Grand Budapest Hotel" """

import argparse
import sys

import requests
import requests.exceptions

import apiu.path

VERSION = "0.1"
JIRA_API_PATH = "rest/api/2/user"


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
        setup_revolori(revolori_url=args.revo_url, create_users_file=args.create_users)
    else:
        parser.print_usage()
        sys.exit(2)


def setup_jira(jira_url: str, login: str):
    if not jira_url.startswith("http"):
        jira_url = f"http://{jira_url}"

    full_api_url = apiu.path.join(jira_url, JIRA_API_PATH)

    try:
        user, password = login.split(":")
    except ValueError:
        print(f'Couldn\'t split login at ":": {login}')
        sys.exit(1)

    # 0. Check connectivity
    try:
        requests.get(jira_url)
    except requests.exceptions.ConnectionError:
        print("Connection error...")
        sys.exit(1)

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


def setup_revolori(revolori_url: str, create_users_file: str = None):
    """
    Sets up Revolori. Currently supports creating users.

    : create_users_file : A file consisting of users to be created, with each line
        representing one JSON payload for Revolori.
    """
    print("Revolori mode")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
