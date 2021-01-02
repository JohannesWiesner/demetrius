# Demetrius
A python library for finding and copying media files.

# NOTE
This repository is under development and currently contains bugs! Feel free to send pull requests :)

# Motivation
Your Grandpa gives you his PC and asks you if you could make a backup of his photos and videos. There's just one problem: All his mediafiles are stored in different folders and in different locations on his drive! A clear case for demetrius. Just pass in the source and destination directories and demetrius will crawl through all the folders, find files whose extensions match the extensions you are looking for and copies the files in the destination directory. And the files are not simply just copied over. Demetrius respects the folder structure. So for example, all files within `holiday_with_family` in the source directory will also be in `holiday_with_family` in the destination directory. Demetrius also takes care of duplicate folder names. For example, if there are several `holiday_with_family` folders on Grandpa's PC (which is not unlikely, because Grandpa forgot that it might be a good idea to specify a unique name for each holiday he spent with the family...) demetrius will conserve the original structure and creates `holiday_with_family_1, holiday_with_family_2, etc.`
# What Demetrius can't do
Demetrius is dumb. If you have a folder in the source directory that is called `foobar123` which contains a file named `X23nadjkn.png` (which is a photo of dickbutt) it will copy that with that folder to the destination directory. Accordingly, you have to weight demetrius's dumbness against how much time you want to spend with manually clicking through Grandpas PC. 
# Links
I can strongly recommend to use [AntiDupl](https://github.com/ermig1979/AntiDupl) after Demetrius was run. This will help you to identify duplicates of files, in case Grandpa saved the same file in different locations on his PC.