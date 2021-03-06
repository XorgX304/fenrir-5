#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from fenrirscreenreader.core import debug

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
    def shutdown(self):
        pass 
    def getDescription(self):
        return _('enter v menu submenu')
    def run(self):
        self.env['runtime']['vmenuManager'].incLevel()
        text = self.env['runtime']['vmenuManager'].getCurrentEntry()
        self.env['runtime']['outputManager'].presentText(text, interrupt=True)
    def setCallback(self, callback):
        pass
