`diff-highlight`: pretty diff highlighter; emphasis changed words in diff

diff-highlight adds word highlighting feature to git, mercurial and other diff viewers.

.. image:: https://drone.io/bitbucket.org/tk0miya/diff-highlight/status.png
   :target: https://drone.io/bitbucket.org/tk0miya/diff-highlight
   :alt: drone.io CI build status

.. image:: https://pypip.in/v/diff-highlight/badge.png
   :target: https://pypi.python.org/pypi/diff-highlight/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/diff-highlight/badge.png
   :target: https://pypi.python.org/pypi/diff-highlight/
   :alt: Number of PyPI downloads

Features
========
* Add highlights to diff output
* mercurial extension for diff highlighting

Setup
=====

Use easy_install or pip::

   $ sudo easy_install diff-highlight

   Or

   $ sudo pip diff-highlight

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
* Python 2.4, 2.5, 2.6, 2.7, 3.2, 3.3, 3.4
  (mercurial extension works on python 2.x only)

License
=======
Apache License 2.0
(highlights/pprint.py is under PSFL)


History
=======

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
