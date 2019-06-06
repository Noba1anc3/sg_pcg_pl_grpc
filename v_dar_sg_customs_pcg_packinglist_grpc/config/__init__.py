# -*- coding: utf-8 -*-
from vconf import Config
import about
import os
from logzero import logger

_model_data_path = "/ws/conf/{}/{}".format(about.domain, about.appname)

if not os.path.exists(_model_data_path):
    os.makedirs(_model_data_path)

