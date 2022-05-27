from __future__ import absolute_import, division, print_function, unicode_literals
from tensorflow import lite
from tensorflow import keras
import logging as lg
model = keras.models.load_model('../checkpoint/multi_class_image_classification.h5')
lg.info(model.summary())
converter = lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
model_size = len(tflite_model) / 1024
lg.info('model size = %dKBs.' % model_size)
converter.optimizations = [lite.Optimize.OPTIMIZE_FOR_LATENCY]
tflite_quantized_model = converter.convert()
quantized_model_size = len(tflite_quantized_model) / 1024
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
lg.info('Quantized model size = %dKBs,' % quantized_model_size)
