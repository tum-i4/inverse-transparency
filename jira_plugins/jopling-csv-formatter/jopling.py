#!/usr/bin/env python3
""" jopling whips CSV files into shape for our Jira
Name inspired by: Jopling, the assassin in "The Grand Budapest Hotel" """

import argparse
import csv
import datetime as dt
import sys
from typing import List


def main(file_paths: List[str], outfile: str):
    print(file_paths)
    print(outfile)
    sys.exit(0)


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
