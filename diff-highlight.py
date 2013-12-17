# -*- coding: utf-8 -*-
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

from hgext import color

# define new style
color._styles['diff.inserted_highlight'] = 'green_background'
color._styles['diff.deleted_highlight'] = 'red_background'


class colorui(color.colorui):
    changes = None

    def __init__(self, src=None):
        super(colorui, self).__init__(src)
        self.changes = []

    def write(self, *args, **opts):
        label = opts.get('label')
        if label in ('diff.inserted', 'diff.deleted'):
            self.changes.append((args, opts))
        elif label == 'diff.trailingwhitespace':  # merge to hunk
            change = self.changes.pop()
            self.changes.append((change[0] + args, change[1]))
        elif label == '' and args == ("\n",) and self.changes:
            self.changes.append((args, opts))
        else:
            self.flush_hunk()
            super(colorui, self).write(*args, **opts)

    def flush_hunk(self):
        if self.changes is None:  # not initialized yet
            return

        new = [c for c in self.changes if c[1]['label'] == 'diff.inserted']
        old = [c for c in self.changes if c[1]['label'] == 'diff.deleted']

        if len(new) == 0 or len(old) == 0:
            # it's new line or old line
            pass
        elif len(new) != len(old):
            # do not markup word-highlights if numbers of lines are mismatched
            pass
        else:
            self.rearrange_highlight(new, old)

        # flush hunk
        for change in self.changes:
            super(colorui, self).write(*change[0], **change[1])

        self.changes = []

    def rearrange_highlight(self, new, old):
        self.changes = []
        oldlines = []
        write = super(colorui, self).write

        for i in range(len(new)):
            new_diff, old_diff = worddiff("".join(new[i][0]),
                                          "".join(old[i][0]))
            oldlines.append(old_diff)

            prefix, highlighted, suffix = new_diff
            if prefix:
                write(prefix, label='diff.inserted')
            if highlighted:
                write(highlighted, label='diff.inserted_highlight')
            if suffix:
                write(suffix, label='diff.inserted')

            write("\n")

        for prefix, highlighted, suffix in oldlines:
            if prefix:
                write(prefix, label='diff.deleted')
            if highlighted:
                write(highlighted, label='diff.deleted_highlight')
            if suffix:
                write(suffix, label='diff.deleted')

            write("\n")

    def flush(self):
        self.flush_hunk()
        super(colorui, self).flush()


def worddiff(new, old):
    # find common prefix
    prefix = 0
    if new[0] == '+' and old[0] == '-':
        prefix = 1

    while prefix < len(new) and prefix < len(old):
        if new[prefix] == old[prefix]:
            prefix += 1
        else:
            break

    # find common suffix
    suffix = 0
    while prefix + suffix < len(new) and prefix + suffix < len(old):
        if new[-suffix - 1] == old[-suffix - 1]:
            suffix += 1
        else:
            break
    suffix_of_newline = len(new) - suffix
    suffix_of_oldline = len(old) - suffix

    ret = []
    if prefix <= 1 and suffix == 0:
        # two lines are different in whole
        ret.append((new, None, None))
        ret.append((old, None, None))
    else:
        if prefix == suffix_of_newline:  # nothing newly changed
            ret.append((new, None, None))
        else:
            ret.append((new[0:prefix],
                        new[prefix:suffix_of_newline],
                        new[suffix_of_newline:]))

        if prefix == suffix_of_oldline:  # nothing newly changed
            ret.append((old, None, None))
        else:
            ret.append((old[0:prefix],
                        old[prefix:suffix_of_oldline],
                        old[suffix_of_oldline:]))

    return ret


def uisetup(ui):
    if ui.plain():
        return
    if not isinstance(ui, colorui):
        colorui.__bases__ = (ui.__class__,)
        ui.__class__ = colorui
