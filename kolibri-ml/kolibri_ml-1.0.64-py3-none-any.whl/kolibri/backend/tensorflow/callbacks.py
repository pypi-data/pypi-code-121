from seqeval import metrics as seq_metrics
from sklearn import metrics
from tensorflow import keras

from kolibri import config
from kolibri.backend.tensorflow.tasks.text.base_model import TextBaseModel


class EvalCallBack(keras.callbacks.Callback):

    def __init__(self, kolibri_model: TextBaseModel, valid_x, valid_y,
                 step=5, batch_size=256, average='weighted'):
        """
        Evaluate callback, calculate precision, recall and f1
        Args:
            kolibri_model: the kolibri.backend model to evaluate
            valid_x: feature texts
            valid_y: label texts
            step: step, default 5
            batch_size: batch size, default 256
        """
        super(EvalCallBack, self).__init__()
        self.kolibri_model = kolibri_model
        self.valid_x = valid_x
        self.valid_y = valid_y
        self.step = step
        self.batch_size = batch_size
        self.average = average
        self.logs = []

    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1) % self.step == 0:
            y_pred = self.kolibri_model.predict(self.valid_x, batch_size=self.batch_size)

            if self.kolibri_model.task == config.TaskType.LABELING:
                y_true = [seq[:len(y_pred[index])] for index, seq in enumerate(self.valid_y)]
                precision = seq_metrics.precision_score(y_true, y_pred)
                recall = seq_metrics.recall_score(y_true, y_pred)
                f1 = seq_metrics.f1_score(y_true, y_pred)
            else:
                y_true = self.valid_y
                precision = metrics.precision_score(y_true, y_pred, average=self.average)
                recall = metrics.recall_score(y_true, y_pred, average=self.average)
                f1 = metrics.f1_score(y_true, y_pred, average=self.average)

            self.logs.append({
                'precision': precision,
                'recall': recall,
                'f1': f1
            })
            print(f"\nepoch: {epoch} precision: {precision:.6f}, recall: {recall:.6f}, f1: {f1:.6f}")


if __name__ == "__main__":
    print("Hello world")
