#!/bin/python
from utils import mark_utils

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        return environment
    def shutdown(self, environment):
        return environment 
    def getDescription(self):
        return 'No Description found'        
    def run(self, environment):
        if (environment['commandBuffer']['Marks']['1'] == None) or \
          (environment['commandBuffer']['Marks']['2'] == None):
            environment['runtime']['outputManager'].presentText(environment, "please set begin and endmark", interrupt=True)
            return environment

        # use the last first and the last setted mark as range
        startMark = environment['commandBuffer']['Marks']['1'].copy()
        endMark = environment['commandBuffer']['Marks']['2'].copy() 
        if environment['commandBuffer']['Marks']['3'] != None:
            endMark = environment['commandBuffer']['Marks']['3'].copy()    

        marked = mark_utils.getTextBetweenMarks(startMark, endMark, environment['screenData']['newContentText'])

        if marked.strip() == '':
            environment['runtime']['outputManager'].presentText(environment, "blank", soundIcon='EmptyLine', interrupt=True)
        else:
            environment['runtime']['outputManager'].presentText(environment, marked, interrupt=True)
        return environment    
    def setCallback(self, callback):
        pass
