""" A simplified way to print, or echo, using colors. """
import pyvim
import vim

# from pyvim import highlight_groups


def echo(
    statement='',
    highlight_style=None,
    style=None,
):

    # QuickFix for other plugins clearing this...
    """Add Custom Highlight Groups"""
    vim.command("highlight PyVimSuccess guifg='Green' ctermfg='Green'")
    vim.command("highlight PyVimCaution guifg='Yellow' ctermfg='DarkYellow'")
    vim.command("highlight PyVimDanger guifg='Red' ctermfg='Red'")

    if highlight_style:
        vim.command(f'echohl {highlight_style}')
        vim.command(f'echo "{statement}"')
        vim.command('echohl None')
        # FIX This should be pyvim.highlight_groups
        if highlight_style not in pyvim.highlight_groups.names:
            vim.command('echohl WarningMsg')
            vim.command('echo "Highlight Group not detected."')
            vim.command('echohl None')
    else:
        vim.command(f'echo "{statement}"')


""" Check pyvim/highlighting.py for this code
highlight PyVimSuccess guifg='Red'
highlight PyVimWarning guifg='Red'
highlight PyVimDanger guifg='Red'
"""

"""
guifg={color-name}					*highlight-guifg*
guibg={color-name}					*highlight-guibg*
guisp={color-name}					*highlight-guisp*

:hi comment guifg='salmon pink'


ctermfg={color-nr}				*highlight-ctermfg* *E421*
ctermbg={color-nr}				*highlight-ctermbg*
ctermul={color-nr}				*highlight-ctermul*
# underline (ctermul)

"""
