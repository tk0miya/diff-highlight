# -*- coding: utf-8 -*-

import sys
from six import u
from difflib import SequenceMatcher
from highlights.pprint import NORMAL, INSERTED, DELETED
from highlights.pprint import pprint_hunk, highlight_pair, is_mergeable

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPPrint(unittest.TestCase):
    def test_pprint_hunk(self):
        # new, new_lo, new_hi, old, old_lo, old_hi):
        new = [u("+print 'hello', 'world'"),
               u("+"),
               u("+"),
               u("+print 'bye world'")]
        old = [u("-print 'nice', 'boat'"),
               u("-print \"bye world\"")]
        ret = pprint_hunk(new, 0, 4, old, 0, 2)

        pairs = list(ret)
        self.assertEqual(26, len(pairs))
        self.assertEqual((u("-print '"), DELETED, False), pairs[0])
        self.assertEqual((u("nice"), DELETED, True), pairs[1])
        self.assertEqual((u("', '"), DELETED, False), pairs[2])
        self.assertEqual((u("boat"), DELETED, True), pairs[3])
        self.assertEqual((u("'"), DELETED, False), pairs[4])
        self.assertEqual((u("\n"), NORMAL, False), pairs[5])
        self.assertEqual((u("+print '"), INSERTED, False), pairs[6])
        self.assertEqual((u("hello"), INSERTED, True), pairs[7])
        self.assertEqual((u("', '"), INSERTED, False), pairs[8])
        self.assertEqual((u("world"), INSERTED, True), pairs[9])
        self.assertEqual((u("'"), INSERTED, False), pairs[10])
        self.assertEqual((u("\n"), NORMAL, False), pairs[11])
        self.assertEqual((u("+"), INSERTED, False), pairs[12])
        self.assertEqual((u("\n"), NORMAL, False), pairs[13])
        self.assertEqual((u("+"), INSERTED, False), pairs[14])
        self.assertEqual((u("\n"), NORMAL, False), pairs[15])
        self.assertEqual((u("-print "), DELETED, False), pairs[16])
        self.assertEqual((u("\""), DELETED, True), pairs[17])
        self.assertEqual((u("bye world"), DELETED, False), pairs[18])
        self.assertEqual((u("\""), DELETED, True), pairs[19])
        self.assertEqual((u("\n"), NORMAL, False), pairs[20])
        self.assertEqual((u("+print "), INSERTED, False), pairs[21])
        self.assertEqual((u("'"), INSERTED, True), pairs[22])
        self.assertEqual((u("bye world"), INSERTED, False), pairs[23])
        self.assertEqual((u("'"), INSERTED, True), pairs[24])
        self.assertEqual((u("\n"), NORMAL, False), pairs[25])

    def test_highlight_pair(self):
        cruncher = SequenceMatcher()
        ret = highlight_pair(cruncher,
                             "+print 'hello', 'world'",
                             "-print 'nice', 'boat'")

        pairs = list(ret)
        self.assertEqual(12, len(pairs))
        self.assertEqual((u("-print '"), DELETED, False), pairs[0])
        self.assertEqual((u("nice"), DELETED, True), pairs[1])
        self.assertEqual((u("', '"), DELETED, False), pairs[2])
        self.assertEqual((u("boat"), DELETED, True), pairs[3])
        self.assertEqual((u("'"), DELETED, False), pairs[4])
        self.assertEqual((u("\n"), NORMAL, False), pairs[5])
        self.assertEqual((u("+print '"), INSERTED, False), pairs[6])
        self.assertEqual((u("hello"), INSERTED, True), pairs[7])
        self.assertEqual((u("', '"), INSERTED, False), pairs[8])
        self.assertEqual((u("world"), INSERTED, True), pairs[9])
        self.assertEqual((u("'"), INSERTED, False), pairs[10])
        self.assertEqual((u("\n"), NORMAL, False), pairs[11])

    def test_highlight_appended_text(self):
        # new, new_lo, new_hi, old, old_lo, old_hi):
        new = [u("+Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                 "incididunt ut labore et commodo magna aliqua. Ut enim ad minim veniam, quis "
                 "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
                 "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
                 "fugiat nulla pariatur.")]
        old = [u("-Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                 "incididunt ut labore et dolore magna aliqua.")]
        ret = pprint_hunk(new, 0, 1, old, 0, 1)

        pairs = list(ret)
        self.assertEqual(10, len(pairs))
        self.assertEqual((u("-Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
                            "tempor incididunt ut labore et "), DELETED, False), pairs[0])
        self.assertEqual((u("dolore"), DELETED, True), pairs[1])
        self.assertEqual((u(" magna aliqua."), DELETED, False), pairs[2])
        self.assertEqual((u(""), DELETED, True), pairs[3])
        self.assertEqual((u("\n"), NORMAL, False), pairs[4])
        self.assertEqual((u("+Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
                            "tempor incididunt ut labore et "), INSERTED, False), pairs[5])
        self.assertEqual((u("commodo"), INSERTED, True), pairs[6])
        self.assertEqual((u(" magna aliqua."), INSERTED, False), pairs[7])
        self.assertEqual((u(" Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi "
                            "ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit "
                            "in voluptate velit esse cillum dolore eu fugiat nulla pariatur."),
                          INSERTED, True), pairs[8])
        self.assertEqual((u("\n"), NORMAL, False), pairs[9])

    def test_highlight_indented_lines(self):
        # new, new_lo, new_hi, old, old_lo, old_hi):
        new = [u("+class Foo(object):"),
               u("+    def hello(name):"),
               u("+        print 'Hello ', name")]
        old = [u("-def hello(name):"),
               u("-    print 'Hello ', name")]
        ret = pprint_hunk(new, 0, 3, old, 0, 2)

        pairs = list(ret)
        self.assertEqual(18, len(pairs))
        self.assertEqual((u("+class Foo(object):"), INSERTED, False), pairs[0])
        self.assertEqual((u("\n"), NORMAL, False), pairs[1])
        self.assertEqual((u("-"), DELETED, False), pairs[2])
        self.assertEqual((u(""), DELETED, True), pairs[3])
        self.assertEqual((u("def hello(name):"), DELETED, False), pairs[4])
        self.assertEqual((u("\n"), NORMAL, False), pairs[5])
        self.assertEqual((u("-"), DELETED, False), pairs[6])
        self.assertEqual((u(""), DELETED, True), pairs[7])
        self.assertEqual((u("    print 'Hello ', name"), DELETED, False), pairs[8])
        self.assertEqual((u("\n"), NORMAL, False), pairs[9])
        self.assertEqual((u("+"), INSERTED, False), pairs[10])
        self.assertEqual((u("    "), INSERTED, True), pairs[11])
        self.assertEqual((u("def hello(name):"), INSERTED, False), pairs[12])
        self.assertEqual((u("\n"), NORMAL, False), pairs[13])
        self.assertEqual((u("+"), INSERTED, False), pairs[14])
        self.assertEqual((u("    "), INSERTED, True), pairs[15])
        self.assertEqual((u("    print 'Hello ', name"), INSERTED, False), pairs[16])
        self.assertEqual((u("\n"), NORMAL, False), pairs[17])

    def test_is_mergeable(self):
        # True/False/True -> ok
        new = [('A', None, True), ('B', None, False), ('C', None, True)]
        old = [('', None, False), ('B', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # False/False/True -> NG
        new = [('A', None, False), ('B', None, False), ('C', None, True)]
        old = [('A', None, False), ('B', None, False), ('', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))

        # True/False/False -> NG
        new = [('A', None, True), ('B', None, False), ('C', None, False)]
        old = [('', None, False), ('B', None, False), ('C', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))

        # False/False/False -> NG
        new = [('A', None, False), ('B', None, False), ('C', None, False)]
        old = [('A', None, False), ('B', None, False), ('C', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))

        # word/word/word -> ok
        new = [('A', None, True), ('B', None, False), ('C', None, True)]
        old = [('', None, False), ('B', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # word/space/word -> ok
        new = [('A', None, True), (' ', None, False), ('C', None, True)]
        old = [('', None, False), (' ', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # word/mark/word -> NG
        new = [('A', None, True), (',', None, False), ('C', None, True)]
        old = [('', None, False), (',', None, False), ('', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))

        # word/word/mark -> ok
        new = [('A', None, True), ('B', None, False), (',', None, True)]
        old = [('', None, False), ('B', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # mark/word/word -> ok
        new = [(',', None, True), ('B', None, False), ('C', None, True)]
        old = [('', None, False), ('B', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # mark/mark/mark -> ok
        new = [(',', None, True), (':', None, False), ('.', None, True)]
        old = [('', None, False), (':', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # mark/word/mark -> ok
        new = [(',', None, True), ('B', None, False), ('.', None, True)]
        old = [('', None, False), ('B', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # mark/space/mark -> ok
        new = [(',', None, True), (' ', None, False), ('.', None, True)]
        old = [('', None, False), (' ', None, False), ('', None, False)]
        self.assertTrue(is_mergeable(new, old, 2))
        self.assertTrue(is_mergeable(old, new, 2))

        # A/ is /C => A/ is /C -> NG
        new = [('A', None, True), (' is ', None, False), ('C', None, True)]
        old = [('', None, False), (' is ', None, False), ('', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))

        # A/ = /C => A/ = /C -> NG
        new = [('A', None, True), (' = ', None, False), ('C', None, True)]
        old = [('', None, False), (' = ', None, False), ('', None, False)]
        self.assertFalse(is_mergeable(new, old, 2))
        self.assertFalse(is_mergeable(old, new, 2))
