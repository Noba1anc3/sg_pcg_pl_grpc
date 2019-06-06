# -*- coding: utf-8 -*-

"""Top-level package for Ping Pong."""

__author__ = """zhangxuanrui"""
__email__ = "xuanrui.zhang@videt.cn"
__version__ = '0.1.0'

import os
import sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)
from . import clients, config, service