import ast
import os
import collections
import argparse
import sys
from git import Repo, GitCommandError

from nltk import pos_tag

TOP_WORDS_AMOUNT = 10


def make_flat(list_of_lists):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_of_lists], [])


def trim_magic_names(names: list) -> list:
    return [name for name in names if not (name.startswith('__') and name.endswith('__'))]


def check_word_type(word: str) -> bool:
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1]


def get_trees(path: str, with_file_names=False, with_file_content=False) -> list:
    file_names = set()
    trees = list()

    for dir_name, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                file_names.add(os.path.join(dir_name, file))
                if len(file_names) == 100:
                    break
        else:
            continue
        break

    print('total %s files' % len(file_names))

    for filename in file_names:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None

        if with_file_names:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)

    print('trees generated')
    return trees


def get_all_names(tree: list) -> list:
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_words_from_function_name(function_name: str, word_type: str) -> list:
    name_parts = []

    for name_part in function_name.split('_'):
        name_part_word_type = check_word_type(name_part)
        if name_part_word_type == word_type:
            name_parts.append(name_part)

    return name_parts


def split_snake_case_name_to_words(snake_name):
    return [name_part for name_part in snake_name.split('_') if name_part]


# def get_all_words_in_path(path: str) -> list:
#     trees = get_trees(path)
#     all_functions = make_flat([get_all_names(tree) for tree in trees])
#     clean_functions = trim_magic_names(all_functions)
#     return make_flat([split_snake_case_name_to_words(function_name) for function_name in clean_functions])


def get_top_words_in_path(path: str, word_types: set, top_size=10) -> dict:
    trees = get_trees(path)
    all_functions = make_flat(
        [[node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)] for tree in
         trees])
    clean_functions = trim_magic_names(all_functions)
    print('functions extracted')

    counted_words = {}
    for word_type in word_types:
        all_words = make_flat([get_words_from_function_name(function_name, word_type) for function_name in clean_functions])
        counted_words[word_type] = collections.Counter(all_words).most_common(top_size)
    # print(counted_words)

    return counted_words


# def get_top_functions_names_in_path(path: str, top_size=10):
#     trees = get_trees(path)
#     all_names = make_flat([[node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
#                            for tree in trees])
#     cleaned_names = trim_magic_names(all_names)
#     return collections.Counter(cleaned_names).most_common(top_size)


def clone_repo_from_git(repo: str):

    repo_name = repo.split('/')[-1].replace('.git', '')
    try:
        Repo.clone_from(repo, '/'.join(('repo', repo_name)))
    except GitCommandError:
        print(f'{repo_name} is not available')
        return None

    repo_path = os.path.join('.', '/'.join((os.getcwd(), 'repo')))
    print(f'{repo_name} downloaded to {repo_path}')

    return repo_path


def get_all_projects_paths(folders, repositories):

    projects_paths = set()

    if folders:
        for folder in folders:
            projects_paths.add(os.path.join('.', folder))

    if repositories:
        for repo_uri in repositories:
            repo_path = clone_repo_from_git(repo_uri)
            if repo_path:
                projects_paths.add(repo_path)

    return projects_paths


def find_words(projects_paths: set, word_types: set, top_size: int):
    result_words = collections.defaultdict(collections.Counter)
    total_words_counter = 0
    unique_words_counter = 0


    for project_path in projects_paths:
        new_words_by_type = get_top_words_in_path(project_path, word_types, top_size)

        for word_type, new_words in new_words_by_type.items():  # update result words dict from new words
            result_words[word_type] += collections.Counter(dict(new_words))
            total_words_counter += len(new_words)

    for word_type, words_list in result_words.items():  # count words
        result_words[word_type] = dict(collections.Counter(words_list).most_common(top_size))
        unique_words_counter += len(result_words[word_type])

    # print('Words ' + str(result_words))
    return result_words, total_words_counter, unique_words_counter


def write_report_to_console(words: dict, total_words_counter:int, unique_words_counter:int) -> None:
    
    print('total %s words, %s unique' % (total_words_counter, unique_words_counter))

    if words:
        for word_type, counted_words in words.items():
            print('---------------------')
            print(f'Word type {word_type}:')
            for word, occurrence in counted_words.items():
                print(f'{word} – {occurrence} times')

    else:
        print('No words found')


if __name__ == '__main__':
    wf_arg_parser = argparse.ArgumentParser(description='analyses usage of words in functions or variables names')
    wf_arg_parser.add_argument(
        "--dirs",
        dest='folders_by_comma',
        action='store',
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
        help=''
    )
    wf_arg_parser.add_argument(
        "--wt",
        dest='word_types_by_comma',
        default='NN',
        action='store',
        help='word types for analysis, split by comma. VB = verb, NN = noun'
    )

    args = wf_arg_parser.parse_args(sys.argv[1:])
    if args.repositories_by_comma:
        repositories = set(args.repositories_by_comma.split(','))
    else:
        repositories = None

    if args.folders_by_comma:
        folders = set(args.folders_by_comma.split(','))
    else:
        folders = None

    word_types = set(args.word_types_by_comma.split(','))

    all_folders = get_all_projects_paths(folders, repositories)

    words, total_words_counter, unique_words_counter = find_words(all_folders, word_types, int(args.max_top))
    write_report_to_console(words, total_words_counter, unique_words_counter)

