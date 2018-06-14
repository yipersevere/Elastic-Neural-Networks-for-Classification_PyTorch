#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 13:53:25 2018

@author: yue
"""

import matplotlib

matplotlib.use("PDF")
import matplotlib.pyplot as plt

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import cv2

import keras
from keras import optimizers
from keras.utils.generic_utils import CustomObjectScope
from keras.layers import Dense, Activation, Flatten
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.inception_v3 import InceptionV3
from keras.applications.xception import Xception
from keras.applications.mobilenet import MobileNet
from keras.applications.resnet50 import ResNet50
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.pooling import GlobalAveragePooling2D

from keras.optimizers import SGD, Adam
from keras.models import Model, load_model
from keras.utils import to_categorical
import keras.backend as K
from keras.callbacks import ReduceLROnPlateau, CSVLogger, EarlyStopping, Callback, ModelCheckpoint, \
    LearningRateScheduler
from keras.utils import plot_model

import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold, cross_val_score
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss, mean_absolute_error
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelBinarizer

import datetime
from io import StringIO
import shutil
import random
import sys
import traceback
import time

def LOG(message):
    global logFile
    ts = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    msg = "[%s] %s" % (ts, message)

    with open(logFile, "a") as fp:
        fp.write(msg + "\n")

    print(msg)

def log_summary(model):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    model.summary()

    sys.stdout = old_stdout
    summary = mystdout.getvalue()

    LOG("Model summary:")

    for line in summary.split("\n"):
        LOG(line)

def pretrain():
    instanceName = "AGE"
    model_name = "hl_ResNet_50_noshearing"

    timestamp = datetime.datetime.now()
    ts_str = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    path = "Pretrained" + os.sep + instanceName + os.sep + model_name + "_" + ts_str
    os.makedirs(path)

    global logFile
    logFile = path + os.sep + "log.txt"

    # pretrain_path = "data/noshearing_IMDB_WIKI/CROPS_AGE"
    # train_path = "data/CROPS/TRAIN"
    # valid_path = "data/noshearing_CVPR/VALID"
    # csv_valid_path = 'csv_file/valid_gt.csv'

    # batch_size = 32
    # epoch_size = 1024

    # LOG("Pre-training on noshearing data (ResNet50)...")

    target_size = (224, 224)
    base_model = ResNet50(include_top=False, input_shape=target_size + (3,))

    for layer in base_model.layers:
        layer.trainable = False

    w = base_model.outputs[0]
    w = Flatten()(w)
    final_output = Dense(101, activation='sigmoid', name='final_output')(w)

    add_layers = [layer for layer in base_model.layers if "add_" in layer.name]

    intermediate_outputs = []

    for layer in add_layers:
        w = layer.output
        name = layer.name
        w = GlobalAveragePooling2D()(w)
        w = Dense(101, activation='sigmoid', name='intermediate_' + name)(w)
        intermediate_outputs.append(w)

    inputs = base_model.inputs
    outputs = intermediate_outputs + [final_output]

    model = Model(inputs=inputs, outputs=outputs)

    output_names = [output.name.split("/")[0] for output in outputs]
    losses = {name: 'categorical_crossentropy' for name in output_names}

    num_outputs = len(outputs)
    print("there are %d outputs.\n" % num_outputs)
    loss_weights = [1] * num_outputs
    loss_weights = {name: w for name, w in zip(output_names, loss_weights)}
    
    model.compile(loss=losses, optimizer=SGD(lr=1e-3), loss_weights=loss_weights)

    # Print the Model summary for the user
    log_summary(model)


if __name__ == "__main__":
    pretrain()
