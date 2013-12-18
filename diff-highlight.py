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

# define new style
color._styles['diff.inserted_highlight'] = 'green_background'
color._styles['diff.deleted_highlight'] = 'red_background'


class colorui(color.colorui):
    hunk = None

    def __init__(self, src=None):
        super(colorui, self).__init__(src)
        self.hunk = []

    def write(self, *args, **opts):
        label = opts.get('label')
        if label in ('diff.inserted', 'diff.deleted'):
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

        new = [c[0] for c in self.hunk if c[1]['label'] == 'diff.inserted']
        old = [c[0] for c in self.hunk if c[1]['label'] == 'diff.deleted']

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
                write(line, "\n", label="diff.deleted")
            for line in new[new_lo:new_hi]:
                write(line, "\n", label="diff.inserted")

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
                    write(line, "\n", label="diff.inserted")
        elif old_lo < old_hi:
            for line in old[old_lo:old_hi]:
                write(line, "\n", label="diff.deleted")

    def pprint_pair(self, cruncher, newline, oldline):
        write = super(colorui, self).write

        new = [[newline[0], 'diff.inserted']]
        old = [[oldline[0], 'diff.deleted']]
        cruncher.set_seqs(newline[1:], oldline[1:])
        for tag, new1, new2, old1, old2 in cruncher.get_opcodes():
            new_piece = newline[new1 + 1:new2 + 1]
            old_piece = oldline[old1 + 1:old2 + 1]
            if tag == 'equal':
                new.append([new_piece, "diff.inserted"])
                old.append([old_piece, "diff.deleted"])
            else:
                new.append([new_piece, "diff.inserted_highlight"])
                old.append([old_piece, "diff.deleted_highlight"])

        # change highlighting: character base -> word base
        endswith_word = lambda s: re.search('[a-zA-Z0-9_.]$', s)
        is_word = lambda s: re.match('^[a-zA-Z0-9_.]+$', s)
        for i in range(len(new) - 1):
            if (new[i][1] == 'diff.inserted_highlight' and
                new[i + 1][1] == 'diff.inserted' and
                ((endswith_word(new[i][0]) and is_word(new[i + 1][0])) or
                 (endswith_word(old[i][0]) and is_word(old[i + 1][0])))):
                new[i][0] += new[i + 1][0]
                old[i][0] += old[i + 1][0]
                new[i + 1] = ['', 'diff.inserted_highlight']
                old[i + 1] = ['', 'diff.deleted_highlight']

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
            write(string, label=label)


def uisetup(ui):
    if ui.plain():
        return
    if not isinstance(ui, colorui):
        colorui.__bases__ = (ui.__class__,)
        ui.__class__ = colorui
