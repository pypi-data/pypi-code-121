""" Vim Highlighting """
import re

import vim


""" Add Custom Highlight Groups """
vim.command("highlight PyVimSuccess guifg='Green' ctermfg='Green'")
vim.command("highlight PyVimCaution guifg='Yellow' ctermfg='DarkYellow'")
vim.command("highlight PyVimDanger guifg='Red' ctermfg='Red'")


class HighlightGroup:
    def __init__(self, name, **attributes):
        self.name = name
        self.attributes = dict(**attributes)

    def __contains__(self, item):
        return item in self.attributes

    def __str__(self):
        return f'{self.name}\n\t{self.attributes}'

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, item):
        self.attributes[key] = item


class HighlightGroupCollection:

    defaults = [
        'ColorColumn',
        'Conceal',
        'Cursor',
        'lCursor',
        'CursorIM',
        'CursorColumn',
        'CursorLine',
        'Directory',
        'DiffAdd',
        'DiffChange',
        'DiffDelete',
        'DiffText',
        'EndOfBuffer',
        'ErrorMsg',
        'VertSplit',
        'Folded',
        'FoldColumn',
        'SignColumn',
        'IncSearch',
        'LineNr',
        'LineNrAbove',
        'LineNrBelow',
        'CursorLineNr',
        'MatchParen',
        'ModeMsg',
        'MoreMsg',
        'NonText',
        'Normal',
        'Pmenu',
        'PmenuSel',
        'PmenuSbar',
        'PmenuThumb',
        'Question',
        'QuickFixLine',
        'Search',
        'SpecialKey',
        'SpellBad',
        'SpellCap',
        'SpellLocal',
        'SpellRare',
        'StatusLine',
        'StatusLineNC',
        'StatusLineTerm',
        'StatusLineTermNC',
        'TabLine',
        'TabLineFill',
        'TabLineSel',
        'Terminal',
        'Title',
        'Visual',
        'VisualNOS',
        'WarningMsg',
        'WildMenu',
    ]

    def __init__(self, highlight_groups=None):
        if not highlight_groups:
            self.groups = self.__class__.get_highlight_groups()
            self.names = [i.name for i in self.groups]
        else:
            self.groups = highlight_groups

    def __str__(self):
        return '\n'.join([str(i) for i in self.groups])

    def __repr__(self):
        return self.__str__()

    def __contains__(self, name):
        return name in self.names

    def __add__(self, highlight_group):
        pass

    def search(self, target, case=False, regex=False):
        """Return a list of items using substring.

        Parameters
        ----------
        target : str
            What you're trying to look for.
        case : bool, optional
            Default: False
            Case-Sensitivity
        regex : bool, optional
            Default: False
            Allows use of regex.

        Returns
        -------
        matches : list
            A list of matches.

        """
        if regex:
            if case:
                re_target = re.compile(target)
            else:
                re_target = re.compile(target, re.IGNORECASE)
            return list(filter(re_target.match, self.names))
        else:
            if case:
                return [name for name in self.names if target in name]
            else:
                return [
                    name
                    for name in self.names
                    if target.lower() in name.lower()
                ]

    @staticmethod
    def get_highlight_groups():
        """Get the highlight groups from Vim."""
        # This function is a simple hack around Vim's redir
        redir_function = """
        function! RedirectCommandOutput(excmd) abort
            try
                redir => out
                exe 'silent! ' . a:excmd
            finally
                redir END
            endtry
                return out
        endfunction
        """
        vim.command(redir_function)

        function = 'RedirectCommandOutput'
        argument = 'highlight'
        command = f'{function}("{argument}")'
        group_lines = vim.eval(command).splitlines()

        highlight_groups = []

        for i, line in enumerate(group_lines):

            if not line:
                continue

            notes = ''
            if line.startswith(' '):
                notes = line.strip()
                continue

            group_list = line.split()
            name = group_list[0]
            example = group_list[1]
            attributes_list = group_list[2:]

            attributes = {}
            for pair in attributes_list:
                key = pair.split('=')[0]
                value = pair.split('=')[-1]
                attributes[key] = value

            group = HighlightGroup(name, **attributes)

            highlight_groups.append(group)

        return highlight_groups


# collection = HighlightGroupCollection()
# highlight_groups = collection.groups
highlight_groups = HighlightGroupCollection()
