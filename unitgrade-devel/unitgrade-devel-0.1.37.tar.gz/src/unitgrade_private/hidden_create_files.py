from unitgrade import evaluate
import jinja2
import pickle
import inspect
import time
import os
from unitgrade_private import hidden_gather_upload
import sys

data = """
{{head}}

report1_source = {{source}}
report1_payload = '{{payload}}'
name="{{Report1}}"

report = source_instantiate(name, report1_source, report1_payload)
output_dir = os.path.dirname(__file__)
gather_upload_to_campusnet(report, output_dir)
"""


def strip_main(report1_source):
    dx = report1_source.find("__main__")
    report1_source = report1_source[:dx]
    report1_source = report1_source[:report1_source.rfind("\n")]
    return report1_source


def rmimports(s, excl):
    s = "\n".join([l for l in s.splitlines() if not any([l.strip().startswith(e) for e in excl])])
    return s

def lload(flist, excl):
    s = ""
    for fname in flist:
        with open(fname, 'r', encoding="utf-8") as f:
            s += f.read() + "\n" + "\n"
    s = rmimports(s, excl)  # remove import statements from helper class.
    return s

def setup_grade_file_report(ReportClass, execute=False, obfuscate=False, minify=False, bzip=True, nonlatin=False, source_process_fun=None, with_coverage=True):
    print("Setting up answers...")
    report = ReportClass()
    payload = report._setup_answers(with_coverage=with_coverage)
    payload['config'] = {}
    from unitgrade_private.hidden_gather_upload import gather_report_source_include
    sources = gather_report_source_include(report)
    known_hashes = [v for s in sources.values() for v in s['blake2b_file_hashes'].values() ]
    # assert len(known_hashes) == len(set(known_hashes)) # Check for collisions.
    payload['config']['blake2b_file_hashes'] = known_hashes
    time.sleep(0.1)
    print("Packing student files...")
    # pack report into a binary blob thingy the students can run on their own.
    # report = ReportClass()
    fn = inspect.getfile(ReportClass)
    with open(fn, 'r') as f:
        report1_source = f.read()
    report1_source = strip_main(report1_source)

    # Do fixing of source. Do it dirty/fragile:
    if source_process_fun == None:
        source_process_fun = lambda s: s

    report1_source = source_process_fun(report1_source)
    picklestring = pickle.dumps(payload)

    import unitgrade
    excl = ["unitgrade.unitgrade_helpers",
            "from . import",
            "from unitgrade.",
            "from unitgrade ",
            "import unitgrade"]

    report1_source = rmimports(report1_source, excl)

    pyhead = lload([evaluate.__file__, hidden_gather_upload.__file__], excl)
    from unitgrade import version
    from unitgrade import utils
    from unitgrade import runners
    print(unitgrade.__file__)
    report1_source = lload([unitgrade.__file__, utils.__file__, runners.__file__, unitgrade.framework.__file__,
                            unitgrade.evaluate.__file__, hidden_gather_upload.__file__,
                            version.__file__], excl) + "\n" + report1_source

    print(sys.getsizeof(picklestring))
    print(len(picklestring))
    s = jinja2.Environment().from_string(data).render({'Report1': ReportClass.__name__,
                                                       'source': repr(report1_source),
                                                       'payload': picklestring.hex(), #repr(picklestring),
                                                       'token_out': repr(fn[:-3] + "_handin"),
                                                       'head': pyhead})
    output = fn[:-3] + "_grade.py"
    print("> Writing student script to", output, "(this script may be shared)")
    # Add the relative location string:

    # Add relative location to first line of file. Important for evaluation/sanity-checking.
    report_relative_dir = report._import_base_relative()[1]
    s = "# " + report_relative_dir + "\n" + s

    with open(output, 'w', encoding="utf-8") as f:
        f.write(s)

    if minify or bzip:  # obfuscate:
        obs = '-O ' if obfuscate else ""
        # output_obfuscated = output[:-3]+"_obfuscated.py"
        extra = [  # "--nonlatin",
            # '--bzip2',
        ]
        if bzip: extra.append("--bzip2")
        if minify:
            obs += " --replacement-length=20"

        cmd = f'pyminifier {obs} {" ".join(extra)} -o {output} {output}'
        print(cmd)
        os.system(cmd)
        time.sleep(0.2)
        with open(output, 'r') as f:
            sauce = f.read().splitlines()
        wa = """ WARNING: Modifying, decompiling or otherwise tampering with this script, it's data or the resulting .token file will be investigated as a cheating attempt. """
        sauce = ["'''" + wa + "'''"] + sauce[:-1]
        sauce = "\n".join(sauce)
        sauce = "# " + report_relative_dir + "\n" + sauce
        with open(output, 'w') as f:
            f.write(sauce)

    if execute:
        time.sleep(0.1)
        print("Testing packed files...")
        fn = inspect.getfile(ReportClass)
        print(fn)
        s = os.path.basename(fn)[:-3] + "_grade"
        print(s)
        exec("import " + s)

    print("====== EXECUTION AND PACKING OF REPORT IS COMPLETE ======")
    return output