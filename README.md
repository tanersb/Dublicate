# Duplicate File Finder

This Python script scans a specified folder for duplicate files based on their MD5 hash values. It then either moves the duplicates to a `duplicates` folder or deletes them, depending on the user's preference. Hidden and inaccessible files are skipped, and all actions are logged, with optional log saving.

## Features
- Scans a folder for duplicate files by MD5 hash.
- Moves duplicates to a `duplicates` folder or deletes them.
- Skips hidden and inaccessible files.
- Logs actions and can save the log.

## Requirements
- Python 3.x

python duplicate.py ./my_folder --remove --log

