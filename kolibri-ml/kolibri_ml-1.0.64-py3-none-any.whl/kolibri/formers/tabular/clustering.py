from kolibri.evaluators.model_plot import ModelPlot
from kolibri import ModelConfig, ModelTrainer


class ClusteringFormer():

    def __init__(self,output_folder, data=None, target=None, model_name="KMeans"):

        if data is not None:
            self.data=data
            config={}
            config["model"]=model_name
            config["pipeline"]=["AutoInferDatatype", "Normalizer", "DummyConverter",  "ClusteringEstimator"]
            config['output-folder']=output_folder
            config["target"]=target

            trainer = ModelTrainer(ModelConfig(config))
            data.fillna(0, inplace=True)
            y=None
            if target is not None:
                y=data[target]
            trainer.fit(data, y)
            self.model=trainer.pipeline.estimator
            self.metrics=self.model.model_results
            self.lables=self.model.model.labels_
            self._model_plot=ModelPlot(pipeline=trainer.pipeline, data=self.data, target=target)
    def plot_model(self):
        self._model_plot.elbow()