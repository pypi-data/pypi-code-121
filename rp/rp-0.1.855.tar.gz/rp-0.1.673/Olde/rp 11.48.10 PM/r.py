# python /Users/Ryan/PycharmProjects/Py27RyanStandard2.7/Groupie.py ftF11dwbP61OfPf9QsXBfS5usCdQdBkkMieObdvZ -g 'The Think Tank'
# Imports that are necessary for the 'r' module:
# Imports I tend to use a lot and include so they their names can be directly imported from th:
# region Import
# This is useful for running things on the terminal app or in blender
from __future__ import unicode_literals
# import r# For rinsp searches for functions in the r module, so I don't need to keep typing 'import r' over and over again
import sys
import numpy as np
import threading
from builtins import *#For autocompletion with pseudo_terminal
from time import sleep

# Places I want to access no matter where I launch r.py
# sys.path.append('/Users/Ryan/PycharmProjects/RyanBStandards_Python3.5')
# sys.path.append('/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages')

# endregion
# region ［entuple， detuple］
def entuple(x):
    # For pesky petty things.
    if isinstance(x,tuple):
        return x
    return x,
def detuple(x: tuple):
    # For pesky petty things. Code is simpler than explanation here.
    try:
        if len(x) == 1:
            return x[0]
    except:
        pass
    return x
# endregion
# region ［enlist， delist］
def enlist(x):
    # For pesky petty things.
    if isinstance(x,list):
        return x
    return [x]

def delist(x: list):
    # For pesky petty things. Code is simpler than explanation here.
    try:
        if len(x) == 1:
            return x[0]
    except:
        pass
    return x
# endregion
# region  rCode: ［run‚ fog‚ scoop‚ seq_map‚ par_map‚ seq‚ par‚ rev‚ pam‚ identity，list_pop，summation，product］
#   ∞
#   ∫𝓍²∂𝓍
# ﹣∞
# region  ［run‚ fog］
def run(f,*g,**kwg):  # Pop () ⟶ )(
    return f(*g,**kwg)
def fog(f,*g,**kwg):  # Encapsulate )( ⟶ ()      'fog' ≣ ƒ ∘ g‚ where g can be any number of parameters.
    return lambda:f(*g,**kwg)
# endregion
# region［scoop］
# scoop could have been implemented with seq. I chose not to.
def scoop(funcⵓscoopˏnew,list_in,init_value=None):
    from copy import copy,deepcopy
    # Try to make a copy just in case init_value is a list
    try:
        scoop_value=deepcopy(init_value)
    except:
        try:
            scoop_value=copy(init_value)
        except:
            scoop_value=init_value
    for element in list_in:
        scoop_value=funcⵓscoopˏnew(scoop_value,element)
    return scoop_value
# endregion
# region ［seq_map‚ par_map］
def seq_map(func,*iterables):
    # Like par_map, this def features non-lazy evaluation! (Unlike python's map function, which does not. Proof: map(print,['hello']) does not print anything, but [*map(print,['hello'])] does.)
    return list(map(func,*iterables))  # Basically it's exactly like python's built-in map function, except it forces it to evaluate everything inside it before it returns the output.
from multiprocessing.dummy import Pool as ThreadPool  # ⟵ par_map uses ThreadPool. We import it now so we don't have to later, when we use par_map.
def par_map(func,*iterables,number_of_threads=None,chunksize=None):
    # Multi-threaded map function. When I figure out a way to do parallel computations, this def (conveniently high-level) will be replaced.
    try:
        par_pool=ThreadPool(number_of_threads)
        try:
            out=par_pool.map(lambda args:func(*args),zip(*iterables),chunksize=chunksize)  # ⟵ A more complicated version of out=par_pool.map(func,iterable,chunksize=chunksize). Current version lets func accept multiple arguments.
        except:
            out=par_pool.map(func,iterables,chunksize=chunksize)
        par_pool.terminate()  # ⟵ If we don't have this line here, the number of threads running AKA threading.active_count() will continue to grow even after this def has returned, ∴ eventually causing the RunTime error exception mentioned below.
        return out
    except RuntimeError:  # ⟵ Assuming we got "RuntimeError: can't start new thread", we will calculate it sequentially instead. It will give the same result, but it won't be in parallel.
        return seq_map(func,*iterables)
# endregion
# region ［seq‚ par］
def seq(funcs,*init):
    # The current flagship function of rCode. This function can, in theory, single-handedly replace all other rCode functions (except par, which is analogous to seq). (Though it might be inconvenient to do so)
    # Possible future add-on: Enable recursive calls with a special value of func? (Probably won't though)
    try:  # Usually funcs will be an iterable. But if it is not, this test will catch it. This is because seq(print,'hello world')≣seq([print],'hello world')
        funcs=list(funcs)  # A simple check to find out whether funcs is iterable or not. If it is, it becomes a list (even if it was originally, let's say, a tuple).
    except TypeError:  # 'funcs' was not iterable; ∴ 'funcs' must be a single, callable function
        return funcs(*init)  # Because we have not yet iterated, we contain certain that 'init' is a tuple.

    # assert isinstance(funcs,list) # Internal logic assertion. This should always be true because of 'funcs=[*funcs]'
    for func in funcs:  # If we reach this line, we know ∴ 'funcs' is a list.
        temp=func(*init) if isinstance(init,tuple) else func(init)
        if temp is not None:
            init=temp
    return init
def par(funcsᆢvoids,*params):
    # NOTE: PARAMS NEVER CHANGES!!! The applications of that would be too limited to justify the effort of creating it. Instead, this def simply treats all functions as voids in the same way that seq could.
    # seq's little sister, and child of par_map. Only analagous to seq in specific contexts. This function is NOT capable of returning anything useful due to the inherent nature of multi-threading.
    par_map(lambda func:func(*params),funcsᆢvoids)  # Shares a similar syntax to seq. AKA multiple functions with a single set of parameters.
# endregion
# region  ［rev］
rev=lambda f,n:lambda *𝓍_:seq([f] * n,*𝓍_)  # Pseudo-revolutions (technically iterations)     Ex: rev(lambda x:x+1,5)(0) == 5
# endregion
# region ［pam］
def pam(funcs,*args,**kwargs):
    # pam is map spelt backwards. pam maps multiple defs onto a single set of arguments (instead of map, which maps multiple sets of arguments onto one function)
    assert is_iterable(funcs),str(funcs) + " ≣ funcs，is NOT iterable. Don't bother using pam! Pam is meant for mapping multiple functions onto one set of arguments; and from what I can tell you only have one function."
    return [f(*args,**kwargs) for f in funcs]
# endregion
# region ［identity］
def identity(*args):
    # The identity function. ƒ﹙𝓍﹚﹦ 𝓍    where   ƒ ≣ identity
    return detuple(args)
# endregion
# region ［list_pop］ (a bit of a misnomer; I know that now, after having taken CSE214.)
list_pop=lambda list_2d:scoop(lambda old,new:list(old) + list(new),list_2d,[])
# endregion
# region ［summation，product］
def product(x):
    # Useful because this literally uses the '*' operator over and over again instead of necessarily treating the elements as numbers.
    return scoop(lambda 𝓍,𝓎:𝓍 * 𝓎,x,x[0]) if len(x) else 1
    # assert is_iterable(x)
    # try:
    #     out=x[0]
    # except:
    #     return 1# x has no indices
    # for y in x[1:]:
    #     out*=y
    # return out
def summation(x,start=None):
    # Useful because this literally uses the '+' operator over and over again instead of necessarily treating the elements as numbers.
    # list_pop(l)≣summation(l)
    # sum(x,[])≣summation(x)
    # sum(x)≣summation(x)
    return scoop(lambda 𝓍,𝓎:𝓍 + 𝓎,x,start if start is not None else x[0]) if len(x) else start
    # assert is_iterable(x)
    # try:
    #     out=x[0]
    # except:
    #     return 0# x has no indices
    # for y in x[1:]:
    #     out+=y
    # return out

# endregion
# endregion
# region  Time:［gtoc，tic‚ toc‚ ptoc‚ ptoctic‚ millis，micros，nanos］
import time
_global_tic=time.time()
gtoc=time.time  # global toc
def tic() -> callable:
    global _global_tic
    _global_tic=local_tic=time.time()
    def local_toc():  # Gives a permanent toc to this tic, specifically
        return gtoc() - local_tic
    return local_toc  # Returns a method so you can do a=tic();a.toc() ⟵ Gives a local (not global) toc value so each tic can be used as a new timer
def toc() -> float:
    return gtoc() - _global_tic
def ptoc(new_line=True) -> None:
    fansi_print(str(toc()) + " seconds",new_line=new_line)
def ptoctic() -> None:
    ptoc()
    tic()
# ⁠⁠⁠⁠                                         ⎧                                      ⎫
# ⁠⁠⁠⁠                                         ⎪     ⎧                               ⎫⎪
# ⁠⁠⁠⁠                                         ⎪     ⎪⎧                         ⎫    ⎪⎪
_milli_micro_nano_converter=lambda s,n:int(round((s() if callable(s) else s) * n))
# ⁠⁠⁠⁠                                         ⎪     ⎪⎩                         ⎭    ⎪⎪
# ⁠⁠⁠⁠                                         ⎪     ⎩                               ⎭⎪
# ⁠⁠⁠⁠                                         ⎩                                      ⎭
# You can do millis(tic()) ⟵ Will probably be about 0， millis(toc)， millis(1315)， millis() ⟵ Gets global time by default
def seconds(seconds=gtoc) -> int:
    return _milli_micro_nano_converter(seconds,10 ** 0)
def millis(seconds=gtoc) -> int:
    return _milli_micro_nano_converter(seconds,10 ** 3)
def micros(seconds=gtoc) -> int:
    return _milli_micro_nano_converter(seconds,10 ** 6)
def nanos(seconds=gtoc) -> int:
    return _milli_micro_nano_converter(seconds,10 ** 9)

# endregion
# region  Files and such: ［get_current_directory‚ get_all_file_names］
import glob,sys
def get_current_directory():
    # SUMMARY: get_current_directory() ≣ sys.path[0] ﹦ ﹙default folder_path﹚ ﹦ ﹙current directory﹚ ﹦ /Users/Ryan/PycharmProjects/RyanBStandards_Python3.5
    return sys.path[0]
def get_all_file_names(file_name_ending: str = '',file_name_must_contain: str = '',folder_path: str = get_current_directory(),show_debug_narrative: bool = False):
    # SUMMARY: This method returns a list of all file names files in 'folder_path' that meet the specifications set by 'file_name_ending' and 'file_name_must_contain'
    # Leave file_name_ending blank to return all file names in the folder.
    # To find all file names of a specific extension, make file_name_ending ﹦ '.jpg' or 'png' etc.
    # Note: It does not matter if you have '.png' vs 'png'! It will return a list of all files whose name's ends…
    #     …with file_name_ending (whether that comes from the file type extension or not). Note that you can use this to search…
    #     …for specific types of file names that YOU made arbitrarily, like 'Apuppy.png','Bpuppy.png' ⟵ Can both be found with…
    #     …file_name_ending ﹦ 'puppy.png'
    # file_name_must_contain ⟶ all names in the output list must contain this character sequence
    # show_debug_narrative ⟶ controls whether to print out details about what this function is doing that might help to debug something.
    #     …By default this is disabled to avoid spamming the poor programmer who dares use this function.
    # ;;::O(if)OOO
    os.chdir(folder_path)
    if show_debug_narrative:
        print(get_all_file_names.__name__ + ": (Debug Narrative) Search Directory ﹦ " + folder_path)
    output=[]
    for file_name in glob.glob("*" + file_name_ending):
        if file_name_must_contain in file_name:
            output.append(file_name)  # I tried doing it with the '+' operator, but it returned a giant list of individual characters. This way works better.
            if show_debug_narrative:
                print(get_all_file_names.__name__ + ": (Debug Narrative) Found '" + file_name + "'")
    if show_debug_narrative:
        print(get_all_file_names.__name__ + ' (Debug Narrative) Output ﹦ ' + str(output))
    return output
# endregion
# region String ⟷ Integer List:  ［int_list_to_string‚ string_to_int_list］
int_list_to_string=lambda int_list:"".join(list(chr(i) for i in int_list))
string_to_int_list=lambda string:list(ord(i) for i in string)
# USAGE EXAMPLE:
#   print((lambda x:int_list_to_string(range(ord(x)-500,ord(x)+500)))("⚢"))
#   print(int_list_to_string([*(a+1 for a in string_to_int_list("♔"))]))
#   #♈♉♊♋♌♍♎♏♐♑♒♓ ♔♕♖♗♘♙♚♛♜♝♞♟ gen
#   #⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯ ❨❩❪❫❬❭❮❯❰❱❲❳❴❵ ⚀⚁⚂⚃⚄⚅ ♔♕♖♗♘♙♚♛♜♝♞♟
# endregion
# region Fansi:［fansi，fansi_print，print_fansi_reference_table，fansi_syntax_highlighting］   (Format-ANSI colors and styles for the console)
# noinspection PyShadowingBuiltins
def currently_running_windows():
    import os
    return os.name=='nt'

def terminal_supports_ansi():
    if currently_running_windows():
        try:
            from colorama import init
            init()  # Trying to enable ANSI coloring on windows console
            return True
        except:
            return False
    return True
    # return sys.stdout.isatty()# There are probably more sophistacated, better ways to check, but I don't know them.
def terminal_supports_unicode():
    if currently_running_windows():# Try to enable unicode, but fail if we can't
        try:
            from win_unicode_console import enable
            enable()  # Trying to enable unicode characters on windows console
            return True
        except:
            return False
    # ∴ we are not running Windows
    return True# I don't know how to check whether you can render characters such as ⮤, ✔, or ⛤ etc

def fansi(text_string,text_color=None,style=None,background_color=None):
    text_string=str(text_string)
    if not terminal_supports_ansi():# We cannot guarentee we have ANSI support; we might get ugly crap like '\[0Hello World\[0' or something ugly like that!
        return text_string# Don't format it; just leave it as-is
    if text_string=='':# Without this, print(fansi("",'blue')+'Hello World'
        return ''
    # 'fansi' is a pun, referring to ANSI and fancy
    # Uses ANSI formatting to give the terminal color outputs.
    # There are only 8 possible choices from each category, in ［０‚７］⋂ ℤ
    # Adding 0,30,and 40 because of the ANSI codes. Subtracting 1 later on because the syntax
    # of this def says that '0' is the absence of any style etc, whereas 1-8 are active styles.
    if isinstance(text_color,str):  # if text_color is a string, convert it into the correct integer and handle the associated exceptions
        try:
            text_color={'black':0,'red':1,'green':2,'yellow':3,'blue':4,'magenta':5,'cyan':6,'gray':7,'grey':7}[text_color.lower()]
        except:
            print("ERROR: def fansi: input-error: text_color = '{0}' BUT '{0}' is not a valid key! Replacing text_color as None.".format(text_color))
            text_color=None
    if isinstance(style,str):  # if background_color is a string, convert it into the correct integer
        try:
            style={'bold':1,'faded':2,'underlined':4,'blinking':5,'outlined':7}[style.lower()]  # I don't know what the other integers do.
        except:
            print("ERROR: def fansi: input-error: style = '{0}' BUT '{0}' is not a valid key! Replacing style as None.".format(style))
            style=None
    if isinstance(background_color,str):  # if background_color is a string, convert it into the correct integer
        try:
            background_color={'black':0,'red':1,'green':2,'yellow':3,'blue':4,'magenta':5,'cyan':6,'gray':7,'grey':7}[background_color.lower()]
        except:
            print("ERROR: def fansi: input-error: background_color = '{0}' BUT '{0}' is not a valid key! Replacing background_color as None.".format(background_color))
            background_color=None

    format=[]
    if style is not None:
        assert 0 <= style <= 7,"style == " + str(style) + " ∴ ¬﹙0 <= style <= 7﹚ ∴ AssertionError"
        style+=0
        format.append(str(style))
    if text_color is not None:
        assert 0 <= text_color <= 7,"text_color == " + str(text_color) + " ∴ ¬﹙0 <= text_color <= 7﹚ ∴ AssertionError"
        text_color+=30
        format.append(str(text_color))
    if background_color is not None:
        assert 0 <= background_color <= 7,"background_color == " + str(background_color) + " ∴ ¬﹙0 <= background_color <= 7﹚ ∴ AssertionError"
        background_color+=40
        format.append(str(background_color))

    return "\x1b[%sm%s\x1b[0m" % (';'.join(format),str(text_string))  # returns a string with the appropriate formatting applied
# region fansi Examples
# print(fansi('ERROR:','red','bold')+fansi(" ATE TOO MANY APPLES!!!",'blue','underlined','yellow'))
# from random import randint
# print(seq([lambda old:old+fansi(chr(randint(0,30000)),randint(0,7),randint(0,7),randint(0,7))]*100,''))
# endregion
def fansi_print(text_string: object,text_color: object = None,style: object = None,background_color: object = None,new_line=True) -> object:
    # Example: print(fansi('ERROR:','red','bold')+fansi(" ATE TOO MANY APPLES!!!",'blue','underlined','yellow'))
    print(fansi(text_string,text_color=text_color,style=style,background_color=background_color),end='\n' if new_line else'',flush=True)
# noinspection PyShadowingBuiltins
def print_fansi_reference_table() -> None:
    # prints table of formatted text format options for fansi. For reference
    for style in range(8):
        for fg in range(30,38):
            s1=''
            for bg in range(40,48):
                format=';'.join([str(style),str(fg),str(bg)])
                s1+='\x1b[%sm %s \x1b[0m' % (format,format)
            print(s1)
        print('\n')
def fansi_syntax_highlighting(code: str,namespace=()):
    # PLEASE NOTE THAT I DID NOT WRITE THIS CODE!!! IT CAME FROM https://github.com/akheron/cpython/blob/master/Tools/scripts/highlight.py
    # Assumes code was written in python.
    # Method mainly intended for rinsp.
    # I put it in the r class for convenience.
    # Works when I paste methods in but doesn't seem to play nicely with rinsp. I don't know why yet.
    # See the highlight_sourse_in_ansi module for more stuff including HTML highlighting etc.
    default_ansi={
        'comment':('\033[0;31m','\033[0m'),
        'string':('\033[0;32m','\033[0m'),
        'docstring':('\033[0;32m','\033[0m'),
        'keyword':('\033[0;33m','\033[0m'),
        'builtin':('\033[0;35m','\033[0m'),
        'definition':('\033[0;33m','\033[0m'),
        'defname':('\033[0;34m','\033[0m'),
        'operator':('\033[0;33m','\033[0m'),
    }
    try:
        import keyword,tokenize,cgi,re,functools
        try:
            import builtins
        except ImportError:
            import builtins as builtins
        def is_builtin(s):
            'Return True if s is the name of a builtin'
            return hasattr(builtins,s) or s in namespace
        def combine_range(lines,start,end):
            'Join content from a range of lines between start and end'
            (srow,scol),(erow,ecol)=start,end
            if srow == erow:
                return lines[srow - 1][scol:ecol],end
            rows=[lines[srow - 1][scol:]] + lines[srow: erow - 1] + [lines[erow - 1][:ecol]]
            return ''.join(rows),end
        def analyze_python(source):
            '''Generate and classify chunks of Python for syntax highlighting.
               Yields tuples in the form: (category, categorized_text).
            '''
            lines=source.splitlines(True)
            lines.append('')
            readline=functools.partial(next,iter(lines),'')
            kind=tok_str=''
            tok_type=tokenize.COMMENT
            written=(1,0)
            for tok in tokenize.generate_tokens(readline):
                prev_tok_type,prev_tok_str=tok_type,tok_str
                tok_type,tok_str,(srow,scol),(erow,ecol),logical_lineno=tok
                kind=''
                if tok_type == tokenize.COMMENT:
                    kind='comment'
                elif tok_type == tokenize.OP and tok_str[:1] not in '{}[](),.:;@':
                    kind='operator'
                elif tok_type == tokenize.STRING:
                    kind='string'
                    if prev_tok_type == tokenize.INDENT or scol == 0:
                        kind='docstring'
                elif tok_type == tokenize.NAME:
                    if tok_str in ('def','class','import','from'):
                        kind='definition'
                    elif prev_tok_str in ('def','class'):
                        kind='defname'
                    elif keyword.iskeyword(tok_str):
                        kind='keyword'
                    elif is_builtin(tok_str) and prev_tok_str != '.':
                        kind='builtin'
                if kind:
                    if written != (srow,scol):
                        text,written=combine_range(lines,written,(srow,scol))
                        yield '',text
                    text,written=tok_str,(erow,ecol)
                    yield kind,text
            line_upto_token,written=combine_range(lines,written,(erow,ecol))
            yield '',line_upto_token
        def ansi_highlight(classified_text,colors=default_ansi):
            'Add syntax highlighting to source code using ANSI escape sequences'
            # http://en.wikipedia.org/wiki/ANSI_escape_code
            result=[]
            for kind,text in classified_text:
                opener,closer=colors.get(kind,('',''))
                result+=[opener,text,closer]
            return ''.join(result)
        return ansi_highlight(analyze_python(code))
    except:
        return code  # Failed to highlight code, presumably because of an import error.

# endregion
# region  Copy/Paste: ［string_to_clipboard，string_from_clipboard］
import os
try:
    from rp.Pyperclip import paste,copy
except:
    copy=paste=None
def string_to_clipboard(string):
    try:
        copy(string)
    except:
        os.system("echo '%_s' | pbcopy" % string)
string_from_clipboard=paste
# endregion
# region pseudo_terminal
# EXAMPLE CODE TO USE pseudo_terminal:
# The next 3 lines are used to import pseudo_terminal
# region pseudo_terminal definition
# #from r import make_pseudo_terminal
# def pseudo_terminal():pass # Easiest way to let PyCharm know that this is a valid def. The next line redefines it.
# exec(make_pseudo_terminal)
# endregion
# NOTE: In my PyCharm Live Templates, I made a shortcut to create the above three lines.
# make pseudo terminal     ⟵ The template keyword.


#   print("Result = "+str(pseudo_terminal()))
# endregion
# region 2d Methods:［width，height，rgb_to_grayscale，gauss_blur，flat_circle_kernel，med_filter，med_filter，med_filter，grid2d，grid2d_map，resize_image］
# noinspection PyShadowingNames
def width(image) -> int:
    return len(image)
def height(image) -> int:
    return len(image[0])
def rgb_to_grayscale(image):  # A demonstrative implementation of this pair
    # Takes an image with multiple color channels
    # Takes a 3d tensor as an input (X,Y,RGB)
    # Outputs a matrix (X,Y ⋀ Grayscale value)
    # Calculated by taking the average of the three channels.
    try:
        return np.average(image,2)  # Very fast if possible
    except:
        # The old way, when I used nested lists to represent images
        # (Only doing this if the numpy way fails so my older scripts don't break)
        # 'z' denotes the grayscale channel.
        # z ﹦﹙r﹢g﹢b﹚÷３
        x,y,r,g,b=image_to_xyrgb_lists(image)
        # z=[*map(lambda a,b,c:(a+b+c)/3.,r,g,b)] ⟵ Got overflow errors!
        z=list(range(assert_equality(len(x),len(y),len(r),len(g),len(b))))
        for i in z:
            z[i]=(float(r[i]) / 256 + float(g[i]) / 256 + float(b[i]) / 256) / 3
        return xyrgb_lists_to_image(x,y,z.copy(),z.copy(),z.copy())
def gauss_blur(image,σ,single_channel: bool = False,mode: str = 'reflect',shutup: bool = False):
    # NOTE: order refers to the derivative of the gauss curve; for edge detection etc.
    if σ == 0:
        return image
    mode=mode.lower()
    assert mode in {'constant','nearest','reflect','mirror','wrap'},"r.med_filter: Invalid mode for blurring edge-areas of image. mode=" + str(mode)
    # single_channel: IMPORTANT: This determines the difference between
    #       [1,2,3,4,5]
    #  and
    #       [[1],[2],[3],[4],[5]] (when False)
    # Works in RGB, RGBA, or any other number of color channels!
    from scipy.ndimage.filters import gaussian_filter
    gb=lambda x:gaussian_filter(x,sigma=σ,mode=mode)
    tp=np.transpose
    # noinspection PyTypeChecker
    sh=np.shape(image)
    assert isinstance(sh,tuple)
    if not single_channel and not sh[-1] <= 4 and not shutup:  # Generally if you have more than 4 channels you are using a single_channel image.
        fansi_print("r.gauss_blur: Warning: Last channel has length of " + str(sh[-1]) + "; you results might be weird. Consider setting optional parameter 'single_channel' to True?",'red')
    s=list(range(len(sh)))
    if len(s) == 1 or single_channel:  # We don't have channels of colors, we only have 1 color channel (AKA we extracted the red of an image etc)
        return gb(image)

    #        ⎛                                                                      ⎞
    #        ⎜⎛                                               ⎞                     ⎟
    #        ⎜⎜                 ⎛                            ⎞⎟                     ⎟
    #        ⎜⎜                 ⎜      ⎛     ⎞       ⎛      ⎞⎟⎟     ⎛     ⎞   ⎛    ⎞⎟
    return tp([gb(x) for x in tp(image,[s[-1]] + list(s[:-1]))],list(s[1:]) + [s[0]])  # Blur each channel individually.
    #        ⎜⎜                 ⎜      ⎝     ⎠       ⎝      ⎠⎟⎟     ⎝     ⎠   ⎝    ⎠⎟
    #        ⎜⎜                 ⎝                            ⎠⎟                     ⎟
    #        ⎜⎝                                               ⎠                     ⎟
    #        ⎝                                                                      ⎠

    # NOTE:
    #     ⮤ _s=(0,1,2)
    #     ⮤ [_s[-1]] + list(_s[:-1])
    # ans=[2,0,1]
    #     ⮤ list(_s[1:]) + [_s[0]]
    # ans=[1,2,0]

    # region Works with RGB but fails on single channels
    # import cv2
    # # noinspection PyUnresolvedReferences
    # return cv2.GaussianBlur(image,(radius,radius),0)
    # endregion
    # def med_filter(image,σ):
    #     # Works in RGB, RGBA, or any other number of color channels!
    #     from scipy.ndimage.filters import gaussian_filter as gb
    #     tp=np.transpose
    #     return tp([gb(x,σ) for x in tp(image,[2,0,1])],[1,2,0])# Blur each channel individually.
    #     # region Works with RGB but fails on single channels
    #     # import cv2
    #     # # noinspection PyUnresolvedReferences
    #     # return cv2.GaussianBlur(image,(radius,radius),0)
    #     # endregion
def flat_circle_kernel(diameter):
    d=int(diameter)
    v=np.linspace(-1,1,d) ** 2
    m=np.zeros([d,d])
    m+=v
    m=np.transpose(m)
    m+=v
    return m <= 1
def max_filter(image,diameter,single_channel: bool = False,mode: str = 'reflect',shutup: bool = False):
    # NOTE: order refers to the derivative of the gauss curve; for edge detection etc.
    if diameter == 0:
        return image
    mode=mode.lower()
    assert mode in {'constant','nearest','reflect','mirror','wrap'},"r.max_filter: Invalid mode for max-filtering edge-areas of image. mode=" + str(mode)
    # single_channel: IMPORTANT: This determines the difference between
    #       [1,2,3,4,5]
    #  and
    #       [[1],[2],[3],[4],[5]] (when False)
    # Works in RGB, RGBA, or any other number of color channels!
    from scipy.ndimage.filters import maximum_filter as filter
    kernel=flat_circle_kernel(diameter)
    f=lambda x:filter(x,footprint=kernel,mode=mode)
    tp=np.transpose
    sh=np.shape(image)
    assert isinstance(sh,tuple)
    if not single_channel and not sh[-1] <= 4 and not shutup:  # Generally if you have more than 4 channels you are using a single_channel image.
        fansi_print("r.med_filter: Warning: Last channel has length of " + str(sh[-1]) + "; you results might be weird. Consider setting optional parameter 'single_channel' to True?",'red')
    s=list(range(len(sh)))
    if len(s) == 1 or single_channel:  # We don't have channels of colors, we only have 1 color channel (AKA we extracted the red of an image etc)
        return f(image)

    #        ⎛                                                                      ⎞
    #        ⎜⎛                                               ⎞                     ⎟
    #        ⎜⎜                 ⎛                            ⎞⎟                     ⎟
    #        ⎜⎜                 ⎜      ⎛     ⎞       ⎛      ⎞⎟⎟     ⎛     ⎞   ⎛    ⎞⎟
    return tp([f(x) for x in tp(image,[s[-1]] + list(s[:-1]))],list(s[1:]) + [s[0]])  # Blur each channel individually.
    #        ⎜⎜                 ⎜      ⎝     ⎠       ⎝      ⎠⎟⎟     ⎝     ⎠   ⎝    ⎠⎟
    #        ⎜⎜                 ⎝                            ⎠⎟                     ⎟
    #        ⎜⎝                                               ⎠                     ⎟
    #        ⎝                                                                      ⎠

    # NOTE:
    #     ⮤ _s=(0,1,2)
    #     ⮤ [_s[-1]] + list(_s[:-1])
    # ans=[2,0,1]
    #     ⮤ list(_s[1:]) + [_s[0]]
    # ans=[1,2,0]
def min_filter(image,diameter,single_channel: bool = False,mode: str = 'reflect',shutup: bool = False):
    # NOTE: order refers to the derivative of the gauss curve; for edge detection etc.
    if diameter == 0:
        return image
    mode=mode.lower()
    assert mode in {'constant','nearest','reflect','mir3ror','wrap'},"r.min_filter: Invalid mode for min-filtering edge-areas of image. mode=" + str(mode)
    # single_channel: IMPORTANT: This determines the difference between
    #       [1,2,3,4,5]
    #  and
    #       [[1],[2],[3],[4],[5]] (when False)
    # Works in RGB, RGBA, or any other number of color channels!
    from scipy.ndimage.filters import minimum_filter as filter
    kernel=flat_circle_kernel(diameter)
    f=lambda x:filter(x,footprint=kernel,mode=mode)
    tp=np.transpose
    sh=np.shape(image)
    assert isinstance(sh,tuple)
    if not single_channel and not sh[-1] <= 4 and not shutup:  # Generally if you have more than 4 channels you are using a single_channel image.
        fansi_print("r.med_filter: Warning: Last channel has length of " + str(sh[-1]) + "; you results might be weird. Consider setting optional parameter 'single_channel' to True?",'red')
    s=list(range(len(sh)))
    if len(s) == 1 or single_channel:  # We don't have channels of colors, we only have 1 color channel (AKA we extracted the red of an image etc)
        return f(image)

    # ⎛                                                                     ⎞
    #        ⎜⎛                                              ⎞                     ⎟
    #        ⎜⎜                ⎛                            ⎞⎟                     ⎟
    #        ⎜⎜                ⎜      ⎛     ⎞       ⎛      ⎞⎟⎟     ⎛     ⎞   ⎛    ⎞⎟
    return tp([f(x) for x in tp(image,[s[-1]] + list(s[:-1]))],list(s[1:]) + [s[0]])  # Blur each channel individually.
    #        ⎜⎜                ⎜      ⎝     ⎠       ⎝      ⎠⎟⎟     ⎝     ⎠   ⎝    ⎠⎟
    #        ⎜⎜                ⎝                            ⎠⎟                     ⎟
    #        ⎜⎝                                              ⎠                     ⎟
    #        ⎝                                                                     ⎠

    # NOTE:
    #     ⮤ _s=(0,1,2)
    #     ⮤ [_s[-1]] + list(_s[:-1])
    # ans=[2,0,1]
    #     ⮤ list(_s[1:]) + [_s[0]]
    # ans=[1,2,0]
def med_filter(image,diameter,single_channel: bool = False,mode: str = 'reflect',shutup: bool = False):
    # NOTE: order refers to the derivative of the gauss curve; for edge detection etc.
    if diameter == 0:
        return image
    mode=mode.lower()
    assert mode in {'constant','nearest','reflect','mirror','wrap'},"r.med_filter: Invalid mode for med-filtering edge-areas of image. mode=" + str(mode)
    # single_channel: IMPORTANT: This determines the difference between
    #       [1,2,3,4,5]
    #  and
    #       [[1],[2],[3],[4],[5]] (when False)
    # Works in RGB, RGBA, or any other number of color channels!
    from scipy.ndimage.filters import median_filter as filter
    kernel=flat_circle_kernel(diameter)
    f=lambda x:filter(x,footprint=kernel,mode=mode)
    tp=np.transpose
    sh=np.shape(image)
    assert isinstance(sh,tuple)
    if not single_channel and not sh[-1] <= 4 and not shutup:  # Generally if you have more than 4 channels you are using a single_channel image.
        fansi_print("r.med_filter: Warning: Last channel has length of " + str(sh[-1]) + "; you results might be weird. Consider setting optional parameter 'single_channel' to True?",'red')
    s=list(range(len(sh)))
    if len(s) == 1 or single_channel:  # We don't have channels of colors, we only have 1 color channel (AKA we extracted the red of an image etc)
        return f(image)

    #        ⎛                                                                     ⎞
    #        ⎜⎛                                              ⎞                     ⎟
    #        ⎜⎜                ⎛                            ⎞⎟                     ⎟
    #        ⎜⎜                ⎜      ⎛     ⎞       ⎛      ⎞⎟⎟     ⎛     ⎞   ⎛    ⎞⎟
    return tp([f(x) for x in tp(image,[s[-1]] + list(s[:-1]))],list(s[1:]) + [s[0]])  # Blur each channel individually.
    #        ⎜⎜                ⎜      ⎝     ⎠       ⎝      ⎠⎟⎟     ⎝     ⎠   ⎝    ⎠⎟
    #        ⎜⎜                ⎝                            ⎠⎟                     ⎟
    #        ⎜⎝                                              ⎠                     ⎟
    #        ⎝                                                                     ⎠

    # NOTE:
    #     ⮤ _s=(0,1,2)
    #     ⮤ [_s[-1]] + list(_s[:-1])
    # ans=[2,0,1]
    #     ⮤ list(_s[1:]) + [_s[0]]
    # ans=[1,2,0]
def range_filter(image,diameter,single_channel: bool = False,mode: str = 'reflect',shutup: bool = False):
    args=image,diameter,single_channel,mode,shutup
    return max_filter(*args) - min_filter(*args)
def grid2d(width: int,height: int,fᆢrowˏcolumn=lambda r,c:None) -> list:
    from copy import deepcopy
    # Perhaps I'll make a future version that extends this to n-dimensions, like rmif in MatLab
    out=deepcopy_multiply([[[None]] * height],width)
    for column in range(height):
        for row in range(width):
            out[row][column]=fᆢrowˏcolumn(row,column)
    return out
def grid2d_map(grid2d_input,value_func) -> list:
    # Similar to rmvf (ryan matrix value function), except restricted to just 2d grids.
    # ⁠⁠⁠⁠                ⎧                                                                                  ⎫
    # ⁠⁠⁠⁠                ⎪                                                              ⎧                  ⎫⎪
    # ⁠⁠⁠⁠                ⎪     ⎧            ⎫       ⎧            ⎫                      ⎪            ⎧ ⎫⎧ ⎫⎪⎪
    return grid2d(width(grid2d_input),height(grid2d_input),lambda x,y:value_func(grid2d_input[x][y]))
# ⁠⁠⁠⁠                ⎪     ⎩            ⎭       ⎩            ⎭                      ⎪            ⎩ ⎭⎩ ⎭⎪⎪
# ⁠⁠⁠⁠                ⎪                                                              ⎩                  ⎭⎪
# ⁠⁠⁠⁠                ⎩                                                                                  ⎭
def resize_image(image,scale,interp='bilinear'):
    """
    resize_image resizes images. Who woulda thunk it? Stretchy-squishy image resizing!
    :param image: a numpy array, preferably. But it can also handle pure-python list-of-lists if that fails.
    :param scale: can either be a scalar (get it? for SCALE? lol ok yeah that died quickly) or a tuple of integers to specify the new dimensions we want like (128,128)
    :param interp: ONLY APPLIES FOR numpy arrays! interp ∈ {'nearest','bilinear','bicubic','cubic'}
    :return: returns the resized image
    """
    assert interp in {'nearest','bilinear','bicubic','cubic'}
    if scale == 1:
        return image
    try:
        from scipy.misc import imresize
        return imresize(image,scale,interp)
    except:
        return grid2d(int(len(image) * scale),int(len(image[0]) * scale),lambda x,y:image[int(x / scale)][int(y / scale)])
# endregion
# region  xyrgb lists ⟷ image:［image_to_xyrgb_lists，xyrgb_lists_to_image，xyrgb_normalize，image_to_all_normalized_xy_rgb_training_pairs，extract_patches］     (Invertible Pair)
try:from sklearn.feature_extraction.image import extract_patches
except:pass
def image_to_xyrgb_lists(image):
    # expects an array like, for example 'image=[[[1,2,3],[4,5,6]],[[7,8,9],[10,11,12]]]'
    out_x=[]
    out_y=[]
    out_r=[]
    out_g=[]
    out_b=[]
    for x_index,x_val in enumerate(image):
        for y_index,y_val in enumerate(x_val):
            out_x.append(x_index)
            out_y.append(y_index)
            out_r.append(y_val[0])
            out_g.append(y_val[1])
            out_b.append(y_val[2])
    return out_x,out_y,out_r,out_g,out_b
def xyrgb_lists_to_image(*xyrgb_lists_as_tuple):
    xyrgb_lists_as_tuple=detuple(xyrgb_lists_as_tuple)  # So we can either accept 5 arguments or one tuple argument with 5 elements.
    assert len(xyrgb_lists_as_tuple) == 5,"One element:list for each channel: X Y R G B"
    x,y,r,g,b=xyrgb_lists_as_tuple
    assert len(x) == len(y) == len(r) == len(g) == len(b),"An outside-noise assumption. If this assertion fails then there is something wrong with the input parameters ⟹ this def is not to blame."
    xyrgb_length=len(x)  # =len(y)=len(r)=len(g)=len(b) etc. We rename it 'xyrgb_length' to emphasize this symmetry.
    out_image=deepcopy_multiply([[None] * (max(y) + 1)],(max(x) + 1))  # Pre-allocating the pixels. [R,G,B] is inserted into each pixel later.
    for index in range(xyrgb_length):
        out_image[x[index]][y[index]]=[r[index],g[index],b[index]]
    return out_image
def xyrgb_normalize(*xyrgb,rgb_old_max=255,rgb_new_max=1,x_new_max=1,y_new_max=1):
    # Converts the (X and Y values, originally ﹙integers: the pixel X and Y indexes﹚) into float values between 0 and 1
    # Also converts the R,G, and B values from the range ［0‚255］⋂ ℤ into the range ［0‚1］⋂ ℝ
    x,y,r,g,b=detuple(xyrgb)
    x_factor=x_new_max / max(x)
    y_factor=y_new_max / max(y)
    x=list(ⵁ * x_factor for ⵁ in x)
    y=list(ⵁ * y_factor for ⵁ in y)

    rgb_factor=rgb_new_max / rgb_old_max
    r=list(ⵁ * rgb_factor for ⵁ in r)
    g=list(ⵁ * rgb_factor for ⵁ in g)
    b=list(ⵁ * rgb_factor for ⵁ in b)

    return x,y,r,g,b
def image_to_all_normalized_xy_rgb_training_pairs(image):
    x,y,r,g,b=xyrgb_normalize(image_to_xyrgb_lists(image))
    return list(zip(x,y)),list(zip(r,g,b))

    # NOTE: This def exists for efficiency purposes.
    # To create a training batch from the image, the minimal syntax would be:
    #     random_parallel_batch(*image_to_all_normalized_xy_rgb_training_pairs(image),a,b)
    # BUT NOTE: It is very inneficient to recalculate this def over and over again.
    # Store the output of this as a vairable, and use like so:
    # precalculated=image_to_all_normalized_xy_rgb_training_pairs(image)
    # new_batch=random_parallel_batch(*precalculated,a,b)


    # region Explanatory Example:
    # # Goal: create input and output from XY to RGB from image and turn them into a random batch for NN input outputs
    # #from r import *
    # x=['x₁','x₂','x₃']
    # y=['y₁','y₂','y₃']
    # r=['r₁','r₂','r₃']
    # g=['g₁','g₂','g₃']
    # b=['b₁','b₂','b₃']
    #
    # inputs=list(zip(x,y))
    # outputs=list(zip(r,g,b))
    # io_pairs=list(zip(inputs,outputs))
    #
    #  ⁠⁠⁠⁠    ⎧                                    ⎫
    #  ⁠⁠⁠⁠    ⎪    ⎧                              ⎫⎪
    # ⁠⁠⁠⁠     ⎪    ⎪   ⎧                         ⎫⎪⎪
    # print(list(zip(*random_batch(io_pairs,2))))
    #  ⁠⁠⁠⁠    ⎪    ⎪   ⎩                         ⎭⎪⎪
    #  ⁠⁠⁠⁠    ⎪    ⎩                              ⎭⎪
    #  ⁠⁠⁠⁠    ⎩                                    ⎭
    #
    #  ⁠⁠⁠⁠ ⎧                                                                      ⎫
    #  ⁠⁠⁠⁠ ⎪⎧                          ⎫  ⎧                                      ⎫⎪
    # # [(('x₂', 'y₂'), ('x₃', 'y₃')), (('r₂', 'g₂', 'b₂'), ('r₃', 'g₃', 'b₃'))]
    #  ⁠⁠⁠⁠ ⎪⎩                          ⎭  ⎩                                      ⎭⎪
    #  ⁠⁠⁠⁠ ⎩                                                                      ⎭
    # endregion
# endregion
# region Randomness:［random_index，random_element，random_permutation，randint，random_float，random_chance，random_batch，shuffled，random_parallel_batch］
import random
def random_index(array_length_or_array_itself):
    # Basically a random integer generator suited for generating array indices.
    # Returns a random integer ∈ ℤ ⋂ [0‚array_length)
    if isinstance(array_length_or_array_itself,int):
        assert array_length_or_array_itself != 0
        return randint(0,array_length_or_array_itself - 1)
    else:
        return random_index(len(array_length_or_array_itself))
def random_element(x):
    assert is_iterable(x)
    return x[random_index(len(x))]
def random_permutation(n) -> list or str:
    # Either n is an integer (as a length) OR n is an iterable
    if is_iterable(n):  # random_permutation([1,2,3,4,5]) ⟶ [3, 2, 4, 5, 1]
        return shuffled(n)
    return list(np.random.permutation(n))  # random_permutation(5) ⟶ [3, 2, 1, 4, 0]
def randint(a_inclusive,b_inclusive=0):
    # If both a and b are specified, the range is inclusive, choose from range［a，b] ⋂ ℤ
    # Otherwise, if only a is specified, choose random element from the range ［a，b) ⋂ ℤ
    from random import randint
    return randint(min([a_inclusive,b_inclusive]),max([a_inclusive,b_inclusive]))
def random_float(exclusive_max: float = 1) -> float:
    return exclusive_max * random.random()
def random_chance(probability: float = .5) -> bool:
    return random_float() < probability
def random_batch(full_list,batch_size: int = None,retain_order: bool = False):
    # Input conditions, assertions and rCode algebra:
    # rCode: Let ⨀ ≣ random_batch ∴
    #       ⨀ a None b ≣ ⨀ a len a b
    #       list a ≣ ⨀ a None True
    #       b ≣ len ⨀ a b
    if batch_size is None:  # The default if not specified
        # If we don't specify the batch size, assume that we simply want a shuffled version of the full_list
        if retain_order:
            return full_list  # A result of the rCode algebra. This simply speeds up the process.
        batch_size=len(full_list)
    else:
        assert 0 <= batch_size <= len(full_list),"batch_size == " + str(batch_size) + " ⋀ len(full_list) == " + str(len(full_list)) + "，∴  ¬ (0 <= batch_size <= len﹙full_list﹚)   Explanation: We do not allow duplicates, ∴ we cannot generate a larger batch than we have elements to choose from full_list"

    ⵁ=list(range(len(full_list)))  # All possible indices of full_list
    random.shuffle(ⵁ)  # This shuffles the ⵁ array but doesn't return anything
    ⵁ=ⵁ[0:batch_size]
    if retain_order:
        ⵁ.sort()
    return list(full_list[i] for i in ⵁ)
def shuffled(l):
    # Shuffle a list
    if isinstance(l,str):  # random_permutation("ABCDE") ⟶ 'EDBCA' special case: if its a string we want a string output, so we can jumble letters in words etc.
        return ''.join(shuffled(list(l)))
    return random_batch(l)  # Due to an r-code identity in random_batch
def random_parallel_batch(*full_lists,batch_size: int = None,retain_order: bool = False):
    # Created for machine learning input/output training-pairs generation.
    # rCode:
    # ⁠⁠⁠⁠        ⎧                                     ⎫
    # ⁠⁠⁠⁠        ⎪   ⎧                                ⎫⎪
    # ⁠⁠⁠⁠        ⎪   ⎪             ⎧                 ⎫⎪⎪
    # ⁠⁠⁠⁠        ⎪   ⎪             ⎪    ⎧       ⎫    ⎪⎪⎪
    #    list(zip(*random_batch(list(zip(*a)),b,c))) ≣ random_parallel_batch(*a,b,c)
    # ⁠⁠⁠⁠        ⎪   ⎪             ⎪    ⎩       ⎭    ⎪⎪⎪
    # ⁠⁠⁠⁠        ⎪   ⎪             ⎩                 ⎭⎪⎪
    # ⁠⁠⁠⁠        ⎪   ⎩                                ⎭⎪
    # ⁠⁠⁠⁠        ⎩                                     ⎭
    # print(parallel_batch(['a','b','c','d'],[1,2,3,4],batch_size=3)) ⟹ [['c', 'b', 'd'], [3, 2, 4]]
    # assert_equality(*full_lists,equality_check=lambda a,b:len(a)==len(b))# All lists ∈ full_lists must have the same length
    # ⁠⁠⁠⁠                         ⎧                                                                               ⎫
    # ⁠⁠⁠⁠                         ⎪    ⎧                         ⎫                                                ⎪
    # ⁠⁠⁠⁠                         ⎪    ⎪     ⎧                  ⎫⎪                                                ⎪
    # ⁠⁠⁠⁠                         ⎪    ⎪     ⎪   ⎧             ⎫⎪⎪                                                ⎪
    batch_indexes=random_batch(list(range(len(full_lists[0]))),batch_size=batch_size,retain_order=retain_order)  # Select random possible indices that will be synchronized across all lists of the output
    # ⁠⁠⁠⁠                         ⎪    ⎪     ⎪   ⎩             ⎭⎪⎪                                                ⎪
    # ⁠⁠⁠⁠                         ⎪    ⎪     ⎩                  ⎭⎪                                                ⎪
    # ⁠⁠⁠⁠                         ⎪    ⎩                         ⎭                                                ⎪
    # ⁠⁠⁠⁠                         ⎩                                                                               ⎭
    # ⁠⁠⁠⁠          ⎧                                                                ⎫
    # ⁠⁠⁠⁠          ⎪   ⎧                                                           ⎫⎪
    # ⁠⁠⁠⁠          ⎪   ⎪              ⎧                                ⎫           ⎪⎪
    # ⁠⁠⁠⁠          ⎪   ⎪              ⎪   ⎧                           ⎫⎪           ⎪⎪
    return list(map(lambda x:tuple(map(lambda i:x[i],batch_indexes)),full_lists))  # Note that batch_indexes is referenced inside a lambda statement that is called multiple times. This is why it is declared as a separate variable above.
    # ⁠⁠⁠⁠          ⎪   ⎪              ⎪   ⎩                           ⎭⎪           ⎪⎪
    # ⁠⁠⁠⁠          ⎪   ⎪              ⎩                                ⎭           ⎪⎪
    # ⁠⁠⁠⁠          ⎪   ⎩                                                           ⎭⎪
    # ⁠⁠⁠⁠          ⎩                                                                ⎭
    # The single-lined return statement shown directly above this line is ≣ to the next 5 lines of code:
    # out=deepcopy_multiply([[]],len(full_lists))
    # for i in batch_indexes:
    #     for j in range(len(out)):
    #         out[j].append(full_lists[j][i])
    # return out
# endregion
# region rant/ranp: ［run_as_new_thread，run_as_new_process］
def run_as_new_thread(funcᆢvoid,*args,**kwargs):  # ⟵ THIS IS DUBIOUS. I DON'T KNOW IF IT DOES WHAT ITS SUPPOSED TO....
    # Used when we simply don't need/want all the complexities of the threading module.
    # An anonymous thread that only ceases once the def is finished.
    new_thread=threading.Thread
    new_thread(target=funcᆢvoid,args=args,kwargs=kwargs).start()
    return new_thread
def run_as_new_process(funcᆢvoid,*args,**kwargs):
    # Used when we simply don't need/want all the complexities of the threading module.
    # An anonymous thread that only ceases once the def is finished.
    import multiprocessing as mp
    new_process=mp.Process(target=funcᆢvoid,args=args,kwargs=kwargs)
    new_process.start()  # can't tell the difference between start and run
    return new_process
# endregion
# region  Saving/Loading Images: ［load_image，load_image_from_url，save_image］
def load_image(file_name):
    from scipy.misc import imread
    return imread(file_name)
def load_image_from_url(url: str):
    from PIL import Image
    import requests
    from io import BytesIO
    response=requests.get(url)
    return np.add(Image.open(BytesIO(response.content)),0)  # Converts it to a numpy array by adding 0 to it.
def save_image(image,file_name=None,add_png_extension: bool = True):
    from scipy.misc import imsave
    if file_name is None:
        file_name=str(millis()) + ".png"  # ⟵ Default image name
    if add_png_extension:
        file_name+=".png"
    imsave(file_name,image)
# endregion
# region Text-To-Speech: ［text_to_speech，text_to_speech_via_apple，text_to_speech_via_google，text_to_speech_voices_comparison，text_to_speech_voices_for_apple，text_to_speech_voices_for_google，text_to_speech_voices_all，text_to_speech_voices_favorites］
# region ［text_to_speech_via_apple］
# region  All text_to_speech_via_apple voices along with their descriptions (type 'say -v ?' into terminal to get this):
"""
Alex                en_US    # Most people recognize me by my voice.
Alice               it_IT    # Salve, mi chiamo Alice e sono una voce italiana.
Alva                sv_SE    # Hej, jag heter Alva. Jag är en svensk röst.
Amelie              fr_CA    # Bonjour, je m’appelle Amelie. Je suis une voix canadienne.
Anna                de_DE    # Hallo, ich heiße Anna und ich bin eine deutsche Stimme.
Carmit              he_IL    # שלום. קוראים לי כרמית, ואני קול בשפה העברית.
Damayanti           id_ID    # Halo, nama saya Damayanti. Saya berbahasa Indonesia.
Daniel              en_GB    # Hello, my name is Daniel. I am a British-English voice.
Diego               es_AR    # Hola, me llamo Diego y soy una voz española.
Ellen               nl_BE    # Hallo, mijn naam is Ellen. Ik ben een Belgische stem.
Fiona               en-scotland # Hello, my name is Fiona. I am a Scottish-English voice.
Fred                en_US    # I sure like being inside this fancy computer
Ioana               ro_RO    # Bună, mă cheamă Ioana . Sunt o voce românească.
Joana               pt_PT    # Olá, chamo-me Joana e dou voz ao português falado em Portugal.
Jorge               es_ES    # Hola, me llamo Jorge y soy una voz española.
Juan                es_MX    # Hola, me llamo Juan y soy una voz mexicana.
Kanya               th_TH    # สวัสดีค่ะ ดิฉันชื่อKanya
Karen               en_AU    # Hello, my name is Karen. I am an Australian-English voice.
Kyoko               ja_JP    # こんにちは、私の名前はKyokoです。日本語の音声をお届けします。
Laura               sk_SK    # Ahoj. Volám sa Laura . Som hlas v slovenskom jazyku.
Lekha               hi_IN    # नमस्कार, मेरा नाम लेखा है.Lekha मै हिंदी मे बोलने वाली आवाज़ हूँ.
Luca                it_IT    # Salve, mi chiamo Luca e sono una voce italiana.
Luciana             pt_BR    # Olá, o meu nome é Luciana e a minha voz corresponde ao português que é falado no Brasil
Maged               ar_SA    # مرحبًا اسمي Maged. أنا عربي من السعودية.
Mariska             hu_HU    # Üdvözlöm! Mariska vagyok. Én vagyok a magyar hang.
Mei-Jia             zh_TW    # 您好，我叫美佳。我說國語。
Melina              el_GR    # Γεια σας, ονομάζομαι Melina. Είμαι μια ελληνική φωνή.
Milena              ru_RU    # Здравствуйте, меня зовут Milena. Я – русский голос системы.
Moira               en_IE    # Hello, my name is Moira. I am an Irish-English voice.
Monica              es_ES    # Hola, me llamo Monica y soy una voz española.
Nora                nb_NO    # Hei, jeg heter Nora. Jeg er en norsk stemme.
Paulina             es_MX    # Hola, me llamo Paulina y soy una voz mexicana.
Samantha            en_US    # Hello, my name is Samantha. I am an American-English voice.
Sara                da_DK    # Hej, jeg hedder Sara. Jeg er en dansk stemme.
Satu                fi_FI    # Hei, minun nimeni on Satu. Olen suomalainen ääni.
Sin-ji              zh_HK    # 您好，我叫 Sin-ji。我講廣東話。
Tessa               en_ZA    # Hello, my name is Tessa. I am a South African-English voice.
Thomas              fr_FR    # Bonjour, je m’appelle Thomas. Je suis une voix française.
Ting-Ting           zh_CN    # 您好，我叫Ting-Ting。我讲中文普通话。
Veena               en_IN    # Hello, my name is Veena. I am an Indian-English voice.
Victoria            en_US    # Isn't it nice to have a computer that will talk to you?
Xander              nl_NL    # Hallo, mijn naam is Xander. Ik ben een Nederlandse stem.
Yelda               tr_TR    # Merhaba, benim adım Yelda. Ben Türkçe bir sesim.
Yuna                ko_KR    # 안녕하세요. 제 이름은 Yuna입니다. 저는 한국어 음성입니다.
Yuri                ru_RU    # Здравствуйте, меня зовут Yuri. Я – русский голос системы.
Zosia               pl_PL    # Witaj. Mam na imię Zosia, jestem głosem kobiecym dla języka polskiego.
Zuzana              cs_CZ    # Dobrý den, jmenuji se Zuzana. Jsem český hlas."""
# endregion
text_to_speech_voices_for_apple=['Alex','Alice','Alva','Amelie','Anna','Carmit','Damayanti','Daniel','Diego','Ellen','Fiona','Fred','Ioana','Joana','Jorge','Juan','Kanya','Karen','Kyoko','Laura','Lekha','Luca','Luciana','Maged','Mariska','Mei-Jia','Melina','Milena','Moira','Monica','Nora','Paulina','Samantha','Sara','Satu','Sin-ji','Tessa','Thomas','Ting-Ting','Veena','Victoria','Xander','Yelda','Yuna','Yuri','Zosia','Zuzana']  # The old voices (that don't work on sierra. They used to work on el-capitan though): ["Samantha",'Bad News','Bahh','Bells','Boing','Bubbles','Cellos','Deranged','Good News','Hysterical','Pipe Organ','Trinoids','Whisper','Zarvox','Agnes','Kathy','Princess','Vicki','Victoria','Alex','Bruce','Fred','Junior','Ralph','Albert']
# Favorites (in this order): Samantha, Alex, Moira, Tessa, Fiona, Fred
def text_to_speech_via_apple(text: str,voice="Samantha",run_as_thread=True,rate_in_words_per_minute=None,filter_characters=True):
    # Only works on macs
    assert voice in text_to_speech_voices_for_apple
    text=str(text)
    if filter_characters:  # So you don't have to worry about confusing the terminal with command characters like '|', which would stop the terminal from reading anything beyond that.
        text=''.join(list(c if c.isalnum() or c in ".," else " " for c in text))  # remove_characters_that_confuse_the_terminal
    if rate_in_words_per_minute is not None and not 90 <= rate_in_words_per_minute <= 720:
        fansi_print("r.text_to_speech_via_apple: The rate you chose is ineffective. Empirically, I found that only rates between 90 and 720 have any effect in terminal, \n and you gave me a rate of " + str(rate_in_words_per_minute) + " words per minute. This is the same thing as not specifying a rate at all, as it won't cap off at the max or min.")
    # ⁠⁠⁠⁠                                                ⎧                                                                                                                                   ⎫
    # ⁠⁠⁠⁠                                                ⎪   ⎧                                                                                                                              ⎫⎪
    # ⁠⁠⁠⁠                                                ⎪   ⎪              ⎧                                                                                                              ⎫⎪⎪
    # ⁠⁠⁠⁠                                                ⎪   ⎪              ⎪                    ⎧                                                                           ⎫             ⎪⎪⎪
    # ⁠⁠⁠⁠                                                ⎪   ⎪              ⎪                    ⎪⎧                                      ⎫                                   ⎪             ⎪⎪⎪
    # ⁠⁠⁠⁠   ⎧                                           ⎫⎪   ⎪              ⎪                    ⎪⎪            ⎧                        ⎫⎪                                   ⎪             ⎪⎪⎪
    (run_as_new_thread if run_as_thread else run)(fog(shell_command,("say -v " + voice + ((" -r " + str(rate_in_words_per_minute)) if rate_in_words_per_minute else"") + " " + text)))
# ⁠⁠⁠⁠   ⎩                                           ⎭⎪   ⎪              ⎪                    ⎪⎪            ⎩                        ⎭⎪                                   ⎪             ⎪⎪⎪
# ⁠⁠⁠⁠                                                ⎪   ⎪              ⎪                    ⎪⎩                                      ⎭                                   ⎪             ⎪⎪⎪
# ⁠⁠⁠⁠                                                ⎪   ⎪              ⎪                    ⎩                                                                           ⎭             ⎪⎪⎪
# ⁠⁠⁠⁠                                                ⎪   ⎪              ⎩                                                                                                              ⎭⎪⎪
# ⁠⁠⁠⁠                                                ⎪   ⎩                                                                                                                              ⎭⎪
# ⁠⁠⁠⁠                                                ⎩                                                                                                                                   ⎭

# OLD, DIRTIER CODE: (for example, it references shell_command twice!! The new one of course doesn't do that.)
# def text_to_speech_via_apple(msg:str,voice="Samantha",run_as_thread=True,filter_characters=True):
#     if filter_characters:
#         msg=''.join(list(c if c.isalnum() or c in ".," else " " for c in msg))# remove_characters_that_confuse_the_terminal
#     # Only works on macs
#     assert voice in text_to_speech_voices_for_apple
#     if run_as_thread:
#         run_as_new_thread(lambda :shell_command("say -v "+voice+" "+msg))
#     else:
#         shell_command("say -v " + voice + " " + msg)
# endregion
# region ［text_to_speech_via_google］
text_to_speech_voices_for_google=['fr','es-us','el','sr','sv','la','af','lv','zh-tw','sq','da','en-au','ko','cy','mk','id','hy','es','ro','is','zh-yue','hi','zh-cn','th','ta','it','de','ca','sw','ar','nl','pt','cs','sk','ja','tr','zh','hr','es-es','eo','pt-br','pl','fi','hu','en','ru','en-uk','bn','no','en-us','vi']
def text_to_speech_via_google(text: str,voice='en',mp3_file_path: str = 'temp.mp3',play_sound: bool = True,run_as_thread: bool = True):
    # This only works when online, and has a larger latency than the native OSX text-to-speech function
    # Favorite voices: da
    # region gTTS: My own version of https://github.com/pndurette/gTTS (I modified it so that it can actually play voices from other languages, which it couldn't do before. I put that functionality in a comment because I don't know how to use Github yet (Feb 2017))
    import re,requests
    from gtts_token.gtts_token import Token
    class gTTS:
        """ gTTS (Google Text to Speech): an interface to Google'_s Text to Speech API """

        GOOGLE_TTS_URL='https://translate.google.com/translate_tts'
        MAX_CHARS=100  # Max characters the Google TTS API takes at a time
        LANGUAGES={
            'af':'Afrikaans',
            'sq':'Albanian',
            'ar':'Arabic',
            'hy':'Armenian',
            'bn':'Bengali',
            'ca':'Catalan',
            'zh':'Chinese',
            'zh-cn':'Chinese (Mandarin/China)',
            'zh-tw':'Chinese (Mandarin/Taiwan)',
            'zh-yue':'Chinese (Cantonese)',
            'hr':'Croatian',
            'cs':'Czech',
            'da':'Danish',
            'nl':'Dutch',
            'en':'English',
            'en-au':'English (Australia)',
            'en-uk':'English (United Kingdom)',
            'en-us':'English (United States)',
            'eo':'Esperanto',
            'fi':'Finnish',
            'fr':'French',
            'de':'German',
            'el':'Greek',
            'hi':'Hindi',
            'hu':'Hungarian',
            'is':'Icelandic',
            'id':'Indonesian',
            'it':'Italian',
            'ja':'Japanese',
            'ko':'Korean',
            'la':'Latin',
            'lv':'Latvian',
            'mk':'Macedonian',
            'no':'Norwegian',
            'pl':'Polish',
            'pt':'Portuguese',
            'pt-br':'Portuguese (Brazil)',
            'ro':'Romanian',
            'ru':'Russian',
            'sr':'Serbian',
            'sk':'Slovak',
            'es':'Spanish',
            'es-es':'Spanish (Spain)',
            'es-us':'Spanish (United States)',
            'sw':'Swahili',
            'sv':'Swedish',
            'ta':'Tamil',
            'th':'Thai',
            'tr':'Turkish',
            'vi':'Vietnamese',
            'cy':'Welsh'
        }

        def __init__(self,text,lang='en',debug=False):
            self.debug=debug
            if lang.lower() not in self.LANGUAGES:
                raise Exception('Language not supported: %s' % lang)
            else:
                self.lang=lang.lower()

            if not text:
                raise Exception('No text to speak')
            else:
                self.text=text

            # Split text in parts
            if len(text) <= self.MAX_CHARS:
                text_parts=[text]
            else:
                text_parts=self._tokenize(text,self.MAX_CHARS)

                # Clean
            def strip(x):
                return x.replace('\n','').strip()
            text_parts=[strip(x) for x in text_parts]
            text_parts=[x for x in text_parts if len(x) > 0]
            self.text_parts=text_parts

            # Google Translate token
            self.token=Token()

        def save(self,savefile):
            """ Do the Web request and save to `savefile` """
            with open(savefile,'wb') as f:
                self.write_to_fp(f)
                f.close()

        def write_to_fp(self,fp):
            LANGUAGES={'af':'Afrikaans','sq':'Albanian','ar':'Arabic','hy':'Armenian','bn':'Bengali','ca':'Catalan','zh':'Chinese','zh-cn':'Chinese (Mandarin/China)','zh-tw':'Chinese (Mandarin/Taiwan)','zh-yue':'Chinese (Cantonese)','hr':'Croatian','cs':'Czech','da':'Danish','nl':'Dutch','en':'English','en-au':'English (Australia)','en-uk':'English (United Kingdom)','en-us':'English (United States)','eo':'Esperanto','fi':'Finnish','fr':'French','de':'German','el':'Greek','hi':'Hindi','hu':'Hungarian','is':'Icelandic','id':'Indonesian','it':'Italian','ja':'Japanese','ko':'Korean','la':'Latin','lv':'Latvian','mk':'Macedonian','no':'Norwegian','pl':'Polish','pt':'Portuguese','pt-br':'Portuguese (Brazil)','ro':'Romanian','ru':'Russian','sr':'Serbian','sk':'Slovak','es':'Spanish','es-es':'Spanish (Spain)','es-us':'Spanish (United States)','sw':'Swahili','sv':'Swedish','ta':'Tamil','th':'Thai','tr':'Turkish','vi':'Vietnamese','cy':'Welsh'}
            """ Do the Web request and save to a file-like object """
            for idx,part in enumerate(self.text_parts):
                payload={'ie':'UTF-8',
                         'q':part,
                         'tl':self.lang,
                         'total':len(self.text_parts),
                         'idx':idx,
                         'client':'tw-ob',
                         'textlen':len(part),
                         'tk':self.token.calculate_token(part)}
                headers={
                    "Referer":"http://translate.google.com/",
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
                }
                if self.debug: print(payload)
                try:
                    r=requests.get(self.GOOGLE_TTS_URL,params=payload,headers=headers)
                    if self.debug:
                        print("Headers: {}".format(r.request.headers))
                        print("Reponse: {}, Redirects: {}".format(r.status_code,r.history))
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=1024):
                        fp.write(chunk)
                except Exception as e:
                    raise

        def _tokenize(self,text,max_size):
            """ Tokenizer on basic roman punctuation """

            punc="¡!()[]¿?.,;:—«»\n"
            punc_list=[re.escape(c) for c in punc]
            pattern='|'.join(punc_list)
            parts=re.split(pattern,text)

            min_parts=[]
            for p in parts:
                min_parts+=self._minimize(p," ",max_size)
            return min_parts

        def _minimize(self,thestring,delim,max_size):
            """ Recursive function that splits `thestring` in chunks
            of maximum `max_size` chars delimited by `delim`. Returns list. """

            if len(thestring) > max_size:
                idx=thestring.rfind(delim,0,max_size)
                return [thestring[:idx]] + self._minimize(thestring[idx:],delim,max_size)
            else:
                return [thestring]
                # endregion
    # endregion
    if run_as_thread:
        return run_as_new_thread(text_to_speech_via_google(text=text,voice=voice,mp3_file_path=mp3_file_path,play_sound=play_sound,run_as_thread=False))
    # Note that this method has to save a sound file in order for it to work. I put a default sound_file_path so that it will overwrite itself each time, so that I can avoid putting a ,delete_sound_file_afterwards:bool=True parameter in there (in case you do infact want to save a file)
    # NOTE: sound_file_path is only compatible with .mp3 files, so don't try putting a wav extension on it (it will break it)!
    lang=voice
    assert lang in text_to_speech_voices_for_google,'r.text_to_speech_via_google: The language you input, "' + lang + '", is not a valid option! Please choose one of the following values for lang instead: ' + ', '.join(text_to_speech_voices_for_google)  # These are the available languages we can choose from.
    gTTS(text=text,lang=lang).save(mp3_file_path)  # gTTS is a class, and .save is a function of an instance of that class.
    if play_sound:
        play_sound_file(mp3_file_path)
# endregion
text_to_speech_voices_all=text_to_speech_voices_for_apple + text_to_speech_voices_for_google
text_to_speech_voices_favorites=['da','en-au','zh-yue','hi','sk','zh','en','it','Samantha','Alex','Moira','Tessa','Fiona','Fred']
def text_to_speech_voices_comparison(text="Hello world",time_per_voice=2,voices=text_to_speech_voices_favorites + shuffled(text_to_speech_voices_all)):
    # Will cycle through different voices so you can choose which one you like best. I selected my favorite voices to be the beginning, and it will cycle through all available voices by the end.
    for voice in voices:
        print("Voice: " + voice)
        text_to_speech(text=text,voice=voice,run_as_thread=True)
        sleep(time_per_voice)
def text_to_speech(text: str,voice: str = None,run_as_thread=True):
    # An abstract combination of the other two text-to-speech methods that automatically selects the right one depending on platform compatiability/whether you specified a compatiable voice etc.
    # Feel free to add more methods into this one: This is what makes the r module so generalizable.
    if run_as_thread:
        run_as_new_thread(text_to_speech,text=text,voice=voice,run_as_thread=False)
    else:
        kwargs=dict(text=text,run_as_thread=False)
        if voice is not None:
            if voice.lower() == 'random':  # A little tidbit i decided to throw in
                voice=random_element(text_to_speech_voices_favorites)
            kwargs['voice']=voice
        try:
            text_to_speech_via_apple(**kwargs)
        except:
            text_to_speech_via_google(**kwargs)
# endregion
# region Audio/Sound Functions: ［load_sound_file，play_sound_from_samples，play_sound_file，play_sound_file_via_afplay，play_sound_file_via_pygame，stop_sound，mp3_to_wav］
try:
    import sounddevice
except:
    pass
try:
    import pygame
except:
    pass

def load_sound_file(file_path: str,samplerate_adjustment=False,override_extension: str = None) -> np.ndarray:
    # Opens sound files and turns them into numpy arrays! Unfortunately right now it only supports mp3 and wav files.
    # Supports only .mp3 and .wav files.
    # samplerate_adjustment:
    # If true, your sound will be re-sampled to match the Đ_samplerate.
    # If false, it will leave it as-is.
    # If it'_s None, this function will output a tuple containing (the original sound, the original samplerate)
    # Otherwise, it should be a number representing the desired samplerate it will re-sample your sound to match the given samplerate.
    # Set override_extension to either 'mp3' or 'wav' to ignore the extension of the file name you gave it. For example, using override_extension='mp3' on 'music.wav' will force it to read music as an mp3 file instead.
    if file_path.endswith(".mp3") or override_extension is not None and 'mp3' in override_extension:
        file_path=mp3_to_wav(file_path)
    else:
        assert file_path.endswith(".wav") or 'wav' in override_extension,'sound_file_to_samples: ' + file_path + " appears to be neither an mp3 nor wav file." + " Try overriding the extension?" * (override_extension is None)
    import scipy.io.wavfile as wav
    samplerate,samples=wav.read(file_path)
    try:
        samples=np.ndarray.astype(samples,float) / np.iinfo(samples.dtype).max  # ⟶ All samples ∈ [-1,1]
    except:
        pass

    if samplerate_adjustment is False:
        return samples
    if samplerate_adjustment is None:
        return samples,samplerate
    new_samplerate=Đ_samplerate if samplerate_adjustment is True else samplerate_adjustment
    if new_samplerate == samplerate:  # Don't waste time by performing unnecessary calculations.
        return samples
    from scipy.signal import resample
    length_in_seconds=len(samples) / samplerate
    new_number_of_samples=int(length_in_seconds * new_samplerate)
    return resample(samples,num=new_number_of_samples)

def save_wav(samples,path,samplerate=None) -> None:  # Usually samples should be between -1 and 1
    from scipy.io import wavfile
    if samples.dtype == np.float64:
        samples=samples.astype(np.float32)
    wavfile.write(path,samplerate or Đ_samplerate,samples)

Đ_samplerate=44100  # In (Hz ⨯ Sample). Used for all audio methods in the 'r' class.
def play_sound_from_samples(samples,samplerate=None,blocking=False,loop=False,**kwargs):
    # For stereo, use a np matrix
    # Example: psfs((x%100)/100 for x in range(100000))
    # Each sample should ∈ [-1,1] or else it will be clipped (if it wasn't clipped it would use modular arithmeti
    # c on the int16, which would be total garbage for sound)
    # Just like matlab'_s 'sound' method, except this one doesn't let you play sounds on top of one-another.
    wav_wave=np.array(np.minimum(2 ** 15 - 1,2 ** 15 * np.maximum(-1,np.minimum(1,np.matrix(list(samples)))).transpose()),dtype=np.int16)  # ⟵ Converts the samples into wav format. I tried int32 and above: None of them worked. 16-bit seems to be the highest resolution available.
    sounddevice.play(wav_wave,samplerate=samplerate or Đ_samplerate,blocking=blocking,loop=loop,**kwargs)

def play_sound_file(path):
    # THIS Function is an abstraction of playing sound files. Just plug in whatever method works on your computer into this one to make it work
    # NOTE: These functions should all run on separate threads from the main thread by default!
    try:
        from playsound import playsound
        playsound(path)# Worked on windows, but didn't work on my mac
    except:
        try:
            play_sound_file_via_afplay(path)
        except:
            play_sound_file_via_pygame(path)

def play_sound_file_via_afplay(absolute_file_path_and_name: str,volume: float = None,rate: float = None,rate_quality: float = None,parallel: bool = True,debug: bool = True):
    # Use stop_sound to stop it.
    # If parallel==False, the code will pause until the song is finished playing.
    # If parallel==True the sound is run in a new process, and returns this process so you can .terminate() it later. It lets things continue as usual (no delay before the next line of code)
    # This seems to be a higher quality playback. On the other hand, I can't figure out any way to stop it.
    # This version doesn't require any dependencies BUT doesn't work on windows and doesn't let us play .mp3 files. The new version uses pygame and DOES allow us to.
    # Only tested on my MacBook. Uses a terminal command called 'afplay' to play a sound file.
    # Might not work with windows or linux.
    command="afplay '" + absolute_file_path_and_name + "'"
    if rate is not None:
        assert rate > 0,"r.play_sound_file_via_afplay: Playback rate cannot rate=" + str(rate)
        command+=' -r ' + str(rate)
    if rate_quality is not None:
        if rate is None and debug:
            print("r.play_sound_file_via_afplay: There'_s no reason for rate_quality not to be none: rate==None, so rate_quality doesn't matter. Just sayin'. To make me shut up, turn the debug parameter in my method to True.")
        command+=' -q ' + str(rate_quality)
    if volume is not None:
        command+=' -v ' + str(volume)
    return (run_as_new_thread if parallel else run)(shell_command,command)  # If parallel==True, returns the process so we can terminate it later.

def play_sound_file_via_pygame(file_name: str,return_simple_stopping_function=True):
    # Old because it uses the pygame.mixer.sound instead of pygame.mixer.music, which accepts more file types and has more controls than this one does.
    # Though, audio and file things are weird. I'm keeping this in case the other two fail for some reason. Other than being a backup like that, this method serves no purpose.
    # noinspection PyUnresolvedReferences
    pygame.init()
    pygame.mixer.init()
    sound=pygame.mixer.Sound(file_name)
    assert isinstance(sound,pygame.mixer.Sound)
    sound.play()
    if return_simple_stopping_function:
        return sound.stop  # The 'Sound' class has only two methods: play and stop. Because we've already used the play method, the only other possible method we would want is the stop() method.
    return sound  # This version gives us a little more control; it gives us the 'play' method too. That'_s the only difference. but python doesn't tell us the method names! This gives us options to, perhaps, stop the sound later on via sound.stop()

def stop_sound():
    # Stop sounds from all sources I know of that the 'r' module can make.
    # So far I have been unsuccessful in stopping
    try:
        shell_command("killall afplay")  # Used with 'play_sound_file_via_afplay' on macs.
    except:
        pass
    # try:run_as_new_thread(shell_command,"killall com.apple.speech.speechsynthesisd")# ⟵ Works when I enter the command in terminal, but doesn't work when called from python! It'_s not very important atm though, so I'm not gonna waste time over it.
    # except:pass
    try:
        sounddevice.stop()
    except:
        pass
    try:
        pygame.mixer.stop()
    except:
        pass

_Đ_wav_output_path='r.mp3_to_wav_temp.wav'  # Expect this file to be routinely overwritten.
def mp3_to_wav(mp3_file_path: str,wav_output_path: str = _Đ_wav_output_path,samplerate=None) -> str:
    # This is a audio file converter that converts mp3 files to wav files.
    # You must install 'lame' to use this function.
    # Saves a new wav file derived from the mp3 file you gave it.
    # shell_command('lame --decode '+mp3_file_path+" "+wav_output_path)# From https://gist.github.com/kscottz/5898352
    shell_command('lame ' + str(samplerate or Đ_samplerate) + ' -V 0 -h --decode ' + mp3_file_path + " " + wav_output_path)  # From https://gist.github.com/kscottz/5898352
    return wav_output_path
# endregion
# region  Matplotlib: ［display_image，brutish_display_image，display_color_255，display_grayscale_image，line_graph，block，clf］
try:
    import matplotlib.pyplot as plt;fig=plt.figure()
except:
    pass
def display_image(image,block=False):
    plt.imshow(image)
    plt.show(block=block)
    if not block:
        plt.pause(0.0001)
def brutish_display_image(image):
    from copy import deepcopy
    image=deepcopy(image)
    for x_index,x in enumerate(image):
        for y_index,y in enumerate(x):
            for channel_index,channel in enumerate(y):
                image[x_index][y_index][channel_index]=max(0,min(1,channel))
    display_image(image)

    plt.show(block=True)
def display_color_255(*color: list):
    # noinspection PyUnresolvedReferences
    # Example: display_color_255(255,0,0)# ⟵ Displays Red
    display_image([(np.matrix(detuple(color)) / 256).tolist()])
def display_grayscale_image(matrix,pixel_interpolation_method_name: str = 'bicubic',refresh=True):
    pixel_interpolation_method_name=str(pixel_interpolation_method_name).lower()  # Note that None⟶'none'
    assert pixel_interpolation_method_name in [None,'none','nearest','bilinear','bicubic','spline16','spline36','hanning','hamming','hermite','kaiser','quadric','catrom','gaussian','bessel','mitchell','sinc','lanczos']  # These are the options. See http://stackoverflow.com/questions/14722540/smoothing-between-pixels-of-imagesc-imshow-in-matlab-like-the-matplotlib-imshow/14728122#14728122
    import matplotlib.pyplot as plt
    plt.imshow(matrix,cmap=plt.get_cmap('gray'),interpolation=pixel_interpolation_method_name)  # "cmap=plt.get_cmap('gray')" makes it show a black/white image instead of a color map.
    if refresh:
        plt.draw()
        plt.show(block=False)  # You can also use the r.block() method at any time if you want to make the plot usable.
        plt.pause(0.0001)  # This is nessecary, keep it here or it will crash. I don't know WHY its necessary, but empirically speaking it seems to be.
def line_graph(*y_values,show_dots: bool = False,clf: bool = True,y_label: str = None,x_label: str = None,use_dashed_lines: bool = False,line_color: str = None,graph_title=None,block: bool = False,background_image=None) -> None:
    # This is mainly here as a simple reference for how to create a line-graph with matplotlib.pyplot.
    # There are plenty of options you can configure for it, such as the color of the line, label of the
    # axes etc. For more information on this, see http://matplotlib.org/users/pyplot_tutorial.html
    import matplotlib.pyplot as plt
    if clf:
        plt.clf()

    def plot(values):
        kwargs={}
        if show_dots:
            # Put a dot on each point on the line-graph.
            kwargs['marker']='o'
        if use_dashed_lines:
            kwargs['linestyle']='--'
        if line_color:
            kwargs['color']=line_color  # could be 'red' 'green' 'cyan' 'blue' etc
        plt.plot(values,**kwargs)

    try:
        plot(*y_values)  # If this works, then y_values must have been a single-graph.
    except:  # y_values must have been an iterable of iterables, so we will graph each one on top of each other.
        old_hold_value=plt.ishold()
        plt.hold(True)  # This lets us plot graphs on top of each other.
        for y in y_values:
            plot(y)
        plt.hold(old_hold_value)

    if y_label:
        plt.ylabel(y_label)
    if x_label:
        plt.xlabel(x_label)
    if graph_title:
        plt.title(graph_title)

    plt.draw()
    plt.show(block=block)  # You can also use the r.block() method at any time if you want to make the plot useable.
def block(on_click=None,on_unclick=None):
    # You may specify methods you would like to overwrite here.
    # Makes the plot interactive, but also prevents python script from running until the user clicks closes the graph window.
    import matplotlib.backend_bases
    def handler(function,event_data: matplotlib.backend_bases.MouseEvent):
        args=event_data.xdata,event_data.ydata,event_data.button,event_data.dblclick
        if None not in args:
            function(*args)
    handler_maker=lambda function:lambda event:handler(function,event)
    if on_click is not None:
        assert callable(on_click)
        # def on_click(x,y,button,dblclick)
        fig.canvas.mpl_connect('button_press_event',handler_maker(on_click))
    if on_unclick is not None:
        assert callable(on_unclick)
        # def on_unclick(x,y,button,dblclick)
        fig.canvas.mpl_connect('button_release_event',handler_maker(on_unclick))
    # PLEASE NOTE THAT MORE METHODS CAN BE ADDED!!!!! A LIST OF THEM IS IN THE BELOW COMMENT:
    # - 'button_press_event'
    # - 'button_release_event'
    # - 'draw_event'
    # - 'key_press_event'
    # - 'key_release_event'

    # - 'motion_notify_event'
    # - 'pick_event'
    # - 'resize_event'
    # - 'scroll_event'
    # - 'figure_enter_event',
    # - 'figure_leave_event',
    # - 'axes_enter_event',
    # - 'axes_leave_event'
    # - 'close_event'
    plt.show(True)
def clf():
    plt.clf()
# endregion
# region Min/Max Indices/Elements:［min_valued_indices，max_valued_indices，min_valued_elements，max_valued_elements，max_valued_index，min_valued_index］
def _minmax_indices(l,f=None):
    if len(l) == 0:
        return l.copy()  # An empty list/tuple/set or whatever
    # A helper method for the min/max methods below. f is either 'min' or 'max'
    return matching_indices(f(l),l)
def min_valued_indices(l):
    # Returns the indices with the minimum-valued elements
    return _minmax_indices(l,min)
def max_valued_indices(l):
    # Returns the indices with the maximum-valued elements
    return _minmax_indices(l,max)
def min_valued_elements(l):
    # Returns the elements with the smallest values
    return gather(l,min_valued_indices(l))
def max_valued_elements(l):
    # Returns the elements with the largest values
    return gather(l,max_valued_indices(l))
def max_valued_index(l):
    return list(l).index(max(l))  # Gets the index of the maximum value in list 'l'. This is a useful def by rCode standards because it references 'l' twice.
def min_valued_index(l):
    return lambda l:list(l).index(min(l))  # Gets the index of the minimum value in list 'l'. This is a useful def by rCode standards because it references 'l' twice.
# endregion
# region  Blend≣Lerp/sign: ［blend，iblend，lerp，interp，linterp］
def blend(𝓍,𝓎,α):  # Also known as 'lerp'
    return (1 - α) * 𝓍 + α * 𝓎  # More α ⟹ More 𝓎 ⋀ Less 𝓍
def iblend(z,𝓍,𝓎):  # iblend≣inverse blend. Solves for α， given 𝓏﹦blend(𝓍,𝓎,α)
    z-=𝓍
    z/=𝓎-𝓍
    return z
def interp(x,x0,x1,y0,y1):  # 2 point interpolation
    return (x - x0) / (x1 - x0) * (y1 - y0) + y0  # https://www.desmos.com/calculator/bqpv7tfvpy
def linterp(x,l,cyclic=False):# Where l is a list or vector etc
    try:
        if cyclic:
            x%=len(l)
            l=l+[l[0]]# Don't use append OR += (which acts the same way apparently); this will mutate l!
        assert x>=0
        x0=int(np.floor(x))
        x1=int(np.ceil(x))
        if x0==x1:
            return l[int(x)]
        return blend(l[x0],l[x1],iblend(x,x0,x1))
    except IndexError as ⵁ:
        if cyclic:
            fansi_print("ERROR: r.linterp: encountered an index error; did you mean to enable the 'cyclic' parameter?",'red')
        raise ⵁ
# def sign(x):
#     return 1 if x>0 else (0 if x==0 else -1)
# endregion
# region  Gathering/Matching: ［matching_indices，gather，pop_gather］
def matching_indices(x,l,check=lambda x,y:x == y):
    # Returns the matching indices of element 'x' in list 'l'
    out=[]
    for i,y in enumerate(l):
        if check(x,y):
            out.append(i)
    return out
def gather(iterable,*indices):
    # indices ∈ list of integers
    indices=detuple(indices)
    assert is_iterable(iterable),"The 'iterable' parameter you fed in is not an iterable!"
    assert is_iterable(indices),"You need to feed in a list of indices, not just a single index.  indices == " + str(indices)
    return [iterable[i] for i in indices]  # ≣list(map(lambda i:iterable[i],indices))
def pop_gather(x,*indices):
    indices=detuple(indices)
    out=gather(x,indices)
    # Uses CSE214 definition of 'pop', in the context of popping stacks.
    # It is difficult to simultaneously delete multiple indices in a list.
    # My algorithm goes through the indices chronologically, compensating for
    # the change in indices by subtracting incrementally larger values from them
    # Example:
    #  ⮤ ⵁ = ['0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    #  ⮤ pop_gather(ⵁ,1,3,5,7,9)
    # ans = ['a', 'c', 'e', 'g', 'i']
    #  ⮤ g
    # ans = ['0', 'b', 'd', 'f', 'h']
    for a,b in enumerate(sorted(set(indices))):
        del x[b - a]
    return out
# endregion
# region  List/Dict Functions/Displays: ［list_to_index_dict，invert_dict，invert_dict，invert_list_to_dict，dict_to_list，list_set，display_dict，display_list］
def list_to_index_dict(l: list) -> dict:
    # ['a','b','c'] ⟶ {0: 'a', 1: 'b', 2: 'c'}
    return {i:v for i,v in enumerate(l)}
def invert_dict(d: dict) -> dict:
    # {0: 'a', 1: 'b', 2: 'c'} ⟶ {'c': 2, 'b': 1, 'a': 0}
    return {v:k for v,k in zip(d.values(),d.keys())}
def invert_list_to_dict(l: list) -> dict:
    # ['a','b','c'] ⟶ {'c': 2, 'a': 0, 'b': 1}
    assert len(set(l)) == len(l),'r.dict_of_values_to_indices: l contains duplicate values, so we cannot return a 1-to-1 function; and thus ∄ a unique dict that converts values to indices for this list!'
    return invert_dict(list_to_index_dict(l))
def dict_to_list(d: dict) -> list:
    # Assumes keys should be in ascending order
    return gather(d,sorted(d.keys()))
def list_set(x):
    # Similar to performing list(set(x)), except that it preserves the original order of the items.
    # You could also think of it as list_set≣remove_duplicates
    # Demo:
    #       ⮤ l=[5,4,4,3,3,2,1,1,1]
    #       ⮤ list(set(l))
    #       ans=[1,2,3,4,5]
    #       ⮤ list_set(l)  ⟵ This method
    #       ans=[5,4,3,2,1]
    from  more_itertools import unique_everseen  # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-whilst-preserving-order
    return list(unique_everseen(x))
# ――――――――――――――――――――――
# Three fansi colors (see the fansi function for all possible color names):
Đ_display_key_color=lambda x123:fansi(x123,'cyan')
Đ_display_arrow_color=lambda x123:fansi(x123,'green')
Đ_display_value_color=lambda x123:fansi(x123,'blue')
def display_dict(d: dict,key_color=Đ_display_key_color,arrow_color=Đ_display_arrow_color,value_color=Đ_display_value_color,clip_width=False,post_processor=identity,key_sorter=sorted,print_it=True) -> None:
    # Made by Ryan Burgert for the purpose of visualizing large dictionaries.
    # EXAMPLE DISPLAY:
    '''
     ⮤ display_dict({'name': 'Zed', 'age': 39, 'height': 6 * 12 + 2})
    age ⟶ 39
    height ⟶ 74
    name ⟶ Zed
    '''
    # Of course, in the console you will see the appropriate colors for each section.
    return (print if print_it else identity)((((lambda x:clip_string_width(x,max_wraps_per_line=2,clipped_suffix='………')) if clip_width else identity)(post_processor('\n'.join((key_color(key) + arrow_color(" ⟶  ") + value_color(d[key])) for key in key_sorter(d.keys()))))))  # Theres a lot of code here because we're trying to make large amounts of text user-friendly in a terminal environment. Thats why this is so complicated and possibly perceived as messy
def display_list(l: list,key_color=Đ_display_key_color,arrow_color=Đ_display_arrow_color,value_color=Đ_display_value_color,print_it=True) -> None:
    # also works with tuples etc
    return display_dict(d=list_to_index_dict(l),key_color=key_color,arrow_color=arrow_color,value_color=value_color,print_it=print_it)
# endregion
# region  'youtube_dl'﹣dependent methods: ［rip_music，rip_info］
# noinspection SpellCheckingInspection

Đ_rip_music_output_filename="rip_music_temp"
def rip_music(URL: str,output_filename: str = Đ_rip_music_output_filename,desired_output_extension: str = 'wav',quiet=False):
    # Ryan Burgert Jan 15 2017
    # Rips a music file off of streaming sites and downloads it to the default directory…
    # URL: Can take URL's from youtube, Vimeo, SoundCloud...apparently youtube_dl supports over 400 sites!!
    # output_filename: Shouldn't include an extension, though IDK if it would hurt. By default the output file is saved to the default directory.
    # desired_output_extension: Could be 'wav', or 'mp3', or 'ogg' etc. You have the freedom to choose the type of file you want to download regardless of the type of the original online file; it will be converted automatically (because youtube is a huge mess of file types)
    #   NOTE: ‘brew install ffmpeg’ (run command in terminal) is necessary for some desired_output_extension types.
    # This method returns the name of the file it created.
    # Dependency: youtube_dl  ﹙See: https://rg3.github.io/youtube-dl/﹚
    # Quiet: If this is true, then nothing will display on the console as this method downloads and converts the file.
    # NOTE: youtube_dl has MANY more cool capabilities such as extracting the title/author/cover picture of the songs…
    #   …as well as breing able to download entire play-lists at once! youtube_dl can also rip videos; which could be very useful in another context!
    # EXAMPLE: play_sound_file_via_afplay(rip_music('https://www.youtube.com/watch?v=HcgEHrwdSO4'))
    import youtube_dl
    ydl_opts= \
        {
            'format':'bestaudio/best',  # Basically, grab the highest quality that we can get.
            'outtmpl':output_filename + ".%(ext)s",  # https://github.com/rg3/youtube-dl/issues/7870  ⟵ Had to visit this because it kept corrupting the audio files: Now I know why! Don't change this line.
            'postprocessors':
                [{
                    'key':'FFmpegExtractAudio',
                    'preferredcodec':desired_output_extension,
                    # 'preferredquality': '192',
                }],
            'quiet':quiet,  # If this is not enough, you can add a new parameter, 'verbose', to make it jabber even more. You can find these parameters in the documentation of the module that contains the 'YoutubeDL' method (used in a line below this one)
            'noplaylist':True,  # only download single song, not playlist
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])
    return output_filename + "." + desired_output_extension
def rip_info(URL: str):
    # A companion method for rip_music, this will give you all the meta-data of each youtube video or vimeo or soundcloud etc.
    # It will give you this information in the form of a dictionary.
    # Known keys:
    # ［abr，acodec，age_limit，alt_title，annotations，automatic_captions，average_rating，…
    # … categories，creator，description，dislike_count，display_id，duration，end_time，ext，…
    # … extractor，extractor_key，format，format_id，formats，fps，height，id，is_live，license，…
    # … like_count，playlist，playlist_index，requested_formats，requested_subtitles，resolution，…
    # … start_time，stretched_ratio，subtitles，tags，thumbnail，thumbnails，title，upload_date，…
    # … uploader，uploader_id，uploader_url，vbr，vcodec，view_count，webpage_url，webpage_url_basename，width］
    from youtube_dl import YoutubeDL
    return YoutubeDL().extract_info(URL,download=False)
# endregion
# region  Sending and receiving emails: ［send_gmail_email，gmail_inbox_summary，continuously_scan_gmail_inbox］
from rp.r_credentials import Đ_gmail_address   # ⟵ The email address we will send emails from and whose inbox we will check in the methods below.
from rp.r_credentials import Đ_gmail_password  # ⟵ Please don't be an asshole: Don't steal this account! This is meant for free use!
Đ_max_ↈ_emails=100  # ≣ _default_max_number_of_emails to go through in the gmail_inbox_summary method.
def send_gmail_email(recipientⳆrecipients,subject: str = "",body: str = "",gmail_address: str = Đ_gmail_address,password: str = Đ_gmail_password,attachmentⳆattachments=None,shutup=False):
    # For attachmentⳆattachments, include either a single string or iterable of strings containing file paths that you'd like to upload and send.
    # param recipientⳆrecipients: Can be either a string or a list of strings: all the emails we will be sending this message to.
    # Heavily modified but originally from https://www.linkedin.com/pulse/python-script-send-email-attachment-using-your-gmail-account-singh
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    import smtplib
    emaillist=[x.strip().split(',') for x in enlist(recipientⳆrecipients)]
    msg=MIMEMultipart()
    msg['Subject']=subject
    # msg['From']='presidentstanely@gmail.com'# ⟵       I couldn't find any visible effect from keeping this active, so I decided to remove it.
    # msg['Reply-to']='ryancentralorg@gmail.com' # ⟵    I couldn't find any visible effect from keeping this active, so I decided to remove it.
    # msg.preamble='Multipart massage mushrooms.\n' # ⟵ I couldn't find any visible effect from keeping this active, so I decided to remove it.
    msg.attach(MIMEText(body))
    if attachmentⳆattachments:
        for filename in enlist(attachmentⳆattachments):
            assert isinstance(filename,str)  # These should be file paths.
            part=MIMEApplication(open(filename,"rb").read())
            part.add_header('Content-Disposition','attachment',filename=filename)  # ⟵ I tested getting rid of this line. If you get rid of the line, it simply lists the attachment as a file on the bottom of the email, …
            # … and wouldn't show (for example) an image. With it, though, the image is displayed. Also, for files it really can't display (like .py files), it will simply act as if this line weren't here and won't cause any sort of error.
            msg.attach(part)
    try:
        with smtplib.SMTP("smtp.gmail.com:587") as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_address,password)
            server.sendmail(gmail_address,emaillist,msg.as_string())
            server.close()
        if not shutup:
            print('r.send_gmail_email: successfully sent your email to ' + str(recipientⳆrecipients))
    except Exception as E:
        if not shutup:
            print('r.send_gmail_email: failed to send your email to ' + str(recipientⳆrecipients) + ". Error message: " + str(E))
# region Old version of send_gmail_email (doesn't support attachments):
"""def send_gmail_email(recipientⳆrecipients, subject:str="", body:str="",gmail_address:str=Đ_gmail_address,password:str=Đ_gmail_password,shutup=False):
    # param recipientⳆrecipients: Can be either a string or a list of strings: all the emails we will be sending this message to.
    import smtplib
    FROM = gmail_address
    TO = enlist(recipientⳆrecipients)# Original code: recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = "From: %s\nTo: %s\nSubject: %s\n\n%s\n" % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_address, password)
        server.sendmail(FROM, TO, message)
        server.close()
        if not shutup:
            print('r: send_gmail_email: successfully sent the mail')
    except:
        if not shutup:
            print( "r: send_gmail_email: failed to send mail")"""
# endregion
def gmail_inbox_summary(gmail_address: str = Đ_gmail_address,password: str = Đ_gmail_password,max_ↈ_emails: int = Đ_max_ↈ_emails,just_unread_emails: bool = True):
    # Parameters captured in this summary include the fields (for the dicts in the output list) of
    # TODO［millis，sender，receiver，subject，sender_email，sender_name］  (Just using a TODO so that it's a different color in the code so it stands out more)  (all accessed as strings, of course)
    # returns a list of dictionaries. The length of this list ﹦ the number of emails in the inbox (both read and unread).
    # max_ↈ_emails ≣ max_number_of_emails ⟹ caps the number of emails in the summary, starting with the most recent ones.
    '''Example output:
    [{'sender_email': 'notification+kjdmmk_1v73_@facebookmail.com', 'sender': '"Richard McKenna" <notification+kjdmmk_1v73_@facebookmail.com>', 'millis': 1484416777000, 'sender_name': '"Richard McKenna"', 'subject': '[Stony Brook Computing Society] 10 games in 10 days. Today\'s game is "Purple...', 'receiver': 'Stony Brook Computing Society <sb.computing@groups.facebook.com>'},
    {'sender_email': 'notification+kjdmmk_1v73_@facebookmail.com', 'sender': '"Richard McKenna" <notification+kjdmmk_1v73_@facebookmail.com>', 'millis': 1484368779000, 'sender_name': '"Richard McKenna"', 'subject': '[Stony Brook Game Developers (SBGD)] New link', 'receiver': '"Stony Brook Game Developers (SBGD)" <sbgamedev@groups.facebook.com>'},
    {'sender_email': 'no-reply@accounts.google.com', 'sender': 'Google <no-reply@accounts.google.com>', 'millis': 1484366367000, 'sender_name': 'Google', 'subject': 'New sign-in from Safari on iPhone', 'receiver': 'ryancentralorg@gmail.com'},
    {'sender_email': 'notification+kjdmmk_1v73_@facebookmail.com', 'sender': '"Richard McKenna" <notification+kjdmmk_1v73_@facebookmail.com>', 'millis': 1484271805000, 'sender_name': '"Richard McKenna"', 'subject': '[Stony Brook Computing Society] 10 games in 10 days. Today\'s game is "Jet LIfe"....', 'receiver': 'Stony Brook Computing Society <sb.computing@groups.facebook.com>'},
    {'sender_email': 'noreply@sendowl.com', 'sender': 'imitone sales <noreply@sendowl.com>', 'millis': 1484240836000, 'sender_name': 'imitone sales', 'subject': 'A new version of imitone is available!', 'receiver': 'ryancentralorg@gmail.com'}]'''
    # The following code I got of the web somewhere and modified a lot, I don't remember where though. Whatevs.
    import datetime
    import email
    import imaplib

    with imaplib.IMAP4_SSL('imap.gmail.com') as mail:
        # ptoc()
        mail.login(gmail_address,password)
        # ptoc()
        mail.list()
        # ptoc()
        mail.select('inbox')
        # ptoc()
        result,data=mail.uid('search',None,"UNSEEN" if just_unread_emails else "ALL")  # (ALL/UNSEEN)
        # ptoc()

        email_summaries=[]  # A list of dictionaries. Will be added to in the for loop shown below.
        ↈ_emails=len(data[0].split())
        for x in list(reversed(range(ↈ_emails)))[:min(ↈ_emails,max_ↈ_emails)]:
            latest_email_uid=data[0].split()[x]
            result,email_data=mail.uid('fetch',latest_email_uid,'(RFC822)')
            # result, email_data = conn.store(num,'-FLAGS','\\Seen')
            # this might work to set flag to seen, if it doesn't already
            raw_email=email_data[0][1]
            raw_email_string=raw_email.decode('utf-8')
            email_message=email.message_from_string(raw_email_string)

            # Header Details
            date_tuple=email.utils.parsedate_tz(email_message['Date'])
            if date_tuple:
                local_date=datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                # local_message_date=local_date.ctime()# formats the date in a nice readable way
                local_message_date=local_date.timestamp()  # Gets seconds since 1970
                local_message_date=int(1000 * local_message_date)  # millis since 1970
            email_from=str(email.header.make_header(email.header.decode_header(email_message['From'])))
            email_to=str(email.header.make_header(email.header.decode_header(email_message['To'])))
            subject=str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
            # noinspection PyUnboundLocalVariable
            email_summaries.append(dict(millis=local_message_date,sender=email_from,receiver=email_to,subject=subject,sender_email=email_from[1 + email_from.find('<'):-1] if '<' in email_from else email_from,sender_name=email_from[:email_from.find('<') - 1]))
            # print('\n'.join(map(str,email_summaries)))//⟵Would display all email summaries in console
    return email_summaries
def _Đ_what_to_do_with_unread_emails(x):
    # An arbitrary default as an example example so that 'continuously_scan_gmail_inbox' can be run with no arguments
    # Example: continuously_scan_gmail_inbox()
    # By default, the continuous email scan will print out the emails and also read their subjects aloud via text-to-speech. (Assumes you're using a mac for that part).
    print(x)
    text_to_speech_via_apple(x['subject'],run_as_thread=False)
    send_gmail_email(x['sender_email'],'EMAIL RECEIVED: ' + x['subject'])
def continuously_scan_gmail_inbox(what_to_do_with_unread_emails: callable = _Đ_what_to_do_with_unread_emails,gmail_address: str = Đ_gmail_address,password: str = Đ_gmail_password,max_ↈ_emails: int = Đ_max_ↈ_emails,include_old_but_unread_emails: bool = False):
    # returns a new thread that is ran constantly unless you kill it. It will constantly scan the subjects of all emails received
    #  …AFTER the thread has been started. When it received a new email, it will run the summary of that email through the
    #  …'what_to_do_with_unread_emails' method, as a triggered event. It returns the thread it's running on so you can do stuff with it later on.
    #  …Unfortunately, I don't know how to make it stop though...
    # include_old_but_unread_emails: If this is false, we ignore any emails that were sent before this method was called. Otherwise, if include_old_but_unread_emails is true, …
    #  …we look at all emails in the inbox (note: this is only allowed to be used in this context because python marks emails as 'read' when it accesses them, …
    #  …and we hard-code just_unread_emails=True in this method so thfat we never read an email twice.)
    return run_as_new_thread(_continuously_scan_gmail_inbox,what_to_do_with_unread_emails,gmail_address,password,max_ↈ_emails,include_old_but_unread_emails)
def _continuously_scan_gmail_inbox(what_to_do_with_unread_emails,gmail_address,password,max_ↈ_emails,include_old_but_unread_emails):
    # This is a helper method because it loops infinitely and is therefore run on a new thread each time.
    exclusive_millis_min=millis()

    # times=[] # ⟵ For debugging. Look at the end of the while loop block to see more.
    while True:
        tic()
        # max_millis=exclusive_millis_min
        for x in gmail_inbox_summary(gmail_address,password,max_ↈ_emails):
            assert isinstance(x,dict)  # x's type is determined by gmail_inbox_summary, which is a blackbox that returns dicts. This assertion is for type-hinting.
            if x['millis'] > exclusive_millis_min or include_old_but_unread_emails:
                #     if x['millis']>max_millis:
                #         max_millis=x['millis']
                what_to_do_with_unread_emails(x)
                # exclusive_millis_min=max_millis

                # times.append(toc())
                # line_graph(times)
                # ptoctic()# UPDATE: It's fine. Original (disproved) thought ﹦ (I don't know why, but the time here just keeps growing and growing...)
# endregion
# region Suppress/Restore all console output/warnings: ［suppress_console_output，restore_console_output，force_suppress_console_output，force_restore_console_output，force_suppress_warnings，force_restore_warnings］
# b=sys.stdout.write;sys.stdout.write=None;sys.stdout.write=b
_original_stdout_write=sys.stdout.write  # ⟵ DO NOT ALTER THIS! It will cause your code to crash.
def _muted_stdout_write(x: str):
    assert isinstance(x,str)  # ⟵ The original method only accepts strings.
    return len(x)  # ⟵ The original method returns the length of the string; I don't know why. '
_console_output_level=1
def suppress_console_output():  # Will turn off ALL console output until restore_console_output() is called.
    global _console_output_level
    _console_output_level-=1
    if _console_output_level < 1:
        sys.stdout.write=_muted_stdout_write
def restore_console_output():  # The antidote for suppress_console_output
    global _console_output_level
    _console_output_level+=1
    if _console_output_level >= 1:
        sys.stdout.write=_original_stdout_write
def force_suppress_console_output():  # Will turn off ALL console output until restore_console_output() is called.
    global _console_output_level
    _console_output_level=0
    sys.stdout.write=_muted_stdout_write
def force_restore_console_output():
    global _console_output_level
    _console_output_level=1
    sys.stdout.write=_original_stdout_write
import warnings
def force_suppress_warnings():
    warnings.filterwarnings("ignore")
def force_restore_warnings():
    warnings.filterwarnings("default")
# def toggle_console_output ⟵ I was going to implement this, but then decided against it: it could get really annoying/confusing if used often.
# endregion
# region Ryan's Inspector: ［rinsp］
def get_bytecode(obj):
    import dis
    return dis.Bytecode(lambda x:x + 1).dis()
_rinsp_temp_object=None
def rinsp(object,search_or_show_documentation:bool=False,show_source_code:bool=False,show_summary: bool = False,max_str_lines: int = 5) -> None:  # r.inspect
    # This method is really uglily written because I made no attempt to refactor it. But it works and its really useful.
    # search_or_show_documentation: If this is a string, it won't show documentation UNLESS show_source_code ⋁ show_summary. BUT it will limit dir⋃dict to entries that contain search_or_show_documentation. Used for looking up that function name you forgot.

    """
    rinsp report (aka Ryan's Inspection):
    	OBJECT: rinsp(object, show_source_code=False, max_str_lines:int=5)
    	TYPE: class 'function'
    	FROM MODULE: module '__main__' from '/Users/Ryan/PycharmProjects/RyanBStandards_Python3.5/r.py'
    	STR: <function rinsp at 0x109eb10d0>"""
    search_filter=isinstance(search_or_show_documentation,str) and search_or_show_documentation or ''
    if search_filter:
        search_or_show_documentation=False or show_source_code or show_summary
    import inspect as i
    tab='   '
    colour='cyan'
    col=lambda x:fansi(x,colour,'bold')
    ⵁ=col('rinsp report (aka Ryan\'s Inspection):\n' + tab + 'OBJECT: ')
    try:
        ⵁ+=object.__name__
    except Exception as e:
        ⵁ+='[cannot obtain object.__name__ without error: ' + str(e) + ']'
    try:
        ⵁ+=str(i.signature(object))
    except:
        pass
    print(ⵁ)
    try:
        temp=object
        from types import ModuleType
        if isinstance(object,ModuleType) and get_subpackages(object):
            print(col(tab + "SUBPACKAGES: ")+(', '.join(get_subpackages(object))),end="\n",flush=False)  # If we can't get the dict of (let's say) a numpy array, we get the dict of it's type which gives all its parameters' names, albeit just their defgault values.
        try:  # noinspection PyStatementEffect
            object.__dict__
            print(col(tab + "DIR⋃DICT: "),end="",flush=False)
        except:
            temp=type(object)
            print(col(tab + "DIR⋃TYPE.DICT: "),end="",flush=False)  # If we can't get the dict of (let's say) a numpy array, we get the dict of it's type which gives all its parameters' names, albeit just their defgault values.
        dict_used=set(temp.__dict__)
        dict_used=dict_used.union(set(dir(object)))
        d=dict_used
        if search_filter:
            print(fansi(tab + "FILTERED: ",'yellow','bold'),end="",flush=False)
            d={B for B in d if search_filter in B}
        def sorty(d):
            A=sorted([x for x in d if x.startswith("__") and x.endswith("__")])  # Moving all built-ins and private variables to the end of the list
            B=sorted([x for x in d if x.startswith("_") and not x.startswith("__") and not x.endswith("__")])
            C=sorted(list(set(d) - set(A) - set(B)))
            return C + B + A
        dict_used=sorty(d)
        if len(dict_used) != 0:
            global _rinsp_temp_object
            _rinsp_temp_object=object
            attrs={}
            for attrname in dict_used:
                try:
                    attrs[attrname]=(eval('_rinsp_temp_object.' + attrname))
                except:
                    attrs[attrname]=(fansi("ERROR: Cannot evaluate",'red'))
            def color(attr):
                try:
                    attr=eval('_rinsp_temp_object.' + attr)  # callable(object.__dir__.__get__(attr))
                except:
                    return 'red','bold'
                if callable(attr):
                    return 'green',  # Green if callable
                return [None]  # Plain and boring if else
            dict_used_with_callables_highlighted_green=[fansi(x,*color(x)) for x in dict_used]
            print(str(len(dict_used)) + ' things: [' + ', '.join(dict_used_with_callables_highlighted_green) + "]")  # Removes all quotes in the list so you can rad ) +" ⨀ ⨀ ⨀ "+str(dict_used).replace("\n","\\n"))
        else:
            print(end="\r")  # Erase the previous line (aka "DICT: " or "TYPE.DICT: ")
    except:
        pass
    print(col(tab + "TYPE: ") + str(type(object))[1:-1])
    if i.getmodule(object) is not None:
        print(col(tab + "FROM MODULE: ") + str(i.getmodule(object))[1:-1])
    def errortext(x):
        return fansi(x,'red','underlined')
    def linerino(x):
        number_of_lines=x.count("\n") + 1
        return '\n'.join(x.split('\n')[:max_str_lines]) + (fansi("\n" + tab + "\t………continues for " + str(number_of_lines - max_str_lines) + " more lines………",colour) if (number_of_lines > max_str_lines + 1) else "")  # max_str_lines+1 instead of just max_str_lines so we dont get '………continues for 1 more lines………'
    try:
        # GETTING CHARACTER FOR TEMP
        print(col(tab + "STR: ") + linerino(str(object)))
    except:
        pass
    if show_summary:
        def to_str(x):
            if x is None:
                return str(x)

            outtype='str()'
            out=str(x)
            if out and out[0] == '<' and out[-1] == '>':
                out=x.__doc__
                if out is None:
                    try:
                        out=i.getcomments(object)
                        outtype='doc()'
                    except:
                        out=str(out)
                        outtype='str()'
                else:
                    outtype='doc()'

            typestr=str(type(x))
            if typestr.count("'") >= 2:
                typestr=typestr[typestr.find("'") + 1:]
                typestr=typestr[:typestr.find("'")]
            elif typestr.count('"') >= 2:
                typestr=typestr[typestr.find('"') + 1:]
                typestr=typestr[:typestr.find('"')]

            out=fansi('[' + typestr + " : " + outtype + "]",'green') + " " + fansi(out,'blue')
            if '\n' in out:
                indent_prefix=''  # '···'
                out='\n'.join((indent_prefix + x) for x in out.split('\n'))
                while '\n\n' in out:
                    out=out.replace('\n\n','\n')
                out=linerino(out)
                out=out.lstrip()
                out=out.rstrip()
            return out
        print(col(tab + "SUMMARY:"))
        display_dict(attrs,key_sorter=sorty,value_color=to_str,arrow_color=lambda x:fansi(x,'green'),key_color=lambda x:fansi(x,'green','bold'),clip_width=True,post_processor=lambda x:'\n'.join(2 * tab + y for y in x.split('\n')))
    if show_source_code:
        print(col(tab + "SOURCE CODE:") + fansi("―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――",'cyan','blinking'))
        ⵁ=code_string_with_comments=''
        ⵁ+=i.getcomments(object) or ''  # ≣i.getc omments(object) if i.getcomments(object) is not None else ''
        ⵁ=fansi_syntax_highlighting(ⵁ)
        try:
            ⵁ+=fansi_syntax_highlighting(str(i.getsource(object)))

        except Exception as e:
            ⵁ+=2 * tab + errortext('[Cannot retrieve source code! Error: ' + linerino(str(e)) + "]")
        print(ⵁ)
    if search_or_show_documentation:
        print(col(tab + "DOCUMENTATION: "))
        try:
            if object.__doc__ and not object.__doc__ in ⵁ:
                print(fansi(str(object.__doc__),'gray'))
            else:
                if not object.__doc__:
                    print(2 * tab + errortext("[__doc__ is empty]"))
                else:  # ∴ object.__doc__ in ⵁ
                    print(2 * tab + errortext("[__doc__ can be found in source code, which has already been printed]"))
        except Exception as e:
            print(2 * tab + errortext("[Cannot retrieve __doc__! Error: " + str(e) + "]"))
# endregion
# region Arduino: ［arduino，read_line］
def arduino(baudrate: int = 115200,port_description_keywords:list=['arduino','USB2.0-Serial'],timeout: float = .1,manually_chosen_port: str = None,shutup: bool = False,return_serial_instead_of_read_write=False,marco_polo_timeout=0) -> (callable,callable):# 'USB2.0-Serial' is for a cheap knock-off arduino I got
    # Finds an arduino, connects to it, and returns the read/write methods you use to communicate with it.
    # Example: read,write=arduino()
    # read() ⟵ Returns a single byte (of length 1)
    # write(x:bytes) ⟵ Writes bytes to the arduino, which reads them as individual characters (the 'char' primitive)
    # If you don't want this method to automatically locate an arduino, set manually_chosen_port to the port name you wish to connect to.
    # marco_polo_timeout is optional: It's used for a situation where the arduino responds marco-polo style with the python code
    '''
    //Simple example code for the arduino to go along with this method: It simply parrots back the bytes you write to it.
    void setup()
    {
      Serial.begin(115200);// set the baud rate
    }
    void loop()
    {
      if (Serial.available())// only send data back if data has been sent
      {
        char inByte = Serial.read(); // read the incoming data
        Serial.write(inByte); // send the data back as a single byte.
      }
    }
    '''
    import serial
    def speak(x: str) -> None:
        if not shutup:
            print("r.arduino: " + x)
    def find_arduino_port(keywords: list = port_description_keywords) -> str:
        # Attempts to automatically determine which port the arduino is on.
        import serial.tools.list_ports
        port_list=serial.tools.list_ports.comports()
        port_descriptions=[port.description for port in port_list]
        keyword_in_port_descriptions=[any(keyword.lower() in port_description.lower()for keyword in keywords) for port_description in port_descriptions]
        number_of_arduinos_detected=sum(keyword_in_port_descriptions)
        assert number_of_arduinos_detected > 0,'r.arduino: No arduinos detected! Port descriptions = ' + str(port_descriptions)
        arduino_port_indices=max_valued_indices(keyword_in_port_descriptions)  # All ports that have 'arduino' in their description.
        if number_of_arduinos_detected > 1:
            speak("Warning: Multiple arduinos detected. Choosing the leftmost of these detected arduino ports: " + str(gather(port_descriptions,arduino_port_indices)))
        chosen_arduino_device=port_list[arduino_port_indices[0]]
        speak("Chosen arduino device: " + chosen_arduino_device.device)
        return chosen_arduino_device.device
    ser=serial.Serial(manually_chosen_port or find_arduino_port(),baudrate=baudrate,timeout=timeout)  # Establish the connection on a specific port. NOTE: manually_chosen_port or find_arduino_port() ≣ manually_chosen_port if manually_chosen_port is not None else find_arduino_port()
    if return_serial_instead_of_read_write:
        return ser
    read_bytes,_write_bytes=ser.read,ser.write  # NOTE: If read_bytes()==b'', then there is nothing to read at the moment.
    def write_bytes(x,new_line=False):
        _write_bytes(printed((x if isinstance(x,bytes) else str(x).encode())+(b'\n'if new_line else b'')))
    start=tic()
    # (next 4 lines) Make sure that the arduino is able to accept write commands before we release it into the wild (the return function):
    arbitrary_bytes=b'_'  # It doesn't matter what this is, as long as it's not empty
    assert arbitrary_bytes != b''  # ⟵ This is the only requirement for that read_bytes must be.
    if marco_polo_timeout:
        while not read_bytes() and start()<marco_polo_timeout: write_bytes(arbitrary_bytes)  # ≣ while read_bytes()==b''
        while read_bytes() and start()<marco_polo_timeout: pass  # ≣ while read_bytes()!=b''. Basically the idea is to clear the buffer so it's primed and ready-to-go as soon as we return it.
        if start()>marco_polo_timeout and not shutup:
            print("Marco Polo Timed Out")
    speak("Connection successful! Returning read and write methods.")
    return read_bytes,write_bytes  # Returns the methods that you use to read and write from the arduino
    # NOTE: read_bytes() returns 1 byte; but read_byte(n ∈ ℤ) returns n bytes (all in one byte―string)!
    # Future: Possibly helpful resources: http://stackoverflow.com/questions/24420246/c-function-to-convert-float-to-byte-array  ⨀ ⨀ ⨀   http://forum.arduino.cc/index.php?topic=43222.0
def read_line(getCharFunction,return_on_blank=False) -> bytes:
    # Example: read,write=arduino();print(read_line(read))
    f=getCharFunction
    t=tic()
    o=b''
    while True:
        n=new=f()
        if n == b'\n' or return_on_blank and n == b'':
            return o
        o+=n
# endregion
# region Webcam: ［load_image_from_webcam］
_cameras=[]
def _initialize_cameras():
    if _cameras:
        return  # Allready initialized
    fansi_print("r._initialize_cameras: Initializing camera feeds; this will take a few seconds...",'green',new_line=False)
    # noinspection PyUnresolvedReferences
    from cv2 import VideoCapture
    i=0
    while True:
        cam=VideoCapture(i)
        if not cam.read()[0]:
            break
        _cameras.append(cam)
        fansi_print("\rr._initialize_cameras: Added camera #" + str(i),'green',new_line=False)
        i+=1
    fansi_print("\rr._initialize_cameras: Initialization complete!",'green')
def load_image_from_webcam(webcam_index: int = 0,shutup=False):
    # Change webcam_index if you have multiple cameras
    # EX: while True: display_image(med_filter(load_image_from_webcam(1),σ=0));sleep(0);clf()#⟵ Constant webcam display
    _initialize_cameras()
    # _,img=_cameras[webcam_index].read()
    # if webcam_index>=_cameras.__len__():
    #     if not shutup:
    #         print("r.load_image_from_webcam: Warning: Index is out of range: webcam_index="+str(webcam_index)+" BUT len(_cameras)=="+str(len(_cameras))+", setting webcam_index to 0")
    #     webcam_index=0
    img=np.add(_cameras[webcam_index].read()[1],0)  # Turns it into numpy array
    img=np.add(img,0)  # Turns it into numpy array
    x=img + 0  # Making it unique/doesnt mutate img
    img[:,:,0],img[:,:,2]=x[:,:,2],x[:,:,0]

    return img
# endregion
# region  Audio Recording: ［record_mono_audio］
Đ_audio_stream_chunk_size=1024  # chunk_size determines the resolution of time_in_seconds as the samplerate. Look in the code for more explanation idk how to describe it.
Đ_audio_mono_input_stream=None  # Initialized in the record_mono_audio function
def record_mono_audio(time_in_seconds,samplerate=Đ_samplerate,stream=None,chunk_size=Đ_audio_stream_chunk_size) -> np.ndarray:
    # You can count on this method having a delay (between when you call the method and when it actually starts recording) on the order of magnitude of 10⁻⁵ seconds
    # PLEASE NOTE: time_in_seconds is not interpreted precisely
    # EXAMPLE: play_sound_from_samples(record_mono_audio(2))
    if stream is None:  # then use Đ_audio_mono_input_stream instead
        global Đ_audio_mono_input_stream
        if Đ_audio_mono_input_stream is None:  # Initialize it.
            import pyaudio  # You need this module to use this function. Download it if you don't have it.
            Đ_audio_mono_input_stream=pyaudio.PyAudio().open(format=pyaudio.paInt16,channels=1,rate=Đ_samplerate,input=True,frames_per_buffer=Đ_audio_stream_chunk_size)
        stream=Đ_audio_mono_input_stream
    number_of_chunks_needed=np.ceil(time_in_seconds * samplerate / chunk_size)  # Rounding up.
    out=np.hstack([np.fromstring(stream.read(num_frames=chunk_size,exception_on_overflow=False),dtype=np.int16) for _ in [None] * int(number_of_chunks_needed)])  # Record the audio
    out=np.ndarray.astype(out,float)  # Because by default it's an integer (not a floating point thing)
    out/=2 ** 15  # ⟹ ∈［﹣1，1］ because we use pyaudio.paInt16. I confirmed this by banging on the speaker loudly and seeing 32743.0 as the max observed value.  ﹙# out/=max([max(out),-min(out)]) ⟵ originally this﹚
    # stream.stop_stream();stream.close() ⟵ Is slow. Takes like .1 seconds. I profiled this method so that it runs very, very quickly (response time is about a 1% of a millisecond)
    return out
# endregion
# region MIDI Input/Output: ［MIDI_input，MIDI_output］
__midiout=None
def MIDI_output(message: list):
    """
    Key:
    NOTE_OFF = [0x80, note, velocity]
    NOTE_ON = [0x90, note, velocity]
    POLYPHONIC_PRESSURE = [0xA0, note, velocity]
    CONTROLLER_CHANGE = [0xB0, controller, value]
    PROGRAM_CHANGE = [0xC0, program]
    CHANNEL_PRESSURE = [0xD0, pressure]
    PITCH_BEND = [0xE0, value-lo, value-hi]
    For more: see http://pydoc.net/Python/python-rtmidi/0.4.3b1/rtmidi.midiconstants/
    """
    try:
        # Can control applications like FL Studio etc
        # Use this for arduino etc
        global __midiout
        if not __midiout:
            import rtmidi  # pip3 install python-rtmidi
            __midiout=rtmidi.MidiOut()
            available_ports=__midiout.get_ports()
            if available_ports:
                __midiout.open_port(0)
                print("r.MIDI_output: Port Output Name: '" + __midiout.get_ports()[0])
            else:
                __midiout.open_virtual_port("My virtual output")
        __midiout.send_message(message)  # EXAMPLE MESSGES: # note_on = [0x90, 98, 20] # channel 1, middle C, velocity 112   note_off = [0x80, 98, 0]
    except OverflowError as e:
        fansi_print("ERROR: r.MIDI_Output: " + str(e) + ": ",'red',new_line=False)
        fansi_print(message,'cyan')
def MIDI_control(controller_number: int,value: float):  # Controller_number is custom integer, and value is between 0 and 1
    MIDI_output([176,controller_number,int(float_clamp(value,0,1) * 127)])
def MIDI_control_precisely(coarse_controller_number: int,fine_controller_number: int,value: float):  # TWO bytes of data!!
    value=float_clamp(value,0,1)
    value*=127
    MIDI_output([176,coarse_controller_number,int(value)])
    MIDI_output([176,fine_controller_number,int((value % 1) * 127)])
def MIDI_jiggle_control(controller_number: int):  # Controller_number is custom integer, and value is between 0 and 1
    MIDI_control(controller_number,0)
    sleep(.1)
    MIDI_control(controller_number,1)
def MIDI_note_on(note: int,velocity: float = 1):  # velocity ∈ ［0，1］
    MIDI_output([144,int_clamp(note,0,255),int(velocity * 127)])  # Notes can only be between 0 and 255, inclusively
def MIDI_note_off(note: int,velocity: float = 0):
    MIDI_output([128,note,int(velocity * 127)])
MIDI_pitch_bend_min=-2  # Measured in Δsemitones.
MIDI_pitch_bend_max=6  # Note: These min/max numbers are Based on the limitations of the pitch bender, which is DAW dependent. This is what it appears to be in FL Studio on my computer. Note that these settings
def MIDI_pitch_bend(Δsemitones: float):  # Δsemitones ∈ [-2,6] ⟵ ACCORDING TO FL STUDIO
    Δsemitones=float_clamp(Δsemitones,MIDI_pitch_bend_min,MIDI_pitch_bend_max)
    coarse=int(((Δsemitones + 2) / 8) * 255)
    fine=0  # ∈ [0,255] Note that fine is...REALLY REALLY FINE...So much so that I can't really figure out a good way to use it
    MIDI_output([224,fine,coarse])
def MIDI_all_notes_off():
    for n in range(256):
        MIDI_note_off(n)
def MIDI_breath(value: float):
    MIDI_output([0x02,int(float_clamp(value,0,1) * 127)])
#
__midiin=None  # This variable exists so the garbage collector doesn't gobble up your midi input if you decide not to assign a variable to the output (aka the close method)
def MIDI_input(ƒ_callback: callable = print) -> callable:
    # Perfect example:
    # close_midi=MIDI_input(MIDI_output) # ⟵ This simply regurgitates the midi-piano's input to a virtual output. You won't be able to tell the difference ;)
    # Then, when you're bored of it...
    # close_midi()# ⟵ This stops the midi from doing anything.
    print("r.MIDI_input: Please specify the details of your request:")
    from rtmidi.midiutil import open_midiport  # pip3 install python-rtmidi
    global __midiin
    __midiin,port_name=open_midiport()
    __midiin.set_callback(lambda x,y:ƒ_callback(x[0]))
    return __midiin.close_port  # Returns the method needed to kill the thread
# endregion
# region  Comparators: ［cmp_to_key，sign］
def cmp_to_key(mycmp):
    # From: http://code.activestate.com/recipes/576653-convert-a-cmp-function-to-a-key-function/
    # Must use for custom comparators in the 'sorted' builtin function!
    # Instead of using sorted(ⵁ,cmp=x) which gives syntax error, use…
    # …sorted(ⵁ,key=cmp_to_key(x))
    # I.E., in rCode:
    #       sorted(ⵁ,cmp=x) ⭆ sorted(ⵁ,key=cmp_to_key(x))   ≣   cmp=x ⭆ key=cmp_to_key(x)
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self,obj,*args): self.obj=obj
        def __lt__(self,other): return mycmp(self.obj,other.obj) < 0
        def __gt__(self,other): return mycmp(self.obj,other.obj) > 0
        def __eq__(self,other): return mycmp(self.obj,other.obj) == 0
        def __le__(self,other): return mycmp(self.obj,other.obj) <= 0
        def __ge__(self,other): return mycmp(self.obj,other.obj) >= 0
        def __ne__(self,other): return mycmp(self.obj,other.obj) != 0
    return K


    # noinspection PyShadowingNames
def sign(x,zero=0):
    # You can redefine zero depending on the context. It basically becomes a comparator.
    if x > zero:
        return 1
    elif x < zero:
        return -1
    return zero
# endregion
# region  Pickling:［load_pickled_value，save_pickled_value］
import pickle
# Pickling is just a weird name the python devs came up with to descript putting the values of variables into files, essentially 'pickling' them for later use
def load_pickled_value(file_name: str):
    # Filenames are relative to the current file path
    pickle.load(open(file_name,"rb"))
def save_pickled_value(file_name: str,*variables):
    # Filenames are relative to the current file path
    pickle.dump(detuple(variables),open(file_name,'wb'))
    # load_pickled_value=lambda file_name:pickle.load(open(file_name,"rb"))
# endregion
# region  .txt ⟷ str: ［string_to_text_file，text_file_to_string］
def string_to_text_file(file_path: str,string: str,) -> None:
    file=open(file_path,"w")
    try:
        file.write(string)
    except:
        file=open(file_path,"w",encoding='utf-8')
        file.write(string,)

    file.close()
def text_file_to_string(file_path: str) -> str:
    # file=open(file_path,"r")
    # try:
    #     return file.read()
    # except Exception as e:
    #     print_stack_trace()
    # finally:
    #     file.close()
    return open(file_path).read()
# endregion
# region MATLAB Integration: ［matlab_session，matlab，matlab_pseudo_terminal］
def matlab_session(matlabroot: str = '/Applications/MATLAB_R2016a.app/bin/matlab',print_matlab_stdout: bool = True):  # PLEASE NOTE: this 'matlabroot' was created on my Macbook Pro, and is unlikely to work on your computer unless you specify your own matlab path!
    # This method is used as an easy-to-use wrapper for creating MATLAB sessions using the pymatbridge module
    # Worth noting: There's a legit purpose for creating a new matlab session before using it:
    #   Each session you create will be separate and will have a separate namespace!
    #   In other words, you can run them simultaneously/separately. For example:
    #         ⮤ sess1=matlab_session();sess2=matlab_session();
    #         ⮤ sess1.run_code("x=1");sess2.run_code("x=1");
    #         ⮤ sess1.get_variable("x"),sess2.get_variable("x")
    #         ans=(1,2)
    # Also worth noting: You can use whatever functions you normally use in MATLAB, including .m files that you wrote and kept in your default matlab function/script saving directory.
    fansi_print("(A message from Ryan): About to try connecting to MATLAB. Please be a patient, this can take a few seconds! (There is a timeout though, so you won't be kept waiting forever if it fails). Another message will be printed when it's done loading.",None,'bold')
    import pymatbridge  # pip3 install pymatbridge     (see https://arokem.github.io/python-matlab-bridge/ )
    session=pymatbridge.Matlab(executable=matlabroot,maxtime=60)  # maxtime=60⟹Wait 1 minute to get a connection before timing out. I got this 'matlabroot' parameter by running "matlabroot" ﹙without quotes﹚in my Matlab IDE (and copy/pasting the output)
    session.start()  # If wait_for_matlab_to_load is true, then this method won't return anything until it'_s made a connection, which will time out if it takes more than max_loading_time_before_giving_up_in_seconds seconds.
    assert session.is_connected(),'(A message from Ryan): MATLAB failed to connect! (So we gotta stop here). I made this assertion error to prevent any further confusion if you try to write methods that use me. If I get too annoying, feel free to delete me (the assertion). \n' \
                                  'Troubleshooting: Perhaps the path you specified in the "matlabroot" argument of this method isn\'t really your matlab root? See the comments in this method for further information.'

    print_matlab_stdout=[print_matlab_stdout]  # Turn the value into a list make it mutable
    def handle_matlab_stdout(x: dict):
        # x will look something like this: ans = {'result': [], 'success': True, 'content': {'datadir': '/private/tmp/MatlabData/', 'stdout': 'a =\n     5\n', 'figures': []}}
        nonlocal print_matlab_stdout
        is_error=not x['success']  # Is a boolean.
        if print_matlab_stdout[0]:
            if is_error:
                fansi_print("MATLAB ERROR: ",'red','bold',new_line=False)
            fansi_print(x['content']['stdout'],'red' if is_error else'gray')
        else:
            return x  # If we're not printing out the output, we give them ALL the data
    def wrapper(code: str = '',**assignments):
        assert isinstance(code,str),'The "Code" parameter should always be a string. If you wish to assign values to variables in the MATLAB namespace, use this method\'_s kwargs instead.'
        assert len(assignments) == 1 or not assignments,'Either one variable assignment or no variable assignments.'
        assert not (code and assignments),'You should either use this method as a way to get values/execute code, XOR to assign variables to non-strings like numpy arrays. NOT both! That could be very confusing to read, and make it difficult for new people to learn how to use this function of the r class. NOTE: This method limits you to a single variable assignment because sessions returns things when you do that, and this wrapper has to return that output. '
        # Note that code and va can be used like booleans, because we know that code is a string and we know that va is a dict that has string-based keys (because of the nature of kwargs).
        nonlocal session,handle_matlab_stdout
        if code:
            eval_attempt=session.get_variable(code)
            return handle_matlab_stdout(session.run_code(code)) if eval_attempt is None else eval_attempt  # If eval_attempt is None, it means MATLAB didn't return a value for the code you gave it (like saying disp('Hello World')), or resulted in an error or something (like saying a=1/0).
        if assignments:
            for var_name in assignments:
                return handle_matlab_stdout(session.set_variable(var_name,assignments[var_name]))
        return session  # If we receive no arguments, return the raw session (generated by the pymatbridge module).

    session.print_matlab_stdout=[print_matlab_stdout]  # A list to make it mutable
    def enable_stdout():  # Enables the pseudo-matlab to print out, on the python console, what a real matlab would print.
        nonlocal print_matlab_stdout
        print_matlab_stdout[0]=True
    def disable_stdout():
        nonlocal print_matlab_stdout
        print_matlab_stdout[0]=False
    wrapper.disable_stdout=disable_stdout
    wrapper.enable_stdout=enable_stdout
    wrapper.reboot=lambda *_:[fansi_print("Rebooting this MATLAB session...",None,'bold'),session.stop(),session.start(),fansi_print("...reboot complete!",None,'bold')] and None  # wrapper.reboot() in case you accidentally call an infinite loop or something
    wrapper.stop=session.stop  # I put this here explicitly, so you don't have to hunt around before figuring out that wrapper().stop() does the same thing as (what now is) wrapper.stop()
    wrapper.start=session.start  # This exists for the same reason that the one above it exists.

    return wrapper

_static_matlab_session=matlab_disable_stdout=matlab_enable_stdout=matlab_reboot=matlab_stop=matlab_start=None  # Should be None by default. This is the default Matlab session, which is kept in the r module.
# noinspection PyUnresolvedReferences
def _initialize_static_matlab_session():
    global _static_matlab_session,matlab_disable_stdout,matlab_enable_stdout,matlab_reboot,matlab_stop,matlab_start
    _static_matlab_session=matlab_session()
    matlab_disable_stdout=_static_matlab_session.disable_stdout
    matlab_enable_stdout=_static_matlab_session.enable_stdout
    matlab_reboot=_static_matlab_session.reboot
    matlab_stop=_static_matlab_session.stop
    matlab_start=_static_matlab_session.start
# noinspection PyUnresolvedReferences
def matlab(*code,**assignments):  # Please note: you can create simultaneous MATLAB sessions by using the matlab_session method!
    # This method seriously bends over-back to make using matlab in python more convenient. You don't even have to create a new session when using this method, it takes care of that for you ya lazy bastard! (Talking about myself apparently...)
    global _static_matlab_session,matlab_disable_stdout,matlab_enable_stdout,matlab_reboot,matlab_stop,matlab_start
    if _static_matlab_session is None:
        fansi_print("r.matlab: Initializing the static matlab session...",None,'bold')
        _initialize_static_matlab_session()
    return _static_matlab_session(*code,**assignments)

def matlab_pseudo_terminal(pseudo_terminal):  # Gives a flavour to a given pseudo_terminal function
    # Example usage: matlab_pseudo_terminal(pseudo_terminal)
    _initialize_static_matlab_session()
    pseudo_terminal("pseudo_terminal() ⟹ Entering interactive MATLAB console! (Running inside of the 'r' module)",lambda x:"matlab('" + x + "')")
# endregion
# region Mini-Terminal: ［mini_terminal:str］
# PLEASE READ: This is not meant to be called from the r class.
# Example usage: import r;exec(r.mini_terminal)
# Intended for use everywhere; including inside other functions (places with variables that pseudo_terminal can't reach)
mini_terminal="""#from r import fansi,fansi_print,string_from_clipboard,fansi_syntax_highlighting
_history=[]
fansi_print("Ryan's Mini-Terminal: A miniature pseudo-terminal for running inside functions!",'blue','bold')
fansi_print("\\tValid commands: ［PASTE，END，HISTORY］",'blue')
while True:
    _header="⟶ "
    _s=input(fansi(_header,'cyan','bold')).replace(_header,"").lstrip()
    if not _s:
        continue
    if _s == "PASTE":
        fansi_print("PASTE ⟶ Entering command from clipboard",'blue')
        _s=string_from_clipboard()
    if _s == 'END':
        fansi_print("END ⟶ Ending mini-terminal session",'blue')
        break
    elif _s == 'HISTORY':
        fansi_print("HISTORY ⟶ Printing out list of commands you entered that didn't cause errors",'blue')
        fansi_print(fansi_syntax_highlighting('\\n'.join(_history)))
    else:
        try:
            _temp=eval(_s)
            if _temp is not None:
                _ans=_temp
                fansi_print('_ans = ' + str(_ans),'green')
            _history.append(_s)
        except:
            try:
                exec(_s)
                _history.append(_s)
            except Exception as _error:
                print(fansi("ERROR: ",'red','bold') + fansi(_error,'red'))"""
# endregion
# region socketWrapper: ［socket_writer，socket_reader，socket_read，socket_write，socket_reading_thread，get_my_ip］
Đ_socket_port=13000
_socket_writers={}# A whole bunch of singletons
def socket_writer(targetIP: str,port: int = None):
    if (targetIP,port) in _socket_writers:
        return _socket_writers[(targetIP,port)]
    from socket import AF_INET,SOCK_DGRAM,socket
    # Message Sender
    host=targetIP  # IP address of target computer. Find yours with print_my_ip
    port=port or Đ_socket_port
    addr=(host,port)
    UDPSock=socket(AF_INET,SOCK_DGRAM)  # UDPSock.close()
    def write(asciiData: str):
        UDPSock.sendto(str(asciiData).encode("ascii"),addr)
    write.targetIP=targetIP# A bit of decorating...
    write.port=port# A bit of decorating...
    _socket_writers[(targetIP,port)]=write
    assert socket_writer(targetIP,port) is write  # Should have been added to _socket_writers
    return write
def socket_write(targetIP,port,message):
    socket_writer(targetIP,port)(message)# Takes advantage of the singleton structure of _socket_writers
_socket_readers={}# A whole bunch of singletons
def socket_reader(port: int = None):# Blocks current thread until it gets a response
    if port in _socket_readers:
        return _socket_readers[port]
    # Message Receiver
    from socket import AF_INET,socket,SOCK_DGRAM
    host=""
    port=port or Đ_socket_port
    buf=1024
    addr=(host,port)
    UDPSock=socket(AF_INET,SOCK_DGRAM)  # UDPSock.close()
    UDPSock.bind(addr)
    # UDPSock.close()
    def read(just_data_if_true_else_tuple_with_data_then_ip_addr:bool=True):
        data,addr=UDPSock.recvfrom(buf)
        data=data.decode("ascii")
        return data if just_data_if_true_else_tuple_with_data_then_ip_addr else (data,addr[0])# addr[0] is a string for ip. addr=tuple(string,int)
    read.port=port# A bit of decorating
    _socket_readers[port]=read
    assert socket_reader(port) is read
    return read
def socket_read(port,just_data_if_true_else_tuple_with_data_then_ip_addr:bool=True):
    return socket_reader(port)(just_data_if_true_else_tuple_with_data_then_ip_addr) # Takes advantage of the singleton structure of _socket_readers
def socket_reading_thread(handler,port:int=None,just_data_if_true_else_tuple_with_data_then_ip_addr:bool=True):
    read=socket_reader(port)
    def go():
        while True:
            handler(read(just_data_if_true_else_tuple_with_data_then_ip_addr=just_data_if_true_else_tuple_with_data_then_ip_addr))
    return run_as_new_thread(go)
def get_my_ip() -> str:
    import socket
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    try:
        return s.getsockname()[0]
    finally:
        s.close()
# endregion
# region OSC≣'Open Sound Control' Output ［OSC_output］:
Đ_OSC_port=12345
try:Đ_OSC_ip=get_my_ip()
except:pass
_OSC_client=None# This is a singleton
_OSC_values={}
def OSC_output(address,value):
    address=str(address)
    if not address[0]=='/':
        address='/'+address
    global Đ_OSC_ip
    Đ_OSC_ip=Đ_OSC_ip or get_my_ip()
    from rp.TestOSC import SimpleUDPClient
    global _OSC_client
    if not _OSC_client:
        _OSC_client=SimpleUDPClient(address=Đ_OSC_ip,port=Đ_OSC_port)
    _OSC_client.send_message(address=address,value=value)
    _OSC_values[address]=value# Attempt to keep track of them (though it might sometimes drift out of sync etc idk i haven't tested it as of writing this)
def OSC_jiggle(address):
    address=str(address)
    if address in _OSC_values:
        original_value=_OSC_values[address]
    OSC_output(address,1)
    sleep(.1)
    OSC_output(address,0)
    sleep(.1)
    if address in _OSC_values:
        # noinspection PyUnboundLocalVariable
        OSC_output(address,original_value)
# endregion
# Intended for use everywhere; including inside other functions (places with variables that pseudo_terminal can't reach)
mini_terminal_for_pythonista="""
_history=[]
print("Ryan's Mini-Terminal For Pythonista: A microscopic pseudo-terminal for running inside functions; optimized for Pythonista!")
print("\\tValid commands: ［PASTE，END，HISTORY］")
while True:
    _header=">>> "
    _s=input(_header).replace(_header,"").lstrip()
    if not _s:
        continue
    if _s == "PASTE":
        import clipboard
        print("PASTE: Entering command from clipboard",'blue')
        _s=clipboard.get()
    if _s == 'END':
        print("END: Ending mini-terminal session",'blue')
        break
    elif _s == 'HISTORY':
        print("HISTORY: Printing out list of commands you entered that didn't cause errors",'blue')
        print('\\n'.join(_history))
    else:
        try:
            _temp=eval(_s)
            if _temp is not None:
                _=_temp
                print('_ = ' + str(_))
            _history.append(_s)
        except:
            try:
                exec(_s)
                _history.append(_s)
            except Exception as _error:
                print("ERROR: " + str(_error))"""
# endregion
# Other stuff I don't know which category to put in:
def k_means_analysis(data_vectors,k_or_initial_centroids,iterations,tries):
    from scipy.cluster.vq import kmeans,vq
    centroids,total_distortion=kmeans(obs=data_vectors,k_or_guess=k_or_initial_centroids,iter=iterations)  # [0] returns a list of the centers of the means of each centroid. TRUE. [1] returns the 'distortion' ＝ ∑||𝓍﹣μ(𝓍ʹs cluster)||² ＝ the sum of the squared distances between each point and it's respective cluster's mean
    for _ in range(tries - 1):
        proposed_centroids,proposed_total_distortion=kmeans(obs=data_vectors,k_or_guess=k_or_initial_centroids,iter=iterations)
        if proposed_total_distortion < total_distortion:
            total_distortion=proposed_total_distortion
            centroids=proposed_centroids
    parent_centroid_indexes,parent_centroid_distances=vq(data_vectors,centroids)  # ⟵ assign each sample to a cluster
    # The rCode Identities section should answer most questions you may have about this def.
    # rCode Identities: Let c≣centroids  ⋀  i≣parent_centroid_indexes  ⋀  d≣parent_centroid_distances …
    # … ⋀  v≣data_vectors  ⋀  dist(a,b)≣﹙the euclidean distance between vectors a and b﹚  ⋀  k≣k_or_initial_centroids
    #   ∴ len(v) == len(i) == len(d)
    #   ∴ ∀ 𝓍 ∈ i， d[𝓍] == dist(v[𝓍],c[𝓍])
    #   ∴ total_distortion == ∑d²
    #   ∴ len(c) == k ⨁ len(c) == len(k)
    return centroids,total_distortion,parent_centroid_indexes,parent_centroid_distances
def is_iterable(x):
    try:
        for _ in x: pass
        return True
    except:
        return False
def space_split(x: str) -> list:
    return list(filter(lambda y:y != '',x.split(" ")))  # Splits things by spaces but doesn't allow empty parts
def deepcopy_multiply(iterable,factor: int):
    # Used for multiplying lists without copying their addresses
    out=[]
    from copy import deepcopy
    for i in range(factor):
        out+=deepcopy(iterable)
    return out
def assert_equality(*args,equality_check=identity):
    # When you have a,b,c,d and e and they're all equal and you just can't choose...when the symmetry is just too much symmetry!
    # PLEASE NOTE: This does not check every combination: it assumes that equality_check is symmetric!
    length=len(args)
    if length == 0:
        return None
    base=args[0]
    if length == 1:
        return base
    for arg in args:
        base_check=equality_check(base)
        arg_check=equality_check(arg)
        assert (base_check == arg_check)," assert_equality check failed, because " + str(base_check) + " ≠ " + str(arg_check)
        base=arg
    return base
def get_nested_value(list_to_be_accessed,*address_int_list,ignore_errors: bool = False):
    # Needs to be better documented. ignore_errors will simply stop tunneling through the array if it gets an error and return the latest value created.
    # Also note: this could con
    # a[b][c][d] ≣ get_nested_value(a,b,c,d)
    for i in detuple(address_int_list):
        try:
            list_to_be_accessed=list_to_be_accessed[i]
        except:
            if ignore_errors:
                break
            else:
                raise IndexError
    return list_to_be_accessed
def shell_command(command: str,as_subprocess=False,return_printed_stuff_as_string: bool = True) -> str or None:
    # region OLD VERSION: had an argument called return_printed_stuff_as_string, which I never really used as False, and run_as_subprocess when True might not return a string anyay. If I recall correctly, I implemented return_printed_stuff_as_string simply because it was sometimes annoying to see the output when using pseudo_terminal
    #       def shell_command(command: str,return_printed_stuff_as_string: bool = True,run_as_subprocess=False) -> str or None:
    #           if return_printed_stuff_as_string:
    #               return (lambda ans:ans[ans.find('\n') + 1:][::-1])(os.popen(command).read()[::-1])  # EX: print(shell_command("pwd")) <-- Gets the current directory
    #           from os import system
    #           system(command)
    # endregion
    if as_subprocess:
        from subprocess import run
        if return_printed_stuff_as_string:
            return (lambda ans:ans[ans.find('\n') + 1:][::-1])(run(command,shell=True).stdout[::-1])  # EX: print(shell_command("pwd")) <-- Gets the current directory
        else:
            run(command)
    else:
        if return_printed_stuff_as_string:
            return (lambda ans:ans[ans.find('\n') + 1:][::-1])(os.popen(command).read()[::-1])  # EX: print(shell_command("pwd")) <-- Gets the current directory
        else:
            from os import system
            system(command)
def delete_file(path: str,permanent: bool = False) -> None:
    # permanent exists for safety reasons. It's False by default in case you make a stupid mistake like deleting this file. When false, it will send your files to the trash bin on your system (Mac,Windows,Linux, etc)
    # http://stackoverflow.com/questions/3628517/how-can-i-move-file-into-recycle-bin-trash-on-different-platforms-using-pyqt4
    # https://pypi.python.org/pypi/Send2Trash
    # pip3 install Send2Trash
    import os
    assert os.path.exists(path),"r.delete_file: There is no file to delete. The path you specified, '" + path + "', does not exist!"  # This is to avoid the otherwise cryptic errors you would get later on with this method
    if permanent:
        os.remove(path)
    else:
        import send2trash  # This is much safer. By default, we move files to the trash bin. That way we can't accidentally delete our whole directory for good ;)
        send2trash.send2trash(path)  # This is MUCH safer than when delete_permanently is turned on. This will have the same effect as deleting it in finder/explorer: it will send your file to the trash bin instead of immediately deleting it forever.
# ANYTHING BELOW THIS LINE IS WILL EVENTUALLY BE EITHER REMOVED OR MOVED ABOVE THIS LINE =======================================================
def printed(message,value_to_be_returned=None,end='\n'):  # For debugging...perhaps this is obsolete now that I have pseudo_terminal though.
    print(str(value_to_be_returned if value_to_be_returned is not None else message),end=end)
    return value_to_be_returned or message
def blob_coords(image: np.ndarray,small_end_radius=10,big_start_radius=50):
    # small_end_radius is the 'wholeness' that we look for. Without it we might-as-well pickthe global max pixel we start with, which is kinda junky.
    assert big_start_radius >= small_end_radius
    if len(image.shape) == 3:
        image=tofloat(rgb_to_grayscale(image))
    def global_max(image):
        # Finds max-valued coordinates. Randomly chooses if multiple equal maximums. Assumes image is SINGLE CHANNEL!!
        assert isinstance(image,np.ndarray)
        assert len(image.shape) == 2  # SHOULD BE SINGLE CHANNEL!!
        return random_element(np.transpose(np.where(image == image.max()))).tolist()
    def get(x,y):
        try:
            return image[x,y]
        except IndexError:
            return 0
    def local_max(image,x0,y0):
        # Gradient ascent pixel-wise. Assumes image is SINGLE CHANNEL!!
        assert isinstance(image,np.ndarray)
        assert len(image.shape) == 2  # SHOULD BE SINGLE CHANNEL!!
        def get(x,y):
            try:
                return image[x,y]
            except IndexError:
                return 0
        def step(x,y):  # A single gradient ascent step
            best_val=0  # We're aiming to maximize this
            best_x=x
            best_y=y
            for Δx in [-1,0,1]:
                for Δy in [-1,0,1]:
                    if get(x + Δx,y + Δy) > best_val:
                        best_val=get(x + Δx,y + Δy)
                        best_x,best_y=x + Δx,y + Δy
            return best_x,best_y
        while step(x0,y0) != (x0,y0):
            x0,y0=step(x0,y0)
        return x0,y0
    # image is now a single channel.
    def blurred(radius):
        return gauss_blur(image,radius,single_channel=True)  # ,mode='constant')
    x,y=global_max(blurred(big_start_radius))
    for r in reversed(range(small_end_radius,big_start_radius)):
        x,y=local_max(blurred(r + 1),x,y)
    return x,y
def tofloat(ndarray):
    # Things like np.int16 or np.int64 will all be scaled down by their max values; resulting in
    # elements that in sound files would be floats ∈ [-1,1] and in images [0,255] ⟶ [0-1]
    return np.ndarray.astype(ndarray,float) / np.iinfo(ndarray.dtype).max
def dot(x,y,color='red',size=3,shape='o',block=False):
    plt.plot([x],[y],marker=shape,markersize=size,color=color)
    plt.show(block=block)
    if not block:
        plt.pause(0.0001)
def translate(to_translate,to_language="auto",from_language="auto"):
    # I DID NOT WRITE THIS!! I GOT IT FROM https://github.com/mouuff/mtranslate/blob/master/mtranslate/core.py
    """Returns the translation using google translate
    you must shortcut the language you define
    (French = fr, English = en, Spanish = es, etc...)
    if not defined it will detect it or use english by default
    Example:
    print(translate("salut tu vas bien?", "en"))
    hello you alright?
    """

    is_valid=lambda x:x in text_to_speech_voices_for_google or x == "auto"
    assert is_valid(to_language) and is_valid(from_language),'Invalid language! Cannot translate.'

    import sys
    import re
    if sys.version_info[0] < 3:
        # noinspection PyUnresolvedReferences
        import urllib2
        import urllib
        # noinspection PyUnresolvedReferences
        import HTMLParser
    else:
        import html.parser
        import urllib.request
        import urllib.parse
    agent={'User-Agent':
               "Mozilla/4.0 (\
                 compatible;\
                 MSIE 6.0;\
                 Windows NT 5.1;\
                 SV1;\
                 .NET CLR 1.1.4322;\
                 .NET CLR 2.0.50727;\
                 .NET CLR 3.0.04506.30\
                 )"}
    def unescape(text):
        if sys.version_info[0] < 3:
            parser=HTMLParser.HTMLParser()
        else:
            parser=html.parser.HTMLParser()
        try:
            # noinspection PyDeprecation
            return parser.unescape(text)
        except:
            return html.unescape(text)
    base_link="http://translate.google.com/m?hl=%s&sl=%s&q=%s"
    if sys.version_info[0] < 3:
        # noinspection PyUnresolvedReferences
        to_translate=urllib.quote_plus(to_translate)
        link=base_link % (to_language,from_language,to_translate)
        request=urllib2.Request(link,headers=agent)
        raw_data=urllib2.urlopen(request).read()
    else:
        to_translate=urllib.parse.quote(to_translate)
        link=base_link % (to_language,from_language,to_translate)
        request=urllib.request.Request(link,headers=agent)
        raw_data=urllib.request.urlopen(request).read()
    data=raw_data.decode("utf-8")
    expr=r'class="t0">(.*?)<'
    re_result=re.findall(expr,data)
    if len(re_result) == 0:
        result=""
    else:
        result=unescape(re_result[0])
    return result
def sync_sort(*lists_in_descending_sorting_priority):
    # Sorts main_list and reorders all *lists_in_descending_sorting_priority the same way, in sync with main_list
    return tuple(zip(*sorted(zip(*lists_in_descending_sorting_priority))))

# noinspection PyAugmentAssignment
def full_range(x,min=0,max=1):
    x=np.array(x)
    x=x - np.min(x)
    x=x / np.max(x)  # Augmented Assignment, AKA x-= or x/= causes numpy errors. I don't know why I wonder if its a bug in numpy.
    x=x * (max - min)
    x=x + min
    return x

# region Math constants (based on numpy)
π=pi=np.pi
τ=tau=2 * π
# endregion

# region Tone Generators
# Note: All Tone Sample Generators have an amplitude of [-1,1]
def sine_tone_sampler(ƒ=None,T=None,samplerate=None):
    T=T or Đ_tone_seconds
    samplerate=samplerate or Đ_samplerate
    ƒ=ƒ or Đ_tone_frequency
    ↈλ=ƒ * T  # ≣number of wavelengths
    return np.sin(np.linspace(0,τ * ↈλ,T * (samplerate or Đ_samplerate)))

def triangle_tone_sampler(ƒ=None,T=None,samplerate=None):
    return 2 / π * np.arcsin(sine_tone_sampler(ƒ,T,samplerate))

def sawtooth_tone_sampler(ƒ=None,T=None,samplerate=None):
    T=T or Đ_tone_seconds
    samplerate=samplerate or Đ_samplerate
    ƒ=ƒ or Đ_tone_frequency
    ↈλ=ƒ * T  # ≣number of wavelengths
    return (np.linspace(0,ↈλ,T * (samplerate or Đ_samplerate)) % 1) * 2 - 1

def square_tone_sampler(ƒ=None,T=None,samplerate=None):
    return np.sign(sawtooth_tone_sampler(ƒ,T,samplerate))

Đ_tone_frequency=440  # also known as note A4
Đ_tone_sampler=sine_tone_sampler
Đ_tone_seconds=1
def play_tone(hz=None,seconds=None,samplerate=None,tone_sampler=None,blocking=False):  # Plays a sine tone
    ƒ,T=hz or Đ_tone_frequency,seconds or Đ_tone_seconds  # Frequency, Time
    play_sound_from_samples((tone_sampler or Đ_tone_sampler)(ƒ,T),samplerate or Đ_samplerate,blocking=blocking)
def play_semitone(ↈ_semitones_from_A4_aka_440hz=0,seconds=None,samplerate=None,tone_sampler=None,blocking=False):
    ↈ=ↈ_semitones_from_A4_aka_440hz
    play_tone(semitone_to_hz(ↈ),seconds,samplerate,tone_sampler,blocking)
def semitone_to_hz(ↈ):
    return 440 * 2 ** (ↈ / 12)
def play_chord(*semitones:list,t=1,block=True,sampler=triangle_tone_sampler):
    play_sound_from_samples(full_range(min=-1,x=sum(sampler(semitone_to_hz(x),T=t)for x in semitones)),blocking=block)
# endregion

from itertools import product as cartesian_product
def mini_editor(out: str = "",namespace=(),message=""):  # Has syntax highlighting. Creates a curses pocket-universe where you can edit text, and then press fn+enter to enter the results. It's like like a normal input() except multiline and editable.
    # message=message or "Enter text here and then press fn+enter to exit. Supported controls: Arrow keys, backspace, delete, tab, shift+tab, enter"
    # Please note: You must be using a REAL terminal to run this! Just using pycharm's "run" is not sufficient. Using apple's terminal app, for example, IS however.
    import curses
    stdscr=curses.initscr()

    # region Initialize curses colors:
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(0,curses.COLOR_BLACK,curses.COLOR_BLACK)
    black=curses.color_pair(0)
    curses.init_pair(1,curses.COLOR_RED,curses.COLOR_BLACK)
    red=curses.color_pair(1)
    curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
    green=curses.color_pair(2)
    curses.init_pair(3,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    yellow=curses.color_pair(3)
    curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
    blue=curses.color_pair(4)
    curses.init_pair(5,curses.COLOR_CYAN,curses.COLOR_BLACK)
    cyan=curses.color_pair(5)
    curses.init_pair(6,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    magenta=curses.color_pair(6)
    curses.init_pair(7,curses.COLOR_WHITE,curses.COLOR_BLACK)
    gray=curses.color_pair(7)
    # endregion
    def main(stdscr):
        print(message,end='',flush=True)
        # region http://colinmorris.github.io/blog/word-wrap-in-pythons-curses-library
        class WindowFullException(Exception):
            pass

        def addstr_wordwrap(window,s,mode=0):
            """ (cursesWindow, str, int, int) -> None
            Add a string to a curses window with given dimensions. If mode is given
            (e.g. curses.A_BOLD), then format text accordingly. We do very
            rudimentary wrapping on word boundaries.

            Raise WindowFullException if we run out of room.
            """
            # TODO Is there really no way to get the dimensions of a window programmatically?
            # passing in height and width feels ugly.

            height,width=window.getmaxyx()
            height-=1
            width-=1
            (y,x)=window.getyx()  # Coords of cursor
            # If the whole string fits on the current line, just add it all at once
            if len(s) + x <= width:
                window.addstr(s,mode)
            # Otherwise, split on word boundaries and write each token individually
            else:
                for word in words_and_spaces(s):
                    if len(word) + x <= width:
                        window.addstr(word,mode)
                    else:
                        if y == height - 1:
                            # Can't go down another line
                            raise WindowFullException()
                        window.addstr(y + 1,0,word,mode)
                    (y,x)=window.getyx()

        def words_and_spaces(s):
            import itertools
            """
            >>> words_and_spaces('spam eggs ham')
            ['spam', ' ', 'eggs', ' ', 'ham']
            """
            # Inspired by http://stackoverflow.com/a/8769863/262271
            return list(itertools.chain.from_iterable(zip(s.split(),itertools.repeat(' '))))[:-1]  # Drop the last space

        # endregion
        nonlocal out
        cursor_shift=0
        while True:
            # region  Keyboard input:
            stdscr.nodelay(1)  # do not wait for input when calling getch
            c=stdscr.getch()  # get keyboard input
            typing=False
            updown=None
            if c != -1:  # getch() returns -1 if none available
                # text_to_speech(c)
                if chr(c) in "":  # ⟵ Up/Down/Left/Right arrow keys (Up/Down ≣ Scroll up down) are not currently implemented. I don't know how.
                    pass
                elif c == ord("Ą"):  # left arrow key
                    cursor_shift+=1
                    cursor_shift=min(len(out),cursor_shift)
                elif c == ord("ą"):  # right arrow key
                    cursor_shift-=1
                    cursor_shift=max(0,cursor_shift)
                elif c == ord("ă"):  # up arrow key
                    updown='up'
                elif c == ord("Ă"):  # down arrow key
                    updown='down'
                elif c == ord('ŗ') == 343:  # fn+enter was pressed# c==10:# Enter key was pressed
                    return out
                else:
                    typing=True
                    # out+=chr(c)

            # out_lines=out.split("\n")
            # cursor_y=len(out_lines)-1
            # while cursor_x<0:
            #     cursor_x+=len(out_lines[cursor_y])
            #     cursor_y-=1

            out_lines=out.split("\n")
            cursor_y=0
            cursor_x=len(out) - cursor_shift
            assert cursor_x >= 0

            if updown:
                if updown == 'up':
                    i0=out[:cursor_x].rfind("\n")
                    i1=out[:i0].rfind("\n")
                    cursor_x=min(len(out) - 1,max(0,min(cursor_x - i0,i0 - i1) + i1))
                    cursor_shift=len(out) - cursor_x

                else:
                    assert updown == 'down'
                    i0=out[:cursor_x].rfind("\n")
                    i1=out.find("\n",i0 + 1)
                    cursor_x=min(len(out) - 1,max(0,min(cursor_x - i0,i1 - i0) + i1))
                    cursor_shift=len(out) - cursor_x

            elif typing:
                if c == 127:  # Backspace key was pressed
                    if cursor_x:
                        out=out[:cursor_x - 1] + out[cursor_x:]
                elif c == ord("Ŋ"):  # Delete key was pressed
                    if cursor_x < len(out):
                        out=out[:cursor_x] + out[cursor_x + 1:]
                        cursor_shift-=1
                        cursor_x+=1
                elif c == ord('\t'):  # tab
                    out=out[:cursor_x] + "    " + out[cursor_x:]  # 4 spaces per tab
                elif c == ord('š'):  # shift+tab
                    if cursor_x:
                        out=out[:max(0,cursor_x - 4)] + out[cursor_x:]  # 4 backspaces
                else:
                    out=out[:cursor_x] + chr(c) + out[cursor_x:]

            for i in range(len(out_lines) - 1):
                out_lines[i]+="\n"  # So that ∑out_lines ＝ out
            while cursor_x > len(out_lines[cursor_y]):
                cursor_x-=len(out_lines[cursor_y])
                cursor_y+=1
            try:
                if out[len(out) - cursor_shift - 1] == "\n":  # c_x+1?
                    cursor_x=0
                    cursor_y+=1
            except:
                pass

            # endregion
            # region Real-time display:
            stdscr.erase()
            stdscr.move(0,0)  # return curser to start position to re-print everything
            height,width=stdscr.getmaxyx()
            height-=1
            width-=1
            def print_fansi_colors_in_curses(stdscr,s: str):  # Only supports text colors; DOES NOT support anything else at the moment. Assumes we are given a fansi sequence.
                text_color=None
                while True:  # Until string is empty.
                    if s.startswith("\x1b["):
                        while s.startswith("["):  # Oddly without this I got -------...... ⭆ ^[[0;33m-^[[0;33m-^[[0;33m-^[[0;33m-^[[0;33m-^[.......
                            s=s[1:]
                        i=s.find('m')  # there should always be a m somewhere, print(repr(fansi_print("h",'red','bold'))) for example.
                        ss=s[:i].split(';')
                        s=s[i + 1:]  # +1 to take care of the m which is gone now
                        if '30' in ss:  # black
                            text_color=black
                        elif '31' in ss:  # red
                            text_color=red
                        elif '32' in ss:  # green
                            text_color=green
                        elif '33' in ss:  # yellow
                            text_color=yellow
                        elif '34' in ss:  # blue
                            text_color=blue
                        elif '35' in ss:  # magenta
                            text_color=magenta
                        elif '36' in ss:  # cyan
                            text_color=cyan
                        elif '37' in ss:  # gray
                            text_color=gray
                        else:  # if'0'in ss:# clear style
                            text_color=None
                    if not s:
                        break  # avoid trying to access indexes in an empty string
                    if text_color is not None:
                        # stdscr.addstr(s[0],text_color)
                        addstr_wordwrap(stdscr,s[0],text_color)
                    else:
                        # stdscr.addstr(s[0])
                        addstr_wordwrap(stdscr,s[0])
                    s=s[1:]
            print_fansi_colors_in_curses(stdscr,fansi_syntax_highlighting(out,namespace))
            assert isinstance(out,str)

            while cursor_x > width:
                cursor_y+=1
                cursor_x-=width
            cursor_y=min(height,cursor_y)
            stdscr.move(cursor_y,cursor_x)
            stdscr.refresh()
            # endregion
    curses.wrapper(main)
    return out

def get_terminal_size():  # In (ↈcolumns，ↈrows) tuple form
    # From http://stackoverflow.com/questions/566746/how-to-get-linux-console-window-width-in-python/14422538#14422538
    import os
    env=os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl,termios,struct,os
            cr=struct.unpack('hh',fcntl.ioctl(fd,termios.TIOCGWINSZ,
                                              '1234'))
        except:
            return
        return cr
    cr=ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd=os.open(os.ctermid(),os.O_RDONLY)
            cr=ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr=(env.get('LINES',25),env.get('COLUMNS',80))

        ### Use get(key[, default]) instead of a try/catch
        # try:
        #    cr = (env['LINES'], env['COLUMNS'])
        # except:
        #    cr = (25, 80)
    return int(cr[1]),int(cr[0])
def is_namespaceable(c: str) -> bool:  # If character can be used as the first of a python variable's name
    try:
        c+=random_permutation("ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # Just in case this overrides some other variable somehow (I don't know how it would do that but just in case)
        exec(c + "=None")
        exec("del " + c)
        return True
    except:
        return False
def is_literal(c: str) -> bool:  # If character can be used as the first of a python variable's name
    return c==":"or (is_namespaceable(c) or c.isalnum())and not c.lstrip().rstrip() in ['False','def','if','raise','None','del','import','return','True','elif','in','try','and','else','is','while','as','except','lambda','with','assert','finally','nonlocal','yield','break','for','not','class','from','or','continue','global','pass']

def clip_string_width(x: str,max_width=None,max_wraps_per_line=1,clipped_suffix='…'):  # clip to terminal size. works with multi lines at once.
    max_width=(max_width or get_terminal_size()[0]) * max_wraps_per_line
    return '\n'.join((y[:max_width - len(clipped_suffix)] + clipped_suffix) if len(y) > max_width else y for y in x.split('\n'))

def properties_to_xml(src_path,target_path):  # Found this during my 219 hw4 assignment when trying to quickly convert a .properties file to an xml file to get more credit
    # SOURCE: https://www.mkyong.com/java/how-to-store-properties-into-xml-file/
    # Their code was broken so I had to fix it. It works now.
    src=open(src_path)
    target=open(target_path,'w')
    target.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n')
    target.write('<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">\n')
    target.write('<properties>\n')

    for line in src.readlines():
        word=line.split('=')
        key=word[0]
        message='='.join(word[1:]).strip()  # .decode('unicode-escape')
        # message=unicode('='.join(word[1:]).strip(),'unicode-escape')
        target.write('\t<entry key="' + key + '"><![CDATA[' + message.encode('utf8').decode() + ']]></entry>\n')

    target.write('</properties>')
    target.close()

def split_letters_from_digits(s: str) -> list:
    # Splits letters from numbers into a list from a string.
    # EXAMPLE: "ads325asd234" -> ['ads', '325', 'asd', '234']
    # SOURCE: http://stackoverflow.com/questions/28290492/python-splitting-numbers-and-letters-into-sub-strings-with-regular-expression
    import re
    return re.findall(r'[A-Za-z]+|\d+',s)

def split_camel_case(s: str) -> list:
    # Split camel case names into lists. Example: camel_case_split("HelloWorld")==["Hello","World"]
    from re import finditer
    matches=finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',s)
    return [m.group(0) for m in matches]

def int_clamp(x: int,min_value: int,max_value: int) -> int:
    return min([max([min_value,x]),max_value])
def float_clamp(x: float,min_value: float,max_value: float) -> float:
    # noinspection PyTypeChecker
    return int_clamp(x,min_value,max_value)

def print_stack_trace(error:BaseException,full_traceback: bool = True,header='r.print_stack_trace: ERROR: ',print_it=True):
    from traceback import format_exception,format_exception_only
    # ⁠⁠⁠⁠        ⎧                                                                                                                                                                                                ⎫
    # ⁠⁠⁠⁠        ⎪                                  ⎧                                                                                                                                                            ⎫⎪
    # ⁠⁠⁠⁠        ⎪                                  ⎪       ⎧                                                           ⎫                               ⎧                                            ⎫           ⎪⎪
    return (print if print_it else identity)(fansi(header,'red','bold') + fansi(''.join(format_exception(error.__class__,error,error.__traceback__)) if full_traceback else ''.join(format_exception_only(error.__class__,error))[:-1],'red'))
# ⁠⁠⁠⁠        ⎪                                  ⎪       ⎩                                                           ⎭                               ⎩                                            ⎭           ⎪⎪
# ⁠⁠⁠⁠        ⎪                                  ⎩                                                                                                                                                            ⎭⎪
# ⁠⁠⁠⁠        ⎩                                                                                                                                                                                                ⎭
def audio_stretch(mono_audio, new_number_of_samples):# Does not take into account the last bit of looping audio
    # ⮤ audio_stretch([1,10],10)
    # ans = [1,2,3,4,5,6,7,8,9,10]
    return [ linterp(x,mono_audio) for x in np.linspace(0,len(mono_audio)-1,new_number_of_samples)]

def cartesian_to_polar(x, y, ϴ_unit=τ)->tuple:
    """Input conditions: x，y ∈ ℝ ⨁ x﹦［x₀，x₁，x₂……］⋀ y﹦［y₀，y₁，y₂……］
    returns: (r, ϴ) where r ≣ radius，ϴ ≣ angle and 0 ≤ ϴ < ϴ_unit. ϴ_unit﹦τ ⟹ ϴ is in radians，ϴ_unit﹦360 ⟹ ϴ is in degrees"""
    return np.hypot(x,y),np.arctan2(y,x)/τ%1*ϴ_unit  # Order of operations: % has same precedence as * and /
def complex_to_polar(complex,ϴ_unit=τ)->tuple:
    """returns: (r, ϴ) where r ≣ radius，ϴ ≣ angle and 0 ≤ ϴ < ϴ_unit. ϴ_unit﹦τ ⟹ ϴ is in radians，ϴ_unit﹦360 ⟹ ϴ is in degrees.
    Input conditions: c ≣ complex ⋀ c ∈ ℂ ⨁ c﹦［c₀，c₁，c₂……］
    Returns r and ϴ either as numbers OR as two lists: all the r's and then all the ϴ's"""
    return np.abs(complex),np.angle(complex)# np.abs is calculated per number, not vector etc
Đ_left_to_right_sum_ratio=0# By default, take a left hand sum
def riemann_sum(f,x0,x1,N,left_to_right_sum_ratio=None):# Verified ✔
    # Desmos: https://www.desmos.com/calculator/tgyr42ezjq
    # left_to_right_sum_ratio﹦0  ⟹ left hand sum
    # left_to_right_sum_ratio﹦.5 ⟹ midpoint hand sum
    # left_to_right_sum_ratio﹦1  ⟹ right hand sum
    # The x1 bound MUST be exclusive as per definition of a left riemann sum
    c=left_to_right_sum_ratio or Đ_left_to_right_sum_ratio
    w=(x1-x0)/N# Width of the bars
    return sum(f(x0+w*(i+c))*w for i in range(N))
def riemann_mean(f,x0,x1,N,left_to_right_sum_ratio=None):# To prevent redundancy of the N parameter
    return riemann_sum(f,x0,x1,N,left_to_right_sum_ratio) / (x1-x0)

def fourier(cyclic_function,freq,cyclic_period=τ,ↈ_riemann_terms=100):
    # Can enter a vector of frequencies to two vectors of outputs if you so desire
    # Returns polar coordinates representing amplitude,phase  (AKA r,ϴ)
    # With period=τ, sin(x) has a freq of 1.
    # With period=1, sin(x) has a freq of 1/τ.
    # ⁠⁠⁠⁠                          ⎧                                                                                                       ⎫
    # ⁠⁠⁠⁠                          ⎪            ⎧                                                                                         ⎫⎪
    # ⁠⁠⁠⁠                          ⎪            ⎪               ⎧                 ⎫                  ⎧               ⎫                    ⎪⎪
    return complex_to_polar(riemann_mean(lambda x:np.exp(freq * τ * x * 1j) * cyclic_function(x*cyclic_period),0,1,ↈ_riemann_terms))
# ⁠⁠⁠⁠                          ⎪            ⎪               ⎩                 ⎭                  ⎩               ⎭                    ⎪⎪
# ⁠⁠⁠⁠                          ⎪            ⎩                                                                                         ⎭⎪
# ⁠⁠⁠⁠                          ⎩                                                                                                       ⎭
def discrete_fourier(cyclic_vector,freq):# Assuming that cyclic_vector is a single wave-cycle, freq represents the number of its harmonic
    # Can enter a vector of frequencies to two vectors of outputs if you so desire
    # Returns polar coordinates representing amplitude,phase  (AKA r,ϴ)
    return fourier(cyclic_function=lambda x:linterp(x,cyclic_vector,cyclic=True),freq=freq,cyclic_period=len(cyclic_vector),ↈ_riemann_terms=len(cyclic_vector))
def matrix_to_tuples(m:np.ndarray,filter=lambda r,c,val:True):# Filter can significantly speed it up
    # ⁠⁠⁠⁠                  ⎧                                                                                        ⎫
    # ⁠⁠⁠⁠                  ⎪⎧                                                                                      ⎫⎪
    # ⁠⁠⁠⁠                  ⎪⎪⎧                                                             ⎫                       ⎪⎪
    # ⁠⁠⁠⁠                  ⎪⎪⎪                            ⎧         ⎫                      ⎪                       ⎪⎪
    # ⁠⁠⁠⁠                  ⎪⎪⎪⎧           ⎫               ⎪   ⎧    ⎫⎪          ⎧          ⎫⎪               ⎧      ⎫⎪⎪
    return list_pop([[(r,c,m[r][c]) for c in range(len(m[r])) if filter(r,c,m[r,c])] for r in range(len(m))])# Creates list of coordinates, (x,y,value). WARNING: Can be very slow
# ⁠⁠⁠⁠                  ⎪⎪⎪⎩           ⎭               ⎪   ⎩    ⎭⎪          ⎩          ⎭⎪               ⎩      ⎭⎪⎪
# ⁠⁠⁠⁠                  ⎪⎪⎪                            ⎩         ⎭                      ⎪                       ⎪⎪
# ⁠⁠⁠⁠                  ⎪⎪⎩                                                             ⎭                       ⎪⎪
# ⁠⁠⁠⁠                  ⎪⎩                                                                                      ⎭⎪
# ⁠⁠⁠⁠                  ⎩                                                                                        ⎭
def perpendicular_bisector_function(x0,y0,x1,y1):
    A,B=x0,y0
    Y,X=x1,y1
    def linear_function(x):
        return ((B+Y)/2)-(X-A)/(Y-B)*(x-(A+X)/2)  # https://www.desmos.com/calculator/1ykebsqtoa
    return linear_function

def harmonic_analysis_via_least_squares(wave,harmonics:int):
    prod=np.matmul
    inv=np.linalg.inv
    b=wave  # In terms of linear algebra in Ax~=b
    samples=len(b)
    m=np.asmatrix(np.linspace(1,harmonics,harmonics)).T*np.matrix(np.linspace(0,tau,samples,endpoint=False))
    A=np.asmatrix(np.concatenate([np.sin(m),np.cos(m)])).T
    Api=prod(inv(prod(A.T,A)),A.T)  # Api====A pseudo inverse
    out=np.asarray(prod(Api,b))[0]
    out=np.reshape(out,[2,len(out)//2])  # First vector is the sin array second is the cos array
    amplitudes=sum(out**2)**.5
    phases=np.arctan2(*out)
    return np.asarray([amplitudes,phases])  # https://www.desmos.com/calculator/fnlwi71n9x

def cluster_filter(vec,filter=identity):  # This has a terrible name...I'm not sure what to rename it so if you think of something, go for it!
    # EXAMPLE: cluster_filter([2,3,5,9,4,6,1,2,3,4],lambda x:x%2==1) --> [[3, 5, 9], [1], [3]]  <---- It separated all chunks of odd numbers
    # region Unoptimized, much slower version (that I kept because it might help explain what this function does):
    # def mask_clusters(vec,filter=identity):
    #  out=[]
    #  temp=[]
    #  for val in vec:
    #    if filter(val):
    #      temp.append(val)
    #    elif temp:
    #      out.append(temp)
    #      temp=[]
    #  return out
    # endregion

    out=[]
    s=None  # start
    for i,val in enumerate(vec):
        if filter(val):
            if s is None:
                s=i
        elif s is not None:
            out.append(vec[s:i])
            s=None
    if s is not None:
        out.append(vec[s:])
    return out

# region Originally created for the purpose of encoding 3 bytes of precision into a single image via r,g,b being three digits
def proportion_to_digits(value,base=256,number_of_digits=3):  # Intended for values between 0 and 1
    digits=[]
    x=value
    while len(digits)<number_of_digits:
        x*=base
        temp=np.floor(x)
        digits.append(temp)
        x-=np.floor(x)
    return digits
def digits_to_proportion(digits,base=256):  # Intended for values between 0 and 1
    return np.sum(np.asarray(digits)/base**np.linspace(1,len(digits),len(digits)),0)
def rgb_encoded_matrix(m:np.ndarray):# Encoded precision of values between 0 and 1 as r,g,b (in 8-bit color) values where r g and b are each digits, with b being the most precise and r being the least precise
    m=np.matrix(m)
    assert len(m.shape)==2,"r.rgb_encoded_matrix: Input should be a matrix of values between 0 and 1, which is not what you gave it! \n m.shape = \n"+str(m.shape)
    r,g,b=proportion_to_digits(m,base=256,number_of_digits=3)
    out=np.asarray([r,g,b])
    out=np.transpose(out,[1,2,0])
    out=out.astype(np.uint8)
    return out
def matrix_decoded_rgb(rgb:np.ndarray):
    rgb=np.asarray(rgb)
    assert len(rgb.shape)==3 and rgb.shape[-1]==3,"r.rgb_encoded_matrix: Input should be an rgb image (with 3 color channels), which is not what you gave it! \n m.shape = \n"+str(rgb.shape)
    return digits_to_proportion(rgb.transpose([2,0,1]))
def print_all_git_paths():
    fansi_print("Searching for all git repositories on your computer...",'green','underlined')
    tmp = shell_command("find ~ -name .git")# Find all git repositories on computer
    dirpaths=[x[:-4]for x in tmp.split('\n')]
    aliasnames=[(lambda s:(s[:s.find("/")])[::-1])((x[::-1])[1:])for x in dirpaths]
    dirpaths,aliasnames=sync_sort(dirpaths,aliasnames)
    for x in sorted(zip(aliasnames,dirpaths)):
        print(fansi(x[0],'cyan')+" "*(max(map(len,aliasnames))-len(x[0])+3)+fansi(x[1],None))
    return dirpaths,aliasnames

def is_int_literal(s:str):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def is_string_literal(s:str):
    try:
        s=eval(s)
        assert isinstance(s,str)
        return True
    except:
        return False

def indentify(s:str,indent='\t'):
    return '\n'.join(indent + x for x in s.split('\n'))
def lrstrip_all_lines(s:str):
    return '\n'.join([x.lstrip().rstrip()for x in s.split('\n')])

random_unicode_hash=lambda l:int_list_to_string([randint(0x110000-1)for x in range(l)])
def search_replace_simul(s:str,replacements:dict):
    if not replacements:
        return s
    # ⮤ search_replace_simul("Hello world",{"Hello":"world","world":"Hello"})
    l1 = replacements.keys()
    l2 = replacements.values()
    l3 = [random_unicode_hash(10) for x in replacements]
    ⵁ,l1,l2,l3=sync_sort([-len(x)for x in l1],l1,l2,l3)# Sort the keys in descending number of characters     # Safe replacements: f and fun as keys: f won't be seen as in 'fun'
    for a,b in zip(l1,l3):
        s=s.replace(a,b)
    for a,b in zip(l3,l2):
        s=s.replace(a,b)
    return s

def shorten_url(url:str)->str:
    # goo.gl links are supposed to last forever, according to https://groups.google.com/forum/#!topic/google-url-shortener/Kt0bc5hx9HE
    # SOURCE: https://stackoverflow.com/questions/17357351/how-to-use-google-shortener-api-with-python
    # API Key source: https://console.developers.google.com/apis/credentials?project=dark-throne-182400
    #  ⮤ goo_shorten_url('ryan-central.org')
    # ans = https://goo.gl/Gkgp86
    import requests
    import json
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBbNJ4ZPCAeDBGAVQKDikwruo3dD4NcsU4'# AIzaSyBbNJ4ZPCAeDBGAVQKDikwruo3dD4NcsU4 is my account's API key.
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    # RIGHT NOW: r.text==
    # '''{
    #     "kind":"urlshortener#url",
    #     "id":"https://goo.gl/ZNp1VZ",
    #     "longUrl":"https://console.developers.google.com/apis/credentials?project=dark-throne-182400"
    # }'''
    out=eval(r.text)
    assert isinstance(out,dict)
    return out['id']

def gist(gist_body="Body",gist_filename="File.file",gist_description="Description"):
    # Older version:
    # def gist(code:str,file_name:str='CodeGist.code',username='sqrtryan@gmail.com',password='d0gememesl0l'):
    #     # Posts a gist with the given code and filename.
    #     #  ⮤ gist("Hello, World!")
    #     # ans = https://gist.github.com/b5b3e404c414f7974c4ccb12106c4fe7
    #     import requests,json
    #     r = requests.post('https://api.github.com/gists',json.dumps({'files':{file_name:{"content":code}}}),auth=requests.auth.HTTPBasicAuth(username, password))
    #     try:
    #         return r.json()['html_url']# Returns the URL
    #     except KeyError as e:
    #         fansi_print("r.gist ERROR:",'red','bold',new_line=False)
    #         fansi_print(" "+str(e)+" AND r.json() = "+str(r.json()),'red')

    from urllib.request import urlopen
    import json
    gist_post_data={'description':gist_description,
                    'public':True,
                    'files':{gist_filename:{'content':gist_body}}}

    json_post_data=json.dumps(gist_post_data).encode('utf-8')

    def upload_gist():
        # print('sending')
        url='https://api.github.com/gists'
        json_to_parse=urlopen(url,data=json_post_data)

        # print('received response from server')
        found_json=(b'\n'.join(json_to_parse.readlines()))
        return json.loads(found_json.decode())['html_url']
    return upload_gist()

sgist=lambda *x:seq([gist,printed,open_url,shorten_url],*x)# Open the url of a gist and print it

def random_namespace_hash(n:int,chars_to_choose_from:str="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"):
    # ⮤ random_namespace_hash(10)
    # ans=DZC7B8GV74
    out=''
    for n in [None]*n:
        out+=random_element(chars_to_choose_from)
    return out

def latex_image(equation: str):
    # Returns an rgba image with the rendered latex string on it in numpy form
    import os,requests
    def formula_as_file(formula,file,negate=False):  # Got this off the web somewhere idr where now
        tfile=file
        if negate:
            tfile='tmp.png'
        r=requests.get('http://latex.codecogs.com/png.latex?\dpi{300} \huge %s' % formula)
        f=open(tfile,'wb')
        f.write(r.content)
        f.close()
        if negate:
            os.system('convert tmp.png -channel RGB -negate -colorspace rgb %s' % file)
    formula_as_file(equation,'temp.png')
    return load_image('temp.png')

def display_image_in_terminal(i):
    from drawille import Canvas
    c=Canvas()
    for x in range(width(i)):
        for y in range(height(i)):
            if i[x,y]:
                c.set(y,x)
    print(c.frame())

def auto_canny(image,sigma=0.33):
    import cv2
    # compute the median of the single channel pixel intensities
    v=np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower=int(max(0,(1.0 - sigma) * v))
    upper=int(min(255,(1.0 + sigma) * v))
    edged=cv2.Canny(image,lower,upper)

    # return the edged image
    return edged

def skeletonize(img):
    """ OpenCV function to return a skeletonized version of img, a Mat object"""
    import cv2
    # Found this on the web somewhere
    #  hat tip to http://felix.abecassis.me/2011/09/opencv-morphological-skeleton/
    img=img.astype(np.uint8)
    img=img.copy()  # don't clobber original
    skel=img.copy()

    skel[:,:]=0
    kernel=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))

    while True:
        eroded=cv2.morphologyEx(img,cv2.MORPH_ERODE,kernel)
        temp=cv2.morphologyEx(eroded,cv2.MORPH_DILATE,kernel)
        temp=cv2.subtract(img,temp)
        skel=cv2.bitwise_or(skel,temp)
        img[:,:]=eroded[:,:]
        if cv2.countNonZero(img) == 0:
            break

    return skel

# noinspection PyTypeChecker
def print_latex_image(latex: str,thin=True,scale=.17,threshold=20):
    # ⮤ print_latex_image("\sum_{n=3}^7x^2")
    # ⠀⠀⠀⠀⠠⠟⢉⠟
    # ⠀⠀⠀⠀⠀⠀⡏
    # ⠀⠀⠀⠀⠀⠀⠃
    # ⢀⢀⣀⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡀
    # ⠀⠙⠄⠀⠀⠀⠀⠀⠀⠈⠉⢦⠀⠀⠀⠀⠀⠀⠀⠛⠀⡸
    # ⠀⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⣡
    # ⠀⠀⠀⠀⠑⡀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠋⣹⠉⠃⠈⠉⠉
    # ⠀⠀⠀⢀⡔⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣠⣏⣠⠆
    # ⠀⠀⡠⠊⠀⠀⠀⠀⠀⠀⠀⣠
    # ⢀⢼⣤⣤⣤⣤⣤⡤⠤⠤⠴⠁
    #
    # ⢀⠀⣀⠀⠀⠀⠀⠀⠀⠐⠏⢹
    # ⢣⠏⢨⠃⢘⣛⣛⣛⣋⢀⠈⠙⡄
    # ⠘⠀⠘⠊⠀⠀⠀⠀⠀⠘⠒⠚
    # Prints it in the console
    # @formatter:off
    DisplayThin=   lambda latex:display_image_in_terminal((resize_image(skeletonize(255 - latex_image(latex)[:,:,0]),scale) > threshold) * 1)
    DisplayRegular=lambda latex:display_image_in_terminal((resize_image(           (255 - latex_image(latex)[:,:,0]),scale) > threshold) * 1)
    #@formatter:on
    if thin:
        DisplayThin(latex)
    else:
        DisplayRegular(latex)

cd=os.chdir
image_acro="""di=display_image
li=load_image
dgi=display_grayscale_image
lg=line_graph
import cv2
"""

# def remove_alpha_channel(image:np.ndarray,shutup=False):
#     # Strips an image of its' alpha channel if it has one, otherwise basically leaves the image alone.
#     sh=image.shape
#     l=len(sh)
#     if l==2 and not shutup:
#         # Don't break the user's script but warn them: this image is not what they thought it was.
#         print("r.remove_alpha_channel: WARNING: You fed in a matrix; len(image.shape)==2")
#         return image
#     if
#     assert l==3,'Assuming that it has color channels to begin with, and that its not just a matrix of numbers'
#     assert 3<=sh[2]<=4,'Assuming it has R,G,B or R,G,B,A'

#     return image[:,:,[0,1,2]]

# def is_valud_url(url: str) -> bool:
#     # PROBLEM:
#     #     ⮤ ivu("google.com")
#     # ans=False
#
#     # I DID NOT WRITE THIS WHOLE FUNCTION ∴ IT MIGHT NOT WORK PERFECTLY. THIS IS FROM: http://stackoverflow.com/questions/452104/is-it-worth-using-pythons-re-compile
#     import re
#     regex=re.compile(
#         r'^(?:http|ftp)s?://'  # http:// or https://
#         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
#         r'localhost|'  # localhost...
#         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
#         r'(?::\d+)?'  # optional port
#         r'(?:/?|[/?]\S+)$',re.IGNORECASE).match(url)
#     return regex is not None and (lambda ans:ans.pos == 0 and ans.endpos == len(url))(g.fullmatch(url))
# import rp.rp_ptpython.prompt_style as ps
# ps.__all__+=("PseudoTerminalPrompt",)
# class PseudoTerminalPrompt(ClassicPrompt):
#     from ptpython.prompt_style import Token
#     def in_tokens(self,cli):
#         return [(Token.Prompt,' ⮤ ')]
# setattr(ps,'PseudoTerminalPrompt',PseudoTerminalPrompt)
# Đ_python_input_eventloop = None#Singleton for python_input
# def python_input(namespace):
#     from prompt_toolkit.shortcuts import create_eventloop
#     from ptpython.python_input import PythonCommandLineInterface,PythonInput as Pyin
#     global Đ_python_input_eventloop
#     pyin=Pyin(get_globals=lambda:namespace)
#     pyin.enable_mouse_support=False
#     pyin.enable_history_search=True
#     pyin.highlight_matching_parenthesis=True
#     pyin.enable_input_validation=False
#     pyin.enable_auto_suggest=False
#     pyin.show_line_numbers=True
#     pyin.enable_auto_suggest=True
#     # exec(mini_terminal)
#     pyin.all_prompt_styles['Pseudo Terminal']=ps.PseudoTerminalPrompt()
#     # ps.PseudoTerminalPrompt=PseudoTerminalPrompt
#     pyin.prompt_style='Pseudo Terminal'
#
#     Đ_python_input_eventloop=Đ_python_input_eventloop or PythonCommandLineInterface(create_eventloop(),python_input=pyin)
#     #
#     # try:
#     code_obj = Đ_python_input_eventloop.run()
#     if code_obj.text is None:
#         print("THE SHARKMAN SCREAMS")
#     return code_obj.text
# except BaseException as re:
# print_stack_trace(re)
# print("THE DEMON SCREAMS")

def split_into_sublists(l,sublist_len:int,strict=True,keep_remainder=True):
    # If strict: sublist_len MUST evenly divide len(l)
    # keep_remainder is not applicable if strict
    # if not keep_remainder and sublist_len DOES NOT evenly divide len(l), we can be sure that all tuples in the output are of len sublist_len, even though the total number of elements in the output is less than in l.
    # EXAMPLES:
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,3 ,0)   ⟶ [(1,2,3),(4,5,6),(7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,4 ,0)   ⟶ [(1,2,3,4),(5,6,7,8),(9,)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,5 ,0)   ⟶ [(1,2,3,4,5),(6,7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,6 ,0)   ⟶ [(1,2,3,4,5,6),(7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,66,0)   ⟶ [(1,2,3,4,5,6,7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,66,0,1) ⟶ [(1,2,3,4,5,6,7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,66,0,0) ⟶ []
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,5 ,0,0) ⟶ [(1,2,3,4,5)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,4 ,0,0) ⟶ [(1,2,3,4),(5,6,7,8)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,3 ,0,0) ⟶ [(1,2,3),(4,5,6),(7,8,9)]
    # ⮤ split_into_sublists([1,2,3,4,5,6,7,8,9］,4 ,1,0) ⟶ ERROR: ¬ 4 | 9
    if strict:
        assert not len(l)%sublist_len,'len(l)=='+str(len(l))+' and sublist_len=='+str(sublist_len)+': strict mode is turned on but the sublist size doesnt divide the list input evenly. len(l)%sublist_len=='+str(len(l)%sublist_len)+'!=0'
    n=sublist_len
    return list(zip(*(iter(l),) * n))+([tuple(l[len(l)-len(l)%n:])] if len(l)%n and keep_remainder else [])

def rotate_image(image, angle_in_degrees):
    #GOT CODE FROM URL: https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
    angle=angle_in_degrees
    import cv2
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def open_url(url:str):
    from webbrowser import open
    open(url)

def restart_python():
    from os import system
    print("killall Python\nsleep 2\npython3 "+repr(__file__))
    system("killall Python\nsleep 2\npython3 "+repr(__file__))

def eta(total_n,min_interval=.3,title="r.eta"):
    # DEMO:
    # a = eta(2000,title='test')
    # for i in range(2000):
    #     sleep(.031)
    #     a(i)
    #
    # This method is slopily written.
    timer=tic()
    interval_timer=[tic()]
    title='\r'+title+": "
    def display_eta(proportion_completed,time_elapsed_in_seconds,TOTAL_TO_CIMPLET,COMPLETSOFAR,print_out=True):
        if interval_timer[0]()>=min_interval:
            interval_timer[0]=tic()
            # Estimated time of arrival printer
            from datetime import timedelta
            out_method=(lambda x:print(x,end='') if print_out else identity)
            temp=timedelta(seconds=time_elapsed_in_seconds)
            completerey="\tProgress: " + str(COMPLETSOFAR) + "/" + str(TOTAL_TO_CIMPLET)
            if proportion_completed<=0:
                return out_method(title +"NO PROGRESS; INFINITE TIME REMAINING. T=" +str(temp) +(completerey))
            # exec(mini_terminal)
            eta=float(time_elapsed_in_seconds) / proportion_completed #Estimated time of arrival
            etr=eta- time_elapsed_in_seconds # Estimated time remaining
            return out_method(title+(("ETR=" + str(timedelta(seconds=etr)) + "\tETA=" + str(timedelta(seconds=eta)) + "\tT="+str(temp) + completerey if etr > 0 else "COMPLETED IN " + str(temp)+completerey+"\n")))
    def out(n,print_out=True):
        return display_eta(n/total_n,timer(),print_out=print_out,TOTAL_TO_CIMPLET=total_n,COMPLETSOFAR=n)
    return out

def get_subpackages(module):
    # SOURCE: https://stackoverflow.com/questions/832004/python-finding-all-packages-inside-a-package
    dir = os.path.dirname(module.__file__)
    def is_package(d):
        d = os.path.join(dir, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))
    return list(filter(is_package, os.listdir(dir)))

def merge_dicts(*dict_args):
    """
    SOURCE: https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def get_source_file(object):
    #Might throw an exception
    import inspect
    return inspect.getfile(inspect.getmodule(object))

#region Editor Launchers
def edit(file_or_object,editor_command='atom'):
    if isinstance(file_or_object,str):
        return shell_command(editor_command +" " + repr(file_or_object),as_subprocess=True)# Idk if there's anything worth returning but maybe there is? run_as_subprocess is true so we can edit things in editors like vim, suplemon, emacs etc.
    else:
        return edit(get_source_file(object=file_or_object),editor_command=editor_command)
#initialize editor methods. Easier to understand when analyzing this code dynamically; static analysis might be really confusing
__known_editors=['vim','emacs','suplemon','atom','sublime']# NONE of these names should intersect any methods or varables in the r module or else they will be overwritten!
for __editor in __known_editors:
    exec("""
def X(file_or_object):
    edit(file_or_object,editor_command='X')""".replace('X',__editor))
del __known_editors,__editor# This is just a setup section to create methods for us, so get rid of the leftovers. __known_editors and __editor are assumed to be unused anywhere else in our current namespace!dz
def xo(file_or_object):# FYI: 'xo' stands for 'exofrills', a console editor. I haven't used it much though. I don't really use console based editors much…
    import xo
    try:
        if not isinstance(file_or_object,str):
            file_or_object=get_source_file(file_or_object)
        xo.main([file_or_object])
    except:
        print("Failed to start exofrills editor")
#endregion


namespace="set(list(locals())+list(globals())+list(dir()))"  # eval-uable
xrange=range#To make it more compatiable when i copypaste py2 code

term='pseudo_terminal(locals(),globals())'# For easy access: exec(term). Can use in the middle of other methods!


# region This section MUST come last! This is for if we're running the 'r' class as the main thread (runs pseudo_terminal)―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
def exeval(code,*dicts):
    # Evaluate or execute within descending hierarchy of dicts
    # merged_dict=merge_dicts(*reversed(dicts))# # Will merge them in descending priority of dicts' namespaces

    #region HOPEFULLY just a temporary patch
    # assert len(dicts)<=1
    # if len(dicts)<=1:
    # print("exeval")
    merged_dict=dicts[0]
    #endregion

    try:
        ans=eval(code,merged_dict,merged_dict)
    except SyntaxError:
        ans=exec(code,merged_dict,merged_dict)# ans = None
    for d in dicts:# Place updated variables back in descending order of priority
        temp=set()
        for k in d:
            if k in merged_dict:
                d[k]=merged_dict.pop(k)
            else:
                temp.add(k)
        for k in temp:
            del d[k]
    for k in merged_dict:# If we declared new variables, put them on the top-priority dict
        dicts[0][k]=merged_dict[k]
    return ans

# def parse(code):
#     # Takes care of:
#     #   - Lazy parsers
#     #   - Indentation fixes
#     #   -
#     pass

def dec2bin(f):
    # Works with fractions
    # SOURCE: http://code.activestate.com/recipes/577488-decimal-to-binary-conversion/
    import math
    if f >= 1:
        g = int(math.log(float(f), 2))
    else:
        g = -1
    h = g + 1
    ig = math.pow(2, g)
    st = ""
    while f > 0 or ig >= 1:
        if f < 1:
            if len(st[h:]) >= 10: # 10 fractional digits max
                break
        if f >= ig:
            st = st + "1"
            f = f - ig
        else:
            st += "0"
        ig /= 2
    st = st[:h] + "." + st[h:]
    return st

import rp.rp_ptpython.prompt_style as ps
Đ_python_input_eventloop = None#Singleton for python_input
Đ_ipython_shell = None#Singleton for python_input
def python_input(scope,header='',enable_ptpython=True,iPython=True):
    if not enable_ptpython:
        return input(header)
    try:
        from prompt_toolkit.shortcuts import create_eventloop
        from rp.rp_ptpython.python_input import PythonCommandLineInterface,PythonInput as Pyin
        if iPython:
            from rp.rp_ptpython.ipython import IPythonInput as Pyin,InteractiveShellEmbed
            global Đ_ipython_shell
            if Đ_ipython_shell is None:
                Đ_ipython_shell=InteractiveShellEmbed()
            pyin=Pyin(Đ_ipython_shell,get_globals=scope)
        else:
            pyin=Pyin(get_globals=scope)
        global Đ_python_input_eventloop
        pyin.enable_mouse_support=False
        pyin.enable_history_search=True
        pyin.highlight_matching_parenthesis=True
        pyin.enable_input_validation=False
        pyin.enable_auto_suggest=False
        pyin.show_line_numbers=True
        pyin.enable_auto_suggest=True
        pyin.show_signature=True
        # pseudo_terminal(pyin)
        # exec(mini_terminal)
        pyin.all_prompt_styles['Pseudo Terminal']=ps.PseudoTerminalPrompt()
        if not currently_running_windows():
            pyin.prompt_style='Pseudo Terminal'
        # ps.PseudoTerminalPrompt=PseudoTerminalPrompt

        Đ_python_input_eventloop=Đ_python_input_eventloop or PythonCommandLineInterface(create_eventloop(),python_input=pyin)
        #
        # try:
        code_obj = Đ_python_input_eventloop.run()
        if code_obj.text is None:
            print("THE SHARKMAN SCREAMS")
        return code_obj.text
    except Exception as E:
        print_stack_trace(E)

        return input(header)

class pseudo_terminal_style:
    def __init__(self):
        self.header=fansi(" ⮤ " if terminal_supports_unicode() else " >>> ",'cyan')
        self.message="pseudo_terminal() ⟹ Entering interactive session! "
"""
TODO:
    - Does NOT return anything
    - Can be used like MiniTerminal
    - But should be able to accept arguments for niche areas! Not sure how yet; should be modular though somehow...
    - History for every variable
    - Scope Hierarchy: [globals(),locals(),others()]:
        - Create new dict that's the composed of all the others then update them accordingly
    - HIST: Contains a list of dicts, whose differences can be seen

"""
def pseudo_terminal(*dicts,get_user_input=python_input,modifier=None,style=pseudo_terminal_style(),enable_ptpython=True):
    # TODO: Make better error reports than are available by default in python! Let it debug things like nested parenthesis and show where error came from instead of just throwing a tantrum.
    # @author: Ryan Burgert 2016，2017，2018
    try:
        import readline# Makes pseudo_terminal nicer to use if in a real terminal (AKA if using pseudo_terminal on the terminal app on a mac); aka you can use the up arrow key to go through history etc.
    except:
        pass# Not important if it fails
    # from r import fansi_print,fansi,space_split,is_literal,string_from_clipboard,mini_editor,merge_dicts,print_stack_trace# Necessary imports for this method to function properly.
    import rp.r_iterm_comm# Used to talk to ptpython

    def level_label(change=0):
        return (("(Level "+str(rp.r_iterm_comm.pseudo_terminal_level)+")")if rp.r_iterm_comm.pseudo_terminal_level else "")
    try:
        fansi_print(style.message + level_label(),'blue','bold')
        rp.r_iterm_comm.pseudo_terminal_level+=1

        from copy import deepcopy,copy

        def dictify(d):# If it's an object and not a dict, use it's __dict__ attribute
            if isinstance(d,dict):
                return d
            return d.__dict__
        # dicts=[{"ans":None},*map(dictify,dicts)]# Keeping the 'ans' variable separate. It has highest priority

        def dupdate(d,key,default=None):  # Make sure a key exists inside a dict without nessecarily overwriting it
            if key not in d:
                d[key]=default

        dupdate(dicts[0],'ans')

        def scope():
            return merge_dicts(*reversed(dicts))

        def equal(a,b):
            if a is b:
                return True

            try:
                if get_bytecode(a)==get_bytecode(b)!=get_bytecode(None):# becaue get_bytecode(None)==get_bytecode(3)==get_bytecode(3498234)
                    return True# Don't return false otherwise
            except:pass
            try:
                if a==b:
                    return True
                # else:
                #     exec(mini_terminal)
                return a==b # Fails on numpy arrays
            except:pass
            return a is b # Will always return SOMETHING at least

        def deep_dark_dict_copy(d):
            # out={}
            # for k in d:
            #     out[k]=d[k]
            # return out
            out={}
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")# /Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/copy.py:164: RuntimeWarning: use movie: No module named 'pygame.movie'
                for k in d:
                    try:
                        try:
                            q=deepcopy(d[k])
                            if equal(d[k],q):
                                out[k]=deepcopy(d[k])
                            else:
                                raise Exception
                        except:
                            # print("Deepcopy failed: "+k)
                            q=copy(d[k])
                            if equal(d[k],q):
                                out[k]=copy(d[k])
                            else:
                                raise Exception
                    except:
                        # print("Copy failed: "+k)
                        out[k]=d[k]# Failed to copy
            return out

        def get_snapshot():# Snapshot of our dicts/scope
            # exec(mini_terminal)
            return list(map(deep_dark_dict_copy,dicts))
        def set_snapshot(snapshot):
            # snapshot is a list of dicts to replace *dicts
            for s,d in zip(snapshot,dicts):
                assert isinstance(d,dict)
                assert isinstance(s,dict)
                sk=set(s)  # snapshot keys
                dk=set(d)  # dict keys
                changed=False
                for k in dk-sk :  # -{'__builtins__'}:# '__builtins__' seems to be put there as a consequence of using eval or exec, no matter what we do with it. It also is confusing and annoying to see it pop up when reading the results of UNDO
                    # assert isinstance(k,str)
                    print(fansi("    - Removed: ",'red')+k)
                    changed=True
                    del d[k]
                for k in sk-dk :  # -{'__builtins__'}:
                    # assert isinstance(k,str)
                    print(fansi("    - Added: ",'green')+k)
                    changed=True
                    d[k]=s[k]
                for k in dk&sk :  # -{'__builtins__'}:
                    assert k in dk
                    assert k in sk
                    assert isinstance(k,str)
                    if not equal(s[k],d[k]):# To avoid spam
                        print(fansi("    - Changed: ",'blue')+k)
                        changed=True
                        d[k]=s[k]
                return changed
        def take_snapshot():
            snapshot_history.append(get_snapshot())

        def get_ans():
            dupdate(dicts[0],'ans')
            return dicts[0]['ans']# This should exist

        # A little python weridness demo: ⮤print(999 is 999)⟶True BUT ⮤a=999⮤print(a is 999)⟶False
        def set_ans(val,save_history=True,snapshot=True):
            dupdate(dicts[0],'ans')
            if snapshot:# default: save changes in a snapshot BEFORE making modifications to save current state! snapshot_history is independent of ans_history
                take_snapshot()
            if save_history:
                ans_history.append(get_ans())
            dicts[0]['ans']=val
            fansi_print("ans = " + str(val),'green'if save_history else 'yellow')

        def print_history():
            fansi_print("HISTORY ⟹ Here is a list of all valid python commands you have entered so far (green means it is a single-line command, whilst yellow means it is a multi-lined command):",'blue','underlined')
            for x in successful_command_history:
                fansi_print(x,'yellow' if '\n' in x else'green')  # Single line commands are green, and multi-line commands are yellow

        display_help_message_on_error=True# A flag that will turn off the first time it displays "Sorry, but that command caused an error that pseudo_terminal couldn't fix! Command aborted. Type 'HELP' for instructions on pseudo_terminal. To see the full error traceback, type 'MORE'." so that we don't bombard the user with an unnessecary amount of stuff
        successful_command_history=[]
        snapshot_history=[]
        ans_history=[]
        user_created_var_names=set()
        allow_keyboard_interrupt_return=False
        use_modifier=True# Can be toggled with pseudo_terminal keyword commands, enumerated via 'HELP'
        error=None# For MORE
        last_assignable=last_assignable_candidate=None
        assignable_history={}

        try:
            while True:
                try:
                    # region Get user_message, xor exit with second keyboard interrupt
                    try:
                        #region Communicate with ptpython via r_iterm_comm
                        def try_eval(x):
                            temp=sys.stdout.write
                            try:
                                out="eval("+repr(x)+") = \n"
                                sys.stdout.write=_muted_stdout_write
                                s=scope()
                                out=out+str((eval(x,merge_dicts(s,globals(),locals()))))#  + '\nans = '+str(dicts[0]['ans'])
                                rp.r_iterm_comm.rp_evaluator_mem=out
                                return str(out)+"\n"
                            except Exception as E:
                                return str(rp.r_iterm_comm.rp_evaluator_mem)+"\nERROR: "+str(E)
                            finally:
                                sys.stdout.write=temp
                        rp.r_iterm_comm.rp_evaluator=try_eval
                        rp.r_iterm_comm.rp_VARS_display=str(' '.join(sorted(list(user_created_var_names))))
                        # endregion
                        user_message=get_user_input(lambda:scope(),header=style.header,enable_ptpython=enable_ptpython)
                        allow_keyboard_interrupt_return=False
                    except KeyboardInterrupt:
                        if allow_keyboard_interrupt_return:
                            fansi_print("Caught repeated KeyboardInterrupt ⟹ RETURN",'cyan','bold')
                            user_message="RETURN"
                        else:
                            allow_keyboard_interrupt_return=True
                            raise
                    # endregion
                    user_created_var_names&=set(scope())# Make sure that the only variables in this list actually exist. For example, if we use 'del' in pseudo_terminal, ∄ code to remove it from this list (apart from this line of course)
                    # region Non-exevaluable Terminal Commands (Ignore user_message)
                    if user_message == 'RETURN':
                        if get_ans() is None:
                            fansi_print("r.pseudo_terminal() ⟹ Session end. No value returned.",'blue','bold')
                        else:
                            fansi_print("r.pseudo_terminal() ⟹ Session end. Returning ans = " + str(get_ans()),'blue','bold')
                        return get_ans()
                    elif user_message == 'HELP':
                        display_help_message_on_error=True# Seems appropriate if they're looking for help
                        fansi_print("HELP ⟹ Here are the instructions:",'blue','underlined')
                        fansi_print("""    For those of you unfamiliar, this will basically attempt to exec(input()) repeatedly.",'blue')
        Note that you must import any modules you want to access; this terminal runs inside a def.
            If the command you enter returns a value other than None, a variable called 'ans' will be assigned that value.
        If the command you enter returns an error, pseudo_terminal will try to fix it, and if it can't it will display a summary of the error.
        Enter 'HISTORY' without quotes to get a list of all valid python commands you have entered so far, so you can copy and paste them into your code.
        Enter 'PASTE' without quotes to run what is copied to your clipboard, allowing you to run multiple lines at the same time
        Enter 'MORE' without quotes to see the full error traceback of the last error, assuming the last attempted command caused an error.
        Enter 'RETURN' without quotes to end the session, and return ans as the output value of this function.
        Note: rinsp is automatically imported into every pseudo_terminal instance; use it to debug your code really easily!
        "rinsp ans 1" is parsed to "rinsp(ans,1)" for convenience (generalized to literals etc)
        "+ 8" is parsed to "ans + 8" and ".shape" is parsed into
        Enter 'MODIFIER ON', 'MODIFIER OFF', 'VARS', 'MORE', 'RETURN NOW', 'EDIT', 'GHISTORY', 'COPY', 'SPASTE', 'CHISTORY', 'DITTO' ""","blue")
                    elif user_message == 'HISTORY':print_history()
                    elif user_message == 'GHISTORY':
                        fansi_print("GHISTORY ≣ GREEN HISTORY ⟹ Here is a list of all valid single-lined python commands you have entered so far:",'blue','underlined')
                        for x in successful_command_history:
                            fansi_print(x if '\n' not in x else '','green')  # x if '\\n' not in x else '' ≣ '\\n' not in x and x or ''
                    elif user_message == 'CHISTORY':
                        from rp import copy
                        fansi_print("CHISTORY ≣ COPY HISTORY ⟹ Copied history to clipboard!",'blue','underlined')
                        copy('\n'.join(successful_command_history))
                    elif user_message == "MORE":
                        fansi_print("The last command that caused an error is shown below in magenta:",'red','bold')
                        fansi_print(error_message_that_caused_exception,'magenta')
                        if error is None:# full_exception_with_traceback is None ⟹ Last command did not cause an error
                            fansi_print( "(The last command did not cause an error)",'red')
                        else:
                            print_stack_trace(error,True,'')
                    elif user_message == "MODIFIER OFF":
                        fansi_print("MODIFIER OFF ⟹ use_modifier=False","blue")
                        use_modifier=False
                    elif user_message == "MODIFIER ON":
                        fansi_print("MODIFIER ON ⟹ use_modifier=True","blue")
                        use_modifier=True
                    elif user_message == "COPY":
                        from rp import copy
                        fansi_print("COPY ⟹ r.copy(str(ans))","blue")
                        copy(str(get_ans()))
                    elif user_message == "VARS":
                        fansi_print("VARS ⟹ ans = user_created_variables (AKA all the names you created in this pseudo_terminal session):","blue")
                        fansi_print("  • NOTE: ∃ delete_vars(ans) and globalize_vars(ans)","blue")
                        set_ans(user_created_var_names,save_history=True)
                    elif user_message in {"#PREV","PREV"}:
                        fansi_print("PREV ⟹  ans = ‹the previous value of ans›:","blue")
                        if not ans_history:
                            fansi_print("    [Cannot get PREV ans because ans_history is empty]",'red')
                        else:
                            set_ans(ans_history.pop(),save_history=False)
                            successful_command_history.append("#PREV")# We put this here in case the user wants to analyze the history when brought back into normal python code
                    elif user_message in {"UNDO","#UNDO"}:
                        fansi_print("UNDO ⟹ UNDO (still a work in progress):","blue")
                        if not snapshot_history:
                            fansi_print("    [Cannot UNDO anything right now because snapshot_history is empty]",'red')
                        else:
                            while snapshot_history and not set_snapshot(snapshot_history.pop()):# Keep undoing until something changes
                                successful_command_history.append("#UNDO")# We put this here in case the user wants to analyze the history when brought back into normal python code
                            successful_command_history.append("#UNDO")# We put this here in case the user wants to analyze the history when brought back into normal python code
                            # set_snapshot([{},{},{}])
                    # endregion
                    # region  Short-hand rinsp
                    elif user_message == "?":
                        fansi_print("? ⟹ rinsp(ans)","blue")
                        rinsp(get_ans())
                    elif user_message == "??":
                        fansi_print("?? ⟹ rinsp(ans,1)","blue")
                        rinsp(get_ans(),1)
                    elif user_message == "???":
                        fansi_print("??? ⟹ rinsp(ans,1,1)","blue")
                        rinsp(get_ans(),1,1)
                    elif user_message == "????":
                        fansi_print("???? ⟹ rinsp(ans,1,0,1)","blue")
                        rinsp(get_ans(),1,0,1)
                    elif user_message == "?????":
                        fansi_print("????? ⟹ rinsp(ans,1,1,1)","blue")
                        rinsp(get_ans(),1,1,1)
                    elif user_message.endswith("?????"):
                        fansi_print("◊????? ⟹ rinsp(◊,1,1,1)","blue")
                        rinsp(eval(user_message[:-5],scope()),1,1,1)
                    elif user_message.endswith("????"):
                        fansi_print("◊???? ⟹ rinsp(◊,1,0,1)","blue")
                        rinsp(eval(user_message[:-4],scope()),1,0,1)
                    elif user_message.endswith("???"):
                        fansi_print("◊??? ⟹ rinsp(◊,1,1)","blue")
                        rinsp(eval(user_message[:-3],scope()),1,1)
                    elif user_message.endswith("??"):
                        fansi_print("◊?? ⟹ rinsp(◊,1)","blue")
                        rinsp(eval(user_message[:-2],scope()),1)
                    elif user_message.endswith("?"):
                        fansi_print("◊? ⟹ rinsp(◊)","blue")
                        rinsp(eval(user_message[:-1],scope()))
                    # endregion
                    else:
                        if user_message == "SHELL":
                            fansi_print("SHELL ⟹ entering Xonsh shell","blue")
                            user_message='import xonsh.main;xonsh.main.main()'
                        elif user_message == "IPYTHON":
                            fansi_print("IPYTHON ⟹ embedding iPython","blue")
                            # user_message='import IPython;IPython.embed()'
                            user_message='import rp.rp_ptpython.ipython;rp.rp_ptpython.ipython.embed()'
                        # region Alternate methods of user_input (PASTE/EDIT/DITTO etc)
                        elif user_message == 'PASTE':
                            fansi_print("PASTE ⟹ Running code from your clipboard (shown in yellow below):",'blue','underlined')
                            user_message=string_from_clipboard()
                            fansi_print(user_message,"yellow")
                        elif user_message == 'SPASTE':
                            fansi_print("PASTE ⟹ ans=str(string_from_clipboard()):",'blue','underlined')
                            user_message=repr(string_from_clipboard())
                        elif user_message == 'DITTO':
                            if not successful_command_history:
                                fansi_print("DITTO ⟹ Cannot use DITTO, the successful_command_history is empty!",'red')
                                user_message=""# Ignore it
                            else:
                                fansi_print("DITTO ⟹ re-running last successful command shown below in yellow:",'blue','underlined')
                                user_message=successful_command_history[-1]
                                fansi_print(user_message,"yellow")
                        elif user_message == 'EDIT':
                            user_message=mini_editor("",list(scope()))
                            fansi_print("EDIT ⟹ Replacing EDIT with your custom text, shown below in yellow:",'blue','underlined')
                            fansi_print(user_message,'yellow')
                        # endregion
                        # region Modifier
                        if use_modifier and modifier is not None:
                            try:
                                new_message=modifier(user_message)
                                original_user_message=user_message
                                user_message=new_message
                            except Exception as E:
                                original_user_message=None
                                fansi_print("ERROR: Failed to modify your command. Attempting to execute it without modifying it.","red","bold")
                        # endregion
                        # region Lazy-Parsers:Try to parse things like 'rinsp ans' into 'rinsp(ans)' and '+7' into 'ans+7'
                        # from r import space_split
                        current_var=rp.r_iterm_comm.last_assignable_comm
                        if current_var is not None and user_message in ['+','-','*','/','%','//','**','&','|','^','>>','<<']+['and','or','not','==','!=','>=','<=']+['>','<','~']:
                            user_message='ans ' + user_message +' ' + current_var
                            fansi_print("Parsed command into " + repr(user_message),'magenta')
                        else:
                            if user_message.startswith("!!"):# For shell commands
                                user_message="shell_command("+repr(user_message[2:])+")"
                                fansi_print("Parsed command into " + repr(user_message),'magenta')
                            elif user_message.startswith("!"):# For shell commands
                                user_message="shell_command("+repr(user_message[1:])+",True)"
                                fansi_print("Parsed command into " + repr(user_message) ,'magenta')
                            if True and len(user_message.split("\n")) == 1:  # If we only have 1 line: no pasting
                                _thing=space_split(user_message)
                                if len(_thing) > 1:
                                    # from r import is_literal
                                    bracketeers="()"
                                    try:
                                        if hasattr(eval(_thing[0]),'__getitem__'):
                                            bracketeers="[]"
                                    except:
                                        pass
                                    flaggy=False
                                    if all(map(is_literal,_thing)):  # If there are no ';' or ',' in the arguments; just 'rinsp' or 'ans' etc
                                        user_message=_thing[0] + bracketeers[0] + ','.join(_thing[1:]) + bracketeers[1]
                                        flaggy=True
                                    elif is_literal(_thing[0]):
                                        user_message=_thing[0] + bracketeers[0] + " " + repr(user_message[len(_thing[0]):]) + bracketeers[1]
                                        flaggy=True
                                    if flaggy:
                                        fansi_print("Parsed command into " + repr(user_message),'magenta')
                            if user_message.lstrip():
                                try:
                                    float(user_message)  # could be a negative number; we dont want Parsed command into 'ans -1324789'
                                except:
                                    arg_0=user_message.lstrip()
                                    if arg_0=='=' or last_assignable and (arg_0[0] == '=' and arg_0[1] != "=" or arg_0[0:2] in ['+=','-=','*=','/=','&=','|=','^=','%='] or arg_0[:3] in ['//=','**=','<<=','>>=']):
                                        if not last_assignable in assignable_history:
                                            assignable_history[last_assignable]=[]
                                        else:
                                            assignable_history[last_assignable].append(eval(last_assignable,scope()))
                                        user_message=last_assignable + user_message
                                        fansi_print("Parsed command into " + repr(user_message),'magenta')
                                    elif arg_0[0] in '.+-/*^=><&|' or space_split(user_message.lstrip().rstrip())[0] in ['and','or','is']:
                                        user_message='ans ' + user_message
                                        fansi_print("Parsed command into " + repr(user_message),'magenta')
                            if user_message.rstrip().endswith("="):
                                user_message=user_message + ' ans'
                                fansi_print("Parsed command into " + repr(user_message),'magenta')
                            # from r import is_namespaceable
                            if True and (user_message.replace("\n","").lstrip().rstrip() and not '\n' in user_message and (("=" in user_message.replace("==","") and not any(x in user_message for x in ["def ",'+=','-=','*=','/=','&=','|=','^=','%='] + ['//=','**=','<<=','>>='])) or is_namespaceable(''.join(set(user_message) - set(",.:[] \\t1234567890"))))):  # Doesn't support tuple unpacking because it might confuse it with function calls. I.E. f(x,y)=z looks like (f,x)=y to it
                                last_assignable_candidate=user_message.split("=")[0].lstrip().rstrip()
                                if last_assignable_candidate.startswith("import "):
                                    last_assignable_candidate=last_assignable_candidate[7:]
                            else:
                                pass
                        # endregion
                        while user_message:  # Try to correct any errors we might find in their code that may be caused mistakes made in the pseudo_terminal environment
                            # region Try to evaluate/execute user_message
                            if last_assignable_candidate:
                                last_assignable=last_assignable_candidate
                                import rp.r_iterm_comm
                                rp.r_iterm_comm.last_assignable_comm=last_assignable
                            try:
                                scope_before=set(scope())
                                take_snapshot()# Taken BEFORE modifications to save current state!
                                result=exeval(user_message,*dicts)
                                # raise KeyboardInterrupt()
                                if result is None:
                                    successful_command_history.append(user_message)
                                else:
                                    dupdate(dicts[0],'ans')
                                    set_ans(result,save_history=not equal(result,dicts[0]['ans']),snapshot=False)# snapshot=False beacause we've already taken a snapshot! Only saves history if ans changed, though. If it didn't, you'll see yellow text instead of green text
                                    if user_message.lstrip().rstrip()!='ans':# Don't record 'ans=ans'; that's useless. Thus, we can view 'ans' without clogging up successful_command_history
                                        successful_command_history.append("ans="+user_message)# ans_history is only changed if there is a change to ans, but command history is always updated UNLESS user_message=='ans' (having "ans=ans" isn't useful to have in history)
                                user_created_var_names=user_created_var_names|(set(scope())-scope_before)
                                break
                            # endregion
                            # region  Try to fix user_input, or not use modifier etc
                            except IndentationError as E:
                                if style.header in user_message:  # They probably just copied and pasted one of their previous commands from the console. If they did that it would contain the header which would cause an error. So, we delete the header.
                                    print(type(E))
                                    fansi_print("That command caused an error, but it contained '" + style.header + "' without quotes. Running your command without any '" + style.header + "'_s, shown below in magenta:","red","bold")
                                    user_message=user_message.replace(style.header,"")  # If we get an error here, try getting rid of the headers and then try again via continue...
                                    fansi_print(user_message,"magenta")
                                elif user_message.lstrip() != user_message:  # If our string is only one line long, try removing the beginning whitespaces...
                                    fansi_print("That command caused an error, but it contained whitespace in the beginning. Running your command without whitespace in the beginning, shown below in magenta:","red","bold")
                                    user_message=user_message.lstrip()  # If we get an error here, try getting rid of the headers and then try again via continue...
                                    fansi_print(user_message,"magenta")
                                else:
                                    raise  # We failed to fix the indentation error. We can't fix anything, so return the error and effectively break the while loop.
                            except:
                                if use_modifier and modifier is not None and original_user_message is not None:# If we're using the modifier and we get a syntax error, perhaps it'_s because the user tried to input a regular command! Let them do that, meaning they have to use the 'MODIFIER ON' and 'MODIFIER OFF' keywords less than they did before.
                                    fansi_print("That command caused an error, but it might have been because of the modifier. Trying to run the original command (without the modifier) shown below in magenta:","red","bold")
                                    # noinspection PyUnboundLocalVariable
                                    fansi_print(user_message,"magenta")
                                    user_message=original_user_message # ⟵ We needn't original_user_message=None. This will literally never happen when use_modifier==True
                                    original_user_message=None# We turn original_user_message to None so that we don't get an infinite loop if we get a syntax error with use_modifier==True.
                                else:
                                    raise
                            # endregion
                    rp.r_iterm_comm.globa=scope()
                except Exception as E:
                    if display_help_message_on_error:
                        display_help_message_on_error=False
                        fansi_print("""Sorry, but that command caused an error that pseudo_terminal couldn't fix! Command aborted.
        Type 'HELP' for instructions on how to use pseudo_terminal in general.
        To see the full traceback of any error, type 'MORE'.
        NOTE: This will be the last time you see this message, unless you enter 'HELP' without quotes.""",'red','bold')
                    error_message_that_caused_exception=user_message# so we can print it in magenta if asked to by 'MORE'
                    print_stack_trace(E,False,'ERROR: ')
                    error=E
                except KeyboardInterrupt:
                    print(fansi('Caught keyboard interrupt','cyan','bold'),end='')
                    if allow_keyboard_interrupt_return:
                        print(fansi(': Interrupt again to RETURN','cyan','bold'),end='')
                    print()
        except BaseException as E:
            print(fansi('FATAL ERROR: Something went very, very wrong. Printing HISTORY so you can recover!','red','bold'))
            print_stack_trace(E)
            print_history()
    finally:
        rp.r_iterm_comm.pseudo_terminal_level-=1
        if level_label():
            fansi_print("    - Exiting pseudo-terminal at "+level_label(),'blue' ,'bold')

# @formatter:off
try:from setproctitle import setproctitle as set_process_title \
        ,getproctitle as get_process_title
except:pass
#@formatter:on

def parenthesizer_automator(x:str):
    # Parenthesis automator for python
    l=lambda q:''.join('(' if x in '([{' else ')' if x in ')]}' else ' ' for x in q)
    def p(x,r=True):
        y=list(l(x))
        if not r and ('(' not in y or ')' not in y):
            return [x]
        n=None
        for i,e in enumerate(y):
            if e == '(':
                n=i
            elif e == ')':
                if n is not None:
                    y[i]='>'
                    y[n]='<'
                    n=None
            else:
                y[i]=' '
        y=''.join(y)
        if r:
            y=p(y,False)
            assert isinstance(y,list)
            y=[x.replace('(','│').replace(')','│').replace('<','┌').replace('>','┐') for x in y]
            z=[x.replace('┌','└').replace('┐','┘') for x in y]
            return '\n'.join(y[::-1] + [x] + z)
        return [x] + p(y,False)
    return p(x)

def timeout(f,t):
    import signal

    class TimeoutException(BaseException):   # Custom exception class
        pass

    def timeout_handler(signum, frame):   # Custom signal handler
        raise TimeoutException

    # Change the behavior of SIGALRM
    signal.signal(signal.SIGALRM, timeout_handler)
    # https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time
    # Start the timer. Once 5 seconds are over, a SIGALRM signal is sent.
    signal.alarm(t)
    # This try/except loop ensures that
    #   you'll catch TimeoutException when it's sent.
    try:
        return f()
    except TimeoutException:
        return "[Timed out]"# continue the for loop if function A takes more than 5 second

try:
    from numpngw import write_apng as save_animated_png#Takes numpy ndarray as input
except:
    pass

def pterm():
    pseudo_terminal(locals(),globals())
if __name__ == "__main__":
    pterm()
# endregion



# TODO: Mini-Terminal, Stereo audio recording/only initialize stream if using audio, Plot over images, error stack-printing extract from pseudo_terminal,
# TODO: See 'pseudolambdaidea' file
# TODO: Git auto-commit: see 'ryan_autogitter.py' file
# TODO: A more detailed pseudo_terminal history
# TODO: Make pseudo_temrinal open source!!!!
# TODO: Make a command for pseudo_terminal to kill the current command's execution. Make it so that we try to run all commands as a thread, but we kill those threads if we type "CANCEL" or "ABORT" or something so we dont need to close pseudo_terminal to cancel the process.
#
#
# class blank:# Just a placeholder for call_non_blank_parameters
#     pass
# def call_non_blank_parameters(f,*args,**kwargs):#will be used to streamline my use of te Đ
#     assert callable(f)
#     Đ_args=f.
#     args=[args]
