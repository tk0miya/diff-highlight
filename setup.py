# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development",
    "Topic :: Software Development :: Version Control",
    "Topic :: Text Processing :: Filters",
]

test_requires = ['nose', 'flake8', 'mock', 'six']

if sys.version_info < (2, 7):
    test_requires.append('unittest2')

if sys.version_info < (3, 0):
    test_requires.append('mercurial')

setup(
    name='diff-highlight',
    version='1.2.0',
    description='pretty diff highlighter; emphasis changed words in diff',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['mercurial', 'git', 'diff', 'highlight'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='https://github.com/tk0miya/diff-highlight',
    license='Apache License 2.0',
    py_modules=['diff_highlight'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require={
        'testing': test_requires,
    },
    tests_require=test_requires,
    entry_points="""
       [console_scripts]
       diff-highlight = highlights.command:highlight_main
    """
)
