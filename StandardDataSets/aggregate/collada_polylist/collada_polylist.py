# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

# This sample judging object does the following:
#
# JudgeBasic: just verifies that the standard steps did not crash.
# JudgeIntermediate: also verifies that the validation steps are not in error.
# JudgeAdvanced: same as intermediate badge.

# We import an assistant script that includes the common verifications
# methods. The assistant buffers its checks, so that running them again
# does not incurs an unnecessary performance hint.
from StandardDataSets.scripts import JudgeAssistant

class SimpleJudgingObject:
    def __init__(self):
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBasic(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        return self.__assistant.DeferJudgement(context)
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
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
