#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

from statistics import mean
from pacbio_data_processing.utils import combine_scores


def ascii_to_quality(seq):
    """>>> ascii_to_quality("")
    """
    return [ord(_)-33 for _ in seq]



if __name__ == "__main__":
    import sys
    try:
        quals = ascii_to_quality(sys.argv[1])
    except IndexError:
        #pre_quals = "~"*100+"1234567890qwertyuiopasdfghjklzxcvbnm,.-<>;"+"~"*200
        pre_quals = "~"*100+"}"*29
        quals = ascii_to_quality(pre_quals)
    combined = combine_scores(quals)
    mean_val = mean(quals)
    print(f"combined = {combined}; mean = {mean_val}")


