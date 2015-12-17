#!/usr/bin/env python

from mediainfo import MediaInfo


class TranscodeItem:
    def __init__(self, filename, mediainfo, mediainfo_err=[]):
        self.filename = filename
        self.mediainfo = MediaInfo(mediainfo)
        self.mediainfo_err = mediainfo_err
        self.isHD1080 = self.isHD1080()
        self.isHD720 = self.isHD720()
        self.aspectratio = self.aspectratio()

    def isHD1080(self):
        videos = self.mediainfo.video
        for i in videos:
            if i.height >= 1080 or i.width >= 1920:
                return True

    def isHD720(self):
        videos = self.mediainfo.video
        for i in videos:
            if i.height >= 720 or i.width >= 1280:
                return True

    def aspectratio(self):
        videos = self.mediainfo.video
        for i in videos:
            return float(i.width) / float(i.height)
