# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This sample judging object does the following:
#
# JudgeBasic: just verifies that the standard steps did not crash.
# JudgeIntermediate: also verifies that the validation steps are not in error.
# JudgeAdvanced: same as intermediate badge.

class SimpleJudgingObject:
    def __init__(self):
        # Might be we pass in the "context" straight here as well and cache
        # the test passing.
        self.__temp = False
        
    def JudgeBasic(self, context):
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during standard steps.")
            return False
        else:
            context.Log("PASSED: No crashes during standard steps.")
            return True
    
    # Since this is a basic badge test, the intermediate and advanced
    # badges should be enabled, but simply execute the basic test function.
    #
    def JudgeIntermediate(self, context):
        if not self.JudgeBasic(context): return False
            
        # Verify that the validation steps did not fail.
        validationResults = context.GetStepResults("Validate")
        if (len(validationResults) == 0):
            context.Log("FAILED: No validation step executed.")
            return False
            
        judgement = True
        for result in validationResults: judgement = judgement and result
        if not judgement:
            context.Log("FAILED: Validation(s) failed.")
            return False
        else:
            context.Log("PASSED: Validation(s) passed.")
            return True
        
    def JudgeAdvanced(self, context):
        return self.JudgeIntermediate(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject();
