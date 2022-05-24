import pypotree
import numpy as np
import pylas
import numpy as np
import os

from PIL import Image
from shareloc_utils.smlm_file import read_smlm_file, plot_histogram

# parse the .smlm file
manifest = read_smlm_file(
    "./datasets/Microtubules and clathrin in a Cos cell/sample-1/data.smlm"
)
# manifest = read_smlm_file("./datasets/2D microtubules stained with Alexa647 part 2/MT2D_170829_C1C1_16898K/data.smlm")
# one file can contain multiple localization tables
tables = manifest["files"]
table = tables[0]["data"]


def render_histogram():
    # generate a histogram image for the first table
    histogram = plot_histogram(tables[0]["data"], value_range=(0, 255))

    # save the histogram image as 16-bit png file
    im = Image.fromarray(histogram.astype("uint16"))
    im.save("output.png")


def convert_potree_2():
    las = pylas.create()
    las.header.x_scale = 1.0
    las.header.y_scale = 1.0
    las.header.z_scale = 1.0

    las.x = table["x"]
    las.y = table["y"]
    las.z = np.zeros_like(table["y"])
    las.write(".tmp.las")
    # For Ubuntu, download the pre-compiled binary here: https://github.com/oeway/PotreeConverter/releases/download/2.1/PotreeConverter
    command = "./PotreeConverter -i .tmp.las -o point_clouds -p demo3 --material ELEVATION --overwrite"
    os.system(command)


def convert_potree_1(unique_dirname):
    # shape example: (100000,3)
    xyz = np.stack([table["x"], table["y"], np.zeros_like(table["y"])], axis=1)
    # dump data and convert
    np.savetxt(".tmp.txt", xyz)
    BIN = os.path.dirname(pypotree.__file__) + "/bin"
    print(
        "{BIN}/PotreeConverter .tmp.txt -f xyz -o point_clouds -p {idd} --material ELEVATION --overwrite".format(
            BIN=BIN, idd=unique_dirname
        )
    )
    os.system(
        "{BIN}/PotreeConverter .tmp.txt -f xyz -o point_clouds -p {idd} --material ELEVATION --overwrite".format(
            BIN=BIN, idd=unique_dirname
        )
    )
