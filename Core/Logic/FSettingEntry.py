# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FSettingEntry:
    def __init__(self, prettyName, command, value):
        self.__prettyName = prettyName
        self.__command = command
        self.__value = value
    
    def __str__(self):
        return self.__prettyName + "\t" + self.__command + "\t" + self.__value
    
    def __eq__(self, other):
        if other is None: return False
        
        return ((self.__prettyName == other.__prettyName) and
                (self.__command == other.__command) and
                (self.__value == other.__value))
    
    def __ne__(self, other):
        return (not (self == other))
    
    def SetValue(self, value):
        self.__value = value
    
    def GetValue(self):
        return self.__value
    
    def GetPrettyName(self):
        return self.__prettyName
    
    def GetCommand(self):
        return self.__command
    