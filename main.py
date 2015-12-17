#!/usr/bin/env python

import sys
import os
import glob
import transcoder


def main():
    # Get the files in the order they should be processed
    files = getfiles(sys.argv[1:])
    for i in files:
        transcoder.transcode(i)


def getfiles(file_args):
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
    return fileList

if __name__ == '__main__':
    main()
