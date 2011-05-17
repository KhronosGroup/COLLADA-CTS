# Copyright (C) 2011 Khronos Group
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
tagLstRoot = [['library_kinematics_scene', 'kinematics_scene', 'instance_kinematics_model', 'newparam']]
attrName = 'sid'
attrVal = ['param.model', 'param.j1.axis']
numericNodeList = []

class SimpleJudgingObject:
    def __init__(self, _tagLstRoot, _attrName, _attrVal, _numericNodeList):
        self.tagListRoot = _tagLstRoot
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.numericNodeList = _numericNodeList
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeKinematicsBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])

        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False

        # check that the element under test and all children are preserved
        self.__assistant.SmartPreservation(context, self.tagListRoot, self.attrName, eachAttrVal[0], self.numericNodeList)
        self.__assistant.SmartPreservation(context, self.tagListRoot, self.attrName, eachAttrVal[1], self.numericNodeList)
        
        self.status_baseline = self.__assistant.DeferJudgement(context)
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeKinematicsSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeKinematicsExemplary(self, context):
        self.status_exemplary = self.status_superior
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLstRoot, attrName, attrVal, numericNodeList);
