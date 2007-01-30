# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
    