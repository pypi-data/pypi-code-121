import json, base64, os, pickle, datetime, string, re

__version__ = "0.1.9"
### from ipynb extract markdown and noted output for document organization

class nbparser:
    def __init__(self, path, output_root = "wiki", gitlabstyle_math = True):
        """ipynb notebook parser. from .ipynb file, generating the markdown file.

        Args:
            path (`os.Pathlike`): path of .ipynb file
        """

        self.path = path
        self.folder, self.basename  = os.path.dirname(path), os.path.splitext(os.path.basename(path))[0]
        self.notebook = json.loads("\n".join(open(path).readlines()))
        self.outroot = os.path.join(output_root,"source")
        self.opath = os.path.join(self.outroot, self.folder, self.basename)
        self.TOC, self.source = [],[]
        self.fig, self.code = [], []
        self.table = []
        self.ref = {}
        os.makedirs(self.opath, exist_ok = True)
        self.refpath = lambda fname : os.path.join(self.basename, fname)
        self.outputpath = lambda fname : os.path.join(self.opath, fname)
        self.fname = self.opath+".md"
        self.gitlab = gitlabstyle_math

    def argparse(self, commandline):
        captions = commandline.lstrip().split()
        if len(captions) == 1: 
            return "No captions"
        if captions[1][:6] == "--ref=":
            self.ref[captions[1][6:]] = len(self.fig)+1
            captions = " ".join(captions[2:])
        else:
            captions = " ".join(captions[1:])
        return captions
    
    def conversion(self):
        self.markdown_parsing()
        self.write_markdown()


    def markdown_parsing(self):
        """from notebook json instance, generating and parsing the markdown syntax.

        Args:
            notebook (_type_): jupyter notebook(.ipynb) file or json parser.

        Return:
            source : markdown source.
            fig : figure
            code : code
        """
        notebook = self.notebook
        
        fig = self.fig
        source = self.source
        code = self.code

        #### Markdown parsing
        for i, cell in enumerate(notebook['cells']):
            if not cell["source"]:continue
            if cell["cell_type"] == 'markdown': #markdown 
                a = cell["source"][0].lstrip()
                #header parsing
                if  a[0]== "#":
                    header = a.split()[0]
                    title = " ".join(a.split()[1:])
                    for character in string.punctuation:
                        if character=="-":continue
                        title = title.replace(character, '')
                    self.TOC.append((header, title))
                #command parsing
                elif a[0] == "!": 
                    command = a.split()[0][1:]
                    if command in ["toc","TOC"]:
                        source.append("!TOC")
                        continue
                    caption = self.argparse(a)
                    if command =="code": #code
                        self.parse_code(cell, notebook['cells'][i+1], captions = caption)
                        continue
                    if command =="cell": #cell
                        self.parse_code(cell, notebook['cells'][i+1], output =  True, captions = caption)
                        continue
                    if command in ["figure","fig"]: #figure
                        #figure parsing
                        self.parse_figure(cell,notebook['cells'][i-1], captions = caption)
                        continue
                    if command == "table":#Dataframe table
                        self.parse_table(cell, self.notebook["cells"][i-1], captions = caption)
                        continue
                    
                            
                source.append("".join(cell["source"]))

    def parse_figure(self, mdcell, figcell, captions):
        """From markdown cell and figure cell, extract figure and extension and markdown.

        Args:
            mdcell : markdown cell
            figcell : equivalent figure cell
        """
        for data in figcell['outputs']:
            if not 'data' in data: continue
            for key in data['data']:
                if key.split("/")[0] == "image":    
                    ext = key.split("/")[1] # PNG, JPEG, etc
                    self.fig.append((data['data'][key],captions))
                    fname = f"fig{len(self.fig)}.{ext}" # e.g.) fig1.png fig2.jpeg
                    fignum = len(self.fig)
                    self.source.append(f"![fig. {fignum}]({self.refpath(fname)})  \n**Fig. {fignum}.** {captions}  \n<br>\n")
                    self.save_fig(self.outputpath(fname), data['data'][key])

    def save_fig(self, fname, base64fig):
        
        with open(fname,"wb") as f:
            f.write(base64.b64decode(base64fig))

    def parse_code(self, mdcell, codecell, captions,  output = False):
        """From markdwon and code cell, extract code and/or text outputs.

        Parameters
        ----------
        mdcell : json dict
            markdown cell dict.
        codecell : json dict
            code cell dict

        """
        self.code.append(0) #number counting
        codenum = len(self.code)
        self.source.append(f"**Code {codenum}.** {captions}  \n")
        if output:
            self.source.append("---")
        self.source.append(f"```python\n{''.join(codecell['source'])}\n```")
        if output:
            self.source.append(f"*Outputs :*  \n")
            i = 0
            for out in codecell["outputs"]:
                if "data" in out: # display output or execute result
                    for data in out["data"]:
                        if data.split("/")[0] == "text":
                            self.source.append("    "+"    ".join(out["data"][data]))
                        elif data.split("/")[0] == "image":
                            ext = data.split("/")[1]
                            fname = f'outputs{len(self.code)}_{i}.{ext}'
                            self.source.append(f"![{ext}]({self.refpath(fname)})")
                            self.save_fig(f"{self.outputpath(fname)}", out['data'][data])
                            i+=1

                else: #stream output
                    if out["name"] =="stdout":
                        self.source.append("    "+"    ".join(out["text"]))
                    else: # std err is ignored.
                        continue 
                
            self.source.append("\n---\n")
        self.source.append("<br>\n<br>\n")

            
    def parse_table(self, mdcell, tablecell, captions):
        """From markdwon and table cell, extract table contents.

        Parameters
        ----------
        mdcell : json dict
            markdown cell dict.
        tablecell : json dict
            table cell dict

        
        """
        self.table.append(0)
        table = [out["data"]["text/html"] for out in tablecell["outputs"] if out["output_type"]=="execute_result"][0]
        #delete blank line
        table = "\n".join([line for line in "".join(table).split("\n") if line]) 
        self.source.append("".join(table))
        self.source.append(f"\n**Table {len(self.table)}.** {captions}  \n<br><br>\n")

    def toc_source(self):
        """Generate markdown source of `Table of Contents` from header in `self.TOC`.
        """
        s = ""
        for content in self.TOC:
            s += ("  "*len(content[0])+"- ["+content[1]+"](#"+"-".join(content[1].lower().split())+")  \n")
        return s
    
    def source_convert(self):
        source = [line if not line =="!TOC" else self.toc_source() for line in self.source if line] # Table of Contents
        source = "\n\n".join(source)
        
        # double bracket to ref
        refexp = "\{\{[A-Za-z-]+\}\}"
        for m in re.finditer(refexp,source):
            if m.group(0)[2:-2] in self.ref:
                source = source[:m.start()]+str(self.ref[m.group(0)[2:-2]])+source[m.end():]
        if self.gitlab:
            # math conversion
            linemath = "\$.+\$[^\$]"
            for m in re.finditer(linemath,source):
                source = source[:m.start()+1] + "`" + m.group(0)[1:-2] + "`" + source[m.end()-2:]

            cellmath = "\$\$.+\$\$"
            for m in re.finditer(cellmath,source, re.DOTALL):
                source = source[:m.start()] + "\n```math\n"+m.group(0)[2:-2]+ "\n```"+source[m.end():]
        return source

    def write_markdown(self):        
        source = self.source_convert()
        if source:
            ### Write markdown
            with open(self.fname,"w") as f:
                f.write(source)


def toc_source(TOC):
    """Generate markdown source of `Table of Contents` from header in `self.TOC`.
    """
    s = ""
    for content in TOC:
        s += (">  "*len(content[0])+"- ["+content[1]+"](#"+"-".join(content[1].lower().split())+")  \n")
    return s
    
def daily_note(note_path, check):
    if not os.path.exists(note_path):
        os.makedirs(os.path.dirname(note_path),exist_ok=True)
        with open(note_path, "w") as f:
            f.write("# Daily notes  \n---\n")
        write_daily(note_path, check, check)
        return
    p = os.path.join(os.path.dirname(note_path),"data.pickle")
    with open(p, "rb") as f:
        source = pickle.load(f)
    
    mod, record = modified_check(source, check)
    if mod:
        write_daily(note_path, mod, record)

def modified_check(source, check):
    mod = {}
    new = {}
    for i in check:
        if i in source:
            diff = check[i] - source[i]
            if diff:
                mod[i] = diff
            new[i] =  check[i] | source[i]
        else:
            mod[i] = check[i]
            new[i] = check[i]
    return mod, new

def write_daily(note_path, mod, record):
    p = os.path.join(os.path.dirname(note_path),"data.pickle")
    with open(p, "wb") as f:
        pickle.dump(record, f)

    if not mod:
        return
    #print(mod, record)    
    today = False
    for line in open(note_path):
        if line[0] != "#": continue
        line = line.rstrip()
        if line.split()[1] == str(datetime.date.today()):
            today = True

    with open(note_path, "a") as f:
        f.write("\n\n")
        if not today:
            f.write(f"## {datetime.date.today()}  \n")
            
        for file in mod:
            f.write(f"### File : [{os.path.splitext(os.path.basename(file))[0]}]({ os.path.join('..','source',os.path.splitext(file)[0])+'.md'})  \n")
            f.write("#### Added headers:  \n")
            for header in mod[file]:
                f.write(f"- {header}  \n")
            f.write("\n")


shellsource = f"""#!/bin/bash
source ~/.bashrc

{"conda activate "+os.environ["CONDA_DEFAULT_ENV"] if "CONDA_DEFAULT_ENV" in os.environ else ""}

git diff --name-only --cached >> __tmp__files

python -m nbresnote git-pre-commit

rm __tmp__files

cd wiki
git add *
if [ `git diff --cached --name-only| wc -l` -eq 0 ]
then
echo "nothing to commit"
else
git commit -m "Auto commit from nbresnote `date +%F`"
fi
"""

pushsource = """#!/bin/bash
cd wiki
git fetch && git pull && git push
"""


if __name__ =="__main__":
    import sys
    #path config
    wikipath = "wiki/"
    daily_path = os.path.join(wikipath, "daily", "daily.md")

    if not len(sys.argv)>1:
        print("Error : There is no target file.")
        exit(1)
    else:
        if sys.argv[1] =="git-pre-commit":
            targets = open("__tmp__files").readlines()
            #print(targets) #DEBUG
        elif sys.argv[1] == "install":
            #Installation
            # Setting git/hooks pre-commit and pre-push
            if not os.path.exists(".git"):
                raise OSError("Please run on the base folder of git repository.")
            if not os.path.exists(".git/hooks/pre-commit"):
                print("Creating 'pre-commit' file on '.git/hooks/'.")
                with open(".git/hooks/pre-commit","a") as f:
                    f.write(shellsource)
                print("Change mod of 'pre-commit' file on '.git/hooks/' into 755(rwxr-xr-x).")
                os.chmod(".git/hooks/pre-commit", 0o755)
            else:
                print("Warning : Already exists 'pre-commit' file on '.git/hooks/'. Command ignored.")
            if not os.path.exists(".git/hooks/pre-push"):
                print("Creating 'pre-push' file on '.git/hooks/'.")
                with open(".git/hooks/pre-push","a") as f:
                    f.write(pushsource)
                print("Change mod of 'pre-push' file on '.git/hooks/' into 755(rwxr-xr-x).")
                os.chmod(".git/hooks/pre-push", 0o755)
            else:
                print("Warning : Already exists 'pre-push' file on '.git/hooks/'. Command ignored.")
            print("Done.")
            
            exit(0)

        else:
            targets = sys.argv[1:]
    
    check = {}
    for file in targets:
        file = file.rstrip()
        if os.path.splitext(file)[1] == ".ipynb":
            notebook = nbparser(file)
            notebook.conversion()
            check[file] = set(map(lambda x:x[1],notebook.TOC))
    
    daily_note(daily_path, check)
    exit(0)
    

    

