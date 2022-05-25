import tensorflow as tf
from tensorflow.python.keras.engine import data_adapter
def creat_FGM(epsilon=1.0):
    @tf.function
    def train_step(self, data):
        '''
        计算在embedding上的gradient
        计算扰动 在embedding上加上扰动
        重新计算loss和gradient
        删除embedding上的扰动，并更新参数
        '''
        data = data_adapter.expand_1d(data)
        x, y, sample_weight = data_adapter.unpack_x_y_sample_weight(data)
        with tf.GradientTape() as tape:
            y_pred = self(x,training=True)
            loss = self.compiled_loss(
                y, y_pred, sample_weight, regularization_losses=self.losses)
        embedding = self.trainable_variables[0]
        embedding_gradients = tape.gradient(loss,[self.trainable_variables[0]])[0]
        embedding_gradients = tf.zeros_like(embedding) + embedding_gradients
        delta = epsilon * embedding_gradients / (tf.math.sqrt(tf.reduce_sum(embedding_gradients**2)) + 1e-8)  # 计算扰动
        self.trainable_variables[0].assign_add(delta)
        with tf.GradientTape() as tape2:
            y_pred = self(x,training=True)
            new_loss = self.compiled_loss(
                y, y_pred, sample_weight, regularization_losses=self.losses)
        gradients = tape2.gradient(new_loss,self.trainable_variables)
        self.trainable_variables[0].assign_sub(delta)

        self.optimizer.apply_gradients(zip(gradients,self.trainable_variables))
        #train_loss.update_state(loss)
        self.compiled_metrics.update_state(y, y_pred, sample_weight)
        return {m.name: m.result() for m in self.metrics}
    return train_step
