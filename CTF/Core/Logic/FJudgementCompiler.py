# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import Core.Common.FGlobals as FGlobals

from Core.Logic.FJudgement import *

class FJudgementCompiler:
    """ Used to generate badge earned statements.
        This class compiles together all the received badge judgements
        into one coherent badge earned statement. """

    def __init__(self):
        # Start with "no_script" for all the badges.
        # "no_script" is considered positive and may be overwritten
        # by a "passed" status if one is found in the list.
        # For any "missing_data" or "failed", the badge earning
        # is canceled.
        self.__badgesStatus = []
        for i in range(len(FGlobals.badgeLevels)):
            self.__badgesStatus.append(FJudgement.NO_SCRIPT)
        
    def ProcessJudgement(self, badgeIndex, badgeResult):
        """ Considers a local judgement for the given badge.
            @param badgeIndex The integer index of the badge that
                this judgement relates to.
            @param badgeResult The local judgement result to consider
                for the given badge level. """
    
        oldResult = self.__badgesStatus[badgeIndex]
        if (oldResult == FJudgement.NO_SCRIPT):
            # No script is overwritten by everything else.
            self.__badgesStatus[badgeIndex] = badgeResult 
        elif (oldResult == FJudgement.PASSED and
                (badgeResult == FJudgement.MISSING_DATA or badgeResult == FJudgement.FAILED)):
            # "Passed" can be overwritten by one of the negative judgements.
            self.__badgesStatus[badgeIndex] = badgeResult 
        # Otherwise, keep the old result.

    def GenerateStatement(self):
        """ Generates the badges earned statement.
            All the processed judgements are considered. The final statement
            will reflect the badges which contain only positive judgements.
            
            @return A string to contains the badges earned statement. """
 
        # Process the badges status, looking for earned badges.
        text = ""
        for i in range(len(FGlobals.badgeLevels)):
            badgeStatus = self.__badgesStatus[i]
            if (badgeStatus == FJudgement.PASSED):
                
                # To get here, at least least one PASSED judgement and
                # zero or more NO_SCRIPTs judgement must have been processed.
                if (len(text) > 0): text += ", "
                text += FGlobals.badgeLevels[i]

        return text
    

