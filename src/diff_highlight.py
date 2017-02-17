# -*- coding: utf-8 -*-
#  Copyright 2013 Takeshi KOMIYA
#  Copyright (c) 2001-2013 Python Software Foundation; All Rights Reserved
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
from mercurial import extensions
from mercurial.i18n import _
from highlights.pprint import INSERTED, DELETED, pprint_hunk

INSERT_NORM = 'diff.inserted'
INSERT_EMPH = 'diff.inserted_highlight'
DELETE_NORM = 'diff.deleted'
DELETE_EMPH = 'diff.deleted_highlight'


class colorui(color.colorui):
    hunk = None
    tab = None

    def __init__(self, src=None):
        super(colorui, self).__init__(src)
        self.hunk = []

    def write(self, *args, **opts):
        label = opts.get('label')
        if label in (INSERT_NORM, DELETE_NORM):
            if self.tab is not None:
                change = self.hunk.pop()
                self.hunk.append((change[0] + self.tab + "".join(args), change[1]))
                self.tab = None
            else:
                self.hunk.append(("".join(args), opts))
        elif label == 'diff.trailingwhitespace':  # merge to hunk
            change = self.hunk.pop()
            self.hunk.append((change[0] + "".join(args), change[1]))
        elif label == 'diff.tab':
            self.tab = "".join(args)
        elif label == '' and args == ("\n",) and self.hunk:
            self.hunk.append((args[0], opts))
        else:
            self.flush_hunk()
            super(colorui, self).write(*args, **opts)

    def flush(self):
        self.flush_hunk()
        super(colorui, self).flush()

    def flush_hunk(self):
        if self.hunk is None:  # not initialized yet
            return

        hunk = [(ret[0].decode('utf-8'), ret[1]) for ret in self.hunk]
        new = [c[0] for c in hunk if c[1]['label'] == INSERT_NORM]
        old = [c[0] for c in hunk if c[1]['label'] == DELETE_NORM]

        write = super(colorui, self).write
        for string, style, highlighted in pprint_hunk(new, 0, len(new),
                                                      old, 0, len(old)):
            if style == INSERTED:
                if highlighted:
                    write(string.encode('utf-8'), label=INSERT_EMPH)
                else:
                    write(string.encode('utf-8'), label=INSERT_NORM)
            elif style == DELETED:
                if highlighted:
                    write(string.encode('utf-8'), label=DELETE_EMPH)
                else:
                    write(string.encode('utf-8'), label=DELETE_NORM)
            else:
                write(string.encode('utf-8'), label='')

        self.hunk = []


def uisetup(ui):
    if ui.plain():
        return

    try:
        extensions.find('color')
    except KeyError:
        ui.warn(_("warning: 'diff-highlight' requires 'color' extension "
                  "to be enabled, but not\n"))
        return

    if not isinstance(ui, colorui):
        colorui.__bases__ = (ui.__class__,)
        ui.__class__ = colorui

    def colorconfig(orig, *args, **kwargs):
        ret = orig(*args, **kwargs)

        styles = color._styles
        if INSERT_EMPH not in styles:
            styles[INSERT_EMPH] = styles[INSERT_NORM] + ' inverse'

        if DELETE_EMPH not in styles:
            styles[DELETE_EMPH] = styles[DELETE_NORM] + ' inverse'

        return ret

    extensions.wrapfunction(color, 'configstyles', colorconfig)
