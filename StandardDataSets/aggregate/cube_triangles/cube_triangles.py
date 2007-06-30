# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

# See "cube_polylist.py" for a simpler sample judging object.

# This sample judging object does the following:
#
# JudgeBasic: just verifies that the standard steps did not crash.
# JudgeIntermediate: same as basic.
# JudgeAdvanced: verifies that the final image rendered is the same
#       as the image rendered by the "cube_polylist" test case.
#
#       This implies ORDERING...
#       Should we add dependency detection or hard-coded dependencies?

class TwoStepJudgingObject:
    def __init__(self):
        self.__cacheBasicResult = None
        self.__cacheBasicLogs = None
        
    def CachedBasic(self, context):
        logs = []
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            logs.append("FAILED: Crashes during required steps.")
            return (logs, False)
        else:
            logs.append("PASSED: No crashes.")
        
        # Check the required steps for positive results.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            logs.append("FAILED: Import, export and validate steps must be present and successful.")
            return (logs, False)

        # Check that a rendering has been done.
        if not context.DoesStepsExists([ "Render" ]):
            logs.append("FAILED: A render step is required.")
            return (logs, False)

        # Look for the "cube_polylist" test case.
        comparativeTestId = context.FindTestId( "aggregate", "cube_polylist" )
        if (comparativeTestId == None):
            logs.append("FAILED: You must also run the 'aggregate|cube_polylist' test case.")
            return (logs, False)
        
        # Retrieve the last image filename for this test case.
        imageFilenames = context.GetStepImageFilenames()
        if (len(imageFilenames) == 0):
            logs.append("FAILED: This test must include a 'Render' step.")
            return (logs, False)
        filename1 = imageFilenames[-1]

        # Retrieve the last image filename for the "cube_polylist" test case.
        imageFilenames = context.GetStepImageFilenames(comparativeTestId)
        if (len(imageFilenames) == 0):
            logs.append("FAILED: The 'aggregate|cube_polylist' test must include a 'Render' step.")
            return (logs, False)
        filename2 = imageFilenames[-1]
        
        # Compare the two images.
        #   FJudgementContext.CompareImages now returns an integer to indicate
        #   how close the images are.
        result = context.CompareImages(filename1, filename2)
        if result > 5:
            logs.append("FAILED: [Comparison: %d] Output doesn't match the 'aggregate|cube_polylist' test. " % result)
            return (logs, False)
        else:
            logs.append("PASSED: [Comparison: %d] Output matches the 'aggregate|cube_polylist' test. " % result)
            return (logs, True)
        
    def JudgeBasic(self, context):
        # This is a cached version of the script.
        # This avoids doing the comparison three times..
        if self.__cacheBasicResult == None:
            (self.__cacheBasicLogs, self.__cacheBasicResult) = self.CachedBasic(context)
        for log in self.__cacheBasicLogs:
            context.Log(log)
        return self.__cacheBasicResult
        
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
judgingObject = TwoStepJudgingObject();
