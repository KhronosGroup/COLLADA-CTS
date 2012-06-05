# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import copy

class FSettingManager:
    def __init__(self):
        self.__settings = {}
    
    def __str__(self):
        string = ""
        for op in self.__settings.keys():
            for app in self.__settings[op].keys():
                for setting in self.__settings[op][app]:
                    string = string + setting.GetName() + "\n"
        return string
    
    def AddSetting(self, op, app, setting):
        if (self.__settings.has_key(op)):
            if (self.__settings[op].has_key(app)):
                for storedSetting in self.__settings[op][app]:
                    if (storedSetting == setting):
                        return False # have it already
                self.__settings[op][app].append(copy.deepcopy(setting))
                return True
        else:
            self.__settings[op] = {}
        
        self.__settings[op][app] = [copy.copy(setting),]
        return True
    
    def DeleteSetting(self, op, app, setting):
        if (not self.__settings.has_key(op)):
            raise ValueError, "<FSettingManager> No op as: " + str(op)
        if (not self.__settings[op].has_key(app)):
            raise ValueError, "<FSettingManager> No app as: " + str(app)
        
        self.__settings[op][app].remove(setting)
    
    def GetSettingsGenerator(self, op, app):
        if (self.__settings.has_key(op)):
            if (self.__settings[op].has_key(app)):
                for setting in self.__settings[op][app]:
                    yield copy.deepcopy(setting)
    