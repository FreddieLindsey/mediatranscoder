import re


class VideoTrack:
    def __init__(self, input, index):
        self.index = index
        for i in input:
            if 'Width' in i:
                self.width = int(re.sub("[^0-9]", "", getValue(i)))
            if 'Height' in i:
                self.height = int(re.sub("[^0-9]", "", getValue(i)))


class AudioTrack:
    def __init__(self, input, index):
        self.index = index
        for i in input:
            if 'Format' in i and not hasattr(self, 'format'):
                self.format = getValue(i)
            if 'Bit rate' in i:
                self.bitrate = getValue(i)
            if 'Channel(s)' in i:
                self.channels = int(
                    re.sub("[^0-9]", "", getValue(i).split('/')[0]))
            if 'Language' in i:
                self.language = getValue(i)
            if 'Forced' in i:
                self.forced = getValue(i)


class SubTrack:
    def __init__(self, input, index):
        self.index = index
        for i in input:
            if 'Format' in i and not hasattr(self, 'format'):
                self.format = getValue(i)
            if 'Language' in i:
                self.language = getValue(i)
            if 'Forced' in i:
                self.forced = getValue(i)


def getKey(input):
    key, _ = input.split(':')
    key = key.strip()
    return key


def getValue(input):
    _, value = input.split(':')
    value = value.strip()
    return value
