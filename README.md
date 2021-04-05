# Demetrius
A python library for finding and copying files within their parent directories.

# NOTE
Feel free to send pull requests by having a look at the FIXMEs and TODOs inside demetrius.py

# Motivation
Your Grandpa gives you his PC and asks you if you could make a backup of his photos and videos. There's just one problem: All his mediafiles are stored in different folders and in different locations on his drive! In case you don't want to go manually through each folder, this is a case for demetrius. Just pass in the source and destination directory and demetrius will crawl through all the folders, find files whose extensions match the extensions you are looking for and copies the files in the destination directory. 

Demetrius will copy files within their parent directory to ensure that you don't end up with one destination folder where all files are stored in. So for example, all files within a folder `holiday` in the source directory will also be in a `holiday` folder  in the destination directory. Demetrius also takes care of duplicate folder names. For example, if there are several `holiday` folders on Grandpa's PC (which is not unlikely, because Grandpa forgot that it might have been a good idea to specify a unique name for each holiday he spent with the family...) demetrius will conserve the original structure and creates `holiday, holiday_2, etc.`. 

Finally, Demetrius also respect case insensitive OS like Windows where you can't create a folder `holiday` and `Holiday` in the same directory (e.g. by adding indices (`'holiday (1)'`,`'Holiday (2)'`)).

# Usage
Demetrius can be used via the console. For example:
```python demetrius.py -src ./foo -dst ./bar``` will copy all found files in `./foo` to `./bar` withing their parent directories. For that, the script uses all file suffixes found in `suffixes.json` for the search. You can also filter for specifc  file suffixes via the `-sfx` flag (e.g. `-sfx png jpg`) or even for broad file categories using the `-cat` flag (e.g. `-cat video` for only searching for video files). Use the `-e` flag if you want to ignore certain directories and their children directories (e.g. `-e Windows "Program Files"`). Use `-v` if you want demetrius to show progress information. 

# What Demetrius can't do
Demetrius is dumb. If you have a folder in the source directory that is called `foobar` which contains a file named `123.png` (which is a photo of dickbutt) it will copy that with that folder to the destination directory. Accordingly, you have to weight demetrius's dumbness against how much time you want to spend with manually clicking through Grandpas PC. U
# Links
I can strongly recommend to run [AntiDupl](https://github.com/ermig1979/AntiDupl) after Demetrius was run to identify file duplicates.