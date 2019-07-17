from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sublime-backup',
    version='0.2',
    py_modules=['cli'],
    author = 'nishantwrp',
    author_email = 'mittalnishant14@outlook.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/nishantwrp/sublime-backup-cli',
    license = 'Apache 2.0',
    description = 'A simple command line tool to backup / sync your sublime snippets',
    install_requires=[
        'Click','configparser','appdirs','requests'
    ],
    entry_points='''
        [console_scripts]
        sublime-backup=cli:cli
    ''',
)
