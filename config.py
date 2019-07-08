# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 09:20:36 2019

@author: nxf52810
"""

import os

PATH = os.getcwd()
RESOURCES_FONT_PATH = PATH + '\\resources\\fonts\\'
RESOURCES_IMAGE_PATH = PATH + '\\resources\\images\\'
PREVIOUS_SESSION = PATH + '\\PREVIOUS-SESSION.aclo'
STATUS_DICTIONARY = {
    'Complete': [True, False, 'Green'], 'Watching': [True, False, 'Blue'],
    'Decided': [True, False, 'Red'], 'Undecided': [True, True, 'White'],
    'Previously_Watched': [True, False, 'Orange'],
    'Rewatch': [False, False, None]}