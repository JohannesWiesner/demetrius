# -*- coding: utf-8 -*-
"""
Demetrius: Find and copy files and their parent directories from a source 
directory to a destination directory .

@author: johwi
"""

import json
import os
import sys
import shutil
import pandas as pd
import argparse
from spinner import Spinner

# TO-DO: Add an option to let user ignore directories in _find_files 
# https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk
# TO-DO: Allow user to decide to save information for all found files. This list 
# should either be placed in the same directory as the destination directories or 
# separately in each of destination directory (showing only the source files for this
# directory)
# TO-DO: Let the user decide over the fashion of added indices (e.g. '_1' or ' (1)')
# in _create_destination_directories

def _get_suffixes_tuple(which_suffixes='all'):
    '''Get a tuple of suffixes based on the attached .json file file or based
    on a user input.
    
    Parameters
    ----------
    which_suffixes : str, list, tuple, optional
        If str and 'all', all suffixes from the .json file will be used for the search.
        If str and not 'all', a single file suffix is provided (e.g. '.png'.).
        If list, the strings represent file subsets of the .json file (e.g. ['video','bitmap']).
        If tuple, multiple file suffixes are provided (e.g. ('.png','.jpeg')).
        
        Default: 'all'

    Returns
    -------
    suffixes : str,tuple of str
        Returns a single suffix or a tuple of file suffixes that should be used
        for the file search.

    '''
    
    if isinstance(which_suffixes, str) and which_suffixes == 'all':
        suffixes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'suffixes.json')
        with open(suffixes_path) as json_file:
            suffixes_dict = json.load(json_file)
            
        suffixes = tuple([suffix for suffixes in suffixes_dict.values() for suffix in suffixes])
    
    elif isinstance(which_suffixes, list):
        suffixes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'suffixes.json')
        with open(suffixes_path) as json_file:
            suffixes_dict = json.load(json_file)
            
        suffixes_dict = {key: suffixes_dict[key] for key in which_suffixes}
        suffixes = tuple([suffix for suffixes in suffixes_dict.values() for suffix in suffixes])
        
    elif isinstance(which_suffixes, (str, tuple)):
        suffixes = which_suffixes

    return suffixes
    
def _find_files(src_dir,suffixes,verbose=False):
    '''Search for files in a source directory based on one or multiple
    file suffixes. This function will only append a found file to the list
    if it exists (using os.path.exists) to check if the file is broken.

    Parameters
    ----------
    src_dir : str
        The source directory.
        
    suffixes : str, tuple of strs 
        A single file suffix or tuple of file suffixes that should be 
        searched for (e.g. '.jpeg' or ('.jpeg','.png')).

    verbose : bool
        If true, print spinning cursor

    Returns
    -------
    filepath_list : list
        A list of all found filepaths

    '''
    
    filepath_list = []

    if verbose == True:
        with Spinner('Searching for files '):
            for (paths,dirs,files) in os.walk(src_dir):
                for file in files:
                    filepath = os.path.join(paths,file)
                    if filepath.lower().endswith(suffixes) and os.path.exists(filepath):
                        filepath_list.append(filepath)

    if verbose == False:
        for (paths,dirs,files) in os.walk(src_dir):
            for file in files:
                filepath = os.path.join(paths,file)
                if filepath.lower().endswith(suffixes) and os.path.exists(filepath):
                    filepath_list.append(filepath)

    if not filepath_list:
        sys.stdout.write('Did not find any files based on the given suffixes')
        sys.exit()
        
    return filepath_list

def _create_destination_directories(filepath_list,dst_dir):
    '''Create a pandas.DataFrame holding the source filepaths as one column and
    corresponding destination directories as another column. In case there are 
    multiple source  directories with the same name, the function will add indices to the 
    destination directories to maintain unique folder names. 
    
    Parameters
    ----------
    filepath_list : list
        The list of all found files as returned from _find_files.
    dst_dir : str
        Path to the master destination directory.

    Returns
    -------
    df : pd.DataFrame
        A data frame that maps each filepath to its corresponding destination
        directory.

    '''

    # create data frame with filepath as column
    df = pd.DataFrame({'filepath':filepath_list})
    
    # get path to parent directory for each source file
    df['src_dir_path'] = df['filepath'].map(os.path.dirname)
    
    # get only the name of the parent for each source file
    df['src_dir_name'] = df['src_dir_path'].map(os.path.basename)
    
    # create destination path directory
    def create_dst_dir_path(row):
        return os.path.join(dst_dir,row['src_dir_name'])
    
    df['dst_dir_path'] = df.apply(create_dst_dir_path,axis=1)
    
    # find literal duplicates and modify the respective destination directories
    for _,dir_name in df.groupby('src_dir_name'):
        if not dir_name['src_dir_path'].nunique() == 1:
            for idx,(_,src_dir_path) in enumerate(dir_name.groupby('src_dir_path'),start=1):
                df.loc[src_dir_path.index,'dst_dir_path'] =  df.loc[src_dir_path.index,'dst_dir_path'] + '_' + str(idx)
    
    # find pseudo duplicates and modify the respective destination directories
    df['dst_dir_path_lower_case'] = df['dst_dir_path'].map(str.lower)
        
    for _,dst_dir_path in df.groupby('dst_dir_path_lower_case'):
        if dst_dir_path['src_dir_path'].nunique() != 1:
            for idx,(_,dir_name) in enumerate(dst_dir_path.groupby('src_dir_name'),start=1):
                df.loc[dir_name.index,'dst_dir_path'] = df.loc[dir_name.index,'dst_dir_path'] + ' (' + str(idx) + ')'
    
    return df

def _copy_files(dst_dirs_df,verbose=False):
    '''Copy files based on a list of source filepaths and a corresponding
    list of destination directories.
    
    Parameters
    ----------
    dst_dirs_df : pd.DataFrame
        A dataframe that holds a column with the source filepaths and one
        column specifying the destination directories.
    verbose : boolean, optional
        If True, copy process is estimated based on total bytes
        copied so far and then printed to console. The default is False.

    Returns
    -------
    None.

    '''
    
    for dst_dir in set(dst_dirs_df['dst_dir_path']):
        os.makedirs(dst_dir)
    
    if verbose == True:
        
        dst_dirs_df['filesize'] = dst_dirs_df['filepath'].map(os.path.getsize)
        bytes_total = dst_dirs_df['filesize'].sum()
        bytes_copied = 0
        
        for idx,(file,dst_dir) in enumerate(zip(dst_dirs_df['filepath'],dst_dirs_df['dst_dir_path'])):
            shutil.copy2(file,dst_dir)
            bytes_copied += dst_dirs_df['filesize'][idx]
            sys.stdout.write(f"Copied ~ {round(bytes_copied / bytes_total * 100,2)}% of files\r")
     
    elif verbose == False:
        for file,dst_dir in zip(dst_dirs_df['filepath'],dst_dirs_df['dst_dir_path']):
            shutil.copy2(file,dst_dir)

def run(src_dir,dst_dir,which_suffixes='all',verbose=False):
    '''Find and copy files with their respective parent directories 
    from a source directory to a destination directory
    
    Parameters
    ----------
    src_dir : str
        Path to the source directory.
    dst_dir : str
        Path to the destination directory.
    which_suffixes : str, list, tuple, optional
        If str and 'all', all suffixes from the .json file will be used for the search.
        If str and not 'all', a single file suffix is provided (e.g. '.png'.).
        If list, the strings represent file subsets of the .json file (e.g. ['video','bitmap']).
        If tuple, multiple file suffixes are provided (e.g. ('.png','.jpeg')).
        
        Default: 'all'
    verbose: bool
        If True, prints user information to console.

    Returns
    -------
    None.

    '''
       
    # get OS conform separator style
    src_dir = os.path.normpath(src_dir)
    dst_dir = os.path.normpath(dst_dir)
    
    # check if the input directories exist
    if not os.path.isdir(src_dir):
        raise NotADirectoryError('The specified source directory does not exist')
    if not os.path.isdir(dst_dir):
        raise NotADirectoryError('The specified destination directory does not exist')
        
    # get suffixes
    suffixes =  _get_suffixes_tuple(which_suffixes)
    
    # find files
    filepath_list = _find_files(src_dir,suffixes,verbose)
    
    # get data frame with destination directories
    dst_dirs_df = _create_destination_directories(filepath_list,dst_dir)
    
    # copy files
    _copy_files(dst_dirs_df,verbose)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Find and copy files from \
                                                a source directory to a \
                                                destination directory \
                                                while preserving the original \
                                                parent directories.')

    # add required arguments source and destination directory
    parser.add_argument('-src','--source_directory',type=str,required=True,help='The source directory which should be searched for files')
    parser.add_argument('-dst','--destination_directory',type=str,required=True,help='The destination directory where the files should be copied to within their parent directories')
    
    # add a mutually exlusive group (user should either provide one or multiple file suffixes
    # themselves or they should choose from already provided categories (e.g. bitmap,video))
    # if they neither provide --suffixes or --categories the default 'all' will be used
    suffix_arg_group = parser.add_mutually_exclusive_group()
    suffix_arg_group.add_argument('-sfx','--suffixes',type=str,nargs='+',help='File suffixes which should be used for the search. Mutually exlusive with -cat argument')
    suffix_arg_group.add_argument('-cat','--categories',type=str,nargs='+',choices=['bitmap','video'],help='Broader file categories (e.g. video or bitmap files) that define the final set of file suffixes. Mutually exclusive with -sfx argument')

    # add verbosity argument
    parser.add_argument('-v','--verbose',action='store_true',help='Show progress information on finding and copying files when demetrius is run')
    
    # parse arguments
    args = parser.parse_args()
    
    if args.suffixes == None and args.categories == None:
        which_suffixes = 'all'
    elif args.categories:
        which_suffixes = args.categories
    elif args.suffixes:
        which_suffixes = tuple(args.suffixes)
    
    # run demetrius
    run(src_dir=args.source_directory,
        dst_dir=args.destination_directory,
        which_suffixes=which_suffixes,
        verbose=args.verbose)