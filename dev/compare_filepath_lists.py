#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Do all files in one directory also appear in another directory? This script
helps to compare outputs from different demetrius versions
@author: johannes
"""

import os

src_dir = '/media/johannes/Elements/gutenwiesner/mediafiles/2015_10_backup_hannes_mediafiles/'
tgt_dir = '/home/johannes/work/repos/demetrius/tests/dst/2015_10_backup_hannes_mediafiles/'

files_tgt = []

for (paths,dirs,files) in os.walk(tgt_dir):
    for file in files:
        files_tgt.append(file)
        
files_src = []

for (paths,dirs,files) in os.walk(src_dir):
    for file in files:
        files_src.append(file)

print('Are all elements src also in tgt?')
print(set(files_src).issubset(files_tgt))

print('Are all elements in tgt also in src?')
print(set(files_src).issuperset(set(files_tgt)))

print('Files that only appear in tgt list but not in src')
print(list(set(files_tgt).difference(files_src)))

print('Files that only appear in src list but not in tgt')
print(list(set(files_src).difference(files_tgt)))
