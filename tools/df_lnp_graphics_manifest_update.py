#!/usr/bin/env python
"""
Written for https://aur.archlinux.org/packages/dwarffortress-lnp-git
Replaces version in line "df_max_version": "0.42.05", to new defined version in
all manifest.json files in ~/.dwarffortress-lnp-git/LNP/graphics'

version 0.1
- Basic idea implemented, option for backing up original target_file
- Not tested on Windows

author: Pulec (pulec@upal.se)
"""
#TODO better logging using logging module?

from os import getenv, walk # for getting linux home and scanning through folder
from os import close, remove # for closing tempfile.mkstemp() and removing files
from os.path import join # for getting the path, alternative?
from shutil import move # for moving files from tmp to orig or making backups
from tempfile import mkstemp # for making temporary file

#--------------------------------input_config-----------------------------------
#for Linux
df_lnp_graphics_path = getenv('HOME') + '/.dwarffortress-lnp-git/LNP/graphics'
#for Windows
#please insert

#which filename to look for
target_filename = 'manifest.json'
#which line to look for
target_line = '"df_max_version": "0.42.05",'
#replace to version
df_max_version = '0.42.06'

#backup original manifests?
backup = False
#show debug from replace function?
debug = False

#------------------------------------defs---------------------------------------

def get_manifests(path, filter):
    manifests = []
    for dirpath, dirnames, filenames in walk(path):
        for file in filenames:
            if filter in file:
                manifests.append(join(dirpath,file))
    return manifests

def replace(file_path, pattern, subst, backup = False, debug = False):
    """
    Stolen from http://stackoverflow.com/posts/39110/revisions
    Added option to backup files instead of removing and debug
    """
    #Create temp file
    fh, abs_path = mkstemp()
    #TODO provide an option to specify?
    backup_path = file_path + '.BAK'
    if debug:
        print('\nDebug info:')
        print('file_path: {0}'.format(file_path))
        print('backup_path: {0}'.format(backup_path))
        print('pattern: {0}'.format(pattern))
        print('subst: {0}'.format(subst))
        input('Confirm by any key to continue')
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #undocumented??
    close(fh)
    #if backup = True:
    if backup:
        move(file_path, backup_path)
    else:
        #otherwise Remove original file
        remove(file_path)
    #Move new file
    move(abs_path, file_path)

def scan_manifests_and_replace_a_line(manifests, pattern, subst, backup = True, debug = False):
    count_fix = 0
    count_skip = 0
    for file in manifests:
        with open(file, 'r') as opened_file:
            for line in opened_file.readlines():
                if '"df_max_version":' in line:
                    if '.BAK' in file:
                        print("\nSkipping backup file:{0}"
                        .format(file))
                        count_skip += 1
                        continue
                    if line.strip().endswith('"' + df_max_version + '",'):
                        print("\nFile: {0}\nalready has version: {1}"
                        .format(file,line.strip()))
                        count_skip += 1
                    else:
                        print("\nFound line: {1}\nin file: {0}\n\nReplacing..."
                        .format(file,line.strip()))
                        replace(file, pattern, subst,
                        backup = backup, debug = debug)
                        count_fix += 1
    return (count_fix, count_skip)


#------------------------------------run----------------------------------------
if __name__ == '__main__':
    input('Will try to get all "{3}" files in:\n\
\n\
{0}\n\
\n\
and replace version in line {1} to "{2}".\n\
\n\
Confirm by any key to continue'
    .format(df_lnp_graphics_path, target_line, df_max_version, target_filename))

    #get manifests list
    manifests = get_manifests(df_lnp_graphics_path,target_filename)
    #get counts of fixed and skipped files and do the replace
    count_fix, count_skip = scan_manifests_and_replace_a_line(manifests,
    target_line, '"df_max_version": "{0}",'.format(df_max_version),
    backup = backup, debug = debug)

    print('\n\Scanned through {0} files\n\
{1} were fixed\n\
{2} were skipped'.format(len(manifests), count_fix, count_skip))
