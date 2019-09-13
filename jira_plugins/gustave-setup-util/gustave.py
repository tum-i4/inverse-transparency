#!/usr/bin/env python3
# encoding=utf-8
""" gustave sets up Jira
Name inspired by: M. Gustave, the concierge in "The Grand Budapest Hotel" """

import argparse
import sys

import requests
import requests.exceptions


def main(jira_url: str, login: str):
    if not jira_url.startswith("http"):
        jira_url = f"http://{jira_url}"

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

    # 1. Create user "inv_api_user"
    pass


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "jira_url", help="The URL of the Jira instance, e.g. localhost:2929/jira"
        )
        parser.add_argument(
            "--login",
            default="admin:admin",
            help="Optionally specify the login to use, formatted as user:password (default: admin:admin)",
        )
        args = parser.parse_args()
        main(jira_url=args.jira_url, login=args.login)

    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
