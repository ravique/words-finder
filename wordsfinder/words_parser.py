import ast
import os
import collections
from typing import Tuple, Union

from git import Repo, GitCommandError
from nltk import pos_tag
import giturlparse

TOP_WORDS_AMOUNT = 10


def make_flat(list_of_lists: list) -> list:
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_of_lists], [])


def is_magic_function(function_name: str) -> bool:
    return all((function_name.startswith('__'), function_name.endswith('__')))


def check_word_type(word: str) -> bool:
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1]


def get_python_files(path: str) -> set:
    file_names = set()
    for dir_name, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                file_names.add(os.path.join(dir_name, file))
                if len(file_names) == 100:
                    return file_names

    return file_names


def get_ast_trees(path: str, lang: str = 'python', with_file_names=False, with_file_content=False) -> list:
    ast_trees_list = list()

    if lang == 'python':
        file_names = get_python_files(path)

    print(f'total {len(file_names)} files')

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
                ast_trees_list.append((filename, main_file_content, tree))
            else:
                ast_trees_list.append((filename, tree))
        else:
            ast_trees_list.append(tree)

    print('ast trees generated')
    return ast_trees_list


def get_words_from_object_name(object_name: str, word_type: str) -> list:
    name_parts = []

    for name_part in object_name.split('_'):
        name_part_word_type = check_word_type(name_part)
        if name_part_word_type == word_type:
            name_parts.append(name_part)

    return name_parts


def get_objects_from_tree(object_types: set, trees: list) -> list:
    object_names = []

    for tree in trees:
        if tree:
            for node in ast.walk(tree):
                if 'functions' in object_types and isinstance(node, ast.FunctionDef) \
                        and not is_magic_function(node.name):
                    object_names.append(node.name.lower())
                if 'variables' in object_types and isinstance(node, ast.Name):
                    object_names.append(node.id.lower())
                if 'classes' in object_types and isinstance(node, ast.ClassDef):
                    object_names.append(node.name.lower())

    return object_names


def get_top_words_in_path(path: str, word_types: set, object_types: set, top_size: int = 10) -> Tuple[dict, int]:
    trees = get_ast_trees(path, lang='python')
    object_names = get_objects_from_tree(object_types, trees)

    counted_words = {}
    total_words_count = 0

    for word_type in word_types:
        all_words = make_flat([get_words_from_object_name(object_name, word_type)
                               for object_name in object_names])
        total_words_count += len(all_words)
        counted_words[word_type] = collections.Counter(all_words).most_common(top_size)

    return counted_words, total_words_count


def clone_repo_from_git(repo_url: str) -> Union[str, None]:
    repo_parse_url = giturlparse.parse(repo_url)
    repo_name = repo_parse_url.repo
    try:
        Repo.clone_from(repo_url, os.path.join('repo', repo_name))
    except GitCommandError as git_error:
        print(f'{repo_name} was not downloaded because of:')
        print(git_error)
        return None

    repo_path = os.path.join('.', os.path.join(os.getcwd(), 'repo'))
    print(f'{repo_name} downloaded to {repo_path}')

    return repo_path


def get_all_projects_paths(local_paths: set, git_repositories_urls: set) -> set:
    projects_paths = set()

    if local_paths:
        for folder in local_paths:
            projects_paths.add(os.path.join('.', folder))

    if git_repositories_urls:
        for repo_uri in git_repositories_urls:
            repo_path = clone_repo_from_git(repo_uri)
            if repo_path:
                projects_paths.add(repo_path)

    return projects_paths


def find_words(projects_paths: set, word_types: set, objects_types: set, top_size: int) -> Tuple[dict, int, int]:
    result_words = collections.defaultdict(collections.Counter)
    unique_words_counter = 0
    total_words_counter = 0

    for project_path in projects_paths:
        new_words_by_type, total_words_count = get_top_words_in_path(project_path, word_types, objects_types, top_size)
        total_words_counter += total_words_count

        for word_type, new_words in new_words_by_type.items():  # update result words dict from new words
            result_words[word_type] += collections.Counter(dict(new_words))

    for word_type, words_list in result_words.items():  # count words
        result_words[word_type] = dict(collections.Counter(words_list).most_common(top_size))
        unique_words_counter += len(result_words[word_type])

    return result_words, total_words_counter, unique_words_counter
