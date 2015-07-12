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

import re
import sys
from highlights.pprint import INSERTED, DELETED, pprint_hunk

colortable = {'none': 0, 'red': 31, 'green': 32}


def highlight_main():
    try:
        new, old = [], []
        in_header = True
        for rawline in sys.stdin:
            if sys.version_info < (3, 0):
                rawline = rawline.decode('utf-8')

            # strip ESC chars and CR/LF
            stripped = re.sub('\x1b\[[0-9;]*m', '', rawline.rstrip("\r\n"))

            if in_header:
                if re.match('^(@|commit \w+$)', stripped):
                    in_header = False
            else:
                if not re.match('^(?:[ +\-@\\\\]|diff)', stripped):
                    in_header = True

            if not in_header and stripped.startswith('+'):
                new.append(stripped)
            elif not in_header and stripped.startswith('-'):
                old.append(stripped)
            else:
                show_hunk(new, old)
                new, old = [], []
                write(rawline)

        show_hunk(new, old)  # flush last hunk
    except IOError:
        pass


def show_hunk(new, old):
    for string, style, highlighted, in pprint_hunk(new, 0, len(new),
                                                   old, 0, len(old)):

        if style == INSERTED:
            if highlighted:
                write(string, 'green', True)
            else:
                write(string, 'green')
        elif style == DELETED:
            if highlighted:
                write(string, 'red', True)
            else:
                write(string, 'red')
        else:
            write(string)


def write(string, color=None, highlight=False):
    if color:
        sys.stdout.write("\x1b[%dm" % colortable[color])

    if highlight:
        sys.stdout.write("\x1b[7m")

    if sys.version_info < (3, 0):
        sys.stdout.write(string.encode('utf-8'))
    else:
        sys.stdout.write(string)

    if highlight or color:
        sys.stdout.write("\x1b[%dm" % colortable['none'])
