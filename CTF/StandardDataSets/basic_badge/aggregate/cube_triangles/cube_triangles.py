# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

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
    
    def JudgeIntermediate(self, context):
        return self.JudgeBasic(context)
        
    def JudgeAdvanced(self, context):
        if not self.JudgeIntermediate(context): return False
        
        # Look for the "cube_polylist" test case.
        comparativeTestId = context.FindTestId("cube_polylist", "aggregate", "basic_badge")
        if (comparativeTestId == None):
            context.Log("FAILED: You must also run the 'basic_badge|aggregate|cube_polylist' test case.")
            return False
        
        # Retrieve the last image filename for this test case.
        imageFilenames = context.GetStepImageFilenames()
        if (len(imageFilenames) == 0):
            context.Log("FAILED: This test case requires a 'Render' step.")
            return False
        filename1 = imageFilenames[-1]

        # Retrieve the last image filename for the "cube_polylist" test case.
        imageFilenames = context.GetStepImageFilenames(comparativeTestId)
        if (len(imageFilenames) == 0):
            context.Log("FAILED: The 'basic_badge|aggregate|cube_polylist' test case must contain a 'Render' step.")
            return False
        filename2 = imageFilenames[-1]
        
        # Compare the two images.
        result = context.CompareImages(filename1, filename2)
        if not result:
            context.Log("FAILED: This test case's image differs from the 'basic_badge|aggregate|cube_polylist' test case.")
            return False
        else:
            context.Log("PASSED: Produces similar output to 'basic_badge|aggregate|cube_polylist' test case.")
            return True

judgingObject = TwoStepJudgingObject();
