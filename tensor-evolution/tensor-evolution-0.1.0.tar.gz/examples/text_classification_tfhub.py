"""Text classification example"""
# Derived from Tensorflow basic text classification example.
# The original work contained the following
# copyright/notice info:

# MIT License
#
# Copyright (c) 2017 François Chollet
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# This derivative work is also licensed under Apache 2.0.

# Please see the original work for a detailed description of the steps not pertaining to evolution:
# https://www.tensorflow.org/tutorials/keras/text_classification

import os
import re
import string

import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_text as text
from configs.__init__ import CONFIG_DIR
from tensorEvolution import evo_config, tensor_evolution
from tensorEvolution.nodes import embedding, hub_node


def main():
    """Main method"""
    train_data, test_data = tfds.load(name="imdb_reviews", split=["train", "test"],
                                      batch_size=-1, as_supervised=True)

    train_examples, train_labels = tfds.as_numpy(train_data)
    test_examples, test_labels = tfds.as_numpy(test_data)

    path = os.path.join(CONFIG_DIR, 'text_classification_config_tfhub.yaml')
    evo_config.master_config.setup_user_config(path)

    data = train_examples, train_labels, test_examples, test_labels
    worker = tensor_evolution.EvolutionWorker()

    embedding_node = hub_node.HubNode("https://tfhub.dev/google/nnlm-en-dim50/2", input_shape=[],
                                      dtype=tf.string, trainable=True)

    embedding_node.has_variable_length_input = True
    embedding_node.accepts_variable_length_input = True
    embedding_node.variable_output_size = False

    initial_node_stack = [embedding_node]
    worker.set_initial_nodes([initial_node_stack])
    worker.evolve(data=data)

    best = worker.get_best_individual()
    print("\n" + str(best[0]))
    # tensor_net = best[1]
    # model = tensor_net.build_model()
    # model.compile(loss=worker.master_config.loss, optimizer=worker.master_config.opt,
    #               metrics=worker.master_config.config['metrics'])
    #
    # model.fit(train_features, train_labels, epochs=20)
    # model.evaluate(test_features, test_labels)


if __name__ == "__main__":
    main()
