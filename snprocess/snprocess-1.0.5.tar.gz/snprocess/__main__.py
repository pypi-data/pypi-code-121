"""Run all scripts on all phases"""
import pathlib
from shutil import copyfile as copy
from snprocess.qc.qc_1 import QC_1
from snprocess.qc.qc_2 import QC_2
from snprocess.model import make_bed, md, printdict, clean, run
import click
import json
import pathlib
import glob
import os


@click.command()
@click.option('--settings', '-s', type=click.STRING, help='Settings JSON for SNProcess parameters')
@click.option('--example','-e', is_flag=True, help='Print an example settings JSON')
@click.option('--generate','-g', is_flag=True, help='Generate a settings JSON')
@click.option('--info','-i', default='', type=click.STRING, help='Display results, argument: output directory from SNProcess')
def main(settings, example, info, generate):
    """
    Run all scripts on input supplied by json config file specified by SETTINGS
    """
    FAIL = '\033[91m'
    OKGREEN = '\033[92m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

    # if snprocess will show the info
    if info != '':
        run(info)
        return 0

    # if snprocess will generate a settings json
    if generate:
        print(OKGREEN + BOLD + "Generate your own settings JSON..." + ENDC)
        settings = {}
        # run these in a loop until they receive quasi-valid responses
        while True:
            settings['1kG_dir'] = input("1k Genome File Route (starts and ends with '/'): ")
            d = settings['1kG_dir']
            if len(d) > 0 and d.endswith('/'):
                break
        while True:
            settings['inFile'] = input("File pattern of input files (should be .bed if binary, .map if not; note: do not include the extension): ")
            d = settings['inFile']
            if len(d) > 0 and not d.endswith('/') and not d.startswith('/') and not d.endswith('.bed') and not d.endswith('.map'):
                break
        while True:
            settings['inDir'] = input("Path to your input files, AKA their folder (starts and ends with '/'): ")
            d = settings['inDir']
            if len(d) > 0 and d.endswith('/'):
                break
        while True:
            settings['outDir'] = input("Path to your output info. (This settings json will be saved there shortly, starts and ends with '/'): ")
            d = settings['outDir']
            if len(d) > 0 and d.endswith('/'):
                break
        while True:
            settings['geno'] = input("SNP missingness threshhold (plink --geno): ")
            if settings['geno'].isnumeric():
                break
        while True:
            settings['mind'] = input("Individual missingness threshhold (plink --mind): ")
            if settings['mind'].isnumeric():
                break
        while True:
            settings['maf'] = input("Minor Allele Frequency threshhold (MAF): ")
            if settings['maf'].isnumeric():
                break
        while True:
            settings['hwe'] = input("Hardy-Weinberg Equillibrium p-value: (HWE): ")
            if settings['hwe'].isnumeric():
                break
        while True:
            settings['indep_pairwise'] = input("Heterozygosity and LD Pruning threshhold: (indep_pairwise): ")
            if settings['indep_pairwise'].isnumeric():
                break
        while True:
            settings['relatedness'] = input("Relatedness threshhold: ")
            if settings['relatedness'].isnumeric():
                break
        outDir = settings['outDir']
        os.makedirs(outDir, exist_ok=True)
        json.dump(settings, open("{}/settings.json".format(outDir), "w"), indent=4)
        print(OKGREEN + BOLD + "Done! Your settings JSON can be found in the folder {}".format(outDir))
        return 0

    # check that plink is installed
    # plink_binary = glob.glob("/usr/bin/*")
    # if 'plink' not in plink_binary:
    #     exit(FAIL + "Plink not installed. Download it here:\nhttps://www.cog-genomics.org/plink/1.9/" + ENDC)

    snprocess_path = os.path.dirname(os.path.realpath(__file__))
    reqd = dict(json.load(open(snprocess_path + "/example.json")))

    if example:
        print(printdict(reqd))
        return 0

    try:
        settings = json.load(open(settings))
    except:
        exit(FAIL + BOLD + "Settings JSON does not exist.\nPrint an example settings JSON using 'snprocess -e', or generate one with 'snprocess -g'" + ENDC)

    try:
        outdir = settings['outDir']
    except:
        exit(FAIL + BOLD + "Output dir parameter missing from settings JSON.\nPrint an example settings JSON using 'snprocess -e'" + ENDC)
    o = pathlib.Path(outdir)
    if not o.exists():
        os.makedirs(o)
    # don't clobber existing output if not empty
    else:
        if len(glob.glob(outdir + "*")) > 0:
            # exit(FAIL + "Output directory is not empty")
            pass

    # make temp folder
    os.makedirs("tmp", exist_ok=True)
    
    
    # check that all parameters are satisfied in the input file, without extras
    s = dict(settings)
    reqd = set(reqd.keys())
    for param in s.keys():
        if param not in reqd:
            exit(FAIL + "Extra parameter in settings JSON: {}.\n\nPrint an example settings JSON using 'snprocess -e'".format(param) + ENDC)
        reqd.remove(param)
    if len(reqd) != 0:
        if len(reqd) == 1:
            exit(
                FAIL + "Parameter missing from settings JSON: {}.\n\nPrint an example settings JSON using 'snprocess -e'".format("".join(reqd)) + ENDC)
        else:
            misslist = ", ".join(reqd)
            exit(FAIL + "Parameters missing from settings JSON: {}.\n\nPrint an example settings JSON using 'snprocess -e'".format(misslist) + ENDC)

    indir = settings['inDir']

    inputFile = indir + settings['inFile']

    flist = glob.glob(inputFile + "*")

    # convert to binary if input file not binary already
    binary = True
    if len(flist) == 0:
        exit(FAIL + "Input files {}* not found in {}".format(settings['inFile'], indir) + ENDC)
    else:
        for fl in flist:
            if fl[-3:] == "bim":
                binary = True
                break
            binary = False

    if not binary:
        make_bed(indir, settings['inFile'])

    # start QC
    print(OKGREEN + BOLD + "Starting QC..." + ENDC)
    markup = QC_1(settings)
    markup = QC_2(settings, markup)

    # remove tmp file
    clean()

    markup["settings"] = {}

    # add input parameters to output file
    for item, val in settings.items():
        markup["settings"][item] = val

    # render output html
    json.dump(markup, open("{}/context.json".format(outdir), "w"), indent=4)
    op = pathlib.Path(outdir)
    md(op/"index.html", markup, snprocess_path)
    OKGREEN = '\033[92m'
    print(OKGREEN + "SNProcess has finished QC successfully!\nOutput files can be found in {}\n\nA summary is provided in the file found at {}index.html".format(outdir, outdir) + ENDC)

    # copy static srcs to output
    copy(snprocess_path + "/logo.png", outdir + "/logo.png")


if __name__ == "__main__":
    main()
