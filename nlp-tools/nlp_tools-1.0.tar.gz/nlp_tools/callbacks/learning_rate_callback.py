from tensorflow.keras.callbacks import Callback
import tensorflow.keras.backend as K
import numpy as np

class WarmupExponentialDecay(Callback):
    def __init__(self,lr_base=0.001,lr_min=0.0,decay=0.05,warmup_epochs=5):
        self.num_passed_batchs = 0   #一个计数器
        self.warmup_epochs=warmup_epochs
        self.lr=lr_base #learning_rate_base
        self.lr_min=lr_min #最小的起始学习率,此代码尚未实现
        self.decay=decay  #指数衰减率
        self.steps_per_epoch=0 #也是一个计数器
    def on_batch_begin(self, batch, logs=None):
        # params是模型自动传递给Callback的一些参数
        if self.steps_per_epoch==0:
            #防止跑验证集的时候呗更改了
            if self.params['steps'] == None:
                self.steps_per_epoch = np.ceil(1. * self.params['samples'] / self.params['batch_size'])
            else:
                self.steps_per_epoch = self.params['steps']
        if self.num_passed_batchs < self.steps_per_epoch * self.warmup_epochs:
            K.set_value(self.model.optimizer.lr,
                        0.1*(self.num_passed_batchs + 1) / self.steps_per_epoch / self.warmup_epochs)
        else:
            K.set_value(self.model.optimizer.lr,
                        self.lr*((1-self.decay)**(self.num_passed_batchs-self.steps_per_epoch*self.warmup_epochs)))
        self.num_passed_batchs += 1
    def on_epoch_begin(self,epoch,logs=None):
    #用来输出学习率的,可以删除
        print("learning_rate:",K.get_value(self.model.optimizer.lr))
