# Words Finder

Script for static code analysis. Search for different parts of speech in function names, class or variable names
in .py files. In this version or script you can search for verbs (base form take) and nouns (singular). 
You can search in multiple local directories and git repositories (script downloads them into /repo folder).
You can get reports to console, csv or json files. 

## Getting Started

To clone this script using pip:
```
$ pip install git+https://github.com/ravique/otus-homework1.git
```
If you have just downloaded script as [script-archive](https://github.com/ravique/otus-homework1/archive/master.zip), unzip it into any folder.

Install requirements:
```
$ pip install requirements.txt
```

### Installing

After script installation, you need to install NLTK model:

In Python console:
```
>> nltk.download('averaged_perceptron_tagger')
```

## How to use
```
usage: words_finder.py [-h] [--dirs [FOLDERS [FOLDERS ...]]]
                       [--git [REPOSITORIES [REPOSITORIES ...]]] [-T MAX_TOP]
                       [-WT [WORD_TYPES [WORD_TYPES ...]]] [-RT REPORT_TYPE]
                       [-O [OBJECTS [OBJECTS ...]]]

Analyses usage of words in functions, classes or variables names

optional arguments:
  -h, --help            show this help message and exit
  --dirs [FOLDERS [FOLDERS ...]]
                        Folders in quotes for analysis, split by space.
                        Default: None.
                        Example: --dirs "C:\Python36\Lib\email" "C:\Python36\Lib\logging"
  --git [REPOSITORIES [REPOSITORIES ...]]
                        Git repo .git urls in quotes for analysis, split by space.
                        Default: None. 
                        Example: --git "https://github.com/nickname/repo1" "https://github.com/nickname/repo2"
  -T MAX_TOP, --top MAX_TOP
                        Count of top of words (by every type). 
                        Default: 10.
                        Example: -T 20
  -WT [WORD_TYPES [WORD_TYPES ...]], --word_types [WORD_TYPES [WORD_TYPES ...]]
                        Word types for analysis, split by space. 
                        VB = verb, NN = noun. 
                        Default: NN. 
                        Example: -WT VB NN
  -RT REPORT_TYPE, --report_type REPORT_TYPE
                        Type of the report: console, json, csv.
                        Default=console. Example: -RT json
  -O [OBJECTS [OBJECTS ...]], --objects [OBJECTS [OBJECTS ...]]
                        Оbjects for search, split by space: functions, classes, variables. 
                        Default: functions.
                        Example: -O functions classes

```
### Important

Always wrap in quotes local paths (--dirs args) and git urls (--git args).

## Authors

* **Andrei Etmanov** - *Student of OTUS :)*

## License

This project is licensed under the MIT License – see the [LICENSE.md](LICENSE.md) file for details
