from unitgrade.evaluate import file_id
import os
import shutil
import glob
from unitgrade_private.token_loader import unpack_sources_from_token
import mosspy
import fnmatch

def moss_prepare(whitelist_dir, submission_dir, blacklist=None):
    # Get all whitelist hashes.
    if blacklist == None:
        blacklist = []
    moss_tmp_dir = os.path.dirname(os.path.abspath(whitelist_dir)) + "/tmp"
    if os.path.isdir(moss_tmp_dir):
        shutil.rmtree(moss_tmp_dir, ignore_errors=True)

    tmp_base = moss_tmp_dir +"/base"
    os.makedirs(tmp_base)

    pys = glob.glob(whitelist_dir+"/**/*.py", recursive=True)
    white_hashes = set()
    for k, py in enumerate(pys):
        id = file_id(py)

        if id not in white_hashes:
            white_hashes.add(id)
            if not fnmatch.fnmatch(py, "*_grade.py"):
                # if fnmatch.fnmatch(py, "*fruit_homework.py"):
                print("> Whitelisting", py)
                shutil.copy(py, tmp_base + f"/{k}_" + os.path.basename(py))


    tmp_submission_dir = moss_tmp_dir + "/submissions"
    for sid in os.listdir(submission_dir):
        student_dir = os.path.join(submission_dir, sid)
        tmp_student_dir = tmp_submission_dir + "/" + sid
        os.makedirs(tmp_student_dir)

        pys = glob.glob(student_dir + "/**/*.py", recursive=True)
        for k, py in enumerate(pys):
            if file_id(py) in white_hashes or any([fnmatch.fnmatch(py, b) for b in blacklist]):
                continue
            print("> Including", py)
            shutil.copy(py, tmp_student_dir + f"/{k}_" + os.path.basename(py))
    return tmp_base, tmp_submission_dir


def ensure_tokens_unpacked(directory, flat=True):
    tokens = glob.glob(directory + "/**/*.token", recursive=True)
    for t in tokens:
        unpack_sources_from_token(t)


def get_id(moss_pl):
    with open(moss_pl, "r") as f:
        pl = [line for line in f.read().splitlines() if "$userid=" in line].pop()
    return pl.split("=")[1][:-1]


def moss_it(whitelist_dir="", submissions_dir="", moss_id=None, blacklist=None):
    whitelist_dir = os.path.abspath(whitelist_dir)
    ensure_tokens_unpacked(whitelist_dir)
    ensure_tokens_unpacked(submissions_dir)
    print("> moss_prepare", whitelist_dir, submissions_dir)
    tmp_base, tmp_submission_dir = moss_prepare(whitelist_dir, submissions_dir, blacklist=blacklist)

    userid = int(moss_id)
    m = mosspy.Moss(userid, "python")
    for f in glob.glob(tmp_base +"/*.py"):
        m.addBaseFile(f)

    m.addFilesByWildcard(tmp_submission_dir + "/*/*.py")
    print("> Calling moss")
    url = m.send(lambda file_path, display_name: print('*', end='', flush=True))
    print()
    print("Report Url: " + url)
    report_dir = os.path.dirname(whitelist_dir) + "/report"
    if not os.path.isdir(report_dir):
        os.mkdir(report_dir)

    r = report_dir + "/report.html"
    m.saveWebPage(url, r)
    print("Saved report to:", r)
    mosspy.download_report(url, report_dir, connections=8, log_level=10, on_read=lambda u: print('*', end='', flush=True))
