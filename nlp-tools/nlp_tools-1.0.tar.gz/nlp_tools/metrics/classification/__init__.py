from tensorflow.keras.callbacks import Callback
import numpy as np
from sklearn.metrics import f1_score,classification_report,confusion_matrix

class F1CategoryCallback(Callback):
    def __init__(self,model_check,model_save_path,valid_data,batch_size=32):
        self.model_check = model_check
        self.model_save_path = model_save_path
        self.best_val_f1 = 0
        self.batch_size= batch_size
        self.valid_x = [x[0] for x in valid_data]
        self.valid_y = [x[1] for x in valid_data]
        self.count = 0


    def caculate_f1(self):
        predict_labels  = self.model_check.predict(self.valid_x,batch_size=self.batch_size)
        f1_score_value = f1_score(self.valid_y,predict_labels,average='macro')
        print(classification_report(self.valid_y,predict_labels))
        print(confusion_matrix(self.valid_y,predict_labels,labels=['不是',"不确定","是"]))

        return f1_score_value


    def on_epoch_end(self, epoch, logs=None):
        f1 = self.caculate_f1()

        if f1 >= self.best_val_f1:
            self.best_val_f1 = f1
            self.model_check.save(self.model_save_path)
            self.count = 0
        self.count += 1
        if self.count >15:
            self.model.stop_training = True
            self.count = 0
        print(
            'valid:  f1: %.5f, best f1: %.5f\n' %
            (f1, self.best_val_f1)
        )