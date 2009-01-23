# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeExemplary: also verifies that the validation steps are not in error.
# JudgeSuperior: same as intermediate badge.

class SimpleJudgingObject:
    def __init__(self):
        pass
        
    def JudgeBaseline(self, context):
            
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")
        
        # Check the required steps for positive results.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            return False

        # Check that a rendering has been done.
        if not context.DoesStepsExists([ "Render" ]):
            context.Log("FAILED: A render step is required.")
            return False
        
        context.Log("PASSED: Required steps executed and passed.")
        return True
      
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBaseline so we don't have to run it again?
    def JudgeExemplary(self, context):
        return self.JudgeBaseline(context)
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeSuperior(self, context):
        return self.JudgeExemplary(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject();
