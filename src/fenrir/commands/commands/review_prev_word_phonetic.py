#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from fenrir.core import debug
from fenrir.utils import word_utils
from fenrir.utils import char_utils

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
    def shutdown(self):
        pass 
    def getDescription(self):
        return _('phonetically spells the current word and set review to it')        
    
    def run(self):
        self.env['runtime']['cursorManager'].enterReviewModeCurrTextCursor()
        self.env['screen']['newCursorReview']['x'], self.env['screen']['newCursorReview']['y'], prevWord, endOfScreen, lineBreak = \
          word_utils.getPrevWord(self.env['screen']['newCursorReview']['x'], self.env['screen']['newCursorReview']['y'], self.env['screen']['newContentText'])
        
        if prevWord.isspace():
            self.env['runtime']['outputManager'].presentText(_("blank"), interrupt=True, flush=False)
        else:
            firstSequence = True
            for c in prevWord:
                currChar = char_utils.getPhonetic(c) 
                self.env['runtime']['outputManager'].presentText(currChar, interrupt=firstSequence, announceCapital=True, flush=False)
                firstSequence = False
        if endOfScreen:
            if self.env['runtime']['settingsManager'].getSettingAsBool('review', 'endOfScreen'):        
                self.env['runtime']['outputManager'].presentText(_('end of screen'), interrupt=True, soundIcon='EndOfScreen')                 
        if lineBreak:
            if self.env['runtime']['settingsManager'].getSettingAsBool('review', 'lineBreak'):        
                self.env['runtime']['outputManager'].presentText(_('line break'), interrupt=False, soundIcon='EndOfLine')    
    def setCallback(self, callback):
        pass
