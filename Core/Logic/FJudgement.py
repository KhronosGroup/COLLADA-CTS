# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
