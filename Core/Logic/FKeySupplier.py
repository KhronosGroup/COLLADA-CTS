# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
    