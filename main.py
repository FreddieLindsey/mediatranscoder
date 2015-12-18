#!/usr/bin/env python

import glob
import os
import sys

import transcoder


def main():
    # Get the files in the order they should be processed
    # Split according to number of computers
    # List<List<String> >
    files = getfiles(sys.argv[1:])
    filecount = 0
    for i in files[0]:
        filecount += 1
        print 'File {count}:\t{name}\n'.format(count=filecount, name=i)
        transcoder.transcode(i)


def getfiles(file_args, split=1):
    fileList = []
    for i in file_args:
        if ('*' in i):
            fileList += glob.glob(i)
        else:
            fileList.append(i)
    for f in fileList:
        if not os.path.exists(f):
            fileList.remove(f)
    fileList = sorted(fileList, key=os.path.getsize)
    fileList.reverse()
    if (split > 1):
        count = 0
        fileLists = [[]]
        for i in range(1, split):
            fileLists.append([])
        for f in fileList:
            fileLists[count].append(f)
            count += 1
            count %= split
        return fileLists
    return [fileList]


if __name__ == '__main__':
    main()
