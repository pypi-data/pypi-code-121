SPARSITY_THRESHOLD = 0.98
K = 50
KMEDOIDS_INIT = "k-medoids++"
MINIBATCH_SIZE = 6
DBSCAN_EPS = 3
DBSCAN_MINSAMPLES = 2
OPTICS_MINSAMPLES = 2
MIN_MEMBER_COUNT = 15
TENDENCY_CUTOFF = 3
ENSEMBLE_SD_CUTOFF = 5
TOP_N_MEMBERS_COUNT = 5

#if None, return the sub-clusters, else merge
#subclusters to this count using Agglomerative Clustering
BIRCH_NCLUSTERS = None

GENDER_MAP = {
    0: -1,
    "na": -1,
    "nan": -1,
    "m": 0,
    "f": 1
}