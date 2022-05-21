from prose import Sequence, Image, blocks
import matplotlib.pyplot as plt

stack = Image("/Users/lgrcia/spirit/observations/M68/stack.fits")

s = Sequence([
    blocks.SegmentedPeaks(n_stars=200, min_separation=100),
    blocks.Cutouts(size=21),
    blocks.MedianPSF(),
    blocks.Moffat2D(),
])

s.run(stack)
stack.show()