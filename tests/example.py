#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download an example file, create an example folder structure and 
run demetrius to demonstrate what it does.

@author: johannes.wiesner
"""

import subprocess
import os
import shutil

import sys
sys.path.append('../')
from demetrius import run


###############################################################################
## Prepare data ###############################################################
###############################################################################

# start with a clean directory
if os.path.isdir('./src'):
    shutil.rmtree('./src')
if os.path.isdir('./dst'):
    shutil.rmtree('./dst')

# download lena.png from GitHub repository
# FIXME: Make python code out of this bash script
subprocess.call(['./download_lenna.sh'])

# generate folder structure
os.makedirs('./src')
os.makedirs('./src/holiday')
os.makedirs('./src/jane.doe/holiday')
os.makedirs('./src/john.doe/Holiday')
os.makedirs('./src/grandpa.doe/Holiday')

# copy file into folders
shutil.copy('lena.png','./src/.lena.png')
shutil.copy('lena.png','./src/holiday/lena.png')
shutil.copy('lena.png','./src/jane.doe/holiday/lena.png')
shutil.copy('lena.png','./src/john.doe/Holiday/lena.png')
shutil.copy('lena.png','./src/grandpa.doe/Holiday/lena.png')

# delete original downloaded file
os.remove('./lena.png')

# create destination directory
os.makedirs('./dst')

###############################################################################
## Run demetrius ##############################################################
###############################################################################

run(src_dir='./src',dst_dir='./dst')