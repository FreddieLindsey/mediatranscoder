#!/usr/bin/env python
import os
import shlex
import subprocess

from transcodeitem import TranscodeItem


def check():
    print 'TODO: Check for system components'


def transcode(input):
    print input
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
        audiotrack = audiotracks[0]

        # Audio track encoding
        if audiotrack.channels > 5:
            if item.isHD1080:
                audioencoding = ('6ch', '448')
            elif item.isHD720:
                audioencoding = ('6ch', '384')
            else:
                audioencoding = ('dpl2', '160')
        else:
            audioencoding = ('dpl2', '160')

        # Subtitles
        subtitles = []
        for i in item.mediainfo.subs:
            subtitles.append(str(i.index))
        subtitles = ','.join(subtitles)

        # Output name
        filename, fileext = os.path.splitext(item.filename)
        output = filename + '-out.mkv'

        command = "HandBrakeCLI -i \"{input}\" -o \"{output}\" -f mkv -m -e x264 " \
                  "-q {quality} --cfr -E ffac3 -6 {a_ch} -B {a_bit} -w {w} -l {h} " \
                  "--modulus 2 --native-language eng --native-dub -a {audio} " \
                  "-s {subs} {custom}".format(
            input=item.filename, output=output, audio=audiotrack,
            subs=subtitles,
            w=dimensions[0], h=dimensions[1], custom=customsettings,
            a_ch=audioencoding[0], a_bit=audioencoding[1], quality=quality
        )
        print 'Running:\n', command, '\n'
        args = shlex.split(command)
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout_, stderr_ = process.communicate()
        if len(stderr_) != 0:
            print 'There was a problem with file {0}'.format(item.filename)
            for i in stderr_:
                print i
        if os.path.getsize(output) <= os.path.getsize(item.filename):
            print 'Transcoding complete for {0}'.format(item.filename)
            return
        else:
            quality -= 2
    print '{0} could not be processed at a high enough quality, '\
          'please use original'.format(item.filename)
