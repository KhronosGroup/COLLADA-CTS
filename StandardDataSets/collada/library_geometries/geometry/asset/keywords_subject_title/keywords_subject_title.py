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

from xml.dom import minidom, Node
from Core.Common.FUtils import FindXmlChild, GetXmlContent
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = [['library_geometries', 'geometry', 'asset', 'subject'],
          ['library_geometries', 'geometry', 'asset', 'title']]
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

    def checkKeywords(self, context):
        # Get the keywords for the input file
        root = minidom.parse(context.GetInputFilename()).documentElement
        inputKeywordList = GetXmlContent(FindXmlChild(root, "library_geometries", "geometry", "asset", "keywords")).split()
        
        if (len(inputKeywordList) == 0):
            context.Log("FAILED: Couldn't find keywords in input file.")
            return False
        
        # Get the output file
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False

        # Get the keywords time for the output file
        root = minidom.parse(outputFilenames[0]).documentElement
        outputKeywordList = GetXmlContent(FindXmlChild(root, "library_geometries", "geometry", "asset", "keywords")).split()
        
        if (len(outputKeywordList) == 0):
            context.Log("FAILED: Couldn't find keywords in output file.")
            return False

        if (len(outputKeywordList) != len(inputKeywordList)):
            context.Log("FAILED: Number of keywords do not match between input and output.")
            return False
        
        for eachInputKeyword in inputKeywordList:
            if (eachInputKeyword not in outputKeywordList):
                context.Log("FAILED: " + eachInputKeyword + " not found in output.")
                return False            
        
        context.Log("PASSED: All keywrods are preserved.")
        return True

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

        if (self.checkKeywords(context) == False):
            self.status_exemplary = False
            return self.status_exemplary

        for eachTagList in self.tagList:
            self.__assistant.ElementDataPreserved(context, eachTagList, "string")

        self.status_exemplary = self.__assistant.DeferJudgement(context)
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);
