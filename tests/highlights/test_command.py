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
def start(*colors):
    return "".join("\x1b[%dm" % c for c in colors)

stop = start(0)


def restart(*colors):
    return stop + start(*colors)


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

    @patch("highlights.command.sys")
    def test_highlight_for_git_diff(self, sys):
        # git styled diff
        diff = ["commit 59f7d0c38d29e3796f554a5e3c60b8ca55a69814\n",
                "Author: Takeshi KOMIYA <i.tkomiya@gmail.com>\n",
                "Date:   Sun Jul 12 14:21:55 2015 +0900\n",
                "\n",
                "    add bar\n",
                "\n",
                "diff --git a/bar b/bar\n",
                "new file mode 100644\n",
                "index 0000000..5716ca5\n",
                "--- /dev/null\n",
                "+++ b/bar\n",
                "@@ -0,0 +1 @@\n",
                "+a\n",
                "b\n",
                "c\n"]
        sys.stdin = diff
        sys.stdout = StringIO()
        sys.version_info = version_info

        highlight_main()

        lines = sys.stdout.getvalue().splitlines()

        self.assertEqual(15, len(lines))
        self.assertEqual("commit 59f7d0c38d29e3796f554a5e3c60b8ca55a69814", lines[0])
        self.assertEqual("Author: Takeshi KOMIYA <i.tkomiya@gmail.com>", lines[1])
        self.assertEqual("Date:   Sun Jul 12 14:21:55 2015 +0900", lines[2])
        self.assertEqual("", lines[3])
        self.assertEqual("    add bar", lines[4])
        self.assertEqual("", lines[5])
        self.assertEqual("diff --git a/bar b/bar", lines[6])
        self.assertEqual("new file mode 100644", lines[7])
        self.assertEqual("index 0000000..5716ca5", lines[8])
        self.assertEqual("--- /dev/null", lines[9])
        self.assertEqual("+++ b/bar", lines[10])
        self.assertEqual("@@ -0,0 +1 @@", lines[11])
        self.assertEqual("%s+a%s" % (start(32), stop), lines[12])
        self.assertEqual("b", lines[13])
        self.assertEqual("c", lines[14])
