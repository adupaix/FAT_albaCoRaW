#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 12:40:20 2021

@author: adupaix

Change all the .npy files of
the folder where the script is
to .csv

"""

import csv
import os
import numpy as np

print("~~~ Converting files to csv ~~~\n")
path = os.path.dirname(os.path.realpath(__file__))

for file in os.listdir(path):
    if file.endswith(".npy"):
        fname = os.path.join(path, file)
        print("Current file: "+file)
        data = np.load(fname)
        with open(os.path.join(path, os.path.splitext(file)[0]+".csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        

