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
from halo import Halo

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

# FIXME: Is there a better test to check if files are broken? Currently
# only os.path.exists is implemented but I still get files image files
# that can't be open using IrfanView
def _find_files(src_dir,suffixes,exclude_dirs=None):
    '''Search for files in a source directory based on one or multiple
    file suffixes. This function will only append a found file to the list
    if it exists (using os.path.exists) wich serves as a minimal test for
    checking if a file is broken. 

    Parameters
    ----------
    src_dir : str
        The source directory.
    suffixes : str, tuple of strs 
        A single file suffix or tuple of file suffixes that should be 
        searched for (e.g. '.jpeg' or ('.jpeg','.png')).
    exclude_dirs : str, list of str, None
        Name of single directory of list of directory names that should be ignored when searching for files.
        All of the specified directories and their children directories will be
        ignored (Default: None)
        
    Returns
    -------
    filepath_list : list
        A list of all found filepaths

    '''
    
    filepath_list = []
    
    for (paths,dirs,files) in os.walk(src_dir):
        
        if exclude_dirs:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            
            filepath = os.path.join(paths,file)
            
            if not filepath.lower().endswith(suffixes):
                continue
            
            if not os.path.exists(filepath):
                continue
            
            filepath_list.append(filepath)

    if len(filepath_list) == 0:
        sys.exit(f"No files that match the given criteria where found within {src_dir}")
        
    return filepath_list

def _find_src_dir_duplicates(df):
    '''Group dataframe by source directory names. If there are different source 
    directory paths that share the same basename we have to differentiate between
    them otherwise files from different directories with same name would be placed 
    within the same folder 
    '''
    
    for _, src_dir_df in df.groupby('src_dir_name'):
        
        # if there are more than just one source directory that share the same
        # base name we have to adapt the destination path to put them in separate folders
        if src_dir_df['src_dir_path'].nunique() != 1:
            for idx, (_, src_dir_paths) in enumerate(src_dir_df.groupby('src_dir_path'),start=1):
                df.loc[src_dir_paths.index,'dst_dir_path'] += f"_{idx}"
                
    return df

def _find_pseudo_src_dir_duplicates(df):
    '''Find pseudo duplicate destination directories (e.g. holiday_1 & Holiday_1)
    because it's not possible on Windows to create those in the same folder'''
    
    df['dst_dir_path_lower_case'] = df['dst_dir_path'].map(str.lower)
        
    for _,dst_dir_df in df.groupby('dst_dir_path_lower_case'):
        if dst_dir_df['src_dir_path'].nunique() != 1:
            for idx,(_,src_dir_names) in enumerate(dst_dir_df.groupby('src_dir_name'),start=1):
                df.loc[src_dir_names.index,'dst_dir_path'] += f" ({idx})"
    
    return df

def _get_dst_dirs_df(filepath_list,dst_dir):
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
    dst_dirs_df : pd.DataFrame
        A data frame that maps each filepath to its corresponding destination
        directory.

    '''

    # create data frame with filepath as column
    dst_dirs_df = pd.DataFrame({'filepath':filepath_list})
    
    # get path to parent directory for each source file
    dst_dirs_df['src_dir_path'] = dst_dirs_df['filepath'].map(os.path.dirname)
    
    # get only the name of the parent for each source file
    dst_dirs_df['src_dir_name'] = dst_dirs_df['src_dir_path'].map(os.path.basename)
    
    # set path to the destination directory    
    dst_dirs_df['dst_dir_path'] = dst_dirs_df['src_dir_name'].map(lambda x: os.path.join(dst_dir, x))
    
    # find literal duplicates and modify the respective destination directories
    dst_dirs_df = _find_src_dir_duplicates(dst_dirs_df)
    
    # find pseudo duplicates and modify the respective destination directories
    dst_dirs_df = _find_pseudo_src_dir_duplicates(dst_dirs_df)

    return dst_dirs_df

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
        copied so far and then printed to console (Default: False).

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

def run(src_dir,dst_dir,which_suffixes='all',exclude_dirs=None,verbose=False):
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
        (Default: 'all').
    exclude_dirs : str, list of str, None
        Name of single directory of list of directory names that should be ignored when searching for files.
        All of the specified directories and their children directories will be
        ignored (Default: None).
    verbose: bool
        If True, prints user information to console (Default: False).

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
    
    # if only a single directory was provided convert to list of single string
    if exclude_dirs and isinstance(exclude_dirs,str):
        exclude_dirs = list(exclude_dirs)
    
    # search for files
    if verbose == True:
        with Halo(text='Searching for files', spinner='dots'):
            filepath_list = _find_files(src_dir,suffixes,exclude_dirs)
    else:
        filepath_list = _find_files(src_dir,suffixes,exclude_dirs)
    
    # get data frame with destination directories
    dst_dirs_df = _get_dst_dirs_df(filepath_list,dst_dir)
    
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
    
    # add exclude dirs argument
    parser.add_argument('-e','--exclude',type=str,nargs='+',help='One or multiple names of directories that should be ignored when searching for files. All of the specified directories and their children directories will be ignored')

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
        exclude_dirs=args.exclude,
        verbose=args.verbose)