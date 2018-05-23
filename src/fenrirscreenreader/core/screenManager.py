#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from fenrirscreenreader.core import debug
from fenrirscreenreader.utils import screen_utils
import time, os, re, difflib

class screenManager():
    def __init__(self):
        self.currScreenIgnored = False
        self.prevScreenIgnored = False
    def initialize(self, environment):
        self.env = environment
        self.env['runtime']['settingsManager'].loadDriver(\
          self.env['runtime']['settingsManager'].getSetting('screen', 'driver'), 'screenDriver')    
        self.getCurrScreen()  
        self.getCurrScreen()
        self.getSessionInformation()        
        self.updateScreenIgnored()
        self.updateScreenIgnored()        

    def getCurrScreen(self):
        try:
            self.env['runtime']['screenDriver'].getCurrScreen()
        except:
            pass
    def getSessionInformation(self):
        try:    
            self.env['runtime']['screenDriver'].getSessionInformation()
        except:
            pass        
            
    def shutdown(self):
        self.env['runtime']['settingsManager'].shutdownDriver('screenDriver')
    def isCurrScreenIgnoredChanged(self):
        return self.getCurrScreenIgnored() != self.getPrevScreenIgnored()
    def hanldeScreenChange(self, eventData):
        self.getCurrScreen()
        self.updateScreenIgnored()         
        if self.isCurrScreenIgnoredChanged():
            self.env['runtime']['inputManager'].setExecuteDeviceGrab()
        self.env['runtime']['inputManager'].handleDeviceGrab()        
        self.getSessionInformation()  
              
        if self.isScreenChange():                 
            self.changeBrailleScreen()              
        if not self.isSuspendingScreen(self.env['screen']['newTTY']):       
            self.update(eventData, 'onScreenChange')
            self.env['screen']['lastScreenUpdate'] = time.time()
                 
    def handleScreenUpdate(self, eventData):
        self.env['screen']['oldApplication'] = self.env['screen']['newApplication'] 
        self.updateScreenIgnored() 
        if self.isCurrScreenIgnoredChanged():
            self.env['runtime']['inputManager'].setExecuteDeviceGrab()
        self.env['runtime']['inputManager'].handleDeviceGrab()     
        if not self.getCurrScreenIgnored():       
            self.update(eventData, 'onScreenUpdate')
            #if trigger == 'onUpdate' or self.isScreenChange() \
            #  or len(self.env['screen']['newDelta']) > 6:
            #    self.env['runtime']['screenDriver'].getCurrApplication() 
            self.env['screen']['lastScreenUpdate'] = time.time()
    def getCurrScreenIgnored(self):
        return self.currScreenIgnored
    def getPrevScreenIgnored(self):
        return self.prevScreenIgnored      
    def updateScreenIgnored(self):
        self.prevScreenIgnored = self.currScreenIgnored              
        self.currScreenIgnored = self.isSuspendingScreen(self.env['screen']['newTTY'])                            
    def update(self, eventData, trigger='onUpdate'):
        # set new "old" values
        self.env['screen']['oldContentBytes'] = self.env['screen']['newContentBytes']
        self.env['screen']['oldContentText'] = self.env['screen']['newContentText']
        self.env['screen']['oldContentAttrib'] = self.env['screen']['newContentAttrib']
        self.env['screen']['oldCursor'] = self.env['screen']['newCursor'].copy()
        if self.env['screen']['newCursorAttrib']:
            self.env['screen']['oldCursorAttrib'] = self.env['screen']['newCursorAttrib'].copy()        
        self.env['screen']['oldDelta'] = self.env['screen']['newDelta']
        self.env['screen']['oldAttribDelta'] = self.env['screen']['newAttribDelta']
        self.env['screen']['oldNegativeDelta'] = self.env['screen']['newNegativeDelta']
        self.env['screen']['newContentBytes'] = eventData['bytes']

        # get metadata like cursor or screensize
        self.env['screen']['lines'] = int( eventData['lines'])
        self.env['screen']['columns'] = int( eventData['columns'])
        self.env['screen']['newCursor']['x'] = int( eventData['textCursor']['x'])
        self.env['screen']['newCursor']['y'] = int( eventData['textCursor']['y'])
        self.env['screen']['newTTY'] = eventData['screen']
        self.env['screen']['newContentText'] = eventData['text']
        self.env['screen']['newContentAttrib'] = eventData['attributes']
        # screen change
        if self.env['screen']['newTTY'] != self.env['screen']['oldTTY']:
            self.env['screen']['oldContentBytes'] = b''
            self.env['screen']['oldContentAttrib'] = None
            self.env['screen']['oldContentText'] = ''
            self.env['screen']['oldCursor']['x'] = 0
            self.env['screen']['oldCursor']['y'] = 0
            self.env['screen']['oldDelta'] = ''
            self.env['screen']['oldAttribDelta'] = ''            
            self.env['screen']['oldCursorAttrib'] = None
            self.env['screen']['newCursorAttrib'] = None            
            self.env['screen']['oldNegativeDelta'] = ''          
        # initialize current deltas
        self.env['screen']['newNegativeDelta'] = ''
        self.env['screen']['newDelta'] = ''
        self.env['screen']['newAttribDelta'] = ''                           

        # changes on the screen
        oldScreenText = re.sub(' +',' ',self.env['runtime']['screenManager'].getWindowAreaInText(self.env['screen']['oldContentText']))
        newScreenText = re.sub(' +',' ',self.env['runtime']['screenManager'].getWindowAreaInText(self.env['screen']['newContentText']))        
        typing = False
        diffList = []        
        
        if (self.env['screen']['oldContentText'] != self.env['screen']['newContentText']):
            if self.env['screen']['newContentText'] != '' and self.env['screen']['oldContentText'] == '':
                if oldScreenText == '' and\
                  newScreenText != '':
                    self.env['screen']['newDelta'] = newScreenText
            else:
                cursorLineStart = self.env['screen']['newCursor']['y'] * self.env['screen']['columns'] + self.env['screen']['newCursor']['y']
                cursorLineEnd = cursorLineStart  + self.env['screen']['columns']         
                if abs(self.env['screen']['oldCursor']['x'] - self.env['screen']['newCursor']['x']) >= 1 and \
                  self.env['screen']['oldCursor']['y'] == self.env['screen']['newCursor']['y'] and \
                  self.env['screen']['newContentText'][:cursorLineStart] == self.env['screen']['oldContentText'][:cursorLineStart] and \
                  self.env['screen']['newContentText'][cursorLineEnd:] == self.env['screen']['oldContentText'][cursorLineEnd:]:
                    cursorLineStartOffset = cursorLineStart
                    cursorLineEndOffset = cursorLineEnd
                    #if cursorLineStart < cursorLineStart + self.env['screen']['newCursor']['x'] - 4:
                    #    cursorLineStartOffset = cursorLineStart + self.env['screen']['newCursor']['x'] - 4
                    if cursorLineEnd > cursorLineStart + self.env['screen']['newCursor']['x'] + 3:
                        cursorLineEndOffset = cursorLineStart + self.env['screen']['newCursor']['x'] + 3                                               
                    oldScreenText = self.env['screen']['oldContentText'][cursorLineStartOffset:cursorLineEndOffset] 
                    # oldScreenText = re.sub(' +',' ',oldScreenText)
                    newScreenText = self.env['screen']['newContentText'][cursorLineStartOffset:cursorLineEndOffset]
                    #newScreenText = re.sub(' +',' ',newScreenText)
                    diff = difflib.ndiff(oldScreenText, newScreenText) 
                    diffList = list(diff)
                    tempNewDelta = ''.join(x[2:] for x in diffList if x[0] == '+')
                    if tempNewDelta.strip() != '':
                        if tempNewDelta != ''.join(newScreenText[self.env['screen']['oldCursor']['x']:self.env['screen']['newCursor']['x']].rstrip()):
                            diffList = ['+ ' + self.env['screen']['newContentText'].split('\n')[self.env['screen']['newCursor']['y']]]
                    typing = True
                else:
                    diff = difflib.ndiff( oldScreenText.split('\n'),\
                      newScreenText.split('\n'))
                    diffList = list(diff)

                if not typing:
                    self.env['screen']['newDelta'] = '\n'.join(x[2:] for x in diffList if x[0] == '+')
                else:
                    self.env['screen']['newDelta'] = ''.join(x[2:] for x in diffList if x[0] == '+')             
                self.env['screen']['newNegativeDelta'] = ''.join(x[2:] for x in diffList if x[0] == '-')

        # track highlighted
        try:
            if self.env['screen']['oldContentAttrib'] != self.env['screen']['newContentAttrib']:
                if self.env['runtime']['settingsManager'].getSettingAsBool('focus', 'highlight'):
                    self.env['screen']['newAttribDelta'], self.env['screen']['newCursorAttrib'] = screen_utils.trackHighlights(self.env['screen']['oldContentAttrib'], self.env['screen']['newContentAttrib'], self.env['screen']['newContentText'], self.env['screen']['columns'])
        except Exception as e:
            self.env['runtime']['debug'].writeDebugOut('screenManager:update:highlight: ' + str(e),debug.debugLevel.ERROR) 

    def formatAttributes(self, attribute, attributeFormatString = None):
        # "black",
        # "red",
        # "green",
        # "brown",
        # "blue",
        # "magenta",
        # "cyan",
        # "white",
        # "default" # white.
        # _order_
        # "fg",
        # "bg",
        # "bold",
        # "italics",
        # "underscore",
        # "strikethrough",
        # "reverse",  
        # "blink"   
        # "fontsieze"
        # "fontfamily" 
        if not attributeFormatString:
            attributeFormatString = self.env['runtime']['settingsManager'].getSetting('general', 'attributeFormatString')
        if not attributeFormatString:
            return ''
        if attributeFormatString == '':
            return ''
        if not attribute:
            return ''
        if len(attribute) != 10:
            return ''
        # 0 FG color (name)
        try:
            attributeFormatString = attributeFormatString.replace('fenrirFGColor', _(attribute[0]))
        except Exception as e:
            attributeFormatString = attributeFormatString.replace('fenrirFGColor', '')
        # 1 BG color (name)
        try:
            attributeFormatString = attributeFormatString.replace('fenrirBGColor', _(attribute[1]))
        except Exception as e:
            attributeFormatString = attributeFormatString.replace('fenrirBGColor', '')
        # 2 bold (True/ False)
        try:
            if attribute[2]:
                attributeFormatString = attributeFormatString.replace('fenrirBold', _('bold'))    
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirBold', '')
        # 3 italics (True/ False)                                       
        try:
            if attribute[3]:        
                attributeFormatString = attributeFormatString.replace('fenrirItalics', _('italic'))
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirItalics', '')
        # 4 underline (True/ False)
        try:
            if attribute[4]:
                attributeFormatString = attributeFormatString.replace('fenrirUnderline', _('underline'))
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirUnderline', '')
        # 5 strikethrough (True/ False)
        try:
            if attribute[5]:
                attributeFormatString = attributeFormatString.replace('fenrirStrikethrough', _('strikethrough'))
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirStrikethrough', '')
        # 6 reverse (True/ False)
        try:
            if attribute[6]:        
                attributeFormatString = attributeFormatString.replace('fenrirReverse', _('reverse'))
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirReverse', '')
        # 7 blink (True/ False)     
        try:
            if attribute[7]:        
                attributeFormatString = attributeFormatString.replace('fenrirBlink', _('blink'))
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirBlink', '')
        # 8 font size (int/ string)
        try:
            try:
                attributeFormatString = attributeFormatString.replace('fenrirFontSize', int(attribute[8]))
            except:
                pass
            try:
                attributeFormatString = attributeFormatString.replace('fenrirFontSize', str(attribute[8]))
            except:
                pass 
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirFontSize', _('default'))
        # 9 font family (string)
        try:
            attributeFormatString = attributeFormatString.replace('fenrirFont', attribute[9])   
        except Exception as e:
            pass
        attributeFormatString = attributeFormatString.replace('fenrirFont', _('default'))
                 
        return attributeFormatString
    
    def isSuspendingScreen(self, screen = None):
        if screen == None:
            screen = self.env['screen']['newTTY']
        ignoreScreens = []
        fixIgnoreScreens = self.env['runtime']['settingsManager'].getSetting('screen', 'suspendingScreen')
        if fixIgnoreScreens != '':
            ignoreScreens.extend(fixIgnoreScreens.split(',')) 
        if self.env['runtime']['settingsManager'].getSettingAsBool('screen', 'autodetectSuspendingScreen'):
            ignoreScreens.extend(self.env['screen']['autoIgnoreScreens'])        
        try:
            ignoreFileName = self.env['runtime']['settingsManager'].getSetting('screen', 'suspendingScreenFile')
            if ignoreFileName != '':
                if os.access(ignoreFileName, os.R_OK):
                    with open(ignoreFileName) as fp:
                        ignoreScreens.extend(fp.read().replace('\n','').split(','))
        except:
            pass
        self.env['runtime']['debug'].writeDebugOut('screenManager:isSuspendingScreen ignore:' + str(ignoreScreens) + ' current:'+ str(screen ), debug.debugLevel.INFO)         
        return (screen in ignoreScreens)
 
    def isScreenChange(self):
        if not self.env['screen']['oldTTY']:
            return False
        return self.env['screen']['newTTY'] != self.env['screen']['oldTTY']
    def isDelta(self, ignoreSpace=False):
        newDelta = self.env['screen']['newDelta']
        if ignoreSpace:
            newDelta = newDelta.strip()                
        return newDelta != ''
    def isNegativeDelta(self):    
        return self.env['screen']['newNegativeDelta'] != ''
    def getWindowAreaInText(self, text):
        if not self.env['runtime']['cursorManager'].isApplicationWindowSet():
            return text
        windowText = ''
        windowList = text.split('\n')
        currApp = self.env['runtime']['applicationManager'].getCurrentApplication()
        windowList = windowList[self.env['commandBuffer']['windowArea'][currApp]['1']['y']:self.env['commandBuffer']['windowArea'][currApp]['2']['y'] + 1]
        for line in windowList:
            windowText += line[self.env['commandBuffer']['windowArea'][currApp]['1']['x']:self.env['commandBuffer']['windowArea'][currApp]['2']['x'] + 1] + '\n'
        return windowText
    
    def injectTextToScreen(self, text, screen = None):
        try:
            self.env['runtime']['screenDriver'].injectTextToScreen(text, screen) 
        except Exception as e:
            self.env['runtime']['debug'].writeDebugOut('screenManager:injectTextToScreen ' + str(e),debug.debugLevel.ERROR) 
            
    def changeBrailleScreen(self):
        if not self.env['runtime']['settingsManager'].getSettingAsBool('braille', 'enabled'):
            return    
        if not self.env['runtime']['brailleDriver']:
            return
        if self.env['screen']['oldTTY']:
            if not self.isSuspendingScreen(self.env['screen']['oldTTY']):
                try:
                    self.env['runtime']['brailleDriver'].leveScreen() 
                except Exception as e:
                    self.env['runtime']['debug'].writeDebugOut('screenManager:changeBrailleScreen:leveScreen ' + str(e),debug.debugLevel.ERROR) 
        if not self.isSuspendingScreen():
            try:
                self.env['runtime']['brailleDriver'].enterScreen(self.env['screen']['newTTY'])      
            except Exception as e:                
                self.env['runtime']['debug'].writeDebugOut('screenManager:changeBrailleScreen:enterScreen ' + str(e),debug.debugLevel.ERROR) 
