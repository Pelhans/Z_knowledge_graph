#!/usr/bin/env python
# coding=utf-8

import nrekit
import numpy as np
import tensorflow as tf
import sys
import os

dataset_name = 'nyt'
if len(sys.argv) > 1:
    dataset_name = sys.argv[1]
dataset_dir = os.path.join('./data', dataset_name)
if not os.path.isdir(dataset_dir):
    raise Exception("[ERROR] Dataset dir %s doesn't exist!" % (dataset_dir))

# The first 3 parameters are train / test data file name, word embedding file name and relation-id mapping file name respectively.
train_loader = nrekit.data_loader.json_file_data_loader(os.path.join(dataset_dir, 'train.json'), 
                                                        os.path.join(dataset_dir, 'word_vec.json'),
                                                        os.path.join(dataset_dir, 'rel2id.json'), 
                                                        mode=nrekit.data_loader.json_file_data_loader.MODE_RELFACT_BAG,
                                                        shuffle=True)
test_loader = nrekit.data_loader.json_file_data_loader(os.path.join(dataset_dir, 'test.json'), 
                                                       os.path.join(dataset_dir, 'word_vec.json'),
                                                       os.path.join(dataset_dir, 'rel2id.json'), 
                                                       mode=nrekit.data_loader.json_file_data_loader.MODE_ENTPAIR_BAG,
                                                       shuffle=False)

framework = nrekit.framework.re_framework(train_loader, test_loader)

class model(nrekit.framework.re_model):
    encoder = 'cnn'
    selector = 'att'

    def __init__(self, train_data_loader, batch_size, max_length=120):
        nrekit.framework.re_model.__init__(self, train_data_loader, batch_size, max_length=max_length)
        
        # Embedding
        x = nrekit.network.embedding.word_position_embedding(self.word, self.word_vec_mat, self.pos1, self.pos2)

        # Encoder cnn
        x_train = nrekit.network.encoder.cnn(x, keep_prob=0.5)
        x_test = nrekit.network.encoder.cnn(x, keep_prob=1.0)
	# Selector att
        self._train_logit, train_repre = nrekit.network.selector.bag_attention(x_train, self.scope, self.ins_label, self.rel_tot, True, keep_prob=0.5)
        self._test_logit, test_repre = nrekit.network.selector.bag_attention(x_test, self.scope, self.ins_label, self.rel_tot, False, keep_prob=1.0)
	# Classifier
        self._loss = nrekit.network.classifier.softmax_cross_entropy(self._train_logit, self.label, self.rel_tot, weights_table=self.get_weights())

    def loss(self):
        return self._loss

    def train_logit(self):
        return self._train_logit

    def test_logit(self):
        return self._test_logit

    def get_weights(self):
        with tf.variable_scope("weights_table", reuse=tf.AUTO_REUSE):
            print("Calculating weights_table...")
            _weights_table = np.zeros((self.rel_tot), dtype=np.float32)
            for i in range(len(self.train_data_loader.data_rel)):
                _weights_table[self.train_data_loader.data_rel[i]] += 1.0 
            _weights_table = 1 / (_weights_table ** 0.05)
            weights_table = tf.get_variable(name='weights_table', dtype=tf.float32, trainable=False, initializer=_weights_table)
            print("Finish calculating")
        return weights_table

framework.train(model, model_name=dataset_name + "_" + model.encoder + "_" + model.selector, max_epoch=60, ckpt_dir="checkpoint", gpu_nums=1)


