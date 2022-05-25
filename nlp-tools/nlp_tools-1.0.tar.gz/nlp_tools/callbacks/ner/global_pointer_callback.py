from tensorflow import keras




class GlobalPointEvaluator(keras.callbacks.Callback):
    def __init__(self,model_check,model_save_path,valid_data,batch_size=32):
        self.model_check = model_check
        self.model_save_path = model_save_path
        self.best_val_f1 = 0
        self.batch_size= batch_size
        self.valid_x = [data[0] for data in valid_data]
        self.valid_y = [data[1] for data in valid_data]


    def caculate_f1(self):
        predict_labels  = self.model_check.predict(self.valid_x)
        X, Y, Z = 1e-10, 1e-10, 1e-10
        for predict_labels,real_labels in zip(predict_labels,self.valid_y):
            predict_labels = set(predict_labels)
            real_labels = set(real_labels)

            X += len(predict_labels & real_labels)
            Y += len(predict_labels)
            Z += len(real_labels)
        f1,precision,recall = round(2 * X/ (Y +Z),5),round(X/Y,5),round(X/Z,5)
        return f1,precision,recall


    def on_epoch_end(self, epoch, logs=None):
        f1,precision,recall = self.caculate_f1()

        if f1 >= self.best_val_f1:
            self.best_val_f1 = f1
            self.model_check.save(self.model_save_path)
        print(
            'valid:  f1: %.5f, precision: %.5f, recall: %.5f, best f1: %.5f\n' %
            (f1, precision, recall, self.best_val_f1)
        )


class GlobalPointCategoryEvaluator(keras.callbacks.Callback):
    def __init__(self,model_check,model_save_path,valid_data,batch_size=32):
        self.model_check = model_check
        self.model_save_path = model_save_path
        self.best_val_f1 = 0
        self.batch_size= batch_size
        self.valid_x = [data[0] for data in valid_data]
        self.valid_y = [data[1] for data in valid_data]


    def caculate_f1(self):
        predict_labels  = self.model_check.predict(self.valid_x)
        X, Y, Z = 1e-10, 1e-10, 1e-10
        for predict_labels,real_labels in zip(predict_labels,self.valid_y):
            predict_labels = set(predict_labels)
            real_labels = set(real_labels)

            X += len(predict_labels & real_labels)
            Y += len(predict_labels)
            Z += len(real_labels)
        f1,precision,recall = round(2 * X/ (Y +Z),5),round(X/Y,5),round(X/Z,5)
        return f1,precision,recall


    def on_epoch_end(self, epoch, logs=None):
        f1,precision,recall = self.caculate_f1()

        if f1 >= self.best_val_f1:
            self.best_val_f1 = f1
            self.model_check.save(self.model_save_path)
        print(
            'valid:  f1: %.5f, precision: %.5f, recall: %.5f, best f1: %.5f\n' %
            (f1, precision, recall, self.best_val_f1)
        )
