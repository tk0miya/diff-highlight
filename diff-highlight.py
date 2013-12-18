# -*- coding: utf-8 -*-
#  Copyright (c) 2001-2013 Python Software Foundation; All Rights Reserved
#  Copyright 2013 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from hgext import color
from difflib import SequenceMatcher

INSERT_NORM = 'diff.inserted'
INSERT_EMPH = 'diff.inserted_highlight'
DELETE_NORM = 'diff.deleted'
DELETE_EMPH = 'diff.deleted_highlight'

# define new style
color._styles[INSERT_EMPH] = 'green_background'
color._styles[DELETE_EMPH] = 'red_background'


class colorui(color.colorui):
    hunk = None

    def __init__(self, src=None):
        super(colorui, self).__init__(src)
        self.hunk = []

    def write(self, *args, **opts):
        label = opts.get('label')
        if label in (INSERT_NORM, DELETE_NORM):
            self.hunk.append(("".join(args), opts))
        elif label == 'diff.trailingwhitespace':  # merge to hunk
            change = self.hunk.pop()
            self.hunk.append((change[0] + "".join(args), change[1]))
        elif label == '' and args == ("\n",) and self.hunk:
            self.hunk.append((args, opts))
        else:
            self.flush_hunk()
            super(colorui, self).write(*args, **opts)

    def flush(self):
        self.flush_hunk()
        super(colorui, self).flush()

    def flush_hunk(self):
        if self.hunk is None:  # not initialized yet
            return

        new = [c[0] for c in self.hunk if c[1]['label'] == INSERT_NORM]
        old = [c[0] for c in self.hunk if c[1]['label'] == DELETE_NORM]

        self.pprint_hunk(new, 0, len(new), old, 0, len(old))

        self.hunk = []

    def pprint_hunk(self, new, new_lo, new_hi, old, old_lo, old_hi):
        # derived from difflib.py (Python stdlib) Differ#_fancy_replace()
        best_ratio, cutoff = 0.59, 0.60
        write = super(colorui, self).write

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
                write(line, "\n", label=DELETE_NORM)
            for line in new[new_lo:new_hi]:
                write(line, "\n", label=INSERT_NORM)

            return

        self.pprint_hunk_helper(new, new_lo, best_i,
                                old, old_lo, best_j)
        self.pprint_pair(cruncher, new[best_i], old[best_j])
        self.pprint_hunk_helper(new, best_i + 1, new_hi,
                                old, best_j + 1, old_hi)

    def pprint_hunk_helper(self, new, new_lo, new_hi, old, old_lo, old_hi):
        # derived from difflib.py (Python stdlib) Differ#_fancy_helper()
        write = super(colorui, self).write

        if new_lo < new_hi:
            if old_lo < old_hi:
                self.pprint_hunk(new, new_lo, new_hi, old, old_lo, old_hi)
            else:
                for line in new[new_lo:new_hi]:
                    write(line, "\n", label=INSERT_NORM)
        elif old_lo < old_hi:
            for line in old[old_lo:old_hi]:
                write(line, "\n", label=DELETE_NORM)

    def pprint_pair(self, cruncher, newline, oldline):
        write = super(colorui, self).write

        new = [[newline[0].decode('utf-8'), INSERT_NORM]]
        old = [[oldline[0].decode('utf-8'), DELETE_NORM]]
        cruncher.set_seqs(newline[1:].decode('utf-8'),
                          oldline[1:].decode('utf-8'))
        for tag, new1, new2, old1, old2 in cruncher.get_opcodes():
            new_piece = newline[new1 + 1:new2 + 1]
            old_piece = oldline[old1 + 1:old2 + 1]
            if tag == 'equal':
                new.append([new_piece, INSERT_NORM])
                old.append([old_piece, DELETE_NORM])
            else:
                new.append([new_piece, INSERT_EMPH])
                old.append([old_piece, DELETE_EMPH])

        # change highlighting: character base -> word base
        for i in range(len(new) - 1, 1, -1):
            if is_mergeable(new, old, i):
                new[i - 2][0] += new[i - 1][0]
                old[i - 2][0] += old[i - 1][0]
                del new[i - 1]
                del old[i - 1]

        # optimize ESC chars
        for i in range(len(new) - 1, 0, -1):
            if new[i][1] == new[i - 1][1]:
                new[i - 1][0] += new[i][0]
                del new[i]

        for i in range(len(old) - 1, 0, -1):
            if old[i][1] == old[i - 1][1]:
                old[i - 1][0] += old[i][0]
                del old[i]

        # write highlighted lines
        for string, label in old + [['\n', '']] + new + [['\n', '']]:
            write(string.encode('utf-8'), label=label)


def is_mergeable(new, old, i):
    chars = '[a-zA-Z0-9_.]'
    startswith_word = lambda s: re.match('^%s' % chars, s)
    endswith_word = lambda s: re.search('%s$' % chars, s)
    is_word = lambda s: re.match('^(%s|\s)+$' % chars, s)

    marks = '[ !"#$%&\'()*+,\-./:;<=>?@\[\\]^_{|}~]'
    startswith_mark = lambda s: re.match('^%s' % marks, s)
    endswith_mark = lambda s: re.search('%s$' % marks, s)
    is_mark = lambda s: re.match('^(%s|\s)+$' % marks, s)

    n1, n2, n3 = new[i - 2: i + 1]
    o1, o2, o3 = old[i - 2: i + 1]
    if not (n1[1] == n3[1] == INSERT_EMPH and n2[1] == INSERT_NORM):
        return False

    # WORD1 ends with word(alnum) and WORD2 is word
    if ((endswith_word(n1[0]) and is_word(n2[0])) or
       (endswith_word(o1[0]) and is_word(o2[0]))):
        return True

    # WORD2 is word and WORD3 starts with word(alnum)
    if ((is_word(n2[0]) and startswith_word(n3[0])) or
       (is_word(o2[0]) and startswith_word(o3[0]))):
        return True

    # WORD1 ends with any marks and WORD2 is any marks
    if ((endswith_mark(n1[0]) and is_mark(n2[0])) or
       (endswith_mark(o1[0]) and is_mark(o2[0]))):
        return True

    # WORD2 is any marks and WORD3 starts with any marks
    if ((is_mark(n1[0]) and startswith_mark(n2[0])) or
       (is_mark(o1[0]) and startswith_mark(o2[0]))):
        return True

    return False


def uisetup(ui):
    if ui.plain():
        return
    if not isinstance(ui, colorui):
        colorui.__bases__ = (ui.__class__,)
        ui.__class__ = colorui
