#!/usr/bin/python
"""
Name: wrapperIAC.py

Context: request from IRCAM RIM to get a unified interface to access, through python, Ircam* (ircambeat, ircamkeymode, ircamchord, ircamstructure) Audio Content (IAC) software

Date: 2014/12/17
Last-update: 201704/04

Author: peeters@ircam.fr, doukhan@ircam.fr

Suppose:
    mpg123 is installed in /opt/local/bin/mpg123
    ircambeat, ircamchord, ircamkeymode, ircamsummary are installed and PATH is configured to point to their location
"""

import os
from xml.dom import minidom
import pdb


class IrcamAudioContent:
    audioFile = []
    beatFile = []
    rhythmFile = []
    keymodeFile = []
    chordFile = []
    structFile = []
    __data = []

    def __getitem__(self, key):
        if key not in self.__data:
            if key in ['beat_Time', 'beat_isBeat', 'beat_isDownBeat']:
                self.readXmlBeat()
            elif key in ['bpm_mean', 'bpm_std', 'meter', 'percussivity', 'complexity', 'speedA', 'speedB', 'periodicity', 'rhythmPattern']:
                self.readXmlRhythm()
            elif key in ['key', 'mode', 'harmonicPattern']:
                self.readXmlKeyMode()
            elif key in ['chord_startTime', 'chord_stopTime', 'chord_label']:
                self.readXmlChord()
            elif key in ['struct_startTime', 'struct_stopTime', 'struct_label']:
                self.readXmlStructure()
            else:
                print "WARNING: field '%s' not part of the definition" % key
                return
        return self.__data[key]

    def __init__(self, audioFile):

        if audioFile.endswith('.mp3'):
            processAudioFile = audioFile.replace('.mp3', '-converted.wav')
            if not os.path.isfile(processAudioFile):
                os.system("/opt/local/bin/mpg123 -r 11025 -m -w '%s' '%s'" % (processAudioFile, audioFile))
            self.audioFile = processAudioFile
        else:
            self.audioFile = audioFile

        self.beatFile = self.audioFile + "_beat.xml"
        self.rhythmFile = self.audioFile + "_rhythm.xml"
        self.keymodeFile = self.audioFile + "_keymode.xml"
        self.chordFile = self.audioFile + "_chord.xml"
        self.structFile = self.audioFile + "_struct.xml"
        self.__data = dict()

    def readXmlBeat(self):
        if not os.path.isfile(self.beatFile):
            os.system('ircambeat -i "%s" -o "%s"' % (self.audioFile, self.beatFile) )

        doc = minidom.parse(self.beatFile)
        root = doc.documentElement
        self.__data['beat_Time'] = []
        self.__data['beat_isBeat'] = []
        self.__data['beat_isDownBeat'] = []
        for myElement in root.getElementsByTagName('beattype'):
            myParent = myElement.parentNode
            self.__data['beat_Time'].append(float(myParent.getAttribute('time')))
            self.__data['beat_isBeat'].append(int(myElement.getAttribute('beat')))
            self.__data['beat_isDownBeat'].append(int(myElement.getAttribute('measure')))



    def readXmlRhythm(self):
        if not os.path.isfile(self.rhythmFile):
            os.system('ircambeat -i "%s" -r "%s"' % (self.audioFile, self.rhythmFile) )
            #os.system("ircambeat -i '%s' -r '%s' -t 60" % (self.audioFile, self.rhythmFile) )

        doc = minidom.parse(self.rhythmFile)
        root = doc.documentElement
        myElement = root.getElementsByTagName('bpm_mean')
        self.__data['bpm_mean'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('bpm_std')
        self.__data['bpm_std'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('meter')
        self.__data['meter'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('percussivity')
        self.__data['percussivity'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('complexity')
        self.__data['complexity'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('speedA')
        self.__data['speedA'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('speedB')
        self.__data['speedB'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('periodicity')
        self.__data['periodicity'] = float(myElement[0].firstChild.nodeValue)
        myElement = root.getElementsByTagName('rhythmpattern')
        self.__data['rhythmPattern'] = myElement[0].firstChild.nodeValue

    def readXmlKeyMode(self):
        if not os.path.isfile(self.keymodeFile):
            os.system('ircamkeymode -i "%s" -o "%s"' % (self.audioFile, self.keymodeFile) )

        doc = minidom.parse(self.keymodeFile)
        root = doc.documentElement
        myElement = root.getElementsByTagName('key')
        self.__data['key'] = myElement[0].firstChild.nodeValue
        myElement = root.getElementsByTagName('mode')
        self.__data['mode'] = myElement[0].firstChild.nodeValue
        myElement = root.getElementsByTagName('harmonicpattern')
        self.__data['harmonicPattern'] = myElement[0].firstChild.nodeValue

    def readXmlChord(self):
        if not os.path.isfile(self.chordFile):
            os.system('ircamchord -i "%s" -o "%s"' % (self.audioFile, self.chordFile) )

        doc = minidom.parse(self.chordFile)
        root = doc.documentElement
        self.__data['chord_startTime'] = []
        self.__data['chord_stopTime'] = []
        self.__data['chord_label'] = []
        for myElement in root.getElementsByTagName('chordtype'):
            myParent = myElement.parentNode
            self.__data['chord_startTime'].append(float(myParent.getAttribute('time')))
            self.__data['chord_stopTime'].append(float(myParent.getAttribute('time'))+float(myParent.getAttribute('length')))
            self.__data['chord_label'].append(myElement.getAttribute('value'))

    def readXmlStructure(self):
        if not os.path.isfile(self.structFile):
            os.system('ircamsummary -i "%s" --xml_struct "%s"' % (self.audioFile, self.structFile)	)

        doc = minidom.parse(self.structFile)
        root = doc.documentElement
        self.__data['struct_startTime'] = []
        self.__data['struct_stopTime'] = []
        self.__data['struct_label'] = []
        for myElement in root.getElementsByTagName('structtype'):
            myParent = myElement.parentNode
            self.__data['struct_startTime'].append(float(myParent.getAttribute('time')))
            self.__data['struct_stopTime'].append(float(myParent.getAttribute('time'))+float(myParent.getAttribute('length')))
            self.__data['struct_label'].append(int(myElement.getAttribute('value')))


def main():
    #a = IrcamAudioContent("/Users/peeters/_work/_bin/_test/audio_phoenix.wav")
    a = IrcamAudioContent("/Users/peeters/_work/_sound/_collection/local_beat_perso/Incorrect_BPM/00000111067725/00000111067725_15_USMC16348806.mp3")
    print a['bpm_mean']
    print a['meter']


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
