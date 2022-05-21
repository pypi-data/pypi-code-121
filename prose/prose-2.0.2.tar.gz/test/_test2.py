from prose.finderchart import *
import matplotlib.pyplot as plt
from prose import blocks, Sequence, Image

image = PhotographicPlate("/Users/lgrcia/code/prose-development/veil_nebulae_60x60/veil_nebulae_poss2ukstu_blue.fits")

im = blocks.SegmentedPeaks(n_stars=100)(image)
im.show(vmin=False)

#detetction_s.run([image])
f = 0