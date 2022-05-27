from sklearn.cluster import KMeans, MiniBatchKMeans, \
    AgglomerativeClustering, DBSCAN, OPTICS, Birch
from sklearn_extra.cluster import KMedoids

from offline_model_builder.user_profile.clustering.clustering_utils import ClusteringUtils
from pandas import DataFrame, Series, get_dummies

from offline_model_builder.user_profile.clustering.config import K, MINIBATCH_SIZE, \
    DBSCAN_EPS, DBSCAN_MINSAMPLES, OPTICS_MINSAMPLES, \
    BIRCH_NCLUSTERS, KMEDOIDS_INIT

from offline_model_builder.user_profile.constants import CUSTOMER_ID, KMEANS_FEATURE, \
    MINIBATCH_KMEANS_FEATURE, WARDS_HIERARCHICAL_FEATURE, \
    KMEDOIDS_FEATURE, DBSCAN_FEATURE, \
    OPTICS_FEATURE, BIRCH_FEATURE, BIRTHDAY, CUSTOMER_CREATED_ON, \
    CUSTOMER_MODIFIED_ON, PAYTVPROVIDER_ID, GENDER


class ClusterGenerator(ClusteringUtils):

    def __init__(
            self,
            data=DataFrame
    ):
        data[CUSTOMER_ID] = data[CUSTOMER_ID].astype(str)
        ClusteringUtils.__init__(self, data=data)
        self.clusters = DataFrame()

    def get_kmeans(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate KMeans Clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        model = KMeans(n_clusters=K, random_state=0)
        return model.fit_predict(features)

    def get_minibatch_kmeans(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate MiniBatch-KMeans clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        model = MiniBatchKMeans(n_clusters=K, random_state=0,
                                batch_size=MINIBATCH_SIZE)
        return model.fit_predict(features)

    def get_wards_hierarchical(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate clusters using Ward's Hierarchical
        Clustering
        :param features: user features
        :return: list of assigned cluster values
        """
        model = AgglomerativeClustering(n_clusters=K)
        return model.fit_predict(features)

    def get_kmedoids(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate KMedoids Clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        model = KMedoids(n_clusters=K, random_state=0,
                         init=KMEDOIDS_INIT)
        return model.fit_predict(features)

    def get_dbscan(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate DBSCAN Clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        model = DBSCAN(eps=DBSCAN_EPS,
                       min_samples=DBSCAN_MINSAMPLES)
        return model.fit_predict(features)

    def get_optics(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate OPTICS clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        model = OPTICS(min_samples=OPTICS_MINSAMPLES)
        return model.fit_predict(features)

    def get_birch(
            self,
            features: DataFrame
    ) -> Series:
        """
        Generate BIRCH subclusters if n_clusters
        is set to None, else merge subclusters to
        obtain n_clusters using Agglomerative
        Clustering.
        :param features: user features
        :return: list of assigned cluster values
        """
        model = Birch(n_clusters=BIRCH_NCLUSTERS)
        return model.fit_predict(features)

    def controller(
            self
    ):
        """
        Driver function for Cluster based feature
        processing and results generation
        :return: None
        """
        features = self.drop_sparse_features()
        #save intermediate results here, if required

        self.clusters[CUSTOMER_ID] = features[CUSTOMER_ID]

        #since we do not want to pass an identifier as a clustering feature
        features = self.remove_attributes(attributes=features,
                                          to_drop=[CUSTOMER_ID,
                                                   BIRTHDAY,
                                                   CUSTOMER_CREATED_ON,
                                                   CUSTOMER_MODIFIED_ON])

        features = get_dummies(
            features,
            columns=[GENDER, PAYTVPROVIDER_ID]
        )

        self.clusters[KMEANS_FEATURE] = self.get_kmeans(features=features)
        self.clusters[MINIBATCH_KMEANS_FEATURE] = self.get_minibatch_kmeans(features=features)
        self.clusters[WARDS_HIERARCHICAL_FEATURE] = self.get_wards_hierarchical(features=features)
        self.clusters[KMEDOIDS_FEATURE] = self.get_kmedoids(features=features)
        self.clusters[DBSCAN_FEATURE] = self.get_dbscan(features=features)
        self.clusters[BIRCH_FEATURE] = self.get_birch(features=features)
        # save intermediate results here, if required
