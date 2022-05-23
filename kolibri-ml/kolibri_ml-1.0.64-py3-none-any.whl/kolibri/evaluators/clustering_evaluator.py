from sklearn import metrics

metrics={
    "silhouette":{
        "scorer": metrics.silhouette_score,
        "description":"",
        "need-true-label": False,
        "higher-is-better": True
    },
    "rand": {
        "scorer":metrics.rand_score,
        "need-true-label": True,
        "decription": " measures the similarity of the two assignments, ignoring permutations",
        "higher-is-better": True
    },
    "adjacted-mutual-info":{
        "scorer": metrics.adjusted_mutual_info_score,
        "need-true-label": True,
        "description": "measures the agreement of the two assignments, ignoring permutations.",
        "higher-is-better": True
    },
    "homogeneity":{
        "scorer": metrics.homogeneity_score,
        "need-true-label": True,
        "description": "Does each cluster contains only members of a single class?",
        "higher-is-better": True

    },
    "completeness":{
        "scorer": metrics.completeness_score,
        "need-true-label": True,
        "description": "Do all members of a given class are assigned to the same cluster?",
        "higher-is-better": True

    },
    "fowlkes-mallows":{
        "scorer": metrics.fowlkes_mallows_score,
        "need-true-label": True,
        "description": "geometric mean of the pairwise precision and recall.",
        "higher-is-better": True

    },
    "calinski-harabasz":{
        "scorer": metrics.calinski_harabasz_score,
        "need-true-label": False,
        "description": "ratio of the sum of between-clusters dispersion and of within-cluster dispersion for all clusters.",
        "higher-is-better": True

    },
    "davies-bouldin":{
        "scorer": metrics.davies_bouldin_score,
        "need-true-label": False,
        "description": "signifies the average ‘similarity’ between clusters, where the similarity is a measure that compares the distance between clusters with the size of the clusters themselves.",
        "higher-is-better": False

}
}

class ClusteringEvaluator():

    def calculate_unsupervised_metrics(self, X,  labels, ground_truth= None):

        score_dict = {}

        for k, v in metrics.items():
            scoring_function=v["scorer"]
            if v["need-true-label"] and ground_truth is not None:
                score_dict[k]= scoring_function(X, labels, ground_truth)
            elif not v["need-true-label"]:
                score_dict[k]= scoring_function(X, labels)

        print(score_dict)
        return score_dict

