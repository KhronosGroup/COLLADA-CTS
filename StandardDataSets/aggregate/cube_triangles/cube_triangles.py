# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from StandardDataSets.scripts import JudgeAssistant

class TwoStepJudgingObject:
    def __init__(self):
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBasic(self, context):
        self.__assistant.ResetJudgement()
        self.__assistant.CheckCrashes(context)
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        self.__assistant.CompareImagesAgainst(context, "aggregate", "cube_polylist")
        return self.__assistant.DeferJudgement(context)
 
    def JudgeIntermediate(self, context): return self.JudgeBasic(context)
    def JudgeAdvanced(self, context): return self.JudgeIntermediate(context)
        
judgingObject = TwoStepJudgingObject();
