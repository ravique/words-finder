import argparse
import sys
import os

from report_writers import write_report_to_console, write_report_to_csv, write_report_to_json
from words_parser import get_all_projects_paths, find_words, TOP_WORDS_AMOUNT

ALLOWED_WORD_TYPES = ('NN', 'VB')
ALLOWED_REPORT_TYPES = ('csv', 'console', 'json')


def check_folders(folders: str):
    if folders:
        folders = set(folders.split(','))
        for folder in folders:
            if not os.path.isdir(folder):
                raise argparse.ArgumentTypeError(f'{folder} does not exist')
            if not os.access(folder, os.R_OK):
                raise argparse.ArgumentTypeError(f'{folder} is not readable')
    else:
        folders = None

    return folders


def check_word_type_input(word_types_by_comma: str):
    word_types = set(word_types_by_comma.split(','))

    for word_type in word_types:
        if word_type not in ALLOWED_WORD_TYPES:
            raise argparse.ArgumentTypeError(f'{word_type} must be in {", ".join(ALLOWED_WORD_TYPES)}')
    return word_types


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
        type=check_folders,
        help='folders for analysis, split by comma'
    )
    wf_arg_parser.add_argument(
        "--git",
        dest='repositories_by_comma',
        action='store',
        help='git repo .git urls for analysis, split by comma'
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
        default='NN',
        action='store',
        type=check_word_type_input,
        help='word types for analysis, split by comma. VB = verb, NN = noun. Example: VB,NN'
    )
    wf_arg_parser.add_argument(
        "--report_type",
        dest='report_type',
        action='store',
        type=check_report_type,
        help='type of the report: console, json, csv. default=console'
    )

    args = wf_arg_parser.parse_args(sys.argv[1:])

    if args.repositories_by_comma:
        git_repositories = set(args.repositories_by_comma.split(','))
    else:
        git_repositories = None

    all_folders = get_all_projects_paths(args.folders, git_repositories)

    words, total_words_counter, unique_words_counter = find_words(all_folders, args.word_types, args.max_top)

    if args.report_type == 'csv':
        write_report_to_csv(words, total_words_counter, unique_words_counter)
    elif args.report_type == 'json':
        write_report_to_json(words, total_words_counter, unique_words_counter)
    elif args.report_type == 'console':
        write_report_to_console(words, total_words_counter, unique_words_counter)

