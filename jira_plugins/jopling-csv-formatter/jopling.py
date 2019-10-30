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
from typing import Dict, List, Set, Tuple

# Some global settings
locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
csv.field_size_limit(sys.maxsize)

# Constants
DELIMITER = ","
QUOTECHAR = '"'


def fix_main(file_paths: List[str], outfile_path: str):
    """ Comb through the given files, fix up the issues, and write to outfile. """

    if os.path.lexists(outfile_path):
        print(f"Output file {outfile_path} exists.")
        sys.exit(1)

    data: List[Dict]
    all_keys: Set[str]
    data, all_keys = read_all_csvs(file_paths)

    # Fix and update fields
    for issue in data:
        fix_issue(issue)

    # 1. Order old to new to ensure links can be set as good as possible
    data.sort(key=lambda issue: issue["Created"])

    # 2. Write out to outfile
    all_keys_sorted: List[str] = sorted(all_keys)
    with open(outfile_path, "w", newline="") as file_pointer:
        file_writer = csv.writer(
            file_pointer,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
            quoting=csv.QUOTE_NONNUMERIC,
        )
        file_writer.writerow(all_keys_sorted)
        for issue in data:
            issue_row: List[str] = csvize_issue(issue, all_keys_sorted)
            file_writer.writerow(issue_row)

    print(f"Created file {outfile_path} with {len(data)} entries")


def read_all_csvs(file_paths: List[str]) -> Tuple[List[Dict], Set[str]]:
    """
    Read all given files with read_csv() and store them in a dict.

    Returns: Dict of all issues, List of all keys
    """

    data: List[Dict] = []
    all_keys: Set[str] = set()

    for file_path in file_paths:
        keys = read_csv(file_path, data)
        if len(keys) < 2:
            raise IOError(
                f'Seem to have misread CSV "{file_path}"...\nParsed keys: {keys}'
            )
        all_keys.update(keys)

    return data, all_keys


def read_csv(file_path: str, data: List[Dict]) -> List[str]:
    """
    Read the given file and drop it into the given list of dicts. Each row will be saved as one dict.

    Returns: List of keys found
    """

    list_of_rows: List[List[str]] = []
    with open(file_path, newline="") as file_pointer:
        file_reader = csv.reader(file_pointer, delimiter=DELIMITER, quotechar=QUOTECHAR)
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

    # COMMENT update: Issue may also not have any comments (comment == "")
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

    # Fix all dates to be locale independent (ISO-like format)
    # CREATED, UPDATED update
    issue[created_key] = format_date(issue[created_key])
    issue[updated_key] = format_date(issue[updated_key])

    # DUE, RESOLVED update: These may be empty
    if issue[due_key]:
        issue[due_key] = format_date(issue[due_key])
    if issue[resolved_key]:
        issue[resolved_key] = format_date(issue[resolved_key])


def format_date(date_s: str) -> str:
    """ Format the given date as "yyyy-MM-dd HH:mm" (SimpleDateFormat) to be locale independent.
    Tries en_US locale for input. """

    assert locale.getlocale(locale.LC_TIME)[0] == "en_US"
    date_dt: dt.datetime = dt.datetime.strptime(date_s, "%d/%b/%y %I:%M %p")

    return date_dt.strftime("%Y-%m-%d %H:%M")


def csvize_issue(issue: Dict, keys: List[str]) -> List[str]:
    """ Convert the given issue dict to a list of its values, sorted by key as given in the key list. """

    result: List[str] = []
    for key in keys:
        if key not in issue:
            result.append("")
            continue

        result.append(issue[key])

    return result


def analyze_main(file_paths: List[str]):
    """ Comb through the given files and analyze them. """

    data: List[Dict]
    data, _ = read_all_csvs(file_paths)

    all_projects: Set[str] = set()
    all_status: Set[str] = set()
    project_names: Dict[str, str] = dict()
    status_per_project: Dict[str, Set[str]] = dict()
    num_issues_per_project: Dict[str, int] = dict()

    for issue in data:
        project_key: str = issue["Project key"]
        project_name: str = issue["Project name"]
        status: str = issue["Status"]

        if project_key not in status_per_project:
            status_per_project[project_key] = set()
        if project_key not in num_issues_per_project:
            num_issues_per_project[project_key] = 0

        all_projects.add((project_key))
        all_status.add(status)
        project_names[project_key] = project_name
        status_per_project[project_key].add(status)
        num_issues_per_project[project_key] += 1

    for proj_key, statuss in status_per_project.items():
        print(f"{project_names[proj_key]}:\n  ", end="")
        for status in statuss:
            print(f"{status}  ", end="")
        print("\n")

    print(f"Unique status found: {sorted(all_status)[:51]}")
    print()

    # Top / bottom projects
    def print_project_table(
        projects: List[Tuple[str, int]], project_names: Dict[str, str]
    ):
        for proj_key, num_issues in projects:
            proj_name = project_names[proj_key]
            if len(proj_name) > 20:
                proj_name = proj_name[:18] + "..."
            print(
                f"{proj_key[:9].ljust(10)}  {(proj_name).ljust(22)}  {str(num_issues).rjust(8)}"
            )

    projects_sorted = sorted(
        num_issues_per_project.items(), key=lambda t: t[1], reverse=True
    )

    # Show all projects if it's 20 or less, otherwise split top / bottom 10
    top_projects: List[Tuple[str, int]] = projects_sorted
    bottom_projects: List[Tuple[str, int]] = []
    if len(projects_sorted) > 20:
        top_projects = projects_sorted[:10]
        bottom_projects = projects_sorted[-10:]

    print(f"Projects {' ' * 26} # issues")
    print_project_table(top_projects, project_names)
    if bottom_projects:
        print("...".ljust(20).rjust(40))
        print_project_table(bottom_projects, project_names)
    print()

    print(f"Issues:   {len(data)}")
    print(f"Projects: {len(all_projects)}")
    print(f"Status:   {len(all_status)}")
    print()
    print("Analysis done.")


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
        parser.add_argument("--mode", "-m", default="fix", choices=["analyze", "fix"])
        args = parser.parse_args()

        # Argument check level 2
        file_paths: List[str] = args.file_path
        for fp in file_paths:
            if not os.path.isfile(fp):
                print(f'Given path "{fp}" is not a valid file.')
                sys.exit(1)

        if args.mode == "fix":
            outfile_path = os.path.join(os.path.dirname(file_paths[0]), args.outfile)
            fix_main(file_paths=file_paths, outfile_path=outfile_path)
        elif args.mode == "analyze":
            analyze_main(file_paths=file_paths)
        else:
            raise NotImplementedError(f"Mode {args.mode} not implemented")

    except KeyboardInterrupt:
        # Exit code for Ctrl-C
        sys.exit(130)
