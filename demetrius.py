# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 20:17:11 2020

@author: johwi
"""

import os
import shutil
import re

# define which directory should be examined
examined_directory = "C:/Users/johwi/Desktop/test_src"

# define in which folder data should be copied (note that this string must end with a slash)
destination_directory = "C:/Users/johwi/Desktop/test_dst/"

# define suffixes to search for 
suffixes = (
    ".bmp",
	".gif",
	".ico",
	".jpeg",
	".jpg",
	".png",
	".tif",
	".tiff",
	".svg",
	".3g2",
	".3gp",
	".avi",
	".asf",
	".flv",
	".m4v",
	".mov",
	".mp4",
	".mpg",
	".mpeg",
	".wmv",
	".rm"
	)

# create destination folder if not yet manually created by user
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# search for files ending with suffixes above
# returns list with file paths
# note: .lower() method is implemented to avoid case sensitiveness concerning suffixes (e.g. files with extension ".JPG" should also be valid)
def find_files(folder,suffixes):

    filepath_list = []

    for (paths, dirs, files) in os.walk(folder):
        for file in files:
            if file.lower().endswith(suffixes):
                filepath_list.append(os.path.join(paths, file))
    
    return(filepath_list)

def copy_media_files(filepathlist,dst_dir):

    # get listlength for later user information
    list_length = len(filepathlist)
    
    # last directory path
    last_dir = None
    
    # last destination folder path
    last_dst = None
	
    for index,filepath in enumerate(filepathlist,start=1):

        # get current directory path
        current_dir = os.path.dirname(filepath)

        # check if current file is in same directory as file before
        # case 1: current file is not in the same directory as file before 
        if current_dir != last_dir:
			
            # get the name of parent folder of file
            parent_name = os.path.split(os.path.dirname(filepath))[1]

            # create a new directory path
            parentfolder_path = dst_dir + parent_name

            # check if this directory already exists
            # if not, just create folder in destination folder
            if not os.path.exists(parentfolder_path):

                os.makedirs(parentfolder_path)

                # save this ajusted folder path as last destination directory
                last_dst = parentfolder_path
            
            # if directory already exists, add an index to original directory
            # to create a unique folder name. For this get all duplicate folders
            # and add unique index to name of parent folder
            else:

                dst_folder_list = os.listdir(destination_directory)
                matches = []
                
                # FIXME: List of indices could already be extracted here
                re_pattern = parent_name + '(_[0-9]+)?$'
                
                for folder in dst_folder_list:
                    if folder == parent_name or re.match(re_pattern,folder):
                        matches.append(folder)

                # subcase 1: there is one but only one duplicate of this folder name.  
                # Append "_1" index to path to avoid WinError 183
                if len(matches) == 1:
					
                    parentfolder_path = parentfolder_path + "_1"

                    # create folder with adjusted folder name
                    os.makedirs(parentfolder_path)

                    # save this ajusted folder path as last destination directory
                    last_dst = parentfolder_path

                # subcase 2: there is more than one duplicate of this folder name. 
                # Look for the current maximum index and increment it by 1 to create
                # a new unique folder path
                elif len(matches) > 1:

                    folder_indexes = []

                    # extract all index integers from matches list
                    # FIXME: List of indices could already be extracted above
                    for match in matches:
                        folder_index = re.match(r'.*?([0-9]+)?$',match).group(1)

                        if folder_index is not None:
                            folder_indexes.append(folder_index)
					
                    # Get the current maximum index
                    # note: before being able to get maximum index, index string list has to be converted to integer list otherwise max() doesn't work
                    print(filepath)
                    print(matches)
                    folder_index_max = max([int(folder_index) for folder_index in folder_indexes])

                    # create new index by incrementing old one by one
                    folder_index_new = str(folder_index_max + 1)
					
                    # create folder with adjusted folder name
                    parentfolder_path = parentfolder_path + "_" + folder_index_new

                    # create folder with adjusted folder name
                    os.makedirs(parentfolder_path)

                    # save this ajusted folder path as last destination directory
                    last_dst = parentfolder_path
					
            # copy file to new subfolder
            shutil.copy2(filepath,parentfolder_path)

            # print user progress information 
            progress = round(index / list_length * 100,2)
            print('Progress: ~ {} %'.format(progress),"\n")

        # case 2: current file is in same directory as file before (they belong to the same folder)
        else:

            # copy file
            shutil.copy2(filepath,last_dst)

            # print user progress information 
            progress = round(index / list_length * 100,2)
            print('Progress: ~ {} %'.format(progress))

        # change last directory to current directory for next iteration
        last_dir = current_dir

        # write original file paths to txt file for user information
        os.chdir(dst_dir)
		
        with open("filepathlist.txt", "w",encoding='utf-8') as text_file:
            for filepath in filepathlist:
                text_file.write(filepath + "\n")

copy_media_files(find_files(examined_directory,suffixes),destination_directory)
