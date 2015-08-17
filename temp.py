# -*- coding: utf-8 -*-
__author__ = 'lufo'
import os
import subprocess

path = '/Users/lufo/Downloads/darknet/'
os.chdir(path)
a = subprocess.check_output('./darknet detection test ./yolo_test_1.cfg ./yolo_test_1_39000.weights a.png', shell=True)
if 'aeroplane' in a:
    print 'have face'
