from prose import FitsManager
from prose import Sequence, blocks
from prose.sequence import MultiProcessSequence

calibration = MultiProcessSequence([
    blocks.Trim(),
    blocks.SegmentedPeaks(n_stars=15),
    blocks.detection.LimitStars()
])

calibration.run("/Users/lgrcia/data/20220405/SPECU2.2022-04-06T01_46_03.570.fits")