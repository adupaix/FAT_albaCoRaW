#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:57:16 2021

@author: adupaix

Delete all the csv files in a folder
"""

import os

print("~~~ Deleting all csv files ~~~\n")
path = os.path.dirname(os.path.realpath(__file__))

for fname in sorted(os.listdir(path)):
    if fname.endswith('.csv'):
        os.remove(path +'/'+ fname)
        print("Current file: "+str(fname))
