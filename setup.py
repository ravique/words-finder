import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="otus-homework1",
    version="dev",
    author="Andrei Etmanov",
    author_email="andres@space-coding.ru",
    description="Script for static code analysis. Search for different parts of speech in function names in .py files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravique/otus-homework1",
    py_modules={'report_writers', 'words_parser'},
    packages=setuptools.find_packages(),
    install_requires=[
        'nltk==3.4.1',
        'GitPython==2.1.11',
        'giturlparse==0.9.2'
    ],
    license="MIT",
)
