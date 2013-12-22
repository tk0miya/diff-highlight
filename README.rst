`diff-highlight`: pretty diff highlighter; emphasis changed words in diff

This mercurial extension adds word highlights to every diff outputs.
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
* Python 2.4, 2.5, 2.6, 2.7, 3.2, 3.3
  (mercurial extension works on python 2.x only)

License
=======
Apache License 2.0
(highlights/pprint.py is under PSFL)


History
=======

1.0.0 (2013-12-22)
-------------------
* Add diff-highlight command
* Support python 2.4, 2.5, 3.2 and 3.3

0.1.0 (2013-12-20)
-------------------
* first release
