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

###############################################################################
## Prepare data ###############################################################
###############################################################################

# start with a clean directory
if os.path.isdir('./src'):
    shutil.rmtree('./src')
if os.path.isdir('./tgt'):
    shutil.rmtree('./tgt')

# download lena.png from GitHub repository
# FIXME: Make python code out of this bash script
subprocess.call(['./download_lenna.sh'])

# generate folder structure
os.makedirs('./src')
os.makedirs('./src/holiday')
os.makedirs('./src/jane.doe/holiday')
os.makedirs('./src/john.doe/Holiday')

# copy file into folders
shutil.copy('lena.png','./src/.lena.png')
os.makedirs('./src/holiday/lena.png')
os.makedirs('./src/jane.doe/holiday/lena.png')
os.makedirs('./src/john.doe/Holiday/lena.png')

# delete downloaded file
os.remove('./lena.png')

# create destination directory
os.makedirs('./dst')

###############################################################################
## Run demetrius ##############################################################
###############################################################################
