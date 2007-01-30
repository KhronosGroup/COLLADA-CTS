# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
    