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
tagLst = ['library_controllers', 'controller']
attrName = 'id'
attrVal = ''
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
  
    def JudgeBaseline(self, context):
        # No step should crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        
        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline
    
    # To pass superior you need to pass baseline, this object could also include additional 
    # tests that were specific to the superior badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
                
    # To pass exemplary you need to pass superior, this object could also include additional
    # tests that were specific to the exemplary badge
    def JudgeExemplary(self, context):
        if (self.status_superior == False):
            self.status_exemplary = self.status_superior
            return self.status_exemplary
            
        # Compare the rendered images between import and export
        # Then compare images against reference test for non equivalence
        if ( self.__assistant.CompareRenderedImages(context) ):
            self.__assistant.CompareImagesAgainst(context, "_reference_morph_one_target_normalized", None, None, 5, True, True)

            # Check for attribute preservation
            self.__assistant.AttributePreserved(context, self.tagList, self.attrName)            

        self.status_exemplary = self.__assistant.DeferJudgement(context)
        return self.status_exemplary

# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);
