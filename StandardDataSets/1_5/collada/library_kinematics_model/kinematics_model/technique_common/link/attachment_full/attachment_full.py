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
tagLst = [['library_kinematics_models', 'kinematics_model', 'technique_common', 'link', 'attachment_full'],
          ['library_kinematics_models', 'kinematics_model', 'technique_common', 'link', 'attachment_full', 'link', 'attachment_full'],
          ['library_kinematics_models', 'kinematics_model', 'technique_common', 'link', 'attachment_full', 'rotate'],
          ['library_kinematics_models', 'kinematics_model', 'technique_common', 'link', 'attachment_full', 'translate']]
attrName = 'joint'
attrVal = ['KIN_GREIFER/j1', 'KIN_GREIFER/j2', 'KIN_GREIFER/j3']
#attrVal = ['j1', 'j2', 'j3']
dataToCheck = ''


class SimpleJudgingObject:
    def __init__(self, _tagLst, _attrName, _attrVal, _data):
        self.tagList = _tagLst
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.dataToCheck = _data
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

        # check for preservation of joint reference
        self.__assistant.AttributeCheck(context, self.tagList[0], self.attrName, self.attrVal[0])
        self.__assistant.AttributeCheck(context, self.tagList[1], self.attrName, self.attrVal[1])
        self.__assistant.AttributeCheck(context, self.tagList[1], self.attrName, self.attrVal[2])
        
#        self.__assistant.CheckForPathTermInAttr(context, self.tagList[0], self.attrName, self.attrVal[0])
#        self.__assistant.CheckForPathTermInAttr(context, self.tagList[1], self.attrName, self.attrVal[1])
#        self.__assistant.CheckForPathTermInAttr(context, self.tagList[1], self.attrName, self.attrVal[2])
        
        # check that the rotate and translate elements exist on export
        self.__assistant.ElementPreserved(context, self.tagList[2])
        self.__assistant.ElementPreserved(context, self.tagList[3])
        
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
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);
