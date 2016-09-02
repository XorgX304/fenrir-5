#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

import os, sys, signal, time

if not os.getcwd() in sys.path:
    sys.path.append(os.getcwd())

from core import environment 
from core import settingsManager
from utils import debug

class fenrir():
    def __init__(self):
        self.environment = settingsManager.settingsManager().initFenrirConfig()
        signal.signal(signal.SIGINT, self.captureSignal)
    
    def proceed(self):
        self.environment['runtime']['outputManager'].presentText(self.environment, "Start Fenrir", soundIcon='ScreenReaderOn', interrupt=True)          
        while(self.environment['generalInformation']['running']):
            try:
                self.handleProcess()
            except Exception as e:
                self.environment['runtime']['debug'].writeDebugOut(self.environment,str(e),debug.debugLevel.ERROR) 
        self.shutdown()

    def handleProcess(self):
        self.environment, timeout = self.environment['runtime']['inputManager'].proceedInputEvents(self.environment)
        try:
            self.environment = self.environment['runtime']['screenManager'].update(self.environment)
        except Exception as e:
            self.environment['runtime']['debug'].writeDebugOut(self.environment, str(e),debug.debugLevel.ERROR)                
        if not self.environment['input']['keyForeward']:        
            self.environment = self.environment['runtime']['commandManager'].getCommandForShortcut(self.environment)        
        if not timeout:
            self.environment = self.environment['runtime']['commandManager'].executeTriggerCommands(self.environment, 'onInput')            
        self.environment = self.environment['runtime']['commandManager'].executeTriggerCommands(self.environment, 'onScreenChanged')        
        if not self.environment['input']['keyForeward']:
            if self.environment['commandInfo']['currCommand'] != '':
                self.handleCommands()

    def handleCommands(self):
        if (self.environment['commandInfo']['currCommand'] != ''):
            self.environment = self.environment['runtime']['commandManager'].executeCommand(self.environment, self.environment['commandInfo']['currCommand'], 'commands')

    def shutdownRequest(self):
        self.environment['generalInformation']['running'] = False

    def captureSignal(self, siginit, frame):
        self.shutdownRequest()

    def shutdown(self):      
        self.environment['runtime']['outputManager'].presentText(self.environment, "Quit Fenrir", soundIcon='ScreenReaderOff', interrupt=True)  

        if self.environment['runtime']['debug'] != None:
            self.environment['runtime']['debug'].closeDebugFile()
        if self.environment['runtime']['soundDriver'] != None:
            self.environment['runtime']['soundDriver'].shutdown()
        if self.environment['runtime']['speechDriver'] != None:
            self.environment['runtime']['speechDriver'].shutdown()
        self.environment['runtime']['inputManager'].freeDevices()

app = fenrir()
app.proceed()
