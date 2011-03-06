# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeExemplary: also verifies that the validation steps are not in error.
# JudgeSuperior: same as intermediate badge.
from StandardDataSets.scripts import JudgeAssistant

# this will check the node hiearchy as well
import os
import subprocess

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
    
    def CheckEnvirmoment(self):
#        if (os.environ.has_key('COLLADA_CTF_EXTERNAL_TOOL')):
#            print "There is checker defined as below:"
#            print os.environ['COLLADA_CTF_EXTERNAL_TOOL']
#            return True
#        else:
#            print "Missing envirmental variable: COLLADA_CTF_EXTERNAL_TOOL"  
#            return False 
         return True
    
    def CheckHierarchy(self, context):
        absInputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())
        #print absInputFileName
        outFileNames = context.GetStepOutputFilenames("Export")
        if len(outFileNames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False 
        #print outFileNames[0]
        
        if self.CheckEnvirmoment():
            # We have the tool installed correctly.
#            command = os.environ['COLLADA_CTF_EXTERNAL_TOOL'] + "\HierarchyPreservationChecking.exe " + absInputFileName + " " + outFileNames[0]
            command = "Tools\HierarchyPreservationChecking.exe " + absInputFileName + " " + outFileNames[0]

            #print command
            p = subprocess.Popen(command)
            result = p.wait()
            #print result
            if (result == 1):
               context.Log("PASSED: Hierarchy is preserved.")
               return True
            elif (result == 0):
               context.Log("FAILED: two tree for node are not same based on schema. Error may come from child parent relation changed or id attribute problem.")
               return False
            else:
               context.Log("FAILED: Hierarchy program can not load DOM correctly.")
               return False
        else:
            context.Log("FAILED: There is no tool for hierarchy checking")
            return False
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        
        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False
            
        # Compare the rendered images between import and export
        # Check preservation of node hierarchy
        if ( self.__assistant.CompareRenderedImages(context) ):
            if not self.CheckHierarchy(context):
                context.Log("Error in node hierarchy checking...")
                return False

        return True
  
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
judgingObject.CheckEnvirmoment();