from os.path import join
import matplotlib.pyplot as plt
import pandas


def hist_miss(indmiss: pandas.DataFrame, snpmiss: pandas.DataFrame, outputDir):
    """
    indmiss: table
    snpmiss: table
    """
    ind = join(outputDir + "Hist-individualMissingness.png")
    snp = join(outputDir + "Hist-snpMissingness.png")

    indCol = indmiss.columns[5]
    snpCol = snpmiss.columns[4]

    plt.hist(indmiss[indCol])
    plt.title("Histogram individual missingness")
    plt.savefig(ind, format="png")
    plt.clf()

    plt.hist(snpmiss[snpCol])
    plt.title("Histogram SNP missingness")
    plt.savefig(snp, format="png")
    plt.clf()


def sexcheck(df: pandas.DataFrame, outputDir):
    gender = join(outputDir + "Gender_check.png")
    women = join(outputDir + "Women_check.png")
    men = join(outputDir + "Men_check.png")

    col = df.columns[5]

    plt.hist(df[col])
    plt.title("Gender")
    plt.xlabel("F")
    plt.savefig(gender)
    plt.clf()

    m = df[df['PEDSEX'] == 1]
    f = df[df['PEDSEX'] == 2]

    plt.hist(m[col])
    plt.title("Men")
    plt.xlabel("F")
    plt.savefig(men)
    plt.clf()

    plt.hist(f[col])
    plt.title("Women")
    plt.xlabel("F")
    plt.savefig(women)
    plt.clf()


def maf_check(df: pandas.DataFrame, outputDir):
    fig = join(outputDir + "MAF_distribution.png")

    col = df.columns[4]

    plt.hist(df[col])
    plt.title("MAF distribution")
    plt.xlabel("MAF")
    plt.savefig(fig)
    plt.clf()


def hwe(hwe_df: pandas.DataFrame, zoom: pandas.DataFrame, outputDir):
    fig = join(outputDir + "HWE_Histogram.png")

    col = hwe_df.columns[8]

    plt.hist(hwe_df[col])
    plt.title("Histogram HWE")
    plt.savefig(fig)
    plt.clf()

    fig = join(outputDir + "HWE_below_theshold_Histogram.png")

    col = zoom.columns[8]

    plt.hist(zoom[col])
    plt.title("Histogram HWE: strongly deviating SNPs only")
    plt.savefig(fig)
    plt.clf()


def heterozygosity_rate(df: pandas.DataFrame,outputDir):
    fig = join(outputDir + "heterozygosity.png")

    df["HET_RATE"] = (df['N(NM)'] - df['O(HOM)']) / df['N(NM)']

    plt.hist(df['HET_RATE'])
    plt.xlabel("Heterozygosity Rate")
    plt.ylabel("Frequency")
    plt.title("Heterozygosity Rate")
    plt.savefig(fig)
    plt.clf()

# df = MDS_merge.mds
# race = raceFile2.txt
def mds_merge(df: pandas.DataFrame, race: pandas.DataFrame, outputDir):
    fig = join(outputDir + "MDS.png")

    datafile = pandas.merge(df, race, left_on=["IID", "FID"], right_on=["IID", "FID"])
    

    plt.savefig(fig)
    plt.clf()