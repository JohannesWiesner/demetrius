#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download an example file, create an example folder structure and 
run demetrius to demonstrate what it does.

@author: johannes.wiesner
"""


import os
import shutil
import requests
import tarfile
import tempfile

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
    
###############################################################################
## Download lena.png from GitHub ##############################################
###############################################################################
    
url = "https://github.com/mikolalysenko/lena/archive/master.tar.gz"
response = requests.get(url)

with tempfile.TemporaryDirectory() as temp_dir:
    
    temp_file_path = f"{temp_dir}/lena.tar.gz"

    with open(temp_file_path, "wb") as f:
        f.write(response.content)

    with tarfile.open(temp_file_path, mode="r:gz") as tar:
        tar.extractall(path=temp_dir)

    shutil.move(f"{temp_dir}/lena-master/lena.png", "./lena.png")

###############################################################################
## Download lena.png from GitHub ##############################################
###############################################################################

# generate folder structure
os.makedirs('./src')
os.makedirs('./src/holiday')
os.makedirs('./src/.hidden')
os.makedirs('./src/jane.doe/holiday')
os.makedirs('./src/john.doe/Holiday')
os.makedirs('./src/grandpa.doe/Holiday')

# copy file into folders
shutil.copy('lena.png','./src/.lena.png')
shutil.copy('lena.png','./src/.hidden/lena.png')
shutil.copy('lena.png','./src/holiday/lena.png')
shutil.copy('lena.png','./src/jane.doe/holiday/lena_1.png')
shutil.copy('lena.png','./src/jane.doe/holiday/lena_2.png')
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
