# -*- coding: utf-8 -*-
#
#  Copyright 2013 Takeshi KOMIYA
#  Copyright (c) 2001-2013 Python Software Foundation; All Rights Reserved
#
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012, 2013 Python Software Foundation; All Rights Reserved" are retained
# in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.
#
# flake8: NOQA

import re
from difflib import SequenceMatcher

NORMAL = 0
INSERTED = 1
DELETED = 2


def pprint_hunk(new, new_lo, new_hi, old, old_lo, old_hi):
    # derived from difflib.py (Python stdlib) Differ#_fancy_replace()
    best_ratio, cutoff = 0.59, 0.60

    cruncher = SequenceMatcher(None)
    for j in range(old_lo, old_hi):
        cruncher.set_seq2(old[j])
        for i in range(new_lo, new_hi):
            cruncher.set_seq1(new[i])
            if (cruncher.real_quick_ratio() > best_ratio and
               cruncher.quick_ratio() > best_ratio and
               cruncher.ratio() > best_ratio):
                best_ratio, best_i, best_j = cruncher.ratio(), i, j

    # no non-identical "pretty close" pair
    if best_ratio < cutoff:
        for line in old[old_lo:old_hi]:
            yield line, DELETED, False
            yield "\n", NORMAL, False
        for line in new[new_lo:new_hi]:
            yield line, INSERTED, False
            yield "\n", NORMAL, False

        return

    for hunk in pprint_hunk_helper(new, new_lo, best_i, old, old_lo, best_j):
        yield hunk

    for hunk in pprint_pair(cruncher, new[best_i], old[best_j]):
        yield hunk

    for hunk in pprint_hunk_helper(new, best_i + 1, new_hi,
                                   old, best_j + 1, old_hi):
        yield hunk


def pprint_hunk_helper(new, new_lo, new_hi, old, old_lo, old_hi):
    # derived from difflib.py (Python stdlib) Differ#_fancy_helper()
    if new_lo < new_hi:
        if old_lo < old_hi:
            for hunk in pprint_hunk(new, new_lo, new_hi, old, old_lo, old_hi):
                yield hunk
        else:
            for line in new[new_lo:new_hi]:
                yield line, INSERTED, False
                yield "\n", NORMAL, False
    elif old_lo < old_hi:
        for line in old[old_lo:old_hi]:
            yield line, DELETED, False
            yield "\n", NORMAL, False


def pprint_pair(cruncher, newline, oldline):
    new = [[newline[0], INSERTED, False]]
    old = [[oldline[0], DELETED, False]]

    cruncher.set_seqs(newline[1:], oldline[1:])
    for tag, new1, new2, old1, old2 in cruncher.get_opcodes():
        new_piece = newline[new1 + 1:new2 + 1]
        old_piece = oldline[old1 + 1:old2 + 1]
        if tag == 'equal':
            new.append([new_piece, INSERTED, False])
            old.append([old_piece, DELETED, False])
        else:
            new.append([new_piece, INSERTED, True])
            old.append([old_piece, DELETED, True])

    # change highlighting: character base -> word base
    for i in range(len(new) - 1, 1, -1):
        if is_mergeable(new, old, i):
            new[i - 2][0] += new[i - 1][0]
            old[i - 2][0] += old[i - 1][0]
            del new[i - 1]
            del old[i - 1]

    # optimize ESC chars
    for i in range(len(new) - 1, 0, -1):
        if new[i][1:] == new[i - 1][1:]:
            new[i - 1][0] += new[i][0]
            del new[i]

    for i in range(len(old) - 1, 0, -1):
        if old[i][1:] == old[i - 1][1:]:
            old[i - 1][0] += old[i][0]
            del old[i]

    # write highlighted lines
    merged = old + [['\n', NORMAL, False]] + new + [['\n', NORMAL, False]]
    for string, style, highlighted in merged:
        yield string, style, highlighted


def is_mergeable(new, old, i):
    chars = '[a-zA-Z0-9_.]'
    startswith_word = lambda s: re.match('^%s' % chars, s[0])
    endswith_word = lambda s: re.search('%s$' % chars, s[0])
    is_word = lambda s: re.match('^(%s+|\s+)$' % chars, s[0])

    marks = '[ !"#$%&\'()*+,\-./:;<=>?@\[\\]^_{|}~]'
    startswith_mark = lambda s: re.match('^%s' % marks, s[0])
    endswith_mark = lambda s: re.search('%s$' % marks, s[0])
    is_mark = lambda s: re.match('^(%s+|\s+)$' % marks, s[0])

    n1, n2, n3 = new[i - 2: i + 1]
    o1, o2, o3 = old[i - 2: i + 1]
    if ((n1[2], n2[2], n3[2]) != (True, False, True) and
       (o1[2], o2[2], o3[2]) != (True, False, True)):
        return False

    # WORD1 ends with word(alnum) and WORD2 is word
    if ((endswith_word(n1) and is_word(n2)) or
       (endswith_word(o1) and is_word(o2))):
        return True

    # WORD2 is word and WORD3 starts with word(alnum)
    if ((is_word(n2) and startswith_word(n3)) or
       (is_word(o2) and startswith_word(o3))):
        return True

    # WORD1 ends with any marks and WORD2 is any marks
    if ((endswith_mark(n1) and is_mark(n2)) or
       (endswith_mark(o1) and is_mark(o2))):
        return True

    # WORD2 is any marks and WORD3 starts with any marks
    if ((is_mark(n2) and startswith_mark(n3)) or
       (is_mark(o2) and startswith_mark(o3))):
        return True

    return False
