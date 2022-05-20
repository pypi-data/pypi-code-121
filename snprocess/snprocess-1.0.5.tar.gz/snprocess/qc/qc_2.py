"""File for second qc method."""

from snprocess.qc.model import plink, read_snp_data, run_command, sort_unique, json_save
import snprocess.graph as g
import pandas as pd
from pathlib import Path

import os


def QC_2(opts, data):
    """Second and final step of QC.

    Impetus on results."""

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

    # outDir = opts['fileroute'] + opts['outDir']
    # outDir = opts['outDir']
    outDir = "tmp/"
    g1kDir = opts['1kG_dir']

    if not Path.is_file(Path(opts['outDir'] + "1kG_qc.bim")):
        print(WARNING + BOLD + "QC needs to be run on 1k Genome file. This will take a while..." + ENDC)
        # Name missing SNPs
        _, data = plink(
            "--bfile {}1kG_MDS --set-missing-var-ids @:#[b37]\$1,\$2 --make-bed --out {}1kG_qca".format(g1kDir, outDir,), data)
        # Filter variants
        # Remove variants based on missing genotype data
        _, data = plink(
            "--bfile {}1kG_qca --geno 0.2 --allow-no-sex --make-bed --out {}1kG_qcb".format(outDir, outDir), data)
        # Remove individuals based on missing genotype data
        _, data = plink(
            "--bfile {}1kG_qcb --mind 0.2 --allow-no-sex --make-bed --out {}1kG_qca".format(outDir, outDir), data)
        # Remove variants again
        _, data = plink(
            "--bfile {}1kG_qca --geno 0.02 --allow-no-sex --make-bed --out {}1kG_qcb".format(outDir, outDir), data)
        # Remove geno again
        _, data = plink(
            "--bfile {}1kG_qcb --mind 0.02 --allow-no-sex --make-bed --out {}1kG_qca".format(outDir, outDir), data)
        # Remove based on MAF
        _, data = plink(
            "--bfile {}1kG_qca --maf 0.05 --allow-no-sex --make-bed --out {}1kG_qcb".format(outDir, outDir), data)
        # Filter on HWE
        _, data = plink(
            "--bfile {}1kG_qcb --hwe 0.001 --allow-no-sex --make-bed --out {}1kG_qc".format(outDir, outDir), data)

    print(OKGREEN + BOLD + "Extracting variants from the data and from 1kG." + ENDC)
    # extract variants present in our data and use them to extract variants in the 1K data

    # awk '{print $2}' ${qcOutFile}.bim > ${psDir}PopStrat_SNPs.txt
    output = read_snp_data(outDir, "qcplink.bim")
    output = output[output.columns[1]]
    output.to_csv(sep="\t", path_or_buf='{}PopStrat_SNPs.txt'.format(
        outDir), index=False, header=False)

    # plink --bfile ${plinkFile}_7 --extract ${psDir}PopStrat_SNPs.txt --make-bed --out ${psDir}1kG
    output, data = plink(
        "--bfile {}1kG_qc --extract {}PopStrat_SNPs.txt --make-bed --out {}1kG_qcb".format(outDir, outDir, outDir), data)

    # # extract variants presents in 1kG which are in our data
    # awk '{print $2}' ${psDir}1kG.bim > ${psDir}1kG_MDS_SNPs.txt
    output = read_snp_data("", outDir + "1kG_qcb.bim")
    output = output[output.columns[1]]
    output.to_csv(sep="\t", path_or_buf='{}1kG_MDS_SNPs.txt'.format(
        outDir), index=False, header=False)

    # plink --bfile ${qcOutFile} --extract ${psDir}1kG_MDS_SNPs.txt --recode --make-bed --out ${psDir}PopStrat_MDS
    output, data = plink(
        "--bfile {}qcplink --extract {}1kG_MDS_SNPs.txt --recode --make-bed --out {}PopStrat_MDS".format(outDir, outDir, outDir), data)

    # # the datasets have the same variants. Now make them have the same build
    # awk '{print $2,$4}' ${psDir}PopStrat_MDS.map > ${psDir}buildReport.txt
    output = read_snp_data(outDir, "PopStrat_MDS.map")
    output = output[[output.columns[1], output.columns[3]]]
    output.to_csv(sep="\t", path_or_buf='{}buildReport.txt'.format(
        outDir), index=False, header=False)
    # plink --bfile ${psDir}1kG --update-map ${psDir}buildReport.txt --make-bed --out ${psDir}1kG_1

    output, data = plink(
        "--bfile {}1kG_qcb --update-map {}buildReport.txt --make-bed --out {}1kG_qca".format(outDir, outDir, outDir), data)

    # # Now the code for merging the two data sets. Prior to merging, the steps are:
    # # 1. Make the genomes similar for all SNPs
    # # 2. Resolve strand issues
    # # 3. Remove SNPs which still differ between the two data sets

    # echo "Combining the data sets."
    # echo "Setting the reference genome"
    # # 1. Set reference genome
    # # The command will generate some warnings for impossible A1 allele assigments, but they now have the same reference genome for all SNPs
    # awk '{print $2, $5}' ${plinkFile}_1.bim > ${psDir}1kG_ref-list.txt

    # plink --bfile ${psDir}PopStrat_MDS --reference-allele ${psDir}1kG_ref-list.txt --make-bed --out ${psDir}PopStrat-adj

    # echo "Resolving strand issues"
    # # 2. Resolve Strand issues
    # # get the differences in the files
    # awk '{ print $2, $5, $6 }' ${plinkFile}_1.bim > ${psDir}1kG1_tmp
    output = read_snp_data("", outDir + "1kG_qca.bim")
    cols = [output.columns[i] for i in [1, 4, 5]]
    output = output[cols]
    output.to_csv(sep="\t", path_or_buf='{}1kG1_tmp'.format(
        outDir), index=False, header=False)
    output = output[[output.columns[0], output.columns[1]]]
    output.to_csv(sep="\t", path_or_buf='{}1kG_ref-list.txt'.format(outDir),
                  index=False, header=False)
    output, data = plink(
        "--bfile {}PopStrat_MDS --reference-allele {}1kG_ref-list.txt --make-bed --out {}PopStrat-adj".format(outDir, outDir, outDir), data)
    # awk '{ print $2, $5, $6 }' ${psDir}PopStrat-adj.bim > ${psDir}PopStrat-adj_tmp
    output = read_snp_data(outDir, "PopStrat-adj.bim")
    cols = [output.columns[i] for i in [1, 4, 5]]
    output = output[cols]
    output.to_csv(sep="\t", path_or_buf='{}PopStrat-adj_tmp'.format(outDir),
                  index=False, header=False)
    # uniq -u shows only unique items, sort -u shows one of each
    # sort ${psDir}1kG1_tmp ${psDir}PopStrat-adj_tmp | uniq -u > ${psDir}all_differences.txt # get uniquerows
    output = sort_unique(outDir, "PopStrat-adj_tmp", "1kG1_tmp")
    output.to_csv(sep="\t", path_or_buf='{}all_differences.txt'.format(
        outDir), index=False, header=False)

    # # Flip SNPs for resolving strand issues
    # awk '{ print $1 }' ${psDir}all_differences.txt | sort -u > ${psDir}flip_list.txt
    output = output[[output.columns[0]]]
    output = output.drop_duplicates()
    output.to_csv(sep="\t", path_or_buf='{}flip_list.txt'.format(
        outDir), index=False, header=False)
    # plink --bfile ${psDir}PopStrat-adj --flip ${psDir}flip_list.txt --reference-allele ${psDir}1kG_ref-list.txt --make-bed --out ${psDir}PopStrat_corrected
    output, data = plink(
        "--bfile {}PopStrat-adj --flip {}flip_list.txt --reference-allele {}1kG_ref-list.txt --make-bed --out {}PopStrat_corrected".format(outDir, outDir, outDir, outDir), data)

    # # check for problematic SNPs after the flip
    # awk '{ print $2, $5, $6 }' ${psDir}PopStrat_corrected.bim > ${psDir}PopStrat_corrected_tmp
    output = read_snp_data(outDir, "PopStrat_corrected.bim")
    cols = [output.columns[i] for i in [1, 4, 5]]
    output = output[cols]
    output.to_csv(sep="\t", path_or_buf='{}PopStrat_corrected_tmp'.format(
        outDir), index=False, header=False)
    # sort ${psDir}1kG1_tmp ${psDir}PopStrat_corrected_tmp | uniq -u > ${psDir}uncorresponding_SNPs.txt
    output = sort_unique(outDir, "1kG1_tmp", "PopStrat_corrected_tmp")
    output.to_csv(sep="\t", path_or_buf='{}uncorresponding_SNPs.txt'.format(
        outDir), index=False, header=False)

    # # There aren't too many problematic SNPs left. Let's remove them
    # awk '{ print $1 }' ${psDir}uncorresponding_SNPs.txt | sort -u > ${psDir}SNPs_excluded.txt
    output = output[[output.columns[0]]]
    output = output.drop_duplicates()
    output.to_csv(sep="\t", path_or_buf='{}SNPs_excluded.txt'.format(
        outDir), index=False, header=False)
    # plink --bfile ${psDir}PopStrat_corrected --exclude ${psDir}SNPs_excluded.txt --make-bed --out ${psDir}PopStrat_MDS2
    output, data = plink(
        "--bfile {}PopStrat_corrected --exclude {}SNPs_excluded.txt --make-bed --out {}PopStrat_MDS2".format(outDir, outDir, outDir), data)
    # plink --bfile ${psDir}1kG_1 --exclude ${psDir}SNPs_excluded.txt --make-bed --out ${psDir}1kG_2
    output, data = plink(
        "--bfile {}1kG_qca --exclude {}SNPs_excluded.txt --make-bed --out {}1kG_qcb".format(outDir, outDir, outDir), data)

    # # now merge them
    # plink --bfile ${psDir}PopStrat_MDS2 --bmerge ${psDir}1kG_2.bed ${psDir}1kG_2.bim ${psDir}1kG_2.fam --allow-no-sex --make-bed --out ${psDir}MDS_merge
    output, data = plink("--bfile {}PopStrat_MDS2 --bmerge {}1kG_qcb.bed {}1kG_qcb.bim {}1kG_qcb.fam --allow-no-sex --make-bed --out {}MDS_merge".format(
        outDir, outDir, outDir, outDir, outDir), data)

    # # Conduct MDS on pruned SNPs
    # plink --bfile ${psDir}MDS_merge --extract ${qcOutDir}indepSNP.prune.in --genome --out ${psDir}MDS_merge
    output, data = plink(
        "--bfile {}MDS_merge --extract {}indepSNP.prune.in --genome --out {}MDS_merge".format(outDir, outDir, outDir), data)
    # plink --bfile ${psDir}MDS_merge --read-genome ${psDir}MDS_merge.genome --cluster --mds-plot 10 --out ${psDir}MDS_merge
    output, data = plink(
        "--bfile {}MDS_merge --read-genome {}MDS_merge.genome --cluster --mds-plot 10 --out {}MDS_merged".format(outDir, outDir, outDir), data)

    # #### Plot it!

    # # Convert population codes into super-population codes (continents)
    # awk '{ print $1, $1, $2 }' ${panelFile} > ${psDir}race_1kG.txt
    panelFile = g1kDir + "20100804.ALL.panel"
    output = pd.read_csv(panelFile, sep='\t', names=range(0, 4))
    cols = [output.columns[i] for i in [0, 0, 1]]
    output = output[cols]
    output.to_csv(sep="\t", path_or_buf='{}race_1kG.txt'.format(
        outDir), index=False, header=False)

    # sed -i 's/JPT/ASN/g' ${psDir}race_1kG.txt
    # sed -i 's/ASW/AFR/g' ${psDir}race_1kG.txt
    # sed -i 's/CEU/EUR/g' ${psDir}race_1kG.txt
    # sed -i 's/CHB/ASN/g' ${psDir}race_1kG.txt
    # sed -i 's/CHD/ASN/g' ${psDir}race_1kG.txt
    # sed -i 's/YRI/AFR/g' ${psDir}race_1kG.txt
    # sed -i 's/LWK/AFR/g' ${psDir}race_1kG.txt
    # sed -i 's/TSI/EUR/g' ${psDir}race_1kG.txt
    # sed -i 's/MXL/AMR/g' ${psDir}race_1kG.txt
    # sed -i 's/GBR/EUR/g' ${psDir}race_1kG.txt
    # sed -i 's/FIN/EUR/g' ${psDir}race_1kG.txt
    # sed -i 's/CHS/ASN/g' ${psDir}race_1kG.txt
    # sed -i 's/PUR/AMR/g' ${psDir}race_1kG.txt

    raceMap = {}
    raceMap['JPT'] = 'ASN'
    raceMap['CHB'] = 'ASN'
    raceMap['CHD'] = 'ASN'
    raceMap['CHS'] = 'ASN'
    raceMap['ASW'] = 'AFR'
    raceMap['YRI'] = 'AFR'
    raceMap['LWK'] = 'AFR'
    raceMap['CEU'] = 'EUR'
    raceMap['TSI'] = 'EUR'
    raceMap['GBR'] = 'EUR'
    raceMap['FIN'] = 'EUR'
    raceMap['MXL'] = 'AMR'
    raceMap['PUR'] = 'AMR'

    continents = [raceMap[country] for country in output[1].tolist()]
    output[2] = continents
    output.to_csv(sep="\t", path_or_buf='{}race_1kG.txt'.format(
        outDir), index=False, header=False)
    # # create our own race file
    # awk '{ print $1, $2, "OWN" }' ${psDir}PopStrat_MDS.fam > ${psDir}raceFile.txt
    output = read_snp_data(outDir, "PopStrat_MDS.fam")
    cols = [output.columns[i] for i in [1, 2]]
    output = output[cols]
    output.columns = [0,1]
    output[2] = 'OWN'
    output[3] = 'OWN'
    output.to_csv(sep="\t", path_or_buf='{}raceFile.txt'.format(
        outDir), index=False, header=False)

    # # concatenate the race file
    # cat ${psDir}race_1kG.txt ${psDir}raceFile.txt | sed -e '1i\FID IID race' > ${psDir}raceFile2.txt
    file1 = read_snp_data(outDir, "race_1kG.txt")
    file2 = read_snp_data(outDir, "raceFile.txt")
    output = pd.concat([file1, file2])
    output.columns = ["IID", "FID", 2, "race"]
    output = output.drop(2, 1)
    output.to_csv(sep="\t", path_or_buf='{}raceFile2.txt'.format(
        outDir), index=False)

    # generate plots
    snprocess_path = os.path.dirname(os.path.realpath(__file__))
    run_command("Rscript {}/MDS_merge.R {}MDS_merged.mds {}raceFile2.txt {}".format(
        snprocess_path, outDir, outDir, outDir))
    
    data = json_save(
        "Population Stratification",
        "MDS_merge.png",
        data
    )
    # merge = read_snp_data(outDir, "MDS_merged.mds", head=0)
    # race = read_snp_data(outDir, "raceFile2.txt", head=0)
    # g.mds_merge(merge, race, opts['outDir'])

    return data
