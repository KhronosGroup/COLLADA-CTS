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
        pass
        
    def JudgeBasic(self, context):
            
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")
            return True
      
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBasic so we don't have to run it again?
    def JudgeIntermediate(self, context):
        if not self.JudgeBasic(context):
            return False
            
        # Check the required steps for positive results and that a rendering was done.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            return False
        if not context.DoesStepsExists([ "Render" ]):
            context.Log("FAILED: A render step is required.")
            return False
        context.Log("PASSED: Required steps executed and passed.")

        # Look for the "cube_polylist" test case.
        comparativeTestId = context.FindTestId( "reference_5_influence", "skin")
        if (comparativeTestId == None):
            context.Log("FAILED: You must also run the 'reference_5_influence' test case.")
            return False
        
        # Retrieve the last image filename for this test case.
        imageFilenames = context.GetStepImageFilenames()
        if (len(imageFilenames) == 0):
            context.Log("FAILED: This test must include a 'Render' step.")
            return False
        filename1 = imageFilenames[-1]

        # Retrieve the last image filename for the "cube_polylist" test case.
        imageFilenames = context.GetStepImageFilenames(comparativeTestId)
        if (len(imageFilenames) == 0):
            context.Log("FAILED: The 'reference_5_influence' test must include a 'Render' step.")
            return False
        filename2 = imageFilenames[-1]
        
        # Compare the two images.
        result = context.CompareImages(filename1, filename2)
        if result > 5:
            context.Log("FAILED: Output doesn't match the 'reference_5_influence' test. (" + str(result) + ")")
            return False
        else:
            context.Log("PASSED: Output matches the 'reference_5_influence' test. (" + str(result) + ")")
            return True
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeAdvanced(self, context):
        return self.JudgeIntermediate(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject();
