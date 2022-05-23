# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Simple Notebook Visualiser
#
# Simple notebook visualiser for one or more Jupyter notebooks.
#
# Visualises markdown and code cells, with block size determined by code cell line count and estimated screen line count for markdown cells.

# +
import math
import matplotlib.pyplot as plt
import list_imports
from io import  BytesIO
import base64  
import jupytext
from .text_quality import md_readtime
from pathlib import Path

def nb_vis(cell_map, img_file='', linewidth = 5, w=20, gap=None,
           gap_boost=1, gap_colour='lightgrey', retval='',
           wordless=False, minimal=False, header_gap=0.2, dpi=80, **kwargs):
    """Visualise notebook gross cell structure."""

    def get_gap(cell_map):
        """Automatically set the gap value based on overall length"""
        
        def get_overall_length(cell_map):
            """Get overall line length of a notebook."""
            overall_len = 0
            gap = 0
            for i ,(l,t) in enumerate(cell_map):
                #i is number of cells if that's useful too?
                overall_len = overall_len + l
            return overall_len

        max_overall_len = 0
        
        #If we are generating a plot for multiple notebooks, get the largest overall length
        if isinstance(cell_map,dict):
            for k in cell_map:
                _overall_len = get_overall_length(cell_map[k])
                max_overall_len = _overall_len if _overall_len > max_overall_len else max_overall_len
        else:
            max_overall_len = get_overall_length(cell_map)

        #Set the gap at 0.5% of the overall length
        return math.ceil(max_overall_len * 0.01)
        
        
    def plotter(cell_map, x, y, label='', header_gap = 0.2):
        """Plot visualisation of gross cell structure for a single notebook."""

        for _cell_map in cell_map:

            #Add a coloured bar between cells
            if y > 0:
                if gap_colour:
                    plt.plot([y,y+gap],[x,x], gap_colour, linewidth=linewidth)

                y = y + gap
            
            _y = y + _cell_map[0] + 1 #Make tiny cells slightly bigger
            plt.plot([y,_y],[x,x], _cell_map[1], linewidth=linewidth)

            y = _y
    
    x = 1
    y = 0
    
    gap = gap if gap is not None else get_gap(cell_map) * gap_boost
    h = 1+len(cell_map) if not minimal else len(cell_map)*linewidth/dpi
    fig, ax = plt.subplots(figsize=(1200/dpi, h))
    
    if not wordless and not minimal:
        plt.text(0, 0, "\nNotebook quality report")
        
    #Add a registration point to the plot
    plt.plot([0,0],[0,0])
    for k in cell_map:
        if not wordless and not minimal:
            #Plot notebook path
            plt.text(y, x, k)
            x = x + header_gap
        plotter(cell_map[k], x, y, k, header_gap=header_gap)
        x = x + 1

    plt.ioff()
    ax.axis('off')
    plt.gca().invert_yaxis()
    
    if img_file:
        plt.savefig(img_file)
    
    if retval=='fig':
        return fig, ax
    elif retval=='img':
        output = BytesIO()
        plt.savefig(output, format="png")
        plt.close(fig)
        # <img src="data:image/png;base64,{}"/>
        return base64.encodebytes(output.getvalue()).decode()
# -

# Define the colour map for different cell types:

VIS_COLOUR_MAP  = {'markdown':'cornflowerblue', 'code':'pink', 'raw':'orange'}
LINE_WIDTH = 160

# The following function will find one or more notebooks on a path and generate cell maps for each of them. All the cell maps are then passed for visualisation on the same canvas.

# +
import nbformat
import os
import textwrap
    
def nb_big_parse_nb(path='', text_formats=True, raw='',  **kwargs):
    """Parse one or more notebooks on a path."""
    
    def _count_screen_lines(txt, width=LINE_WIDTH):
        """Count the number of screen lines that an overflowing text line takes up."""
        ll = txt.split('\n')
        _ll = []
        for l in ll:
            #Model screen flow: split a line if it is more than `width` characters long
            _ll=_ll+textwrap.wrap(l, width)
        n_screen_lines = len(_ll)
        return n_screen_lines
    
    
    def _nb_big_parse_nb(fn='.', text_formats=True, raw='', **kwargs):
        """Parse a notebook and generate the nb_vis cell map for it."""

        cell_map = []
        imports = []
        text_report = {'reading_time':0}
          
        if raw:
            nb = raw
        elif fn:
            fmts = ['.ipynb']
            if text_formats:
                fmts = fmts + ['.md', '.Rmd', '.py']
            _fn, fn_ext = os.path.splitext(fn)

            if fn_ext not in fmts or not os.path.isfile(fn):
                # Better to return this as empty and check downstream?
                return { 'cell_map':{}, 'imports':{}, 'text_report':{}}

            if fn_ext=='.ipynb':
                with open(fn,'r') as f:
                    nb = nbformat.reads(f.read(), as_version=4)
            else:
                nb = jupytext.read(fn)
        else:
            return { 'cell_map':{}, 'imports':{}, 'text_report':{}}

        for cell in nb.cells:
            if cell['cell_type'] not in VIS_COLOUR_MAP:
                continue
            cell_map.append((_count_screen_lines(cell['source']), VIS_COLOUR_MAP[cell['cell_type']]))
            if cell['cell_type']=='code':
                # AST parser breaks on ipython magic, etc
                clean_code = [c for c in cell['source'].split('\n') if not c.startswith(('!','%'))]
                for code in clean_code:
                    try:
                        imports = imports + list_imports.parse(code)
                    except:
                        pass
            elif cell['cell_type']=='markdown':
                text_report['reading_time'] += md_readtime(cell['source'], rounding_override=True, **kwargs)
        if 'rounded_minutes' in kwargs and kwargs['rounded_minutes']:
            if 'reading_time' in text_report:
                text_report['reading_time'] =  math.ceil(text_report['reading_time']/60)
        return { 'cell_map':cell_map, 'imports':list(set(imports)), 'text_report':text_report }

    def _dir_walker(path='.', exclude = 'default', text_formats=True):
        """Profile all the notebooks in a specific directory and in any child directories."""

        if exclude == 'default':
            exclude_paths = ['.ipynb_checkpoints', '.git', '.ipynb', '__MACOSX']
        else:
            #If we set exclude, we need to pass it as a list
            exclude_paths = exclude
        nb_multidir_cell_map = {}
        nb_multidir_imports = {}
        nb_multidir_text_report = {}
        path = Path(path)
        if not path.is_dir():
            return
        for fn in path.rglob("*.ipynb"):
            #Start walking...
            if not set(exclude_paths).intersection(set(fn.parts)):
                #Profile that directory...
                    reports = _nb_big_parse_nb(fn, text_formats, **kwargs )
                    cell_map = reports['cell_map']
                    imports = reports['imports']
                    text_report = reports['text_report']
                    if cell_map:
                        nb_multidir_cell_map = {**nb_multidir_cell_map, fn: cell_map}
                    if imports:
                        nb_multidir_imports = {**nb_multidir_imports, fn: imports}
                    if text_report:
                        nb_multidir_text_report = {**nb_multidir_text_report, fn: text_report}
        return {"cell_map": nb_multidir_cell_map,
                "imports": nb_multidir_imports,
                "text_report": nb_multidir_text_report}
        
    # Also: we need to be able to switch on and off which reports are run
    # Need to think about handling this properly e.g. in context of plugins
    if not raw and os.path.isdir(path):
        reports = _dir_walker(path, text_formats=text_formats)
        cell_map = reports['cell_map']
        imports = reports['imports']
        text_report = reports['text_report']
    else:
        reports =  _nb_big_parse_nb(path, text_formats, raw=raw, **kwargs)
        
        cell_map = {path: reports['cell_map']}
        imports = {path: reports['imports']}
        text_report = {path: reports['text_report']}
    
    return {"cell_map": cell_map,
            "imports": imports,
            "text_report": text_report}


def nb_vis_parse_nb(path='.', img_file='', linewidth = 5, w=20, text_formats=True, retval='', raw='', **kwargs):
    """Do a big parse and then chart the result."""
    reports = nb_big_parse_nb(path, text_formats, raw=raw, **kwargs)
    cell_map = reports["cell_map"]
    response = nb_vis(cell_map, img_file, linewidth, w, retval=retval, **kwargs)
    if retval:
        return response

def nb_imports_parse_nb(path='.', text_formats=True,
                        raw='', installed=True):
    """Do a big parse and then print the result."""

    reports = nb_big_parse_nb(path, text_formats, raw=raw)
    imports = reports["imports"]
    all_packages = []
    for i in imports:
        packages = [p.split('.')[0] for p in imports[i]]
        all_packages = all_packages + packages
        print(f"Imports in {i}: {', '.join(packages)}")
    all_packages = set(all_packages)
    print(f"All imports: {', '.join(all_packages)}")
    if installed:
        import importlib
        fails = [p for p in all_packages if not importlib.util.find_spec(p)]
        if fails:
            print(f"The following packages cannot be imported: {''.join(fails)}")
        else:
            print("All packages can be imported.")

    # For package details:
    #import pkg_resources
    #print([p.project_name for p in pkg_resources.working_set])
    # We can also pull out things like package requirements, etc.


def nb_text_parse_nb(path='.', text_formats=True, reading_rate=100, rounded_minutes=False, raw=''):
    """Parse markdown text in notebook(s)."""
    reports = nb_big_parse_nb(path, text_formats, reading_rate=reading_rate, rounded_minutes=rounded_minutes, raw=raw)
    print(reports['text_report'])


# + tags=["active-ipynb"]
# Test a single notebook mapper:

# + tags=["active-ipynb"]
# TEST_NOTEBOOK = 'Notebook_profile_test.ipynb'

# + tags=["active-ipynb"]
# nb_vis_parse_nb(TEST_NOTEBOOK)

# + tags=["active-ipynb"]
# Test a plot of multiple notebooks down a path:

# + tags=["active-ipynb"]
# nb_vis_parse_nb('../Documents/GitHub/tm351-undercertainty/notebooks/tm351/Part 02 Notebooks',
#                 linewidth=10, gap_colour='white', gap=1, img_file='test-nbvis.png')

# + tags=["active-ipynb"]
# nb_vis_parse_nb('../Documents/GitHub/tm351-undercertainty/notebooks/tm351/Part 02 Notebooks',
#                 linewidth=10, gap=0, img_file='test-nbvis.png')

# + tags=["active-ipynb"]
# Can we see the saved test file?
#
# ![](test-nbvis.png)
