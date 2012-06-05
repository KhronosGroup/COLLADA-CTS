# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import Core.Common.FGlobals as FGlobals

from Core.Logic.FJudgement import *

class FJudgementCompiler:
    """ Used to generate badge earned statements.
        This class compiles together all the received badge judgements
        into one coherent badge earned statement. """

    def __init__(self):
        self.__badgesStatus = []
        for i in range(len(FGlobals.badgeLevels)):
            # Create a new tally list for each badge level.
            tally = []
            for i in range(FJudgement.STATUS_COUNT): tally.append(0)
            self.__badgesStatus.append(tally)
        
    def ProcessJudgement(self, badgeIndex, badgeResult):
        """ Considers a local judgement for the given badge.
            @param badgeIndex The integer index of the badge that
                this judgement relates to.
            @param badgeResult The local judgement result to consider
                for the given badge level. """
    
        # Just increment the total for this result value in the tally for this badge level.
        tally = self.__badgesStatus[badgeIndex]
        tally[badgeResult] = tally[badgeResult] + 1
        
    def RemoveJudgement(self, badgeIndex, badgeResult):
        """ In order to support partial refreshes, this function allows the UI to remove one
            judgement from the current tally.
            @param badgeIndex The integer index of the badge that
                this judgement relates to.
            @param badgeResult The local judgement result to remove. """

        # Decrement the total for this result value in the tally for this badge level.
        tally = self.__badgesStatus[badgeIndex]
        tally[badgeResult] = tally[badgeResult] - 1

    def GenerateStatement(self):
        """ Generates the badges earned statement.
            All the processed judgements are considered. The final statement
            will reflect the badges which contain only positive judgements.
            
            @return A string to contains the badges earned statement. """
 
        # For a badge to be earned, you must not have any of the MISSING_DATA and FAILED results.
        # And you must have at least one PASSED. The number of NO_SCRIPT results is not relevant.
 
        # Process the badges status, looking for earned badges.
        text = ""
        for i in range(len(FGlobals.badgeLevels)):
            tally = self.__badgesStatus[i]
            missingData = tally[FJudgement.MISSING_DATA]
            failed = tally[FJudgement.FAILED]
            passed = tally[FJudgement.PASSED]
            if (passed > 0) and (failed + missingData == 0):
                
                # This badge is earned!
                if (len(text) > 0): text += ", "
                text += FGlobals.badgeLevels[i]

        return text
    

