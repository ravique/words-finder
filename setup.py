import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wordsfinder",
    version="dev",
    author="Andrei Etmanov",
    author_email="andres@space-coding.ru",
    description="Script for static code analysis. Search for different parts of "
                "speech in different objects in .py files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravique/wordsfinder",
    py_modules={'report_writers', 'words_parser', '__init__', 'words_finder'},
    packages=setuptools.find_packages(),
    scripts=['wordsfinder/words_finder.py'],
    install_requires=[
        'nltk==3.4.5',
        'GitPython==3.1.37',
        'giturlparse==0.9.2'
    ],
    license="MIT",
)
