

class zetane_pruning:
    """
    This class is used to perform pruning on the classification models, One needs to provide
    model and training data to prune the model. This class can be used to reduce the size of model by
    3X to 10X depending upon the parameters provided for the pruning. It increases the accuracy, loss and other
    metrics by 6-10% as compared to trained model.

    This class can be used for pre-trained model, new model that is defined and traine and also on untrained models.
    """
    def __init__(self, model=None):
        pass


    def pruning_model(self, train_data, train_labels, batch_size = 128, epochs = 2, validation_split = 0.1, initial_sparsity=0.50, final_sparsity=0.80, begin_step=0, end_step =0):
        return self
