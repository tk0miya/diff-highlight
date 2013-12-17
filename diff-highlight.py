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

        inserted = [change for change in self.changes
                    if change[1]['label'] == 'diff.inserted']
        deleted = [change for change in self.changes
                   if change[1]['label'] == 'diff.deleted']

        if len(inserted) == 0 or len(deleted) == 0:
            # it's new line or deleted line
            pass
        elif len(inserted) != len(deleted):
            # do not markup word-highlights if numbers of lines are mismatched
            pass
        else:
            self.rearrange_highlight(inserted, deleted)

        # flush hunk
        for change in self.changes:
            super(colorui, self).write(*change[0], **change[1])

        self.changes = []

    def rearrange_highlight(self, inserted, deleted):
        self.changes = []
        deleted_lines = []
        write = super(colorui, self).write

        for i in range(len(inserted)):
            inserted_diff, deleted_diff = worddiff("".join(inserted[i][0]),
                                                   "".join(deleted[i][0]))
            deleted_lines.append(deleted_diff)

            prefix, highlighted, suffix = inserted_diff
            if prefix:
                write(prefix, label='diff.inserted')
            if highlighted:
                write(highlighted, label='diff.inserted_highlight')
            if suffix:
                write(suffix, label='diff.inserted')

            write("\n")

        for prefix, highlighted, suffix in deleted_lines:
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


def worddiff(inserted, deleted):
    # find common prefix
    prefix = 0
    if inserted[0] == '+' and deleted[0] == '-':
        prefix = 1

    while prefix < len(inserted) and prefix < len(deleted):
        if inserted[prefix] == deleted[prefix]:
            prefix += 1
        else:
            break

    # find common suffix
    suffix = 0
    while prefix + suffix < len(inserted) and prefix + suffix < len(deleted):
        if inserted[-suffix - 1] == deleted[-suffix - 1]:
            suffix += 1
        else:
            break
    suffix_of_inserted = len(inserted) - suffix
    suffix_of_deleted = len(deleted) - suffix

    ret = []
    if prefix <= 1 and suffix == 0:
        # two lines are different in whole
        ret.append((inserted, '', ''))
        ret.append((deleted, '', ''))
    else:
        if prefix == suffix_of_inserted:  # nothing newly inserted
            ret.append((inserted, '', ''))
        else:
            ret.append((inserted[0:prefix],
                        inserted[prefix:suffix_of_inserted],
                        inserted[suffix_of_inserted:]))

        if prefix == suffix_of_deleted:  # nothing newly deleted
            ret.append((deleted, '', ''))
        else:
            ret.append((deleted[0:prefix],
                        deleted[prefix:suffix_of_deleted],
                        deleted[suffix_of_deleted:]))

    return ret


def uisetup(ui):
    if ui.plain():
        return
    if not isinstance(ui, colorui):
        colorui.__bases__ = (ui.__class__,)
        ui.__class__ = colorui
