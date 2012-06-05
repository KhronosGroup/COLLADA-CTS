# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

class FJudgement:
    # Indicates that a judgement was executed and is negative.
    FAILED = 0
    
    # Indicates that a judgement was executed and is positive.
    PASSED = 1
    
    # Indicates that a given test does not define a jugding script
    # or a judging procedure for this badge level.
    # This value is positive and does not stop an application from passing a badge level.
    NO_SCRIPT = 2
    
    # Indicates that this badge level was not original run and checked-for.
    # This value is negative and does stop an application from passing a badge level.
    MISSING_DATA = 3
    
    # These enums are used in a list, so this member must always be last.
    STATUS_COUNT = 4

    def __init__(self, result, message):
        if (result == None): self.__result = MISSING_DATA
        else: self.__result = result

        if (message == None): self.__message = "N/A"
        else: self.__message = message;
        
    def GetMessage(self):
        return self.__message
        
    def GetResult(self):
        return self.__result
