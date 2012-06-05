# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

class FResult:
    PASSED_IMAGE = 0
    PASSED_ANIMATION = 1
    PASSED_VALIDATION = 2
    FAILED_IMAGE = 3
    FAILED_ANIMATION = 4
    FAILED_VALIDATION = 5
    FAILED_MISSING = 6
    IGNORED_TYPE = 7
    IGNORED_NO_BLESS_IMAGE = 8
    IGNORED_NO_BLESS_ANIMATION = 9
    IGNORED_NONE = 10
    CRASH = 11
    
    def __init__(self):
        self.__passOverride = False
        self.__failOverride = False
        self.__passExecution = False
        self.__passOutput = False
        self.__outputs = []
        self.__messages = []
    
    def __cmp__(self, other):
        """__cmp__(other)-> -1, 0, 1
        
        Compares two FResult. Results are ordered by pass/fail criterial where
        passing results are ordered before failing.
        
        returns:
            int representing ordering. 1 means before, 0 means equivalent, -1 
            means after.
        
        """
        if (other == None): return 1
        
        myResult = self.GetResult()
        otherResult = other.GetResult()
        if (myResult and not otherResult):
            return -1
        elif (myResult == otherResult):
            myText = self.GetTextArray()
            otherText = other.GetTextArray()
            if (myText > otherText):
                return 1
            if (myText < otherText):
                return -1
            return 0
        else:
            return 1
    
    def BackwardCompatibility(self):
        """BackwardCompatibility() -> bool
        
        Fixes backward compatibility issues due to loading a FResult from disk.
        
        returns
            bool indicating if a change occurred. True if a change occurred.
        
        """
        if (not "_FResult__messages" in self.__dict__.keys()):
            self.__messages = []
            for output in self.__outputs:
                self.__messages.append("")
            return True
        return False
    
    def IsOverriden(self):
        return self.__passOverride or self.__failOverride
    
    def GetTextArray(self):
        textArray = []
        if (self.GetResult()):
            textArray.append("Passed")
        else:
            textArray.append("Failed")
        
        if (self.__passOverride):
            textArray.append("    - User override to Pass")
        elif (self.__failOverride):
            textArray.append("    - User override to Fail")
        elif (self.__passExecution):
            textArray.append("    - Matched a blessed execution.")
        else:
            i = 0
            for output in self.__outputs:
                text = "    - step <" + str(i) + ">: "
                if (output == FResult.PASSED_VALIDATION):
                    text = text + "Passed (Passed Validation)"
                elif (output == FResult.FAILED_VALIDATION):
                    text = text + "Failed (Failed Validation)"
                elif (output == FResult.FAILED_MISSING):
                    text = text + "Failed (Missing)"
                elif (output == FResult.IGNORED_TYPE):
                    text = text + "Ignored (Not Image Type)"
                elif (output == FResult.IGNORED_NO_BLESS_IMAGE):
                    text = text + "Ignored (No Blessed Images)"
                elif (output == FResult.IGNORED_NO_BLESS_ANIMATION):
                    text = text + "Ignored (No Blessed Animations)"
                elif (output == FResult.IGNORED_NONE):
                    text = text + "Ignored (Got None From Application)"
                elif (output == FResult.CRASH):
                    text = text + "Crashed"
                elif (self.__messages[i] != ""): # must be before default ones
                    text = text + self.__messages[i]
                elif (output == FResult.PASSED_IMAGE):
                    text = text + "Passed (Matched Image)"
                elif (output == FResult.PASSED_ANIMATION):
                    text = text + "Passed (Matched Animation)"
                elif (output == FResult.FAILED_IMAGE):
                    text = text + "Failed (No Matched Image)"
                elif (output == FResult.FAILED_ANIMATION):
                    text = text + "Failed (No Matched Animation)"
                
                
                textArray.append(text)
                i = i + 1
        return textArray
    
    def GetResult(self):
        if (self.__passOverride): return True
        if (self.__failOverride): return False
        return self.__passExecution or self.__passOutput
    
    def GetPassFromExecution(self):
        return self.__passExecution
    
    def GetPassFromOutput(self):
        return self.__passOutput
        
    def GetOutputGenerator(self):
        for i in range(len(self.__outputs)):
            yield i, self.__outputs[i]
            
    def GetOutput(self, index):
        return self.__outputs[index]
    
    def Override(self, value):
        if (value == True):
            self.__passOverride = True
            self.__failOverride = False
        elif (value == False):
            self.__passOverride = False
            self.__failOverride = True
        elif (value == None):
            self.__passOverride = False
            self.__failOverride = False
    
    def SetPassFromExecution(self, value):
        self.__passExecution = value
    
    def SetPassFromOutput(self, value):
        self.__passOutput = value
    
    def AppendOutput(self, value, message = ""):
        self.__outputs.append(value)
        self.__messages.append(message)
    
    def ReplaceOutput(self, index, value, message = ""):
        self.__outputs[index] = value
        self.__messages[index] = message
    