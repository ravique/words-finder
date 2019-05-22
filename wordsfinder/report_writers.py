import os
import csv
import json
import datetime


def compose_report_name(file_format: str) -> str:
    file_name = f'{datetime.datetime.now().date()}-report.{file_format}'
    counter = 1

    while os.path.isfile(f'./{file_name}'):
        file_name = f'{datetime.datetime.now().date()}-{counter}-report.{file_format}'
        counter += 1

    return file_name


def write_report_to_console(words: dict, total_words_counter: int, unique_words_counter: int) -> None:
    print('total %s words, %s unique' % (total_words_counter, unique_words_counter))
    if words and total_words_counter != 0:
        for word_type, counted_words in words.items():
            print('---------------------')
            print(f'Word type {word_type}:')
            for word, occurrence in counted_words.items():
                print(f'{word} – {occurrence} times')

    else:
        print('No words found')


def write_report_to_csv(words: dict, total_words_counter: int, unique_words_counter: int) -> bool:
    csv_file_name = compose_report_name('csv')

    with open(csv_file_name, 'a', newline='', encoding='utf-8') as report_file:
        report_writer = csv.writer(report_file, delimiter=';')

        report_writer.writerow(('total %s words, %s unique' % (total_words_counter, unique_words_counter),))

        if words:
            for word_type, counted_words in words.items():
                report_writer.writerow((word_type,))
                for word, occurrence in counted_words.items():
                    report_writer.writerow((word, occurrence))
        else:
            report_writer.writerow('No words found')

    return True


def write_report_to_json(words: dict, total_words_counter: int, unique_words_counter: int) -> bool:
    report_dict = dict()
    report_dict['general_report'] = {'total_words': total_words_counter, 'unique_words': unique_words_counter}
    if words:
        report_dict['words_report'] = words

    json_file_name = compose_report_name('json')

    with open(json_file_name, 'w', newline='', encoding='utf-8') as report_json_file:
        json.dump(report_dict, report_json_file, indent=4)

    return True
