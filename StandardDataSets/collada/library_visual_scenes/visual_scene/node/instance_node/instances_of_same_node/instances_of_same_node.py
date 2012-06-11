
# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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

from Core.Common.DOMParser import *
from Core.Common.NodeInsCheck import *
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = ['library_visual_scenes', 'visual_scene']
tagName = 'instance_node'
attrName = 'url'
attrVal = 'pointlight'
dataToCheck = ''

class SimpleJudgingObject:
    def __init__(self, _tagLst, _tagName, _attrName, _attrVal, _data):
        self.tagList = _tagLst
        self.tagName = _tagName
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.dataToCheck = _data
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
        self.inputFilleName = ''
        self.outputFilleNameLst = []
        self.visualSceneCheck = False
        self.nodeCheck = False

    def CheckNodes(self, context):
        # Get the input file
        self.inputFilleName = context.GetAbsInputFilename(context.GetCurrentTestId())
        
        # Get the output file
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False
        else:
            del self.outputFilleNameLst[:]
            self.outputFilleNameLst.extend( outputFilenames )
        
        testIO = DOMParserIO(self.inputFilleName, self.outputFilleNameLst)
        
        try:
            testIO.Init()
        except Exception, info:
            print 'Exception is thrown at line %d in DOMParserTest.py' %sys.exc_traceback.tb_lineno
            print ''
            print info
    
        # DOM Root 
        testNodeChker = NodeChecker( testIO.GetRoot(self.inputFilleName), testIO.GetRoot(self.outputFilleNameLst[0]))
        
        # Add the struct id for both root
        testNodeChker.AddStructID()
        
        # validate equivalence        
        if testNodeChker.CheckTwoVS() == True:
            self.visualSceneCheck = True
            
            if testNodeChker.CheckVSLN() == True:
                self.nodeCheck = True
            else:
                self.nodeCheck = False
        else:
            self.visualSceneCheck = False
        
        testIO.Delink()
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        
        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False
        
        # Compare the rendered images, then check for visual scene equivalence
        if ( self.__assistant.CompareRenderedImages(context) ):
            self.CheckNodes(context)
            if (self.visualSceneCheck == True):
                context.Log("PASSED: Visual scenes are equivalent.")
            else:
                context.Log("FALSE: Visual scenes are not equivalent.")
                
            self.status_baseline = self.visualSceneCheck
            return self.status_baseline

        self.status_baseline = self.__assistant.DeferJudgement(context)
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        # if baseline fails, no point in further checking
        if (self.status_baseline == False):
            self.status_superior = self.status_baseline
            return self.status_superior

        # Check for library_nodes preservation
        if (self.nodeCheck == True):
            context.Log("PASSED: Library nodes are preserved.")
            self.__assistant.CompareImagesAgainst(context, "_reference_instances_of_same_node", None, None, 5, True, True)
            self.__assistant.CompareElementCount(context, self.tagList, self.tagName, self.attrName, self.attrVal)
                    
            self.status_superior = self.__assistant.DeferJudgement(context)
            return self.status_superior 
        else:
            context.Log("FALSE: Library nodes are not preserved.")
            
        self.status_superior = self.nodeCheck
        return self.status_superior
        
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
        self.status_exemplary = self.status_superior
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, tagName, attrName, attrVal, dataToCheck);