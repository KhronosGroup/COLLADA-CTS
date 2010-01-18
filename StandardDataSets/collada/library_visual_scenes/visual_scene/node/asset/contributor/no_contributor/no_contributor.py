# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeSuperior: also verifies that the validation steps are not in error.
# JudgeExemplary: same as intermediate badge.

# We import an assistant script that includes the common verifications
# methods. The assistant buffers its checks, so that running them again
# does not incurs an unnecessary performance hint.
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = ['library_visual_scenes', 'visual_scene', 'node', 'asset', 'contributor', 'authoring_tool']
nodeType = 'node'
nodeId = 'cube_node'
ignoreList = ['asset']

class SimpleJudgingObject:
    def __init__(self, _tagLst, _nodeType, _nodeId, _ignoreList):
        self.tagList = _tagLst
        self.nodeType = _nodeType
        self.nodeId = _nodeId
        self.ignoreList = _ignoreList
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])

        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
	# if superior fails, no point in further checking
        if (self.status_superior == False):
            self.status_exemplary = self.status_superior
            return self.status_exemplary

        # if element is not preserved, then authoring_tool must exist
        # if element is preserved, return true
        if (not self.__assistant.CompletePreservation(context, self.nodeType, self.nodeId, self.ignoreList)):
            self.status_exemplary = self.__assistant.ElementDataExists(context, self.tagList)
            return self.status_exemplary
        else:
            self.status_exemplary = True
            return self.status_exemplary 
        
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, nodeType, nodeId, ignoreList);
