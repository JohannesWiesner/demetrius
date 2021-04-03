# -*- coding: utf-8 -*-
"""
Demetrius: Find and copy files and their parent directories from a source 
directory to a destination directory .

@author: johwi
"""

import json
import os
import shutil
import pandas as pd

# TO-DO: Add spinning curser (https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor)
# https://www.google.com/search?q=halo+spinning+cursor&rlz=1C1CHZN_deDE919DE919&oq=halo+spinning+cursor&aqs=chrome..69i57.4012j0j7&sourceid=chrome&ie=UTF-8
# TO-DO: Estimate 'Doneness' by number of items x file size. 
# TO-DO: Allow module to be executed via terminal using argparse module
# TO-DO: Add an option to let user ignore directories in _find_files
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
    
def _find_files(src_dir,suffixes):
    '''Search for files in a source directory based on one or multiple
    file suffixes.

    Parameters
    ----------
    src_dir : str
        The source directory.
        
    suffixes : str, tuple of strs 
        A single file suffix or tuple of file suffixes that should be 
        searched for (e.g. '.jpeg' or ('.jpeg','.png')).

    Returns
    -------
    filepath_list : list
        A list of all found filepaths

    '''
    
    filepath_list = []

    for (paths,dirs,files) in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(suffixes):
                filepath_list.append(os.path.join(paths,file))
    
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
    
    # find literal duplicates and add indices
    for _,dir_name in df.groupby('src_dir_name'):
        if not dir_name['src_dir_path'].nunique() == 1:
            for idx,(_,src_dir_path) in enumerate(dir_name.groupby('src_dir_path'),start=1):
                df.loc[src_dir_path.index,'dst_dir_path'] =  df.loc[src_dir_path.index,'dst_dir_path'] + '_' + str(idx)
    
    # find pseudo duplicates and add indices
    df['dst_dir_path_lower_case'] = df['dst_dir_path'].map(str.lower)
        
    for _,dst_dir_path in df.groupby('dst_dir_path_lower_case'):
        if dst_dir_path['src_dir_path'].nunique() != 1:
            for idx,(_,dir_name) in enumerate(dst_dir_path.groupby('src_dir_name'),start=1):
                df.loc[dir_name.index,'dst_dir_path'] = df.loc[dir_name.index,'dst_dir_path'] + ' (' + str(idx) + ')'
    
    return df

def _copy_files(dst_dirs_df):
    '''Copy files based on a list of source filepaths and a corresponding
    list of destination directories.'''
    
    for dst_dir in set(dst_dirs_df['dst_dir_path']):
        os.makedirs(dst_dir)

    for file,dst_dir in zip(dst_dirs_df['filepath'],dst_dirs_df['dst_dir_path']):
        shutil.copy2(file,dst_dir)

def run(src_dir,dst_dir,which_suffixes='all'):
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

    Returns
    -------
    None.

    '''
   
    # get OS conform separator style
    src_dir = os.path.normpath(src_dir)
    dst_dir = os.path.normpath(dst_dir)
    
    # get suffixes
    suffixes =  _get_suffixes_tuple(which_suffixes)
    
    # find files
    filepath_list = _find_files(src_dir,suffixes)
    
    # get data frame with destiantion directories
    dst_dirs_df = _create_destination_directories(filepath_list, dst_dir)
    
    # copy files
    _copy_files(dst_dirs_df)

if __name__ == '__main__':
    pass