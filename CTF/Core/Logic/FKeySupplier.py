# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FKeySupplier:
    def __init__(self):
        self.__returnedKeys = []
        self.__maxKey = -1
    
    def __str__(self):
        string = "["
        for key in self.GetKeyGenerator():
            string = string + str(key) + ", "
        if (len(string) > 1):
            string = string[:-2] # remove the comma and space
        string = string + "]"
        return string
    
    def NextKey(self):
        if (len(self.__returnedKeys) == 0):
            self.__maxKey = self.__maxKey + 1
            return self.__maxKey
        else:
            return self.__returnedKeys.pop()
    
    # Assumes you return a key that was given out.
    def ReturnKey(self, key):
        if (key == self.__maxKey):
            self.__maxKey = self.__maxKey - 1
            while (self.__returnedKeys.count(self.__maxKey) != 0):
                self.__returnedKeys.remove(self.__maxKey)
                self.__maxKey = self.__maxKey - 1
        else:
            self.__returnedKeys.append(key)
    
    def GetKeyGenerator(self):
        for key in range(0, self.__maxKey + 1):
            if (self.__returnedKeys.count(key) == 0):
                yield key
    