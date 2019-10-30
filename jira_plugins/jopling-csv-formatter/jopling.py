#!/usr/bin/env python3
""" jopling whips CSV files into shape for our Jira
Name inspired by: Jopling, the assassin in "The Grand Budapest Hotel" """

import argparse
import csv
import datetime as dt
import locale
import os.path
import re
import sys
from typing import Dict, List, Set

locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


def main(file_paths: List[str], outfile: str):
    for fp in file_paths:
        if not os.path.isfile(fp):
            print(f'Given path "{fp}" is not a valid file.')
            sys.exit(1)

    data: List[Dict] = []
    all_keys: Set[str] = set()

    for file_path in file_paths:
        keys = read_csv(file_path, data)
        if len(keys) < 2:
            raise IOError(
                f'Seem to have misread CSV "{file_path}"...\nParsed keys: {keys}'
            )
        all_keys.update(keys)

    # TODO Fix and update fields

    for issue in data:
        fix_issue(issue)

    raise NotImplementedError()

    # TODO Write out to new file
    # IMPORTANT: Write in REVERSE date order to ensure links can be set as best as possible


def read_csv(file_path: str, data: List[Dict]) -> List[str]:
    """
    Read the given file and drop it into the given list of dicts. Each row will be saved as one dict.

    Returns: List of keys found
    """

    list_of_rows: List[List[str]] = []
    with open(file_path, newline="") as file_pointer:
        file_reader = csv.reader(file_pointer, delimiter=",", quotechar='"')
        for row in file_reader:
            list_of_rows.append(row)

    keys, vals = list_of_rows[0], list_of_rows[1:]
    for row in vals:
        row_dict: Dict = dict()
        for k, v in zip(keys, row):
            row_dict[k] = v
        data.append(row_dict)

    return keys


def fix_issue(issue: Dict) -> None:
    """ Fix the given issue in-place """

    comment_key = "Comment"
    created_key = "Created"
    due_key = "Due Date"
    resolved_key = "Resolved"
    updated_key = "Updated"
    expected_keys = {comment_key, created_key, due_key, resolved_key, updated_key}

    for k in expected_keys:
        if k not in issue:
            raise IOError(f'Expected key "{k}" not in row: {issue}')

    # COMMENT update
    comment: str = issue[comment_key]
    if comment:
        # Expected input comment format: 19/Feb/19 9:30 AM;laidan6000;Does this need a linked documentation task?
        # Target comment format: 05/05/2010 09:20:30; adam; This is a comment.
        # Changes: Reformat date to dd/dd/dddd dd:dd:dd

        match = re.fullmatch(r"(\d\d/\w{3}/\d\d \d{1,2}:\d\d\s\wM)(;[^;].*)", comment)
        if not match:
            raise IOError(
                f'Comment not in expected format "dd/www/dd dd:dd ww;...":\n  "{comment}"'
            )

        new_date_s: str = format_date(match.group(1))
        new_comment = f"{new_date_s}{match.group(2)}"

        if not re.match(r"^\d\d\d\d-\d\d-\d\d \d\d:\d\d;[^;]+", new_comment):
            raise RuntimeError(
                f'Invalid conversion; missed own target...:\n  "{new_comment}"'
            )

        issue[comment_key] = new_comment

    # TODO Fix all dates to be locale independent (ISO-like format)
    # Comment (above)
    # Created
    # Due Date
    # Resolved
    # Updated


def format_date(date_s: str) -> str:
    """ Format the given date as "yyyy-MM-dd HH:mm" (SimpleDateFormat) to be locale independent.
    Tries en_US locale for input. """

    assert locale.getlocale(locale.LC_TIME)[0] == "en_US"
    date_dt: dt.datetime = dt.datetime.strptime(date_s, "%d/%b/%y %I:%M %p")

    return date_dt.strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file_path", nargs="+", help="The path(s) of the CSV file(s) to transform"
        )
        parser.add_argument(
            "--outfile",
            "-o",
            default=f"jira_csv_{dt.datetime.now().strftime('%y%m%d-%H%M%S')}.csv",
            help="The output file",
        )
        args = parser.parse_args()
        main(file_paths=args.file_path, outfile=args.outfile)

    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
