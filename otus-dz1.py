import ast
import os
import collections

from nltk import pos_tag


def make_flat(list_of_lists):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_of_lists], [])


def trim_magic_names(names):
    return [name for name in names if not (name.startswith('__') and name.endswith('__'))]


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_trees(path, with_file_names=False, with_file_content=False):
    file_names = []
    trees = []

    for dir_name, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                file_names.append(os.path.join(dir_name, file))
                if len(file_names) == 100:
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


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [name_part for name_part in function_name.split('_') if is_verb(name_part)]


def split_snake_case_name_to_words(snake_name):
    return [name_part for name_part in snake_name.split('_') if name_part]


def get_all_words_in_path(path):
    trees = get_trees(path)
    all_functions = make_flat([get_all_names(tree) for tree in trees])
    clean_functions = trim_magic_names(all_functions)
    return make_flat([split_snake_case_name_to_words(function_name) for function_name in clean_functions])


def get_top_verbs_in_path(path, top_size=10):
    trees = get_trees(path)
    all_functions = make_flat(
        [[node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)] for tree in
         trees])
    clean_functions = trim_magic_names(all_functions)
    print('functions extracted')
    verbs = make_flat([get_verbs_from_function_name(function_name) for function_name in clean_functions])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    trees = get_trees(path)
    all_names = make_flat([[node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                           for tree in trees])
    cleaned_names = trim_magic_names(all_names)
    return collections.Counter(cleaned_names).most_common(top_size)


words = []
projects = [
    'django',
    'flask',
    'pyramid',
    'reddit',
    'requests',
    'sqlalchemy',
]

for project in projects:
    project_path = os.path.join('.', project)
    words += get_top_verbs_in_path(project_path)

depth = 200
print('total %s words, %s unique' % (len(words), len(set(words))))
for word, occurrence in collections.Counter(words).most_common(depth):
    print(word, occurrence)
