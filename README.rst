`diff-highlight`: pretty diff highlighter; emphasis changed words in diff

diff-highlight adds word highlighting feature to git, mercurial and other diff viewers.

.. image:: https://travis-ci.org/tk0miya/diff-highlight.svg?branch=master
   :target: https://travis-ci.org/tk0miya/diff-highlight

.. image:: https://coveralls.io/repos/tk0miya/diff-highlight/badge.png?branch=master
   :target: https://coveralls.io/r/tk0miya/diff-highlight?branch=master

.. image:: https://codeclimate.com/github/tk0miya/diff-highlight/badges/gpa.svg
   :target: https://codeclimate.com/github/tk0miya/diff-highlight

Features
========
* Add highlights to diff output
* mercurial extension for diff highlighting

Setup
=====

Use easy_install or pip::

   $ sudo easy_install diff-highlight

   Or

   $ sudo pip install diff-highlight

Applying to git
---------------

Add pager settings to your $HOME/.gitconfig to enable word highlights::

   [pager]
       log = diff-highlight | less
       show = diff-highlight | less
       diff = diff-highlight | less

Applying to mercurial
---------------------

Add `color` and `diff_highlight` extensions to your $HOME/.hgrc to enable word highlights::

   [extensions]
   color =
   diff_highlight =


Requirements
============
* Python 2.6 or 2.7, or Python 3.2, 3.3, 3.4 (or higher
  (mercurial extension works on python 2.x only)

License
=======
Apache License 2.0
(`highlights/pprint.py` is under PSFL).


History
=======

1.2.0 (2016-02-07)
-------------------
* Grouping indented hunks
* Fix #1: highlight if large text appended
* Fix mercurial extension has been broken since mercurial-3.7.0

1.1.0 (2015-07-12)
-------------------
* Drop py24 and py25 support
* Support git styled diff

1.0.3 (2015-03-30)
-------------------
* Ignore IOError on showing result

1.0.2 (2014-06-08)
-------------------
* Fix result of diff-highlight commannd is broken when diff-text includes new file
  (thanks @troter)

1.0.1 (2013-12-22)
-------------------
* Fix diff-highlight command failed with python 2.4

1.0.0 (2013-12-22)
-------------------
* Add diff-highlight command
* Support python 2.4, 2.5, 3.2 and 3.3

0.1.0 (2013-12-20)
-------------------
* first release
