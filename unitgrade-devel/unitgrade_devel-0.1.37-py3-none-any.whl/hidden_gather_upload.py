from unitgrade.evaluate import evaluate_report, python_code_str_id
import lzma
import base64
import textwrap
import hashlib
import bz2
import pickle
import os
import zipfile
import io


def bzwrite(json_str, token): # to get around obfuscation issues
    with getattr(bz2, 'open')(token, "wt") as f:
        f.write(json_str)


def gather_imports(imp):
    resources = {}
    m = imp
    f = m.__file__
    if hasattr(m, '__file__') and not hasattr(m, '__path__'):
        top_package = os.path.dirname(m.__file__)
        module_import = True
    else:
        im = __import__(m.__name__.split('.')[0])
        if isinstance(im, list):
            print("im is a list")
            print(im)
        # the __path__ attribute *may* be a string in some cases. I had to fix this.
        print("path.:",  __import__(m.__name__.split('.')[0]).__path__)
        # top_package = __import__(m.__name__.split('.')[0]).__path__._path[0]
        top_package = __import__(m.__name__.split('.')[0]).__path__[0]
        module_import = False

    found_hashes = {}
    # pycode = {}
    resources['pycode'] = {}
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip:
        for root, dirs, files in os.walk(top_package):
            for file in files:
                if file.endswith(".py"):
                    fpath = os.path.join(root, file)
                    v = os.path.relpath(fpath, os.path.dirname(top_package) if not module_import else top_package)
                    zip.write(fpath, v)
                    if not fpath.endswith("_grade.py"): # Exclude grade files.
                        with open(fpath, 'r') as f:
                            s = f.read()
                        found_hashes[v] = python_code_str_id(s)
                        resources['pycode'][v] = s

    resources['zipfile'] = zip_buffer.getvalue()
    resources['top_package'] = top_package
    resources['module_import'] = module_import
    resources['blake2b_file_hashes'] = found_hashes
    return resources, top_package


import argparse
parser = argparse.ArgumentParser(description='Evaluate your report.', epilog="""Use this script to get the score of your report. Example:

> python report1_grade.py

Finally, note that if your report is part of a module (package), and the report script requires part of that package, the -m option for python may be useful.
For instance, if the report file is in Documents/course_package/report3_complete.py, and `course_package` is a python package, then change directory to 'Documents/` and run:

> python -m course_package.report1

see https://docs.python.org/3.9/using/cmdline.html
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--noprogress',  action="store_true",  help='Disable progress bars')
parser.add_argument('--autolab',  action="store_true",  help='Show Autolab results')

def gather_report_source_include(report):
    sources = {}
    # print("")
    # if not args.autolab:
    if len(report.individual_imports) > 0:
        print("By uploading the .token file, you verify the files:")
        for m in report.individual_imports:
            print(">", m.__file__)
        print("Are created/modified individually by you in agreement with DTUs exam rules")
        report.pack_imports += report.individual_imports

    if len(report.pack_imports) > 0:
        print("Including files in upload...")
        for k, m in enumerate(report.pack_imports):
            nimp, top_package = gather_imports(m)
            _, report_relative_location, module_import = report._import_base_relative()

            nimp['report_relative_location'] = report_relative_location
            nimp['report_module_specification'] = module_import
            nimp['name'] = m.__name__
            sources[k] = nimp
            print(f" * {m.__name__}")
    return sources

# def report_script_relative_location(report):
#     """
#     Given the grade script corresponding to the 'report', work out it's relative location either compared to the
#     package it is in or directory.
#     """
#     if len(report.individual_imports) == 0:
#         return "./"
#     else:
#
#     pass

def gather_upload_to_campusnet(report, output_dir=None, token_include_plaintext_source=False):
    # n = report.nL
    args = parser.parse_args()
    results, table_data = evaluate_report(report, show_help_flag=False, show_expected=False, show_computed=False, silent=True,
                                          show_progress_bar=not args.noprogress,
                                          big_header=not args.autolab,
                                          )
    print("")
    sources = {}
    if not args.autolab:
        results['sources'] = sources = gather_report_source_include(report)

    token_plain = """
# This file contains your results. Do not edit its content. Simply upload it as it is. """

    s_include = [token_plain]
    known_hashes = []
    cov_files = []
    use_coverage = True
    if report._config is not None:
        known_hashes = report._config['blake2b_file_hashes']
        for Q, _ in report.questions:
            from unitgrade import UTestCase
            use_coverage = use_coverage and isinstance(Q, UTestCase)
            for key in Q._cache:
                if len(key) >= 2 and key[1] == "coverage":
                    for f in Q._cache[key]:
                        cov_files.append(f)

    for s in sources.values():
        for f_rel, hash in s['blake2b_file_hashes'].items():
            if hash in known_hashes and f_rel not in cov_files and use_coverage:
                print("Skipping", f_rel)
            else:
                if token_include_plaintext_source:
                    s_include.append("#"*3 +" Content of " + f_rel +" " + "#"*3)
                    s_include.append("")
                    s_include.append(s['pycode'][f_rel])
                    s_include.append("")

    if output_dir is None:
        output_dir = os.getcwd()

    payload_out_base = report.__class__.__name__ + "_handin"

    obtain, possible = results['total']
    vstring = "_v"+report.version if report.version is not None else ""

    token = "%s_%i_of_%i%s.token"%(payload_out_base, obtain, possible,vstring)
    token = os.path.normpath(os.path.join(output_dir, token))

    save_token(results, "\n".join(s_include), token)

    if not args.autolab:
        print("> Testing token file integrity...", sep="")
        load_token(token)
        print("Done!")
        print(" ")
        print("To get credit for your results, please upload the single unmodified file: ")
        print(">", token)



def dict2picklestring(dd):
    b = lzma.compress(pickle.dumps(dd))
    b_hash = hashlib.blake2b(b).hexdigest()
    return base64.b64encode(b).decode("utf-8"), b_hash

def picklestring2dict(picklestr):
    b = base64.b64decode(picklestr)
    hash = hashlib.blake2b(b).hexdigest()
    dictionary = pickle.loads(lzma.decompress(b))
    return dictionary, hash


token_sep = "-"*70 + " ..ooO0Ooo.. " + "-"*70
def save_token(dictionary, plain_text, file_out):
    if plain_text is None:
        plain_text = ""
    if len(plain_text) == 0:
        plain_text = "Start token file"
    plain_text = plain_text.strip()
    b, b_hash = dict2picklestring(dictionary)
    b_l1 = len(b)
    b = "."+b+"."
    b = "\n".join( textwrap.wrap(b, 180))

    out = [plain_text, token_sep, f"{b_hash} {b_l1}", token_sep, b]
    with open(file_out, 'w') as f:
        f.write("\n".join(out))

def load_token(file_in):
    with open(file_in, 'r') as f:
        s = f.read()
    splt = s.split(token_sep)
    data = splt[-1]
    info = splt[-2]
    head = token_sep.join(splt[:-2])
    plain_text=head.strip()
    hash, l1 = info.split(" ")
    data = "".join( data.strip()[1:-1].splitlines() )
    l1 = int(l1)

    dictionary, b_hash = picklestring2dict(data)

    assert len(data) == l1
    assert b_hash == hash.strip()
    return dictionary, plain_text


def source_instantiate(name, report1_source, payload):
    eval("exec")(report1_source, globals())
    pl = pickle.loads(bytes.fromhex(payload))
    report = eval(name)(payload=pl, strict=True)
    return report
