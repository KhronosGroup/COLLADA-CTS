# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path

from Core.Common.FConstants import *
from Core.Logic.FSettingEntry import *

class FSetting:
    def __init__(self, name, op, app):
        self.__shortName = name
        self.__name = "<" + op + "><" + app + ">" + name
        self.__settings = []
        
        filename = (name + "." + SETTING_EXT)
        filename = os.path.join(SETTINGS_DIR, op, app, filename)
        filename = os.path.normpath(filename)
        
        if (not os.path.isfile(filename)): 
            print filename
            raise ValueError, "No such setting found for " + self.__name + "."
        
        file = open(filename)
        line = file.readline()
        while (line != ""):
            # remove the new line char and split as prettyName, command, value
            self.__settings.append(FSettingEntry(*((line[:-1]).split("\t"))))
            line = file.readline()
        file.close()
    
    def __str__(self):
        string = self.__name + "\n"
        for setting in self.__settings:
            string = string + str(setting) + "\n"
        return string
    
    def __eq__(self, other):
        if other is None: return False
        
        if (self.__name != other.__name):
            return False
        
        for i in range(len(self.__settings)):
            if (self.__settings[i] != other.__settings[i]):
                return False
        
        return True
    
    def __ne__(self, other):
        return (not (self == other))
    
    def GetSettings(self):
        return self.__settings
    
    def GetName(self):
        return self.__name
    
    def GetShortName(self):
        return self.__shortName
    