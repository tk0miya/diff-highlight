# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Software Development",
    "Topic :: Software Development :: Version Control",
    "Topic :: Text Processing :: Filters",
]

setup(
    name='diff-highlight',
    version='0.1.0',
    description='pretty diff highlighter; emphasis changed words in diff',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['mercurial', 'git', 'diff', 'highlight'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/diff-highlight',
    license='Apache License 2.0',
    py_modules=['diff_highlight'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points="""
       [console_scripts]
       diff-highlight = highlights.command:highlight_main
    """
)
