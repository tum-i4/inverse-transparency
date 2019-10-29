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

    # TODO Write out to new file
    # IMPORTANT: Write in REVERSE date order to ensure links can be set as best as possible


def read_csv(file_path: str, data: List[Dict]) -> List[str]:
    """
    Read the given file and drop it into the given list of dicts. Each row will be saved as one dict.

    Returns: List of keys found
    """
    raise NotImplementedError()


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
