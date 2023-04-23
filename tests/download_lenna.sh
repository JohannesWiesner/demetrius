#!/bin/bash

# Download the lena.png file from this GitHub repository´
wget -qO- https://github.com/mikolalysenko/lena/archive/master.tar.gz | tar xz --wildcards '*lena.png' --strip-components=1
