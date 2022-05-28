# type: ignore
#%%
import weka.core.jvm as jvm
import weka.core.converters as converters
from weka.filters import Filter
from weka.clusterers import Clusterer
import weka.core.serialization as serialization
from weka.core.dataset import Instances

class WekaClusterer:
    def __init__(self, model_filename=None, data_filename=None, columns_to_drop=[]):
        if not jvm.started:
            jvm.start()
        self._data_filename = data_filename
        self._columns_to_drop = columns_to_drop
        self._model_filename = model_filename
        if self._model_filename is not None:
            self.load_model()
        elif self._data_filename is not None:
            self.load_data()

    def load_data(self, data_filename=None, columns_to_drop=None):
        self._data_filename = data_filename if data_filename is not None else self._data_filename
        self._columns_to_drop = columns_to_drop if columns_to_drop is not None else self._columns_to_drop
        data = converters.load_any_file(self._data_filename)

        if self._columns_to_drop == []:
            self._data = data
        else:
            remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=['-R', ', '.join(str(i) for i in self._columns_to_drop)])
            remove.inputformat(data)     # let the filter know about the type of data to filter
            self._data = remove.filter(data)   # filter the data

    def cluster(self, clustering_method='EM', number_of_clusters=-1, **options):
        try:
            classname = {'em': 'weka.clusterers.EM',
                         'kmeans': 'weka.clusterers.SimpleKMeans'}[clustering_method.lower()]
        except KeyError:
            raise KeyError(f'Method {clustering_method} not found!')
        
        self._clusterer = Clusterer(classname=classname, options=['-N', str(number_of_clusters)] + options)
        self._clusterer.build_clusterer(self._data)

        return self._clusterer

    def assign_label(self, data, distribution=False, **kwargs):
        results = [0]*len(data)
        if distribution:
            for index, inst in enumerate(data):
                cl = clusterer.cluster_instance(inst)  # 0-based cluster index
                dist = clusterer.distribution_for_instance(inst)   # cluster membership distribution
                results[index] = (cl, dist)
        else:
            for index, inst in enumerate(data):
                results[index] = self._clusterer.cluster_instance(inst)  # 0-based cluster index

        return results

    def save_model(self, model_filename=None, include_instances=True):
        filename = self._model_filename if model_filename is None else model_filename
        if include_instances:
            serialization.write_all(filename, [self._clusterer, Instances.template_instances(self._data)])
        else:
            serialization.write(filename, self._clusterer)

    def load_model(self, model_filename=None, has_instances=True):
        filename = self._model_filename if model_filename is None else model_filename
        if has_instances:
            objects = serialization.read_all(filename)
            self._clusterer = Clusterer(jobject=objects[0])
            self._instances = Instances(jobject=objects[1])
        else:
            self._clusterer = Clusterer(jobject=serialization.read(filename))

    def __del__(self):
        jvm.stop()
    

#%%
if __name__ == "__main__":
    filename = 'data_for_clustering_dose_only.csv'
    test = WekaClusterer(data_filename=filename, columns_to_drop=[1])
    test.cluster(number_of_clusters=4)
    test.save_model(model_filename='weka_output.model')
    test.load_model(model_filename='weka_output.model')
    test.assign_label(test._data)