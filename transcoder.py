#!/usr/bin/env python
import os
import sys
import shlex
import subprocess

from transcodeitem import TranscodeItem


def check():
    print 'TODO: Check for system components'


def transcode(input):
    item = getinfo(input)
    transcode_(item)
    print 'Complete'


def getinfo(input):
    command = "mediainfo \"{0}\"".format(input)
    args = shlex.split(command)
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout_, stderr_ = process.communicate()
    return TranscodeItem(input, stdout_, stderr_)


def error(item):
    complete(item, '_error')


def outfile(item):
    complete(item, '_outfile')


def complete(item, folder='_complete'):
    filename, fileext = os.path.splitext(item)
    name = filename.split('/')[-1]
    filedir = '/'.join(filename.split('/')[:-1] + [folder])
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    print 'Moving original file:\t{name}\nTo:\t\t{dir}'.format(
        name=name, dir=filedir
    )
    out = filedir + '/' + name + fileext
    print out
    os.rename(item, out)


def transcode_(item):
    quality = 20
    while quality > 10:
        customsettings = ''

        # Dimensions
        if item.isHD1080 and item.aspectratio >= 1.7:
            dimensions = (1920, 1080)
        elif item.isHD720 and item.aspectratio >= 1.7:
            dimensions = (1280, 720)
        elif not item.isHD720 and not item.isHD1080:
            dimensions = (1024, 576)
            customsettings = '--custom-anamorphic --display-width 1024'

        # Audio tracks
        def getchannels(x):
            return x.channels

        audiotracks = sorted(item.mediainfo.audio, key=getchannels)
        for i in audiotracks:
            if 'English' not in i.language:
                audiotracks.remove(i)

        # Audio track encoding
        audioencoding = ([], [])
        for i in audiotracks:
            if i.channels > 5:
                if item.isHD1080:
                    i.audioencoding = ('6ch', '448')
                elif item.isHD720:
                    i.audioencoding = ('6ch', '384')
                else:
                    i.audioencoding = ('dpl2', '160')
            else:
                i.audioencoding = ('dpl2', '160')
            audioencoding[0].append(i.audioencoding[0])
            audioencoding[1].append(i.audioencoding[1])
        audioencoding = ','.join(audioencoding[0]), ','.join(audioencoding[1])
        audiotracks = ','.join(str(i.index) for i in audiotracks)

        # Subtitles
        subtitles = []
        for i in item.mediainfo.subs:
            if 'English' in i.language or 'Unknown' in i.language:
                subtitles.append(str(i.index))
        if len(subtitles) > 0:
            subtitles = '-s ' + ','.join(subtitles)
        else:
            subtitles = ''

        # Output name
        filename, fileext = os.path.splitext(item.filename)
        output = filename + '-out.mkv'

        command = "HandBrakeCLI -i \"{input}\" -o \"{output}\" -f mkv -m -e x264 " \
                  "-q {quality} --cfr -E ffac3 -6 {a_ch} -B {a_bit} -w {w} -l {h} " \
                  "--modulus 2 --native-language eng --native-dub -a {audio} " \
                  "{subs} {custom}".format(
          input=item.filename, output=output, audio=audiotracks,
          subs=subtitles, w=dimensions[0], h=dimensions[1],
          custom=customsettings, a_ch=audioencoding[0], a_bit=audioencoding[1],
          quality=quality
        )
        print 'Running:\n', command, '\n'
        args = shlex.split(command)
        proc = subprocess.Popen(args, bufsize=1,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True)
        stderr_ = ''
        while proc.poll() is None:
            line = proc.stdout.readline()
            stderr_ += line
            if line:
                if 'Encoding' in line:
                    if 'at frame' in line:
                        print '\x1b[2K\r', line,
                    else:
                        print '\x1b[2K\r',
                        sys.stdout.write(line.replace('\n', ''))
        if 'Encode done!' not in stderr_:
            print 'The file did not finish encoding {0}'.format(item.filename)
            print stderr_
            print '----------------------------------'
            error(item.filename)
            return
        elif os.path.getsize(output) <= os.path.getsize(item.filename):
            print 'Transcoding complete for {0}'.format(item.filename)
            complete(item.filename)
            outfile(output)
            return
        else:
            quality -= 2
    print '{0} could not be processed at a high enough quality, ' \
          'please use original'.format(item.filename)
    complete(item.filename)
