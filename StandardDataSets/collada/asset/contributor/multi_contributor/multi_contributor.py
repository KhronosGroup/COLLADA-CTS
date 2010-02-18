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
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = ['asset', 'contributor', 'authoring_tool']
attrName = ''
attrVal = ''
dataToCheck = ''
childList = ['author', 'comments', 'copyright', 'source_data']

class SimpleJudgingObject:
    def __init__(self, _tagLst, _attrName, _attrVal, _data, _childList):
        self.tagList = _tagLst
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.dataToCheck = _data
        self.childList = _childList
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()

    # Checks for contributor preservation by using the authoring_tool as the identifier
    # tagList: tag list to search for the authoring_tool element
    # childList: name of the childs of the contributor
    def checkContributor(self, context, tagList, childList):
        root = minidom.parse(context.GetInputFilename()).documentElement
        inAuthToolList = FindElement(root, tagList)
        
        outputFilenames = context.GetStepOutputFilenames("Export")
        root = minidom.parse(outputFilenames[0]).documentElement
        outAuthToolList = FindElement(root, tagList)
        
        if (len(outAuthToolList) < len(inAuthToolList)):
            context.Log("FAILED: contributor is not preserved.")
            return False
        
        for inAuthTool in inAuthToolList:
            inputContributor = inAuthTool.parentNode

            for outAuthTool in outAuthToolList:
                found = False

                # found the matching node
                if (inAuthTool.childNodes[0].nodeValue == outAuthTool.childNodes[0].nodeValue):
                
                    found = True
                    outputContributor = outAuthTool.parentNode
                    
                    for eachTag in childList:
                        inChildList = inputContributor.getElementsByTagName(eachTag)
                        outChildList = outputContributor.getElementsByTagName(eachTag)

                        if ( len(inChildList) != len(outChildList) ):
                            context.Log("FAILED: " + eachTag + " is not found.")
                            return False
                        
                        if (inChildList[0].childNodes[0].nodeValue != outChildList[0].childNodes[0].nodeValue):
                            context.Log("FAILED: " + eachTag + " is not preserved.")
                            return False
            
                if (found):
                    break
                    
            if (not found):
                context.Log("FAILED: " + tagList[len(tagList)-1] + " is not preserved.")
                return False
                    
        context.Log("PASSED: contributor is preserved.")
        return True

    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])
        
        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False
        
        # Check for preservation of element
        self.__assistant.ElementDataExists(context, self.tagList)
        
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
        
        self.status_exemplary = self.checkContributor(context, self.tagList, self.childList)
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck, childList);
