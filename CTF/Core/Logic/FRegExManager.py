# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import copy
import types
import os
import os.path

from Core.Common.FConstants import *

class FRegExManager:
    def __init__(self):
        #[[setting, [regEx1, regEx2,], [ignoredRegEx1, ignoredRegEx1,]], ]
        self.__regExs = []
    
    # this method is called to fix backward compatibility issues
    def BackwardCompatibility(self):
        message = False
        for i in range(len(self.__regExs)):
            # in v1.1b and prior, no ignoredRegEx
            if (len(self.__regExs[i]) == 2):
                if (not message):
                    message = True
                    print "<FRegExManager> backward compatibility fix"
                self.__regExs[i].append([""])
            
            # in v1.1b and prior, no multiple regular expressions
            if (type(self.__regExs[i][1]) != types.ListType):
                if (not message):
                    message = True
                    print "<FRegExManager> backward compatibility fix"
                self.__regExs[i][1] = [self.__regExs[i][1]]
            
            # in v1.1b and prior, no multiple ignored regular expressions
            if (type(self.__regExs[i][2]) != types.ListType):
                if (not message):
                    message = True
                    print "<FRegExManager> backward compatibility fix"
                self.__regExs[i][2] = [self.__regExs[i][2]]
        return message
    
    def BackwardCompatibilityPath(self):
        for regEx in self.__regExs:
            for i in range(len(regEx[1])):
                if (regEx[1][i] != ""):
                    regEx[1][i] = ("(" + os.path.basename(ROOT_DIR) + 
                            os.sep.replace("\\", "\\\\") + ")(" + regEx[1][i] + 
                            ")")
            for i in range(len(regEx[2])):
                if (regEx[2][i] != ""):
                    regEx[2][i] = ("(" + os.path.basename(ROOT_DIR) + 
                            os.sep.replace("\\", "\\\\") + ")(" + regEx[2][i] + 
                            ")")
    
    def AddRegEx(self, settings, regEx, ignoredRegEx):
        self.__regExs.append(
                [copy.deepcopy(settings), regEx, ignoredRegEx])
    
    def DeleteRegEx(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        self.__regExs.pop(index)
    
    def GetRegExSettings(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        return self.__regExs[index][0]
    
    def GetRegEx(self, index, page):
        if (index < 0): raise IndexError, "list index out of range"
        
        return self.__regExs[index][1][page]
    
    def GetRegExList(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        return self.__regExs[index][1]
    
    def GetIgnoredRegEx(self, index, page):
        if (index < 0): raise IndexError, "list index out of range"
        
        return self.__regExs[index][2][page]
    
    def GetIgnoredRegExList(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        return self.__regExs[index][2]
    
    def SetRegEx(self, index, regEx):
        if (index < 0): raise IndexError, "list index out of range"
        
        self.__regExs[index][1] = regEx
    
    def SetIgnoredRegEx(self, index, IgnoredRegEx):
        if (index < 0): raise IndexError, "list index out of range"
        
        self.__regExs[index][2] = IgnoredRegEx
    
    def GetRegExId(self, settings):
        """GetRegExId(settings) --> int
        
        Gets the id of the regular expression for the given settings. It 
        returns -1 if the setting isn't in the list.
        
        """
        for j in range(len(self.__regExs)):
            savedSettings, regEx, ignoredRegEx = self.__regExs[j]
            if (len(savedSettings) != len(settings)): continue
            same = True
            for i in range(len(savedSettings)):
                if (savedSettings[i] != settings[i]):
                    same = False
                    break;
            if (same): return j
        return -1
    
    def GetRegExIdGenerator(self):
        for i in range(len(self.__regExs)):
            yield i
    
    def GetRegExPageGenerator(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        for i in range(len(self.__regExs[index][1])):
            yield i
    
    def GetIgnoredRegExPageGenerator(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        for i in range(len(self.__regExs[index][2])):
            yield i
    
    def GetRegExString(self, index):
        if (index < 0): raise IndexError, "list index out of range"
        
        message = ""
        pagesCount = len(self.__regExs[index][1]) 
        if (pagesCount > 0):
            message = message + "Page 0:\n" + self.GetRegEx(index, 0) + "\n"
        if (pagesCount > 1):
            message = (message + "[...skipping pages...]\nPage " + 
                       str(pagesCount - 1) + ":\n" + 
                       self.GetRegEx(index, pagesCount - 1) + "\n")
        return message
    