# regexplace: regular expression search and replace
# Stefano Spinucci
# 2006-02-07 (rev 4)

# thanks to roadrunner.py
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52553
# for some ideas and some code

# some small changes to the original receipt
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/473828
# - use getopt for parameters,
# - added ignore regex with default for hidden files
# - regex search changed from search to match for the filenames
# Mathias Weber
# 2007-12-05 (rev 5)

# remove getopt for optparse
# Mathias Weber
# 2008-31-01 (rev 6)

# tested with python 2.5.1

import sys
import os
import re
import string
from optparse import OptionParser


# pupulate and return 'fileslist[]' with all files inside 'dir' matching 'regx'
def make_files_list(dir_name, regx, iregx, recursive):

    # if dir is not a directory, exit with error
    if not os.path.isdir(dir_name):
        sys.exit(dir_name + ' is not a valid dir to walk !!!')

    # compile the search regexp
    cregex = re.compile(regx)
    ciregex = re.compile(iregx)

    # initialize the file list
    fileslist = []
    # loop on all files and select files matching 'regx'
    for root, dirs, files in os.walk(dir_name, topdown=True):
        if recursive:
            # maybe this could be done better?
            remove = []
            for i in xrange(len(dirs)):
                if ciregex.search(dirs[i]):
                    remove.append(i)
            remove.reverse()
            for i in remove:
                dirs.pop(i)
        else:
            # how to clear a list in an other way?
            while len(dirs) > 0:
                dirs.pop()
        for name in files:
            # ignore hidden files
            if ciregex.match(name):
                continue
            if cregex.match(name):
                path = os.path.join(root, name)
                fileslist.append(path)

    # return the file list
    return fileslist[:]


# in all files in 'fileslist' search the regexp 'searchregx' and replace
# with 'replacestring'; real substitution in files only if 'simulation' = 0;
# real substitution may also be step by step (if 'stepbystep' = 1)
def replace_in_files(fileslist, searchregx, replacestring, simulation,
        stepbystep):
    # compile regexp
    cregex = re.compile(searchregx)

    # print message to the user
    if simulation == 1:
        print '\nReplaced (simulation):\n'
    else:
        print '\nReplaced:\n'

    # loop on all files
    for xfile in fileslist:

        # initialize the replace flag
        replaceflag = 0

        # open file for read
        readlines = open(xfile, 'r').readlines()
        # intialize the list counter
        listindex = -1

        # search and replace in current file printing to the user changed lines
        for currentline in readlines:

            # increment the list counter
            listindex = listindex + 1

            # if the regexp is found
            if cregex.search(currentline):

                # make the substitution
                f = re.sub(searchregx, replacestring, currentline)

                # print the current filename, the old string and the new string
                print '\n' + xfile
                print '- ' + currentline,
                if currentline[-1:] != '\n': print '\n',
                print '+ ' + f,
                if f[-1:] != '\n': print '\n',

                # if substitution is real
                if simulation == 0:

                    # if substitution is step by step
                    if stepbystep == 1:

                        # ask user if the current line must be replaced
                        question = raw_input('write(Y), skip (n), quit (q) ? ')
                        question = string.lower(question)

                        # if quit
                        if question == 'q':
                            sys.exit('\ninterrupted by the user !!!')

                        # if skip
                        elif question == 'n':
                            pass

                        # if write
                        else:

                            # update the whole file variable ('readlines')
                            readlines[listindex] = f
                            replaceflag = 1

                    # if substitution is not step by step
                    else:

                        # update the whole file variable ('readlines')
                        readlines[listindex] = f
                        replaceflag = 1

        # if some text was replaced
        # overwrite the original file
        if replaceflag == 1:

            # open the file for writting
            write_file = open(xfile, 'w')

            # overwrite the file
            for line in readlines:
                write_file.write(line)

            # close the file
            write_file.close()


# main function
def main():
    parser = OptionParser(usage="usage: %prog [options] dirname search-regexp "
            "replace-string", version="%prog 1.0")
    parser.add_option("-f", "--files", dest="fileregex", default=".*",
            help="set the regular expression of files to search through. The "
                    " default vaule is: '.*' (All files)")
    parser.add_option("-i", "--ignorefiles", dest="ignorefileregex",
            default="\..*", help="set the regualr expression for the files to "
                    "ignore. This parameter applies as well to the directory "
                    "on the recursive search. The default value is: '\..*' "
                    "(Ignore files with leading dot)")
    parser.add_option("-r", "--recursive", dest="recursive", default=False,
            action="store_true", help="Prse files in subdirectories "
                    "recursively.")

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.error("Got the wrong number of parameters see usage.")

    # ask user for simulated execution or real substitution
    print '\nyou are replacing %s with %s in %s' % (args[1], args[2], args[0])
    print 'with the search for the files: %s ' % options.fileregex
    print 'and ignore files and directories that match: %s ' % \
            options.ignorefileregex
    question1 = raw_input('continue with real substitution (y/N) ? ')
    question1 = string.lower(question1)

    # if user selected real substitution, ask user if execution must be step
    # by step
    if question1 == 'y':
        question2 = raw_input('\nsubstitute step by step (Y/n) ? ')
        question2 = string.lower(question2)

    # make the file list
    fileslist = make_files_list(args[0], options.fileregex, \
            options.ignorefileregex, options.recursive)

    # if real substitution
    if question1 == 'y':

        # if step by step
        if question2 != 'n':
            replace_in_files(fileslist, args[1], args[2], 0, 1)

        # if not step by step
        else:
            replace_in_files(fileslist, args[1], args[2], 0, 0)

    # if simulated execution
    else:
        replace_in_files(fileslist, args[1], args[2], 1, 0)


if __name__ == '__main__':
    main()
