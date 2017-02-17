# -*- coding: utf-8 -*-
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3, 0):
    try:
        from mercurial import color
    except ImportError:
        from hgext import color
    from diff_highlight import colorui
    from mercurial.util import version as mercurial_version
else:
    color = None


class TestDiffHighlight(unittest.TestCase):
    @unittest.skipIf(color is None, "mercurial is not supported py3")
    def test_colorui(self):
        import curses
        curses.setupterm("xterm", 1)
        color._styles['diff.inserted_highlight'] = 'green inverse'
        color._styles['diff.deleted_highlight'] = 'red inverse'

        ui = colorui()
        if mercurial_version() >= "3.7.0":
            ui.pushbuffer(labeled=True)
        else:
            ui.pushbuffer()

        ui.write("@@ -10,4 +10,6 @@")
        ui.write("\n", '')
        ui.write(" ", '')
        ui.write("\n", '')
        ui.write("-print 'nice', 'boat'", label='diff.deleted')
        ui.write("-print \"bye world\"", label='diff.deleted')
        ui.write("+print 'hello', 'world'", label='diff.inserted')
        ui.write("+", label='diff.inserted')
        ui.write("+", label='diff.inserted')
        ui.write("+print 'bye world'", label='diff.inserted')
        ui.write(" ", '')
        ui.write("\n", '')

        stop = "\x1b(B\x1b[m"

        def start(*colors):
            return stop + "".join("\x1b[%dm" % c for c in colors)

        def restart(*colors):
            return stop + start(*colors)

        if mercurial_version() >= "3.7.0":
            lines = ui.popbuffer().splitlines()
        else:
            lines = ui.popbuffer(True).splitlines()
        self.assertEqual(9, len(lines))
        self.assertEqual("@@ -10,4 +10,6 @@", lines[0])
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
