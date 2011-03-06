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

# Status value:
# -1000 : Initail status: test does not start yet.
# 0 : Failed
# 1 : Successful

class SimpleJudgingObject:
    def __init__(self, status_basic_, status_intermediate_, status_advanced_):
        self.status_basic = status_basic_
        self.status_intermediate = status_intermediate_
        self.status_advanced = status_advanced_
        #pass
        
    def JudgeBaseline(self, context):
        
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")

        # Check the required steps for positive results and that a rendering was done.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            self.status_basic = 0
            return False
        if not context.DoesStepsExists([ "Render" ]):
            context.Log("FAILED: A render step is required.")
            self.status_basic = 0
            return False
        context.Log("PASSED: Required steps executed and passed.")
        self.status_basic = 1
        return True
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBaseline so we don't have to run it again?
    def JudgeExemplary(self, context):
        #print(self.status_basic)
        #print("\n")
        if (self.status_basic == 1):
            # Add additional test code here if needed
            context.Log("Pass")
        else:
            contex.Log("Did not pass basic test, not continue.")
            self.status_intermediate = 0
            return False
        self.status_intermediate = 1
        return True

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeSuperior(self, context):
        context.Log("N/A")
        return False

    # To pass FX you need to pass basic?
    # This object could also include additional
    # tests that were specific to the FX badges
    def JudgeFx(self, context):
        context.Log("N/A")
        return False

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgePhysics(self, context):
        context.Log("N/A")
        return False

# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(-1000, -1000, -1000);
