# -*- coding: utf-8 -*-
import sys
from cStringIO import StringIO
from highlights.command import highlight_main

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

try:
    from mock import patch
except:
    pass


@unittest.skipIf(sys.version_info < (2, 5), "python 2.4 is not supported")
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

        start = lambda *colors: "".join("\x1b[%dm" % c for c in colors)
        stop = start(0)
        restart = lambda *colors: stop + start(*colors)

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

