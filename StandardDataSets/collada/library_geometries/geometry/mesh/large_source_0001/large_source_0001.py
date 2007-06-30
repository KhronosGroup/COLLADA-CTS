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
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")

        # The outer loop makes sure that the named steps were all executed
        stepTypeToVerify = [ "Import", "Render", "Export", "Validate" ]
	for stepType in stepTypeToVerify:
            validationResults = context.GetStepResults(stepType)
            if (len(validationResults) == 0):
                context.Log("FAILED: No " + stepType.lower() + " step executed.")
                return False
	    # The inner loop makes sure each test completed without errors
	    # QUESTION, does this need to be a loop or can we just do if(validationResults,
	    # are there ever more than one result per step?
	    judgement = True
	    for result in validationResults: judgement = judgement and result
	    if not judgement:
	        context.Log("FAILED: " + stepType.lower() + " had errors.")
		return False
	context.Log("PASSED: Required steps executed and passed.")
	return True
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBasic so we don't have to run it again?
    def JudgeIntermediate(self, context):
        return self.JudgeBasic(context)
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeAdvanced(self, context):
        return self.JudgeIntermediate(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject();
