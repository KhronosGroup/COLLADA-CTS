
# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeExemplary: also verifies that the validation steps are not in error.
# JudgeSuperior: same as intermediate badge.

# Status value:
# -1000 : Initail status: test does not start yet.
# 0 : Failed
# 1 : Successful

from Core.Common.DOMParser import *

from xml.dom.minidom import parse, parseString
import os

# Please feed your node list here:
nodeIdLst = ['']

class SimpleJudgingObject:
    def __init__(self, status_basic_, status_intermediate_, status_advanced_, nodeIdLst_):
        self.status_basic = status_basic_
        self.status_intermediate = status_intermediate_
        self.status_advanced = status_advanced_
        self.nodeIdLst = nodeIdLst_ # the node list where we will check        
    
    # This will check transformation for input file and output file
    # level 0: did not pass base line
    def TransCheckingExemplary(self, context):
        
        absInputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())
        outFileNames = context.GetStepOutputFilenames("Export")
        
        # if there is no file exported, then fail the test
        if len(outFileNames) <= 0:
            return 0
        
        testIO = DOMParserIO(absInputFileName, outFileNames)
        
        # check whether we have correct initilization.
        if testIO.Init() == 0:
            # can not parse files correctly
            testParser.Delink()
            return 0
        
        # Find matrix stack from the node list, the id should be preserved
        for eachNode in self.nodeIdLst:
            # exported nodes with transformation for testing
            nodeExContTrs = GetElementByID(testIO.GetRoot( outFileNames[0] ), eachNode)
            
            # get transformation from it
            trsExList = GetTransformationsOfNode(nodeExContTrs)
            
            # check if there are at 5 elements distribution:
            if len(trsExList) == 5:
                if trsExList[0].nodeName != 'translate' or trsExList[1].nodeName != 'rotate' or trsExList[2].nodeName != 'rotate' or trsExList[3].nodeName != 'rotate' or trsExList[4].nodeName != 'scale':
                    testIO.Delink()
                    return 0
            else:
                testIO.Delink()
                return 0
        
        testIO.Delink()
        
        return 1
        
    def TransCheckingSuperior(self, context):
        absInputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())
        outFileNames = context.GetStepOutputFilenames("Export")
        
        # if there is no file exported, then fail the test
        if len(outFileNames) <= 0:
            return 0
        
        testIO = DOMParserIO(absInputFileName, outFileNames)
        
        # check whether we have correct initilization.
        if testIO.Init() == 0:
            # can not parse files correctly
            testIO.Delink()
            return 0
            
        # check if two matrix are equalivent between each other
        # Find matrix stack from the node list, the id should be preserved
        for eachNode in self.nodeIdLst:
            rootOut = testIO.GetRoot( outFileNames[0] )
            rootIn = testIO.GetRoot( absInputFileName )
            
            # input nodes with transformation for testing
            nodeOutContTrs = GetElementByID(rootOut, eachNode)
            nodeInContTrs = GetElementByID(rootIn, eachNode)
            
            # get transformation from it
            trsOutList = GetTransformationsOfNode(nodeOutContTrs)
            trsInList = GetTransformationsOfNode(nodeInContTrs)
            
            # get unit and up_axis information about it
            unitOut = GetUnitValue(rootOut)
            unitIn = GetUnitValue(rootIn)
            
            upAxisOut = GetUnitValue(rootOut)
            upAxisIn = GetUnitValue(rootIn)
            
            # compare matrix stack
            if len( trsOutList ) != len( trsInList ):
                testIO.Delink()
                return 0
            
            for index in range(0, len(trsExList)):
                matOutStd = ConvertXMLtoMat(rootOut, unitOut, upAxisOut)
                matInStd = ConvertXMLtoMat(rootIn, unitIn, upAxisIn)
                
                if matOutStd != matInStd:
                    testIO.Delink()
                    return 0
            
            testIO.Delink()
            return 1
        
    # This function is enough to test whether baked matrix is correct or not. through image comparison
    def JudgeBaseline(self, context):
        
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")

        # Check the required steps for positive results and that a rendering was done.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            self.status_basic = 0
            return False
        if not context.DoesStepsExists([ "Render" ]):
            context.Log("FAILED: A render step is required.")
            self.status_basic = 0
            return False
        context.Log("PASSED: Required steps executed and passed.")
        
        self.status_basic = 1
        return True
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBaseline so we don't have to run it again?
    def JudgeExemplary(self, context):
        #print(self.status_basic)
        #print("\n")
        if (self.status_basic == 1):
            # Add additional test code here if needed
            statusExemplary = self.TransCheckingExemplary(context)
            if statusExemplary == 1:
                context.Log("Pass")
                return True
            else:
                # check the advantage badge:
                context.Log("Though it is not in Exemplary level, it may be in Superior level.\n")
                statusSuperior = self.TransCheckingSuperior(context) 
                if statusSuperior== 1:                
                    self.status_advanced = 1
                    context.Log("Pass")
                    return True
                else:
                    return False
        else:
            context.Log("Did not pass basic test, not continue.")
            self.status_intermediate = 0
            return False
        self.status_intermediate = 1
        return True

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeSuperior(self, context):
        if (self.status_advanced == 1):
            # Add additional test code here if needed
            context.Log("Pass")
            return True
        else:
            context.Log("Did not pass advanced badges.")
            self.status_advanced = 0
            return False

    # To pass FX you need to pass basic?
    # This object could also include additional
    # tests that were specific to the FX badges
    def JudgeFx(self, context):
        context.Log("N/A")
        return False

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgePhysics(self, context):
        context.Log("N/A")
        return False

# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(-1000, -1000, -1000, nodeIdLst);