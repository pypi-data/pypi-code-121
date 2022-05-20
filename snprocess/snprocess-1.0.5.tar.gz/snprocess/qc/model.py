"""Shared methods for the snprocess package."""

from contextlib import redirect_stdout
import subprocess
import pandas as pd


def isfloat(val):
    res = val.replace('.', '', 1).isdigit()
    return res


def run_command(cmd):
    """Run a bash command and handle errors."""
    # might want to use subprocess.run instead
    with open("snprocess.log", "a") as f:
        with redirect_stdout(f):
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output = process.communicate()
            if process.returncode != 0:
                WARNING = '\033[93m'
                FAIL = '\033[91m'
                ENDC = '\033[0m'
                exit(WARNING + "ERROR: snprocess unable to run. Is plink installed?\nhttps://www.cog-genomics.org/plink/1.9/" + FAIL + "\n\n{}\n^^^ Process exited with error".format(cmd) + ENDC)
            return str(output).split("\\n")


def plink(cmd, data):
    """Run a plink command using run_command."""
    cmd = "plink " + cmd
    output = run_command(cmd)
    filter = [x for x in output if "pass filters and QC." in x]
    if len(filter) != 0:
        data["lost"].append({cmd: '\n'.join(filter)})
    return output, data


def read_from_output(output, key, sep=" "):
    """Return a dataframe from command output, rows and cols established using KEY"""
    output = output.split()
    output = [(lambda elt: elt.decode("utf-8"))(elt) for elt in output]
    rows = output.count(key)
    cols = int(len(output) / rows)
    output = [output[i:i + cols] for i in range(0, len(output), cols)]
    output = pd.DataFrame(output)
    for col in range(len(output)):
        if output[col][0].isnumeric():
            output[col] = output[col].astype("int")
        elif isfloat(output[col][0]):
            output[col] = output[col].astype("float")
    return output


def read_snp_data(outDir, filename, head=None) -> pd.DataFrame:
    return pd.read_csv(delim_whitespace=True, filepath_or_buffer=outDir + filename, header=head)


def json_save(title: str, route: str, data):
    data['graphs'] = data['graphs'] + [
        {
            "name": title,
            "file": route
        }
    ]
    return data


def sort_unique(outDir: str, fn1: str, fn2: str) -> pd.DataFrame:
    file1 = read_snp_data(outDir, fn1)
    file2 = read_snp_data(outDir, fn2)
    output = pd.concat([file1, file2])
    output = output.drop_duplicates(keep=False)
    return output
