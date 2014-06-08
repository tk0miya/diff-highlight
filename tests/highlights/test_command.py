# -*- coding: utf-8 -*-
import sys
from mock import patch
from highlights.command import highlight_main

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3, 0):
    from cStringIO import StringIO
else:
    from io import StringIO

version_info = sys.version_info

# ESC utility
start = lambda *colors: "".join("\x1b[%dm" % c for c in colors)
stop = start(0)
restart = lambda *colors: stop + start(*colors)


class TestHighlightCommand(unittest.TestCase):
    @patch("highlights.command.sys")
    def test_highlight_main(self, sys):
        diff = ["\x1b[33m@@ -10,4 +10,6 @@\x1b[m\n",
                " \n",
                "\x1b[31m-print 'nice', 'boat'\x1b[m\n",
                "\x1b[31m-print \"bye world\"\x1b[m\n",
                "\x1b[32m+print 'hello', 'world'\x1b[m\n",
                "\x1b[32m+\x1b[m\n",
                "\x1b[32m+\x1b[m\n",
                "\x1b[32m+print 'bye world'\x1b[m\n",
                " \n"]
        sys.stdin = diff
        sys.stdout = StringIO()
        sys.version_info = version_info

        highlight_main()

        lines = sys.stdout.getvalue().splitlines()

        self.assertEqual(9, len(lines))
        self.assertEqual("\x1b[33m@@ -10,4 +10,6 @@\x1b[m", lines[0])
        self.assertEqual(" ", lines[1])
        self.assertEqual(("%s-print '%snice%s', '%sboat%s'%s" %
                          (start(31), restart(31, 7), restart(31),
                           restart(31, 7), restart(31), stop)),
                         lines[2])
        self.assertEqual(("%s+print '%shello%s', '%sworld%s'%s" %
                          (start(32), restart(32, 7), restart(32),
                           restart(32, 7), restart(32), stop)),
                         lines[3])
        self.assertEqual("%s+%s" % (start(32), stop), lines[4])
        self.assertEqual("%s+%s" % (start(32), stop), lines[5])
        self.assertEqual(("%s-print %s\"%sbye world%s\"%s" %
                          (start(31), restart(31, 7), restart(31),
                           restart(31, 7), stop)),
                         lines[6])
        self.assertEqual(("%s+print %s'%sbye world%s'%s" %
                          (start(32), restart(32, 7), restart(32),
                           restart(32, 7), stop)),
                         lines[7])
        self.assertEqual(" ", lines[8])

    @patch("highlights.command.sys")
    def test_highlight_including_new_file(self, sys):
        # diff including new file (new.txt)
        diff = ["--- /dev/null\n",
                "+++ b/new.txt\n",
                "@@ -0,0 +1,1 @@\n",
                "+aaa\n",
                "diff --git a/exist.txt b/exist.txt\n",
                "index 1d95c52..8bffa50 100644\n",
                "@@ -0,0 +1,1 @@\n",
                "-bbbb\n",
                "+aaaa\n"]
        sys.stdin = diff
        sys.stdout = StringIO()
        sys.version_info = version_info

        highlight_main()

        lines = sys.stdout.getvalue().splitlines()
        diff = ["@@ -0,0 +1,1 @@\n",
                "+aaa\n",
                "diff --git a/exist.txt b/exist.txt\n",
                "index 1d95c52..8bffa50 100644\n",
                "@@ -0,0 +1,1 @@\n",
                "-bbbb\n",
                "+aaaa\n"]

        self.assertEqual(9, len(lines))
        self.assertEqual("--- /dev/null", lines[0])
        self.assertEqual("+++ b/new.txt", lines[1])
        self.assertEqual("@@ -0,0 +1,1 @@", lines[2])
        self.assertEqual("%s+aaa%s" % (start(32), stop), lines[3])
        self.assertEqual("diff --git a/exist.txt b/exist.txt", lines[4])
        self.assertEqual("index 1d95c52..8bffa50 100644", lines[5])
        self.assertEqual("@@ -0,0 +1,1 @@", lines[6])
        self.assertEqual("%s-bbbb%s" % (start(31), stop), lines[7])
        self.assertEqual("%s+aaaa%s" % (start(32), stop), lines[8])
