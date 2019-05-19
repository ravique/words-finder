import argparse
import sys
import os
import giturlparse

from report_writers import write_report_to_console, write_report_to_csv, write_report_to_json
from words_parser import get_all_projects_paths, find_words, TOP_WORDS_AMOUNT

ALLOWED_WORD_TYPES = ('NN', 'VB')
ALLOWED_REPORT_TYPES = ('csv', 'console', 'json')


# TODO: add analysis for variables and class names
# TODO: write good readme file


def check_folders(folder):
    if not os.path.isdir(folder):
        raise argparse.ArgumentTypeError(f'{folder} does not exist')
    if not os.access(folder, os.R_OK):
        raise argparse.ArgumentTypeError(f'{folder} is not readable')

    return folder


def check_git_url(repo_url):
    if not giturlparse.validate(repo_url):
        raise argparse.ArgumentTypeError(f'{repo_url} is not valid GitHub url')
    return repo_url


def check_word_type_input(word_type):
    if word_type not in ALLOWED_WORD_TYPES:
        raise argparse.ArgumentTypeError(f'{word_type} must be in {", ".join(ALLOWED_WORD_TYPES)}')
    return word_type


def check_report_type(report_type: str):
    if report_type not in ALLOWED_REPORT_TYPES:
        raise argparse.ArgumentTypeError(f'{report_type} must be in {", ".join(ALLOWED_REPORT_TYPES)}')
    return report_type


def check_top_words(max_top: str):
    try:
        int(max_top)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{max_top} must be integer")
    if int(max_top) < 0:
        raise argparse.ArgumentTypeError(f"{max_top} must be a positive integer")

    return max_top


if __name__ == '__main__':
    wf_arg_parser = argparse.ArgumentParser(description='analyses usage of words in functions or variables names')
    wf_arg_parser.add_argument(
        "--dirs",
        dest='folders',
        action='store',
        nargs='*',
        type=check_folders,
        help='Folders in quotes for analysis, split by space. Example: --dirs "C:\Python36\Lib\email" "C:\Python36\Lib\logging"'
    )
    wf_arg_parser.add_argument(
        "--git",
        dest='repositories',
        action='store',
        nargs='*',
        type=check_git_url,
        help='Git repo .git urls in quotes for analysis, split by space. Example: "https://github.com/nickname/repo1" "https://github.com/nickname/repo2"'
    )
    wf_arg_parser.add_argument(
        "--top",
        dest='max_top',
        default=TOP_WORDS_AMOUNT,
        action='store',
        type=check_top_words,
        help=f'count of top of words in every project. default={TOP_WORDS_AMOUNT}'
    )
    wf_arg_parser.add_argument(
        "--word_types",
        dest='word_types',
        nargs='*',
        default=['NN'],
        action='store',
        type=check_word_type_input,
        help='word types for analysis, split by space. VB = verb, NN = noun. Example: --word_types VB NN'
    )
    wf_arg_parser.add_argument(
        "--report_type",
        dest='report_type',
        default='console',
        action='store',
        type=check_report_type,
        help='type of the report: console, json, csv. default=console'
    )

    args = wf_arg_parser.parse_args(sys.argv[1:])

    folders = set(args.folders) if args.folders else None
    repositories = set(args.repositories) if args.repositories else None

    all_folders = get_all_projects_paths(folders, repositories)

    words, total_words_counter, unique_words_counter = find_words(all_folders, args.word_types, args.max_top)

    if args.report_type == 'csv':
        write_report_to_csv(words, total_words_counter, unique_words_counter)
    elif args.report_type == 'json':
        write_report_to_json(words, total_words_counter, unique_words_counter)
    elif args.report_type == 'console':
        write_report_to_console(words, total_words_counter, unique_words_counter)
