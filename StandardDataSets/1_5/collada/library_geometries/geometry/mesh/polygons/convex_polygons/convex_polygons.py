# Copyright (C) 2007 - 2009 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
#

# This sample judging object does the following:
#
# JudgeBaseline: verifies that app did not crash, the required steps have been performed, 
#  the rendered images match, and the required element(s) has been preserved
# JudgeExemplary: returns Baseline status.
# JudgeSuperior: returns Baseline status.

# We import an assistant script that includes the common verifications
# methods. The assistant buffers its checks, so that running them again
# does not incurs an unnecessary performance hint.
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = []
attrName = ''
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
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])

        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False
            
        # Compare the rendered images between import and export
        # Then compare images against reference test for equivalence
        if ( self.__assistant.CompareRenderedImages(context) ):
            self.__assistant.CompareImagesAgainst(context, "_reference_convex_triangulated", None, None, 5, True, True)
        
        self.status_baseline = self.__assistant.DeferJudgement(context)
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
        self.status_exemplary = self.status_superior
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);