#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   f1score_save_callback.py
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/20 下午3:07   qiufengfeng      1.0         None
'''
import json
import os.path

from tensorflow.keras.callbacks import Callback
from sklearn.metrics import f1_score,classification_report
from nlp_tools.metrics.plot.confusion_seaborn import plot_confusion_mat

class F1SaveCallback(Callback):
    def __init__(self,model_check,model_save_path,valid_data,batch_size=32,label_names=None,early_stop_num=15 ):
        """

        @param model_check:
        @param model_save_path:
        @param valid_data:
        @param batch_size:
        @param label_names:
        @param early_stop_num:
        """
        self.model_check = model_check
        self.model_save_path = model_save_path
        self.batch_size= batch_size
        self.label_names = label_names
        self.early_stop_num = early_stop_num
        self.valid_x = [x[0] for x in valid_data]
        self.valid_y_ids = model_check.label_processor.transform([x[1] for x in valid_data])


        self.best_val_f1 = 0
        self.count = 0


        self.confusion_save_path = os.path.join(self.model_save_path,'confusion.jpg')
        self.classify_report_path = os.path.join(self.model_save_path,'classify_report.txt')



    def caculate_f1(self):
        predict_labels  = self.model_check.predict(self.valid_x,batch_size=self.batch_size,return_type='index')
        f1_score_value = f1_score(self.valid_y_ids,predict_labels,average='macro')
        report = classification_report(self.valid_y_ids,predict_labels,target_names=self.label_names,)
        print(report)
        figure = plot_confusion_mat(self.valid_y_ids, predict_labels, self.label_names)
        if f1_score_value >= self.best_val_f1:
            self.best_val_f1 = f1_score_value
            self.model_check.save(self.model_save_path)
            self.count = 0

            figure.savefig(self.confusion_save_path, dpi=600)
            with open(self.classify_report_path,'w',encoding='utf-8') as fwrite:
                if type(report) == dict:
                    report = json.dumps(report,indent=4,ensure_ascii=False)
                fwrite.write(report)

            print("new best f1: %.5f\n" % f1_score_value )
        else:
            print(
                'valid:  f1: %.5f, best f1: %.5f\n' %
                (f1_score_value, self.best_val_f1)
            )







    def on_epoch_end(self, epoch, logs=None):
        self.caculate_f1()
        self.count += 1
        if self.count >self.early_stop_num:
            self.model.stop_training = True
            self.count = 0