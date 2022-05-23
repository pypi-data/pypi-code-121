# ---
# jupyter:
#   jupytext:
#     formats: ipynb,nb_quality_profile//py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Notebook Profiles
#
# This exploratory coding notebook explores several techniques to support the static profiling of Jupyter notebooks as texts, reporting on various metrics, including:
#
# - notebook size (markdown and code line counts);
# - readability scores;
# - reading time estimates;
# - code complexity and maintability.
#
# The motivating context was a tool for generating summary reports on the estimated workload associated with 100 or so  notebooks over 25 or so directories (1 directory / 4 notebooks per week) for a third year undergraduate equivalent Open University course on data management and analysis.
#
# Previous notebook recipes include generating simple reports that pull out headings from notebooks to act as notebook summaries (eg [`Get Contents`](https://github.com/innovationOUtside/TM351_forum_examples/blob/master/Get%20Contents.ipynb)). Such recipes may provide a useful component in a notebook quality report if the report is also intended to provide a summary / overview of notebooks. (It might be most useful to offer heading summaries as an option in a notebook profiling report?)
#
# Tools supporting the profiling of one or more notebooks across one or more directories and the generation of simple statistics over them are also provided.
#
# The profiler is also capabale of running simple health checks over a notebook, for example reporting on:
#
# - whether code cells have been executed, and if so, whether code cell execution in complete and in linear order;
# - packages / modules loaded in to the notebook;
# - unused code items in a notebook (for example, modules loaded but not used).
#
# Currently, code profiling is only applied to code that appears in code cells, not code that is quoted or described in markdown cells. 
#
# There is a potential for making IPython magics for some of the reporting functions (for example, `radon` or `wily` reports) to provide live feedback / reporting during the creation of content in a notebook.
#
# ### Notebooks
#
# In the first instance, reports are generated for code cell inputs and markdown cells; code outputs and raw cells are not considered. Code appearing in markdown cells is identified as code-like but not analysed in terms of code complexity etc.
#
# For each markdown cell, we can generate a wide range of simple text document statistics. Several packages exist to support such analyses (for example, [`textstat`](https://github.com/shivam5992/textstat), [`readability`](https://github.com/andreasvc/readability/)) but the focus in this notebook will be on metrics derived using the [`spacy`](https://spacy.io/) underpinned [`textacy`](https://github.com/chartbeat-labs/textacy) package for things like [readability](https://chartbeat-labs.github.io/textacy/api_reference/misc.html?highlight=readability#text-statistics) metrics. Several simple custom metrics are also suggested.
#
# For code in code cells, the [`radon`](https://radon.readthedocs.io) package is used to generate code metrics, with additional packages providing further simple metrics.
#
# A test notebook is provided (`Notebook_profile_test.ipynb`) against which we can test various elements of this notebook.
#
# ### Potential Future Work
#
# In terms of analysing cell outputs (not covered as yet), reports could be generated on the sorts of asset that appear to be displayed in each cell output, whether code warnings or errors are raised, etc. There is also potential for running in association with something like [`nbval`](https://github.com/computationalmodelling/nbval) to test that notebooks test correctly against previously run cell outputs.
#
# We might also explore the extent to which interactive notebook profiling tools, such as magics or notebook extensions, be used to support the authoring of new instructional notebooks.
#
# We might also ask to what extent might interactive notebook profiling tools be used to support learners working through instructional material and reflecting on their work? Code health metrics, such as [cell execution success](https://nbgallery.github.io/health_paper.html) used by *nbgallery* may provide clues regarding which code activity cells students struggled to get working, for example. By looking at statistics across students (for example, in assessment notebooks with cell execution success log monitoring enabled) we may be able to identify "healthy" or "unhealthy" activities; for example, a healthy activity is one in which students can get their code to run with one or two tries, an unhealthy activity is one where they make repeated attempts at trying to get the code to work as they desire. 
#
# The notebook profiler should also be runnable against notebooks created using Jupytext from markdown rendered from OU-XML. It would probably make *more* sense to build a custom OU-XML profiler, eg one that could perhaps draw on a summary XML doc generated from OU-XML source docs using XSLT. I'll try to bear in mind creating reporting functions that might be useable in this wider sense. (OU-XML will also have thngs like a/v components, and may have explicit time guidance on expected time spent on particular activities.)
#

# ## Settings
#
# The following parameters are used notebook wide in the generation of reports.

# +
READING_RATE = 100 # words per minute
# What is a sensible reading rate for undergraduate level academic teaching material?
# 250 wpm gives a rate of 15,000 wph
# 10,000 wph corresponds to about 170 words per minute
# OU guidance: 35 wpm for challenging texts, 70 wpm for medium texts, 120 wpm for easy texts

CODE_READING_RATE = 35 # tokens per minute -- UNUSED

CODE_LINE_READING_TIME = 1 # time in seconds to read a code line

LINE_WIDTH = 160 #character width of a line of markdown text; used to calculate "screen lines"

CODE_CELL_REVIEW_TIME = 5 # nominal time in seconds to run each code cell / review each code cell output

CELL_SKIP_TIME = 1 # nomimal time in seconds to move from one cell to the next
# -

# ## Open Notebook
#
# Open and read a notebook, such as the associated test notebook:

import nbformat

# + tags=["active-ipynb"]
# TEST_NOTEBOOK = 'Notebook_profile_test.ipynb'
# with open(TEST_NOTEBOOK,'r') as f:
#     nb = nbformat.reads(f.read(), as_version=4)
# -

# ## Analyse Markdown Cells
#
# Iterate through markdown cells and generate cell by cell reports.
#
# We can start off by generating some simple counts for a single notebook.
#
# Let's preview the contents of a single cell:

# + tags=["active-ipynb"]
# nb.cells[0]
# -

# We can look at just the markdown component associated with a markdown cell - this will be the basis for our markdown text analysis.

# + tags=["active-ipynb"]
# txt = nb.cells[0]['source']
# -

# Estimates of reading time are often based on word count estimates. The Medium website use a reading time estimator that also factors in the presence of images in a text as well as wordcount / sentence length. The [`readtime`](https://github.com/alanhamlett/readtime) package uses the Medium reading time estimation algorithm to give a reading time estimate.
#
#
# ?? TO DO - more on the reading time equation; also need something like maybe: +10s for every code cell to run it and look at output? Different reading time per line of code?
#
# *It might be worth looking at forking this reading time estimator and try to factor in reading time elements that reflect the presence of code? Or maybe use a slower reading rate for code? Or factor in code complexity? The presence of links might also affect reading time.*

# +
#https://github.com/alanhamlett/readtime
# #%pip install readtime

import readtime
import math

# + tags=["active-ipynb"]
# rt = readtime.of_markdown(txt, wpm=READING_RATE).delta.total_seconds()
#
# #Round up on the conversion of estimated reading time in seonds, to minutes...
# f'Reading time in seconds: {rt}; in minutes: {math.ceil(rt/60)}.'
# -

# The `spacy` natural language processing package provides a wide ranging of basic tools for parsing texts.

# +
# #%pip install spacy
import spacy

#Check we have the small English model at least
SPACY_LANG_MODEL = 'en_core_web_sm'

try:
    import en_core_web_sm
except:
    import spacy.cli
    spacy.cli.download(SPACY_LANG_MODEL)

#Load a model that a text is parsed against
nlp = spacy.load(SPACY_LANG_MODEL)
# -

# To call on `spacy`, we need to create tokenised document representation of the text (conveniently, the original text version is also stored as part of the object).

# + run_control={"marked": false} tags=["active-ipynb"]
# doc = nlp(txt)
# -

# The `textacy` package builds on `spacy` to provide a range of higher level tools and statistics, from simple statistics such as word and sentence counts to more complex readability scores using a variety of [readability measures](https://readable.com/blog/the-flesch-reading-ease-and-flesch-kincaid-grade-level/).
#
# One way of using readability measures would be to set reading rates dynamically for each markdown cell based on calculated readability scores.

# #%pip install textacy
from textacy.text_stats.api import TextStats
from textacy import text_stats


# The following statistics are providied by `text_stats`.
#
# Basic counts (mirrored from (`text_stats.basics`):
#
# - `n_chars`
# - `n_chars_per_word`
# - `n_long_words`
# - `n_monosyllable_words`
# - `n_polysyllable_words`
# - `n_sents`
# - `n_syllables`
# - `n_syllables_per_word`
# - `n_unique_words`
# - `n_words`
#
#
#
# Readability (mirrored from `text_stats.readability`):
#
# - `automated_readability_index`
# - `automatic_arabic_readability_index`
# - `coleman_liau_index`
# - `flesch_kincaid_grade_level`
# - `flesch_reading_ease`
# - `gulpease_index`
# - `gunning_fog_index`
# - `lix`
# - `mu_legibility_index`
# - `perspicuity_index`
# - `smog_index`
# - `wiener_sachtextformel`

# + tags=["active-ipynb"]
# text_stats.automated_readability_index(doc)
# -

def text_stats_summary(doc):
    """Generate summary stats report."""
    counts = {
        "n_chars": text_stats.n_chars(doc),
        #"n_chars_per_word": text_stats.n_chars_per_word(doc),
        "n_long_words": text_stats.n_long_words(doc),
        "n_monosyllable_words": text_stats.n_monosyllable_words(doc),
        "n_polysyllable_words": text_stats.n_polysyllable_words(doc),
        "n_sents": text_stats.n_sents(doc),
        "n_syllables": text_stats.n_syllables(doc),
        #"n_syllables_per_word": text_stats.n_syllables_per_word(doc),
        "n_unique_words": text_stats.n_unique_words(doc),
        "n_words": text_stats.n_words(doc)
    }
    
    readability = {
        "automated_readability_index": text_stats.automated_readability_index(doc),
        "automatic_arabic_readability_index": text_stats.automatic_arabic_readability_index(doc),
        "coleman_liau_index": text_stats.coleman_liau_index(doc),
        "flesch_kincaid_grade_level": text_stats.flesch_kincaid_grade_level(doc),
        "flesch_reading_ease": text_stats.flesch_reading_ease(doc),
        "gulpease_index": text_stats.gulpease_index(doc),
        "gunning_fog_index": text_stats.gunning_fog_index(doc),
        "lix": text_stats.lix(doc),
        "mu_legibility_index": text_stats.mu_legibility_index(doc) if counts["n_words"] > 2 else None,
        "perspicuity_index": text_stats.perspicuity_index(doc),
        "smog_index": text_stats.smog_index(doc),
        "wiener_sachtextformel": text_stats.wiener_sachtextformel(doc)
    } if counts["n_words"] else {}
    
    return counts, readability


# + tags=["active-ipynb"]
# counts, readability = text_stats_summary(doc)
# counts, readability
# -

# The `textacy` package can also pull out notable features in a text, such as key terms or acronyms, both of which may be useful as part of a notebook summary.

#Extract keyterms
from textacy import extract

# + tags=["active-ipynb"]
# extract.keyterms.textrank(doc, normalize="lemma", topn=10)
# -

from textacy.extract import acronyms_and_definitions

# + tags=["active-ipynb"]
# acronyms_and_definitions(doc)
# -

# As well as using measures provided by off-the-shelf packages, it's also useful to define some simple metrics of our own that don't appear in other packages.

# To start with, let's try to estimate the notebook length as it appears on screen by calculating how many "screen lines" a markdown cell is likely to take up. This can be calculated by splitting long lines of text over multiple lines based on a screen line width parameter.

# +
import textwrap

def _count_screen_lines(txt, width=LINE_WIDTH):
    """Count the number of screen lines that a markdown cell takes up."""
    ll = txt.split('\n\n')
    _ll = []
    for l in ll:
        #Model screen flow: split a line if it is more than `width` characters long
        _ll=_ll+textwrap.wrap(l, width)
    n_screen_lines = len(_ll)
    return n_screen_lines


# + tags=["active-ipynb"]
# screen_txt='As well as "text", markdown cells may contain cell blocks. The following is a basic report generator for summarising key statistical properties of code blocks. (We will see later an alternative way of calculating such metrics for well form Python code at least.)'
# _count_screen_lines(screen_txt)
# -

# The `textacy` package does not appear to provide average sentence length statistics (although sentence length metrics may play a role in calculating readability scores? So maybe there are usable functions somewhere in there?) but we can straightforwardly define our own.

# +
import statistics

def sentence_lengths(doc):
    """Generate elementary sentence length statistics."""
    s_mean = None
    s_median = None
    s_stdev = None
    s_lengths = []
    for sentence in doc.sents:
        #Punctuation elements are tokens in their own right; remove these from sentence length counts
        s_lengths.append(len( [tok.text for tok in sentence if tok.pos_ != "PUNCT"]))
        
    if s_lengths:
        #If we have at least one measure, we can generate some simple statistics
        s_mean = statistics.mean(s_lengths)
        s_median = statistics.median(s_lengths)
        s_stdev = statistics.stdev(s_lengths) if len(s_lengths) > 1 else 0
        
    return s_lengths, s_mean, s_median, s_stdev


# -

# The sentence statistics are generated from a `spacy` `doc` object and returned as separate statistics.

# + tags=["active-ipynb"]
# s_lengths, s_mean, s_median, s_stdev = sentence_lengths(doc)
# print(s_lengths, s_mean, s_median, s_stdev)
# -

# As well as "text", markdown cells may contain cell blocks. The following is a basic report generator for summarising key statistical propererties of code blocks. (We will see later an alternative way of calculating such metrics for well form Python code at least.)

def _code_block_summarise(lines,
                          n_blank_code_lines = 0,
                          n_single_line_comment_code_lines = 0,
                          n_code_lines = 0):
    
    lines = lines.splitlines() if isinstance(lines, str) else lines
    
    #if lines[0].startwsith('%%'): 
        ##block magic - we could detect which?
        #This would let us report on standard block magic such as %%bash
        #as well as custom magic such as %%sql
    for l in lines:
        if not l.strip():
            n_blank_code_lines = n_blank_code_lines + 1
        elif l.strip().startswith(('#')): #Also pattern match """.+""" and '''.+'''
            n_single_line_comment_code_lines = n_single_line_comment_code_lines + 1
            #How should we detect block comments?
        #elif l.strip().startswith(('!')):
            ## IPython shell command
        #elif l.startswith('%load_ext'):
            ##Import some magic - we could detect which?
        else:
            n_code_lines = n_code_lines + 1
    return n_blank_code_lines, n_single_line_comment_code_lines, n_code_lines


# We can use the code block summary in a more general report on "features" within a markdown cell (sentence statistics are handled elsewhere):

def _report_md_features(txt):
    """Report on features in markdown documents.
        For example, number of headings or paragraphs, or code block analysis."""
    n_headers = 0
    n_paras = 0
    n_total_code_lines = 0
    n_code_lines = 0
    n_blank_code_lines = 0
    n_single_line_comment_code_lines = 0

    in_code_block = False
    
    n_screen_lines = _count_screen_lines(txt)
                        
    #Markdown processor ignores whitespace at start and end of a markdown cell
    txt = txt.strip()
    
    n_code_blocks = 0
    
    #We will see how to improve the handling of code blocks in markdown cells later
    for l in txt.split('\n'):
        if l.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                n_code_blocks = n_code_blocks + 1
        elif in_code_block:
            n_total_code_lines = n_total_code_lines + 1
            n_blank_code_lines, n_single_line_comment_code_lines, \
                n_code_lines = _code_block_summarise(l,
                                                     n_blank_code_lines,
                                                     n_single_line_comment_code_lines,
                                                     n_code_lines)
        elif l.startswith('#'):
            #Markdown heading
            n_headers = n_headers + 1
        elif not l.strip():
            #A paragraph is identified by an double end of line (\n\n) outside a code block
            #So if we have an empty line that signifies a paragraph break?
            n_paras = n_paras + 1
            
    n_code = (n_total_code_lines, n_code_lines, \
              n_blank_code_lines, n_single_line_comment_code_lines)
    
    return n_headers, n_paras, n_screen_lines, n_code_blocks, n_code


# So for example, the features we can report on might include the number of headings paragraphs, screen lines, or code block features.

# + tags=["active-ipynb"]
# n_headers, n_paras, n_screen_lines, n_code_blocks, n_code = _report_md_features(txt)
# n_headers, n_paras, n_screen_lines, n_code_blocks, n_code

# + tags=["active-ipynb"]
# (n_total_code_lines, n_code_lines, n_blank_code_lines, n_single_line_comment_code_lines) = n_code
# n_total_code_lines, n_code_lines, n_blank_code_lines, n_single_line_comment_code_lines
# -

# #### Code Blocks in Markdown Cells
# A question arises when we have code blocks appearing in markdown cells. How should these be treated? Should we report the code toward markdown counts, or should we separately treat the code, discounting it from markdown word counts but reporting it as "code in markdown"?
#
# Another approach might be to include and codes of block appearing in markdown cells as part of the markdown word count, but provide an additional report identifying how many lines of code appeared as part of the markdown.

# The `excode` package (renamed [`exdown`](https://github.com/nschloe/exdown), now deprecated in favour of [`pytest-codeblocks`](https://github.com/nschloe/pytest-codeblocks/)) provides an easy way of grabbing code blocks from markdown text, so we might be able to use that to mprove the handling of code blocks inside markdown cells.
#
# Could we also just use the detected code in a replace to strip out the code? eg when checking headers?
# Lets grab a simple text case of some markdown containing some code blocks:

# + tags=["active-ipynb"]
# mc = nb.cells[2]['source']
# print(mc)
# -

# Let's see if we can extract those code blocks...

# +
# Deprecated in favour of pytest-codeblocks
#import excode

import io
from pytest_codeblocks import extract_from_buffer


# + tags=["active-ipynb"]
# #excode seems to expect a file buffer...
# extract_from_buffer(io.StringIO(mc))
# -

# We can now report on the structure of code blocks in markdown cells more directly:

def code_block_report(c):
    """Generate simple code report when passed a list of code lines
        or a string containing multiple `\n` separated code lines."""
    
    # Grab code from extracted CodeBlock object
    c = c if isinstance(c, str) else c.code
    
    n_total_code_lines = 0
    n_code_lines = 0
    n_blank_code_lines = 0
    n_single_line_comment_code_lines = 0
    
    #We won't count leading or lagging empty lines as code lines...
    lines = c.strip().splitlines() if isinstance(c, str) else c
        
    #print(lines)
    
    n_total_code_lines = len(lines)
    
    n_blank_code_lines, n_single_line_comment_code_lines, \
        n_code_lines = _code_block_summarise(lines,
                                             n_blank_code_lines,
                                             n_single_line_comment_code_lines,
                                             n_code_lines)
    
    return (n_total_code_lines, n_blank_code_lines,\
            n_single_line_comment_code_lines, n_code_lines)


# Running the above function should generate some simple code statistics:

# + tags=["active-ipynb"]
# print(mc)
# for c in extract_from_buffer(io.StringIO(mc)):
#     (n_total_code_lines, n_blank_code_lines, \
#          n_single_line_comment_code_lines, n_code_lines) = code_block_report(c)
#     
#     print(n_total_code_lines, n_blank_code_lines, \
#           n_single_line_comment_code_lines, n_code_lines )
# -

# We could also use the `radon` code analyser (which does count empty lines as code lines unless we explictly strip them).
#
# However, it should be noted that the `radon` code analysis relies on well formed Python code that can be loaded as into the Python AST parser. This means that code that doesn't parse as valid Python, either because it contains an error or because the code is not actually Python code (for example, in course materials we make use of SQL block magic to allow us to write SQL code in a code cell).
#
# The `radon` parser will also report an error if it comes across IPython line or cell magic code, or `!` prefixed shell commands.
#
# We will see later how we can start to cleanse a code string of IPython `!` and `%` prefixed directives when we consider parsing code cells. 

# #%pip install radon
from radon.raw import analyze


# + tags=["active-ipynb"]
# for c in extract_from_buffer(io.StringIO(mc)):
#     c = c.code
#     r = analyze(c.strip())
#     print(r)
# r.loc, r.lloc, r.sloc, r.comments, r.multi, r.blank, r.single_comments
# -

# We can bundle up the `radon` analyzer to make it a little easier to call for our purposes:

def r_analyze(c):
    """Analyse a code string using radon.analyze."""
    c = c if isinstance(c, str) else c.code
    r = analyze(c.strip())
    n_total_code_lines = r.loc
    n_blank_code_lines = r.blank
    n_single_line_comment_code_lines = r.comments
    n_code_lines = r.sloc
    return (n_total_code_lines, n_blank_code_lines, \
            n_single_line_comment_code_lines, n_code_lines)


# We can then simply call `r_analyze()` function with a code string:

# + tags=["active-ipynb"]
# for c in extract_from_buffer(io.StringIO(mc)):
#     (n_total_code_lines, n_blank_code_lines, \
#          n_single_line_comment_code_lines, n_code_lines) = r_analyze(c)
#     
#     print(n_total_code_lines, n_blank_code_lines, \
#           n_single_line_comment_code_lines, n_code_lines)
# -

# ### Code Reading (and Execution) Time
#
# It would be useful if we had a heuristic for code reading time.
#
# One approach would be to tokenise the code and estimate reading time from a simple "tokens per minute" reading rate, or use a reading rate appropriate for "difficult" text. Another approach might be to try to make use of code complexity scores and code length.
#
# A pragmatic way may just be to estimate based on lines of code, with a nominal reading time allocated to each line of code.

def code_reading_time(n_code_lines, n_single_line_comment_code_lines, line_time=CODE_LINE_READING_TIME):
    """Crude reading time estimate for a code block."""
    code_reading_time = line_time * (n_code_lines + n_single_line_comment_code_lines)
    return code_reading_time


# The way we currently process code in markdown cells, it will be timed at the standard reading rate. It may be appropriate to add a simple modifier that also adds a "code reading overhead" to the reading time based on the amount of code in a markdown cell.
#
# For code in code cells, rather than code blocks in markdown cells, might also be worth exploring *code execution time*, that is, an overhead associated with running each code cell. A crude way of calculating this would be to levy a fixed amount of time to account for running the code cell and inspecting the result. A more considered approach would look to cell profiling / execution time logs and code cell outputs in a run notebook.

# ### Custom Report Aggregator
#
# For convenience, we can bundle up the custom metrics we have created into a function that returns a single report object.

# +
import math

def process_extras(doc):
    """Generate a dict containing additional metrics."""
    
    n_headers, n_paras, n_screen_lines, n_code_blocks, n_code = _report_md_features(doc.text)
    s_lengths, s_mean, s_median, s_stdev = sentence_lengths(doc)
    (n_total_code_lines, n_code_lines, n_blank_code_lines, n_single_line_comment_code_lines) = n_code
    
    _reading_time = readtime.of_markdown(doc.text, wpm=READING_RATE).delta.total_seconds()
    #Add reading time overhead for code
    line_of_code_overhead = 1 #time in seconds to add to reading of each code line
    _reading_time = _reading_time + code_reading_time(n_code_lines, n_single_line_comment_code_lines,
                                                     line_of_code_overhead)
    
    extras = {'n_headers':n_headers,
              'n_paras':n_paras,
              'n_screen_lines':n_screen_lines,
              's_lengths':s_lengths,
              's_mean':s_mean,
              's_median':s_median,
              's_stdev':s_stdev,
              'n_code_blocks':n_code_blocks,
              'n_total_code_lines':n_total_code_lines,
              'n_code_lines':n_code_lines,
              'n_blank_code_lines':n_blank_code_lines,
              'n_single_line_comment_code_lines':n_single_line_comment_code_lines,
              'reading_time_s':_reading_time,
              'reading_time_mins': math.ceil(_reading_time/60),
              'mean_sentence_length': s_mean,
              'median_sentence_length': s_median,
              'stdev_sentence_length': s_stdev,
              #The following are both listy, so we need to handle them when we move to a dataframe
              # TO DO  - paramterise the number of key terms
              'keyterms':extract.keyterms.textrank(doc, normalize="lemma", topn=10),
              'acronyms':acronyms_and_definitions(doc)
             }
    return extras


# -

# Running the `process_extras()` function on a `doc` object returns the extra metrics as keyed items in a single `dict`:

# + tags=["active-ipynb"]
# counts, readability = text_stats_summary(doc)
# counts, readability, process_extras(doc)
# -

# ### Generate a Whole Notebook Markdown Report
#
# The whole notebook report can come in various flavours:
#     
# - top level summary statistics that merge all the markdown content into a single cell and then analyse that;
# - aggregated cell level statistics that summarise the statistics calculated for each markdown cell separately;
# - individual cell level statistics that report the statistics for each cell separately.
#
# Whilst the individual cell level statistics presented in a textual fashion may be overkill, it may be useful to generate visual displays of a notebook that graphically summarise its structure.

# #### Top-Level Summary
#
# Let's start with a report that munges the all the markdown text together and report on that...

def process_notebook_full_md(nb):
    """Given a notebook, return all the markdown cell content as one string,
        and all the code cell content as another string."""
    
    txt = []
    code = []
    for cell in nb.cells:
        if cell['cell_type']=='markdown':
            txt.append(cell['source'])
        elif cell['cell_type']=='code':
            code.append( cell['source'])

    doc = nlp('\n\n'.join(txt))
    code = '\n\n'.join(code)
    
    return doc, code


# The `process_notebook_full_md()` function takes a notebook object and returns two strings: one containing all the notebook's markdown cell content, one containing all its code cell content.

# + tags=["active-ipynb"]
# full_doc, full_code = process_notebook_full_md(nb)
# full_doc.text[:280], full_code[:250]
# -

# Let's make things a bit more tabular in our reporting:

# +
import pandas as pd

def process_notebook_md_doc(doc):
    counts, readability = text_stats_summary(doc)
    return pd.DataFrame([{'text':doc.text,
                          **counts, **readability,
                          **process_extras(doc)}])


# -

# Running the `process_notebook_md_doc()` function on a `doc` object returns a single row dataframe containing summary statistics calculated over the full markdown content of the notebook.

# + tags=["active-ipynb"]
# process_notebook_md_doc(full_doc)
# -

# #### Check Images
#
# Using the monolithic markdown blob, we can parse the markdown to HTML and then process it to extract links, images etc.

# +
import markdown
from lxml import etree
from pathlib import Path
from nbformat.notebooknode import NotebookNode

def make_html_tree(md):
    """Generate etree HTML structure from markdown text."""
    html_tree = etree.fromstring(f"<div>{markdown.markdown(md)}</div>")
    return html_tree

def get_images(html_tree):
    """Extract images and alt text from HTML tree."""
    images = []
    for img in html_tree.xpath('//img'):
        images.append((img.get('src'), img.get('alt')))

    return images

def get_links(html_tree):
    """Extract links and link text from HTML tree."""
    links = []
    for link in html_tree.xpath('//a'):
        links.append((link.text, link.get('href')))

    return links

def get_nb(nb):
    """Get notebook."""
    def _read_as_notebook(nb):
        """Read notebook from file."""
        # Have we been provided a path to a file?
        path = Path(nb)
        if path.is_file():
            with open(path) as f:
                nb = nbformat.reads(f.read(), as_version=4)
        return nb

    nb = nb if isinstance(nb, NotebookNode) else _read_as_notebook(nb)
    return nb

def nb_md_links_and_images(nb):
    """Extract links and images from notebook."""
    def _nb_report(_nb):
        """Get report for a single notebook."""
        nb = get_nb(_nb)
        full_doc, full_code = process_notebook_full_md(nb)
        html_ = make_html_tree(full_doc.text)
    
        return {"notebook": "RAW" if isinstance(_nb, NotebookNode) else str(_nb),
                "images": get_images(html_),
                "links": get_links(html_)
               }
        
    retvals = []
    
    # If we are passed a directory path,
    # let's recursively iterate through it
    # and look for notebooks
    # We could perhaps generalise more and also allow md files
    # perhaps parsing to NotebookNode using jupytext?
    if Path(nb).is_dir():
        for p in sorted(Path(nb).rglob("*.ipynb")):
            if '.ipynb_checkpoints' not in p.parts:
                retvals.append(_nb_report(p))
    else:
        retvals.append(_nb_report(nb))

    return retvals


# + tags=["active-ipynb"]
# body_markdown = "This is an ![alt-text](./broke.png) [my inline link](http://google.com). This is a [non inline link][1]\r\n\r\n  [1]: http://yahoo.com"
#
# html_ = make_html_tree(body_markdown)
#
# print(get_images(html_))
# print(get_links(html_))
# #full_doc

# + tags=["active-ipynb"]
# nb_md_links_and_images(TEST_NOTEBOOK)
# TEST_DIR = '../tm351-undercertainty/notebooks/tm351/Part 02 Notebooks'
# test_links_images = nb_md_links_and_images(TEST_DIR)
# test_links_images
# -

# Test links for liveness by reusing elements of https://github.com/innovationOUtside/ouxml-link-checker:

# + tags=["active-ipynb"]
# from ouxml_link_checker import link_checker as olc
#
# test_links = list({l[1] for li in test_links_images for l in li['links'] if l[1].startswith('http')})
# #test_links
#
# reps = olc.check_multiple_links(test_links)
# reps
# -

# #### Summarised Cell Level Reporting
#
# For the summarised cell level reporting, generate measures on a per cell basis and then calculate summary statistics over those.

def process_notebook_md(nb, fn=''):
    """Process all the markdown cells in a notebook."""
    cell_reports = pd.DataFrame()
    
    for i, cell in enumerate(nb.cells):
        if cell['cell_type']=='markdown':
            _metrics = process_notebook_md_doc( nlp( cell['source'] ))
            _metrics['cell_count'] = i
            _metrics['cell_type'] = 'md'
            cell_reports = cell_reports.append(_metrics, sort=False)
    
    cell_reports['filename'] = fn
    cell_reports.reset_index(drop=True, inplace=True)
    return cell_reports


# Processing a single notebook returns a dataframe with one row per markdown cell with each metric reported in its own column.

# + tags=["active-ipynb"]
# total_report = process_notebook_md(nb)
# total_report.head(3)
# -

# It is trivial to create summary statistics directly from the *per* cell report table by aggregating over rows associated with the same notebook; in this case, we can find the total readtime as a simple sum.
#
# However, more generally we may wish to apply the aggegation over a set of grouped results (for example, in a dataframe containing materics from mutliple notebooks, we would want to group by each notebook and then perform the agggragatin on the measures associated with each notebook).

# + tags=["active-ipynb"]
# total_report['reading_time_mins'].sum()
# -

# Let's also create a function to profile a notebook from a file:

def process_notebook_file(fn):
    """Grab cell level statistics across a whole notebook."""
    
    with open(fn,'r') as f:
        try:
            nb = nbformat.reads(f.read(), as_version=4)
            cell_reports = process_notebook_md(nb, fn=fn)
        except:
            print(f'FAILED to process {fn}')
            cell_reports = pd.DataFrame()
        
        cell_reports.reset_index(drop=True, inplace=True)
        return cell_reports


# The `process_notbook_file()` function returns a dataframe containing row level reports for each markdown cell in a specified notebook:

# + tags=["active-ipynb"]
# process_notebook_file(TEST_NOTEBOOK)
# -

# ### Analysing Multiple Notebooks in the Same Directory
#
# As well as analysing notebooks at the notebook level, we may also want to generate individual and aggregated reports for all the notebooks contained in a single directory.
#
# Aggregated reports might include the total estimated time to work through all the notebooks in the directory, for example.
#
# It might be useful to have one entry point and a switch that selects between the notebook summary reports and the full cell level report? Or maybe we should report two dataframes always - aggregated notebook level and individual cell level?

# +
import os

def _nb_dir_file_profiler(path, _f, report=False):
    """Get the profile for a single file on a specified path."""
    f = os.path.join(path, _f)
    if f.endswith('.ipynb'):
        if report:
            print(f'Profiling {f}')
        return process_notebook_file(f)
    return pd.DataFrame()
    
def nb_dir_profiler(path):
    """Profile all the notebooks in a specific directory."""
    nb_dir_report = pd.DataFrame()
    for _f in os.listdir(path):
        nb_dir_report = nb_dir_report.append( _nb_dir_profiler(path, _f), sort=False )
    #nb_dir_report['path'] = path
    return nb_dir_report   


# +
#nb_dir_profiler('.')
# -

# ### Analysing Notebooks Across Multiple Directories
#
# As well as analysing all the notebooks contained within a single directory, we may want to automate the production of reports at the directory level across multiple directories.

def nb_multidir_profiler(path, exclude = 'default'):
    """Profile all the notebooks in a specific directory and in any child directories."""
    
    if exclude == 'default':
        exclude_paths = ['.ipynb_checkpoints', '.git', '.ipynb', '__MACOSX']
    else:
        #If we set exclude, we need to pass it as a list
        exclude_paths = exclude
    nb_multidir_report = pd.DataFrame()
    for _path, dirs, files in os.walk(path):
        #Start walking...
        #If we're in a directory that is not excluded...
        if not set(exclude_paths).intersection(set(_path.split('/'))):
            #Profile that directory...
            nb_dir_report = pd.DataFrame()
            for _f in files:
                nb_dir_report = nb_dir_report.append( _nb_dir_file_profiler(_path, _f), sort=False )
            if not nb_dir_report.empty:
                nb_dir_report['path'] = _path
                nb_multidir_report = nb_multidir_report.append(nb_dir_report, sort=False)
    
    nb_multidir_report = nb_multidir_report.sort_values(by=['path', 'filename'])
    
    nb_multidir_report.reset_index(drop=True, inplace=True)
    
    return nb_multidir_report   


# + tags=["active-ipynb"]
# ddf = nb_multidir_profiler(TEST_DIR)
# ddf.head()
# -

# Under the grouped report, we note that the summed reading time in minutes is likely to significantly overestimate the reading time requirement, representing as it does the sum of time in minutes rounded up from seconds. The lower bound giving by the summed reading time in *seconds* more closely relates to the markdown word count.
#
# However, the larger estimate perhaps does also factor in context switching time going from one cell to another. Whilst this may be invisible to the reader if a markdown cell follows a markdown cell, it may be more evident when going from a markdown cell to a code cell. On the other hand, if a markdown cell follows another because there is a change from one subsection to another, there may be a pause for reflection as part of that context switch that *is* captured by the rounding.

# + tags=["active-ipynb"]
# ddf.groupby(['path','filename'])[['n_total_code_lines','n_words',
#                                   'reading_time_mins', 'reading_time_s' ]].sum()

# + tags=["active-ipynb"]
# ddf_dict = ddf.groupby(['path'])[['n_words', 'reading_time_mins',  'reading_time_s' ]].sum().to_dict(orient='index')
# ddf_dict
# -

# ## Reporting Templates
#
# It's all very well having the data in a dataframe, but it could be more useful to be able to generate some written reports. So what might an example report look like?
#
# How about something like:
#
# > In directory X there were N notebooks. The total markdown wordcount for notebooks in the directory was NN. The total number of lines of code across the notebooks was NN. The total estimated reading time across the notebooks was NN.
# >
# > At the notebook level:
# > - notebook A: markdown wordcount NN, lines of code NN, estimated reading time NN;
#
# It might also be useful to provide simple rule (cf. linter rules) that raise warnings about notebooks that go against best practice. For example, notebooks with word counts / code line counts or reading or completion times that exceed recommended limits.

# Let's start with a simple template:

# + tags=["active-ipynb"]
# report_template_simple_md = '''
# In directory `{path}` there were {nb_count} notebooks.
# The total markdown wordcount for the notebooks in the directory was {n_words} words,
# with an estimated total reading time of {reading_time_mins} minutes.
# '''
# -

# We can feed this from a `dict` containing fields required by the report template:

# #%pip install deepmerge
from deepmerge import always_merger


# + tags=["active-ipynb"]
# notebook_counts_by_dir = ddf.groupby(['path'])['filename'].nunique().to_dict()
# notebook_counts_by_dir = {k:{'nb_count':notebook_counts_by_dir[k]} for k in notebook_counts_by_dir}
#
# report_dict = always_merger.merge(ddf_dict, notebook_counts_by_dir )
# for k in report_dict:
#     report_dict[k]['path'] = k
# report_dict
# -

# Feeding the `dict` to the template generates the report:

# + tags=["active-ipynb"]
# report_template_simple_md.format(**report_dict[TEST_DIR])
# -

# Create a function to make it easier to generate the feedstocl `dict`:

def notebook_report_feedstock_md_test(ddf):
    """Create a feedstock dict for report generation. Keyed by directory path."""
    ddf_dict = ddf.groupby(['path'])[['n_words', 'reading_time_mins',  'reading_time_s' ]].sum().to_dict(orient='index')
    
    notebook_counts_by_dir = ddf.groupby(['path'])['filename'].nunique().to_dict()
    notebook_counts_by_dir = {k:{'nb_count':notebook_counts_by_dir[k]} for k in notebook_counts_by_dir}
    
    report_dict = always_merger.merge(ddf_dict, notebook_counts_by_dir )
    
    for k in report_dict:
        report_dict[k]['path'] = k
    
    return report_dict


# We can now use the `notebook_report_feedstock()` function to generate the feedstock `dict` directlry from the report dataframe:

# + tags=["active-ipynb"]
# notebook_report_feedstock_md_test(ddf)
# -

# ### Additional Reporting Levels
# For additional reports, we could start to look for particular grammatical constructions in the markdown text.

# When it comes to looking for particular grammatical constructions in the text, the `textacy` package allows us to define patterns of interest in various ways. Are there any particular constructions that we may want to look out for in an instructional text?

import textacy

# + tags=["active-ipynb"]
# extract.keyterms.textrank(doc, normalize="lemma", topn=10)

# +
# extract.to_bag_of_terms?

# + tags=["active-ipynb"]
# for i in extract.to_bag_of_terms(doc, ents=True,
#                                  ngs=True, ncs=True):
#     print(i)

# + tags=["active-ipynb"]
# #But how do you define the pattern to extract the largest phrase over a sequence of tokens?
# verb_phrase = r'(<VERB>?<ADV>*<VERB>+)' #extract.pos_regex_matches DEPRECATED
#
# verb_phrase2 = [{"POS": "VERB", "OP":"?"}, {"POS": "ADV", "OP": "*"},
#                 {"POS": "VERB", "OP":"+"}] #extract.matches
#
# verb_phrase3 = r'POS:BERB:? POS:ADV:* POS:VERB:+' #extract.matches
#
# # pos tagger no longer available?
# #[vp for vp in extract.matches(doc, verb_phrase3)][:5]
# -

from collections import Counter

# + tags=["active-ipynb"]
# dict(Counter(([token.pos_ for token in doc])))
# -

# ## Code Cell Analysis
#
# As well as reporting on markdown cells, we can also generate reports on code cells. (We could also use similar techiques to report on code blocks found in markdown cells.)
#
# Possible code cell reports include reporting on:
#
# - packages imported into a notebook;
# - number of lines of code  / code comments;
# - code complexity.
#
# We could also run static analysis tests over *all* the code loaded into a notebook, for example using things like [`importchecker`](https://github.com/zopefoundation/importchecker) to check that imports are actually used.
#
# Checks against whether code cells in a notebooks: a) have been run; b) whether they have been run in order are also possible. If we extend the analysis to code cell outputs, we could also report on whether cells had been run without warning or error and what sort of output they produced.
#
# Tools such as [`pyflakes`](https://github.com/PyCQA/pyflakes) can also be used to run a wider range of static tests over a codebase, as can other code linters. See also [*Thinking About Things That Might Be Autogradeable or Useful for Automated Marking Support*](https://blog.ouseful.info/2019/12/10/thinking-about-things-that-might-be-autogradeable/) for examples of tests that may be used in autograding, some of which might also be useful for notebook code profiling.
#
# It might also be worth trying to collate possible useful guidelines / heuristics / rules of thumb for creating notebooks that could also provide the basis of quality minded linting checks.
#
# For example:
#
# - a markdown cell should always appear before a code cells to set the context for what the code cell is expected to achieve;
# - a markdown cell commenting on the output of a code cell immediately preceding may be appropriate in some cases;
# - one cell should be defined per code cell. A markdown cell immediately following a code cell that defines a function might include a line of text that might also serve as the function doc text, describing what the function does an dprefacing a code cell that demonstrates the behaviour of the function.

# ### Generating code reports over a single notebook
#
# Let's start to put together some metrics we can run against code cells, either at an individual level or from code aggregated from across all the code cells in a notebook.

# + tags=["active-ipynb"]
# c='''#print\nimport pandas\n\nprint('a')\nimport abjad\nimport numpy as np\nfrom IPython.display import HTML, JSON'''
#
# #https://github.com/andrewp-as-is/list-imports.py #list imports
# #%pip install list-imports
# import list_imports
# list_imports.parse(c)
# #Would also need to capture magics?
#
# # TO DO  - NOT CURRENTLY REPORTED
# -

# Some utilities may not make sense in the reporting when applied at a cell level. For example, it's quite likely that a package imported into a cell may not be used in that cell, which `pyflakes` would report unfavourably on:

# +
# #%pip install pyflakes
#pyflakes seems to print the report, so we'd need to find a way to capture it
from pyflakes.api import check
from pyflakes.reporter import Reporter

import io


# + tags=["active-ipynb"]
# output_w = io.StringIO()
# output_e = io.StringIO()
#
# check('''import pandas as pd''', 'dummy', Reporter(output_w, output_e))
# output_w.getvalue()
# -

# Another form of analysis that only makes sense at the notebook level is the code cell execution analysis:

# + tags=["active-ipynb"]
# # Check execution across notebook - TO DO - NOT CURRENTLY REPORTED
# cell_execution_order = []
# num_code_cells = 0
# for cell in nb.cells:
#     if cell['cell_type']=='code':
#         cell_execution_order.append(cell['execution_count'])
#         num_code_cells = num_code_cells + 1
#
#
# _executed_cells = [i for i in cell_execution_order if i is not None and isinstance(i,int) ]
# in_order_execution = _executed_cells == sorted(_executed_cells)
#
# all_cells_executed = len(_executed_cells)==num_code_cells
# print(cell_execution_order, all_cells_executed, in_order_execution,)
# -

# ### Parsing IPython Code
#
# One thing to bear in mind is that code cells may contain block magic that switches code from the assumed default Python code to potentially a different language. For this reason, we might want to fall back from the `radon` metrics as a result of trying to load code into a Python AST parser when meeting cells that employ cell block magic, or explore whether an IPyhton parser could be used instead.

# Let's try to cleanse IPython directives such as shell commands (`!` prefix) or magics (`%` prefix) from a code string so that we can present it to `radon`.

def sanitise_IPython_code(c):
    """Cleanse an IPython code string so we can parse it with radon."""
    #Comment out magic and shell commands
    c = '\n'.join([f'#{_r}' if _r.lstrip().startswith(('%','!')) else _r for _r in c.splitlines()])
    
    return c


# The `sanitise_IPython_code()` function partially sanitises an IPython code string so that it can be passed to, and parsed by, the `radon`. Note that where magic or shell statements are used on the right hand side of an assignment statement, this will still cause an error. 

#Use the `radon` analyzer
# #%pip install radon
from radon.raw import analyze


# + tags=["active-ipynb"]
# c = '''%load_ext magic\nimport pandas\n\n!ls\nprint(a)'''
# c = sanitise_IPython_code(c)
#
# print(c)
# n_total_code_lines, n_blank_code_lines, \
#     n_single_line_comment_code_lines, n_code_lines = r_analyze(sanitise_IPython_code(c))
#
# n_total_code_lines, n_blank_code_lines, n_single_line_comment_code_lines, n_code_lines
# -

# To parse a code cell, we can try to use the `radon` analyser, with a sanitised code string, or fall back to using the simpler code sanitiser. It will also be convenient to return the results as a Python `dict` object.

def robust_code_cell_analyse(c, parser='radon'):
    """Use the `radon` code analyser if we can else fall back to the simple custom code analyser."""
    
    def cleansed_radon(c):
        return r_analyze(sanitise_IPython_code(c))
    
    if c.startswith('%%'):
        #use local code analyser
        parser = 'local'

    if parser == 'radon':
        try:
            _response = cleansed_radon(c)
        except:
            #fallback to simple analyser
            _response = code_block_report(c)
    else:
        _response = code_block_report(c)
        
    (n_total_code_lines, n_blank_code_lines, \
         n_single_line_comment_code_lines, n_code_lines) = _response
    
    _reading_time = code_reading_time(n_code_lines, n_single_line_comment_code_lines)
    
    response = {
        'n_total_code_lines': n_total_code_lines,
        'n_blank_code_lines': n_blank_code_lines,
        'n_single_line_comment_code_lines': n_single_line_comment_code_lines,
        'n_code_lines': n_code_lines,
        'n_screen_lines':n_total_code_lines,
        'reading_time_s':_reading_time,
        'reading_time_mins': math.ceil(_reading_time/60)
    }
    
    return response


# The robust analyser should cope with  a variety of strings.

# + tags=["active-ipynb"]
# print(robust_code_cell_analyse('import pandas\n\n# comment\n!ls'))
# print(robust_code_cell_analyse('%%sql\nSELECT * FROM TABLE'))
# -

# We now need to start pulling together a function that we can cal to run the basic report and other code cell reports.

def process_notebook_code_text(txt):
    """Generate code cell report."""
    report = pd.DataFrame()
    basic_code_report = robust_code_cell_analyse(txt)
    return pd.DataFrame([{'text':txt,
                          **basic_code_report }])


# The report generates a single row report dataframe from a code string:

# + tags=["active-ipynb"]
# process_notebook_code_text('import pandas\n\n# comment\n!ls')
# -

# In order to process code cells as well as markdown cells in our notebook processer, we will need build on the `process_notebook_md()` function to create a more general one. Note that the current approach will give us an inefficient dataframe, column wise, in that whilst each row represents the report from a code cell *or* a markdown cell, the columns cover reports from both code *and* markdown cells.

def process_notebook(nb, fn=''):
    """Process all the markdown and code cells in a notebook."""
    cell_reports = pd.DataFrame()
    
    for i, cell in enumerate(nb.cells):
        if cell['cell_type']=='markdown':
            _metrics = process_notebook_md_doc( nlp( cell['source'] ))
            _metrics['cell_count'] = i
            _metrics['cell_type'] = 'md'
            cell_reports = cell_reports.append(_metrics, sort=False)
        elif cell['cell_type']=='code':
            _metrics = process_notebook_code_text(cell['source'] )
            _metrics['cell_count'] = i
            _metrics['cell_type'] = 'code'
            cell_reports = cell_reports.append(_metrics, sort=False)
        
    cell_reports['filename'] = fn
    cell_reports.reset_index(drop=True, inplace=True)
    return cell_reports


# We should now be able to generate a report that includes statistics from code as well as markdown cells.

# + tags=["active-ipynb"]
# report = process_notebook(nb)
# report.head(5)
# -

# Let's just check what columns we are potentially reporting on:

# + tags=["active-ipynb"]
# report.columns
# -

# And let's see if our directory processor now also includes code cell statistics:

# + tags=["active-ipynb"]
# ddf2 = nb_multidir_profiler('../tm351-undercertainty/notebooks/tm351/Part 02 Notebooks')
# ddf2['cell_type'].value_counts()
# -

# Let's also check to see how the code cells are reported:

# + tags=["active-ipynb"]
# code_cols = [c for c in ddf2.columns if 'code' in c]
# ddf2[ddf2['cell_type']=='code'][code_cols].sum()
# -

# ### Generating Reports Across Multiple Directories
#
# We are now in a position to start generating rich report for notebooks across several directories.
#
# Let's grab data for notebooks across an example set of directories:

# + tags=["active-ipynb"]
# #ddf3 = nb_multidir_profiler('../tm351-undercertainty/notebooks/tm351/')
# ddf3=ddf2
# -

# And just quickly test we can generate a report that summarises the notebooks in each directory:

# + tags=["active-ipynb"]
# big_feedstock = notebook_report_feedstock_md_test(ddf3)
# report_txt=''
# for d in big_feedstock:
#     if 'tm351/Part ' in d:
#         report_txt = report_txt + '\n\n' + report_template_simple_md.format(**big_feedstock[d])
#     
# print(report_txt[:500])
# -

# Let's update the report template and the report feedstock function.
#
# First, what shall we report on?

# + tags=["active-ipynb"]
# ddf3.columns
# -

# Let's make a start on a complete report template...

report_template_full = '''
In directory `{path}` there were {nb_count} notebooks.

- total markdown wordcount {n_words} words across {n_md_cells} markdown cells
- total code line count of {n_total_code_lines} lines of code across {n_code_cells} code cells
  - {n_code_lines} code lines, {n_single_line_comment_code_lines} comment lines and {n_blank_code_lines} blank lines

Estimated total reading time of {reading_time_mins} minutes.

'''


# Now let's add those extra requirements to the the feedstock generator:

def notebook_report_feedstock(ddf):
    """Create a feedstock dict for report generation. Keyed by directory path."""
    ddf_dict = ddf.groupby(['path'])[['n_words', 'reading_time_mins', 'reading_time_s',
                                     'n_code_lines', 'n_single_line_comment_code_lines',
                                     'n_total_code_lines','n_blank_code_lines']].sum().to_dict(orient='index')
    
    notebook_counts_by_dir = ddf.groupby(['path'])['filename'].nunique().to_dict()
    notebook_counts_by_dir = {k:{'nb_count':notebook_counts_by_dir[k]} for k in notebook_counts_by_dir}
        
    report_dict = always_merger.merge(ddf_dict, notebook_counts_by_dir )
    
    code_cell_counts = ddf[ddf['cell_type']=='code'].groupby(['path']).size().to_dict()
    md_cell_counts = ddf[ddf['cell_type']=='md'].groupby(['path']).size().to_dict()
    
    for k in report_dict:
        report_dict[k]['path'] = k
        report_dict[k]['n_code_cells'] = code_cell_counts[k] if k in code_cell_counts else 'NA'
        report_dict[k]['n_md_cells'] = md_cell_counts[k] if  k in md_cell_counts else 'NA'
    
    return report_dict


# Create a wrapper function for generating the report text:

def reporter(df, template, path_filter=''):
    feedstock = notebook_report_feedstock(df)
    report_txt=''
    for d in feedstock:
        if path_filter in d:
            report_txt = report_txt + '\n\n' + template.format(**feedstock[d])
    return report_txt


# We can now use the `reporter()` function to generate a report based on filtered paths from a report dataframe and a template:

# + tags=["active-ipynb"]
# print(reporter(ddf2, report_template_full, 'tm351/Part '))

# + tags=["active-ipynb"]
# print(reporter(ddf3, report_template_full, 'tm351/Part ').replace('../Documents/GitHub/tm351-undercertainty/notebooks/tm351/',''))
# -

# ## Visualising Notebook Structure
#
# To provide a glanceable, macroscopic way of comparing the size and structure of multiple notebooks, we can generate a simple visualisation based on screen line counts and colour codes for different cell types or cell state.
#
# Reports that include cell index and a simple line count (for example, reprting the number of code lines or screen lines for markdown) can be rendered directly as linear visualisations showing the overall structure of a notebook. 
#
# For example:
#
# - markdown: header;
# - markdown: paragraph;
# - markdown: code block;
# - markdown: blank line;
# - code: code;
# - code: comment;
# - code: magic;
# - code: blank line;
# - other: other cells.
#
# To profile within a cell requires access to cell internals, or generating a cell profile during cell processing.
#
# However, it's easy enough to generate a view over the code and markdown cells.
#
# Let's start by exploring a simple representation:

import matplotlib.pyplot as plt

# + tags=["active-ipynb"]
# fig, ax = plt.subplots()
# ax.axis('off')
#
# #Simple representation of lines per cell and cell colour based on cell type
# n_c = [(1,'r'),(2,'pink'), (1,'cornflowerblue'), (2,'pink')]
#
# x=0
# y=0
#
# for _n_c in n_c:
#     _y = y + _n_c[0]
#     plt.plot([x,x], [y,_y], _n_c[1], linewidth=5)
#     y = _y   #may want to add a gap when moving from one cell to next
# plt.gca().invert_yaxis()
# -

# We can get the list of cell size and colour tuples from a notebook's report data frame:

# +
VIS_COLOUR_MAP  = {'md':'cornflowerblue','code':'pink'}

def cell_attrib(cell, colour='cell_type', size='n_screen_lines'):
    _colour = VIS_COLOUR_MAP[ cell[colour] ]
    return (cell[size], _colour)


# + tags=["active-ipynb"]
# report.apply(cell_attrib, axis=1).to_list()
# -

# Let's create a function to visualise a notebook based on its list of cell size and colour tuples; we'll also allow it to habdle multiple lists:

def nb_vis(cell_map, w=20, gap_boost=1, **kwargs):
    """Visualise notebook gross cell structure."""
    
    def get_gap(cell_map):
        """Automatically set the gap value based on overall length"""
        
        def get_overall_length(cell_map):
            """Get overall length of a notebook."""
            overall_len = 0
            gap = 0
            for i ,(l,t) in enumerate(cell_map):
                #i is number of cells if that's useful too?
                overall_len = overall_len + l
            return overall_len

        max_overall_len = 0
        
        if isinstance(cell_map,dict):
            for k in cell_map:
                _overall_len = get_overall_length(cell_map[k])
                max_overall_len = _overall_len if _overall_len > max_overall_len else max_overall_len
        else:
            max_overall_len = get_overall_length(cell_map)

        #Set the gap at 0.5% of the overall length
        return math.ceil(max_overall_len * 0.01)
        
        
    def plotter(cell_map, x, y, label='', header_gap = 0.2,
                linewidth = 5,
                orientation ='v', gap_colour = 'lightgrey'):
        """Plot visualisation of gross cell structure for a single notebook."""
        
        if orientation =='v':
            plt.text(x, y, label)
            y = y + header_gap
        else:
            plt.text(y, x, label)
            x = x + header_gap
            
        for _cell_map in cell_map:
            _y = y + gap if gap_colour else y
            __y = _y + _cell_map[0] + 1 #Make tiny cells slightly bigger
            
            if orientation =='v':
                X = _X = __X = x
                Y = y
                _Y =_y
                __Y = __y
            else:
                X = y
                _X = _y
                __X = __y
                Y = _Y = __Y = x
            
            #Add a coloured bar between cells
            if y > 0:
                if gap_colour:
                    plt.plot([X,_X],[Y,_Y], gap_colour, linewidth=linewidth)

            
            plt.plot([_X,__X], [_Y,__Y], _cell_map[1], linewidth=linewidth)

            y = __y

    x=0
    y=0
    
    if isinstance(cell_map,list):
        gap = get_gap(cell_map) * gap_boost
        fig, ax = plt.subplots(figsize=(w, 1))
        plotter(cell_map, x, y, **kwargs)
    elif isinstance(cell_map,dict):
        gap = get_gap(cell_map) * gap_boost
        fig, ax = plt.subplots(figsize=(w,len(cell_map)))
        for k in cell_map:
            plotter(cell_map[k], x, y, k, **kwargs)
            x = x + 1

    ax.axis('off')
    plt.gca().invert_yaxis()


# We can now easily create a simple visualisation of the gross cell structure of the notebook:

# + tags=["active-ipynb"]
# cell_mapping = report.apply(cell_attrib, axis=1).to_list()
# nb_vis(cell_mapping, orientation='h')
# -

# We can alo visualisation multiple notebooks, labelling each with the notebook name and plotted against the same length axis so that we can compare notebook sizes and structures directly.

# + tags=["active-ipynb"]
# nb_vis({'a':cell_mapping, 'b':cell_mapping[:3],
#        'c':cell_mapping+cell_mapping, 'd':cell_mapping,}, orientation='h')
# -

def cell_attribs(cells, colour='cell_type', size='n_screen_lines'):
    return cells.apply(cell_attrib, axis=1, args=(colour,size)).to_list()

# + tags=["active-ipynb"]
# zz = ddf.groupby(['filename'])[['cell_type', 'n_screen_lines']].apply(cell_attribs)
# nb_vis(zz.to_dict(), orientation='h', gap_boost=1)
# #[['n_total_code_lines','n_words','reading_time_mins', 'reading_time_s' ]].sum()
# -

# We can also see how they look based on reading time.

# + tags=["active-ipynb"]
# zz = ddf.groupby(['filename'])[['cell_type', 'reading_time_s']].apply(cell_attribs,'cell_type','reading_time_s')
# nb_vis(zz.to_dict(), orientation='h', gap_boost=2)
# -

# ### Visualing Intra-Cell Structure
#
# For example, paragraphs and code blocks in markdown cells; comment lines, empty lines, code lines, magic lines / blocks, shell command lines in code cells.
#
# Supporting the level of detail may be be tricky. A multi-column format is probably best showing eg an approximate "screen's worth" of content in a column then the next "scroll" down displayed in the next column along.

# ---
#
# # BELOW HERE - NOTES AND TO DO

# + tags=["active-ipynb"]
# #Maintainability index
# from radon.metrics import mi_visit
#
# #If True, then count multiline strings as comment lines as well.
# #This is not always safe because Python multiline strings are not always docstrings.
#
# multi = True
# mi_visit(c,multi)

# + tags=["active-ipynb"]
# from radon.metrics import mi_parameters
# mi_parameters(c, multi)
#
# """
# the Halstead Volume
# the Cyclomatic Complexity
# the number of LLOC (Logical Lines of Code)
# the percent of lines of comment
# """

# + tags=["active-ipynb"]
# from radon.complexity import cc_visit
#
# #Doesn't like %% or % magic
# cc_visit(c)

# + tags=["active-ipynb"]
# from radon.metrics import h_visit
# h_visit(c)
# -

# ## Checking Notebook Metrics Evolution Over Time
#
# The `wily` package uses `radon` to produce code quality reports across a git repository history and generate charts showin the evolution of metrics over the lifetime of a repository. This suggests various corollaries:
#
# - could we generate `wily` style measures over the recent history of a notebook code cell?
# - could we generate `wily` style temporal measures over all the reports (markdown text, as well as code) generated from a notebook across several commits of it to a git repository.

# ## Other Cell Analysis
#
# As a placeholder, should we also at least report on a count of cells that are note code or markdown cells?
#
# Also a count of empty cells?
#
# Is this moving towards some sort of notebook linter?
