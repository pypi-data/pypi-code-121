from typing import List,Any,Dict
import tensorflow as tf
from tensorflow import keras

from nlp_tools.tasks.abs_task_model import ABCTaskModel


class EvalCallBack(keras.callbacks.Callback):

    def __init__(self,
                 model:ABCTaskModel,
                 x_data: List[Any],
                 y_data: List[Any],
                 *,
                 step: int = 5,
                 truncating: bool = False,
                 batch_size: int = 64) -> None:
        """
        Evaluate callback, calculate precision, recall and f1
        Args:
            kash_model: the task model to evaluate
            x_data: feature data for evaluation
            y_data: label data for evaluation
            step: step, default 5
            truncating: truncating: remove values from sequences larger than `model.encoder.sequence_length`
            batch_size: batch size, default 64
        """
        super(EvalCallBack,self).__init__()
        self.model:ABCTaskModel = model
        self.x_data = x_data
        self.y_data = y_data
        self.step = step
        self.truncating = truncating
        self.batch_size = batch_size
        self.logs:List[Dict] = []


    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1)% self.step == 0:
            report = self.model.evaluate(
                self.x_data,
                self.y_data,
                truncating = self.truncating,
                batch_size = self.batch_size
            )

            self.logs.append(
                {
                    'precision':report['precision'],
                    'recall':report['recall'],
                    'f1-score':report['f1-score']
                }
            )

            tf.summary.scalar('eval f1-score',data=report['f1-score'],step=epoch)
            tf.summary.scalar('eval recall',data=report['recall'],step=epoch)
            tf.summary.scalar('eval precision',data=report['precision'],step=epoch)
            print(f"\nepoch: {epoch} precision: {report['precision']:.6f},"
                  f" recall: {report['recall']:.6f}, f1-score: {report['f1-score']:.6f}")




class NerF1ScoreSaveCallBack(keras.callbacks.Callback):

    def __init__(self,
                 nlp_tools_model,
                 x_data: List[Any],
                 y_data: List[Any],
                 model_save_path=None,
                 truncating: bool = False,
                 batch_size: int = 64) -> None:
        """
        Evaluate callback, calculate precision, recall and f1
        Args:
            x_data: feature data for evaluation
            y_data: label data for evaluation
            truncating: remove values from sequences larger than `model.encoder.sequence_length`
            batch_size: batch size, default 64
        """
        super(NerF1ScoreSaveCallBack,self).__init__()
        self.nlp_tools_model = nlp_tools_model
        self.x_data = x_data
        self.y_data = y_data
        self.truncating = truncating
        self.batch_size = batch_size
        self.model_save_path = model_save_path
        self.best_f1_score = 0


    def on_epoch_end(self, epoch, logs=None):
        report = self.nlp_tools_model.evaluate(
            self.x_data,
            self.y_data,
            truncating=self.truncating,
            batch_size = self.batch_size,

        )
        f1_score = report['f1-score']

        print("current f1_score: %s,best f1_score:%s" % (f1_score,self.best_f1_score))
        if f1_score >= self.best_f1_score:
            if self.model_save_path:
                self.nlp_tools_model.save(self.model_save_path)
            self.best_f1_score = f1_score


