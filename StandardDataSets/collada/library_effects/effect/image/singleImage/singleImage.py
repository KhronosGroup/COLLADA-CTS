# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# Basic: verifies validation and doesn't allow crashes.
# Intermediate and Advanced: just verify that the Basic badge passes.

from StandardDataSets.scripts import JudgeAssistant

class SimpleJudgingObject:
    def __init__(self):
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBaseline(self, context):
        self.__assistant.ResetJudgement()
        self.__assistant.CheckCrashes(context)
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        return self.__assistant.DeferJudgement(context)
      
    def JudgeExemplary(self, context): return self.JudgeBaseline(context)
    def JudgeSuperior(self, context): return self.JudgeExemplary(context)

judgingObject = SimpleJudgingObject();
