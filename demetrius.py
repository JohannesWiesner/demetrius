# -*- coding: utf-8 -*-
"""
Find and copy files from a source directory to a destination directory while 
preserving the original parent directories.

@author: johwi
"""

import json
import os
import re
import shutil

# TO-DO: Add spinning curser (https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor)
# https://www.google.com/search?q=halo+spinning+cursor&rlz=1C1CHZN_deDE919DE919&oq=halo+spinning+cursor&aqs=chrome..69i57.4012j0j7&sourceid=chrome&ie=UTF-8
# TO-DO: Estimate 'Doneness' by number of items x file size. 
# TO-DO: Allow module to be executed via terminal using argparse module
# TO-DO: Add an option to let user ignore directories in _find_files
# TO-DO: Allow user to decide to save a list of all found files. This list 
# should either be placed in the same directory as the destination directories or 
# separately in each of destination directory (showing only the source files for this
# directory)

def _get_suffixes_tuple(which_suffixes='all'):
    '''Get a tuple of suffixes based on the attached .json file file or based
    on a user input.
    
    Parameters
    ----------
    which_suffixes : str, list, tuple, optional
        If str and 'all', all suffixes from the .json file will be used for the search.
        If str and not 'all', a single file suffix is provided (e.g. '.png'.).
        If list, the strings represent subsets of the .json file (e.g. ['video','bitmap']).
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
    
def _find_files(src,suffixes):
    '''Search for files in a source directory based on one or multiple
    file suffixes.

    Parameters
    ----------
    src : str
        The source directory.
        
    suffixes : str, tuple of strs 
        A single file suffix or tuple of file suffixes that should be 
        searched for (e.g. '.jpeg' or ('.jpeg','.png')).

    Returns
    -------
    filepath_list : list
        A list of all found filepaths

    '''
    
    src = os.path.normpath(src)

    filepath_list = []

    for (paths,dirs,files) in os.walk(src):
        for file in files:
            if file.lower().endswith(suffixes):
                filepath_list.append(os.path.join(paths,file))
    
    return(filepath_list)

# FIXME: Is current_max_index really necessary? Couldn't it be automatically
# inferred from n_matches? If there's only one match, than there can't be an index,
# therefore current_max_index == None? If there are > 1 match than current_max_index
# automatically is n_matches - 1? But maybe the current method is not necessary but at least more
# fail-safe? One could also simply increase an integer-counter, instead of appending
# elements to a list and taking len(list). 
def _get_number_of_matches(dst_dir_set,dst_dir_name):
    '''Get number of matches for a given name of a directory in a set of
    directory paths.
    

    Parameters
    ----------
    dst_dir_set : str
        A set of directory paths (e.g. {'dst/foo','dst/bar'})
    dst_dir_name : str
        Name of a single directory

    Returns
    -------
    n_matches: int
        Number of found matches for the given input name of the directory
    current_max_index : int
        The current maximum index of any of the found matches

    '''
    
    dst_dir_name_set = {os.path.basename(os.path.normpath(dir_path)) for dir_path in dst_dir_set}
    re_pattern = dst_dir_name + '(_)([0-9]+)?$'
    matches = []
    matches_indexes = []

    for dir_name in dst_dir_name_set:
        re_match = re.match(re_pattern,dir_name)
        
        if dir_name == dst_dir_name or re_match:
            matches.append(dir_name)
        if re_match:
            match_index = int(re_match.group(2))
            matches_indexes.append(match_index)
    
    n_matches = len(matches)
    
    if n_matches > 1:
        current_max_index = max(matches_indexes)
    else:
        current_max_index = None
    
    return n_matches,current_max_index

def _get_dst_dirs_list(filepath_list,dst):
    '''Get a list of destination directories based on a filepath list. 
    The function will automatically create unique destination directories
    for groups of files that belong to the same source directory. In case
    there are multiple source directories with the same name, the function
    will add an index to the destination directories to maintain unique
    names for all destination directories. 
    
    Parameters
    ----------
    filepath_list : list
        A list of filepaths
    dst : str
        Path to the master destination directory.

    Returns
    -------
    dst_dirs_list : list
        A list of destination directories for the input list of filepaths.

    '''
    
    dst = os.path.normpath(dst)
    last_src_dir = None
    dst_dirs_list = []
    
    for filepath in filepath_list:

        current_src_dir = os.path.dirname(filepath)
        dst_dir_name = os.path.split(os.path.dirname(filepath))[1]
        dst_dir_path = os.path.join(dst,dst_dir_name)

        if current_src_dir == last_src_dir:
            dst_dirs_list.append(dst_dirs_list[-1])

        elif current_src_dir != last_src_dir:
            
            dst_dir_set = set(dst_dirs_list)
            
            if dst_dir_path in dst_dir_set:

                n_matches,current_max_index = _get_number_of_matches(dst_dir_set,dst_dir_name)

                if n_matches == 1:
                    dst_dir_path = dst_dir_path + "_1"
                    dst_dirs_list.append(dst_dir_path)
                    
                elif n_matches > 1:
                    dst_dir_path = f"{dst_dir_path}_{str(current_max_index + 1)}"
                    dst_dirs_list.append(dst_dir_path)
                
            elif not dst_dir_path in dst_dir_set:
                dst_dirs_list.append(dst_dir_path)
        
        last_src_dir = current_src_dir
        
    return(dst_dirs_list)

def _copy_files(filepath_list,dst_dirs_list):
    '''Copy files based on a list of filepaths and a corresponding
    list of destination directories.'''
    
    for dst_dir in set(dst_dirs_list):
        os.makedirs(dst_dir)

    for file,dst_dir in zip(filepath_list,dst_dirs_list):
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
    which_suffixes : str, tuple of str, optional
        If str and 'all', all suffixes from the .json file will be used for the search.
        If list, the strings represent subsets of the .json file (e.g. ['video','bitmap'])
        If str and not 'all', a single file suffix is provided (e.g. '.png'.
        If tuple, multiple file suffixes are provided (e.g. ('.png','.jpeg').
        
        Default: 'all'

    Returns
    -------
    None.

    '''
    
    suffixes =  _get_suffixes_tuple(which_suffixes)
    filepath_list = _find_files(src_dir,suffixes)
    dst_dirs_list = _get_dst_dirs_list(filepath_list,dst_dir)
    
    _copy_files(filepath_list,dst_dirs_list)

if __name__ == '__main__':
    pass