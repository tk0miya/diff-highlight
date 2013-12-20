`diff-highlight`: pretty diff highlighter; emphasis changed words in diff

This mercurial extension adds word highlights to every diff outputs.

Setup
=====

Use easy_install or pip::

   $ sudo easy_install diff-highlight

   Or

   $ sudo pip diff-highlight

And then, add color and diff_highlight to your extensions list on $HOME/.hgrc::

   [extensions]
   color =
   diff_highlight =


Requirements
============
* Python 2.6, 2.7

License
=======
Apache License 2.0
(highlights/pprint.py is under PSFL)


History
=======

0.1.0 (2013-12-20)
-------------------
* first release

