from floodlight.io.kinexon import read_kinexon_file

from floodlight import Pitch

from floodlight.models.geometry import CentroidModel#, StretchIndexModel, PlayerDistanceModel


# PATHS
sample_kinexon_path = "C:\\Users\\Dominik\\sciebo\\floodlight\\Kinexon\\Game 1.csv"
sample_f24_path = "C:\\Users\\Dominik\\sciebo\\floodlight\\Opta\\f24-4-2017-958085-eventdetails.xml"
sample_tracab_data_path = "C:\\Users\\Dominik\\sciebo\\floodlight\\Tracab (ChyronHego)\\1044528_shortened.dat"
sample_tracab_meta_path = "C:\\Users\\Dominik\\sciebo\\floodlight\\Tracab (ChyronHego)\\1044528_metadata.xml"


# KINEXON DATA
xy0, xy1, xy3 = read_kinexon_file(sample_kinexon_path)

pitch = Pitch((0, 40), (0, 20), 'percent', 'flexible', 40, 20, 'handball')
cm = CentroidModel()
# cm.fit(xy0)
cent = cm.centroid()
cent = cm.centroid_distance(xy0)

# sim = StretchIndexModel()
# sim.fit(xy0, cent)
# stretch = sim.get_stretch_index()
#
# pdm = PlayerDistanceModel(pitch)
# pdm.fit(xy0)
# dist = pdm.get_player_distances()
# pdm.fit(xy0, xy1)
# dist2 = pdm.get_player_distances()

