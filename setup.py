# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Software Development",
    "Topic :: Software Development :: Version Control",
    "Topic :: Text Processing :: Filters",
]

test_requires = ['mercurial']
if sys.version_info < (2, 7):
    test_requires.append('unittest2')
if sys.version_info > (2, 4):
    test_requires.append('mock')
else:
    test_requires.append('mock==0.8.0')

setup(
    name='diff-highlight',
    version='1.0.0',
    description='pretty diff highlighter; emphasis changed words in diff',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['mercurial', 'git', 'diff', 'highlight'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='https://bitbucket.org/tk0miya/diff-highlight',
    download_url='http://pypi.python.org/pypi/diff-highlight',
    license='Apache License 2.0',
    py_modules=['diff_highlight'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    tests_require=test_requires,
    entry_points="""
       [console_scripts]
       diff-highlight = highlights.command:highlight_main
    """
)
