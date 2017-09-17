# -*- coding: utf-8 -*-
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3, 0):
    try:
        from hgext import color

        colorext = color
    except ImportError:
        colorext = None
    try:
        from mercurial import color
    except ImportError:
        pass
    from diff_highlight import colorui
    from mercurial.util import version as mercurial_version
else:
    color = None


class TestDiffHighlight(unittest.TestCase):
    @unittest.skipIf(color is None, "mercurial is not supported py3")
    def test_colorui(self):
        try:
            import curses

            curses.setupterm("xterm", 1)
        except ImportError:
            pass

        ui = colorui()
        if mercurial_version() >= "4.2.0":
            ui.setconfig('ui', 'color', 'always')
            color.setup(ui)
            styles = ui._styles
        else:
            colorui.__bases__ = (colorext.colorui,)
            styles = color._styles
        styles['diff.inserted_highlight'] = 'green inverse'
        styles['diff.deleted_highlight'] = 'red inverse'

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

        if mercurial_version() >= "4.2.0":
            stop = "\x1b[0m"

            def start(*colors):
                return "\x1b[0;" + ";".join(str(c) for c in colors) + "m"

            def restart(*colors):
                return stop + start(*colors)
        else:
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
