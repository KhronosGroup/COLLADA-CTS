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

# Status value:
# -1000 : Initail status: test does not start yet.
# 0 : Failed
# 1 : Successful

from Core.Common.DOMParser import *
from Core.Common.CheckingModule import *

from xml.dom.minidom import parse, parseString
import os

# Please feed your source id list here:
sourceIdLst = ['mesh1-positions', 'mesh1-normals', 'mesh1-map-channel1']
tagLst = ['param']
attrLst = ['name']

class SimpleJudgingObject:
    def __init__(self, status_basic_, status_intermediate_, status_advanced_, sourceIdLst_, tagLst_, attrLst_):
        self.status_basic = status_basic_
        self.status_intermediate = status_intermediate_
        self.status_advanced = status_advanced_
        self.sourceIdLst = sourceIdLst_ # the source element where we will check
        self.tagLst = tagLst_ # tag under source element
        self.attrLst = attrLst_ # the attributes list where we will check.
        self.inputFilleName = ''
        self.outputFilleNameLst = []
    
    def ParamChecker(self):
        
        testIO = DOMParserIO( self.inputFilleName, self.outputFilleNameLst )
        # load files and generate root
        testIO.Init()
        
        root = testIO.GetRoot(self.outputFilleNameLst[0])
        if root == None:
            return [False, 'root is not availiable']
        else:
            for eachSourceId in sourceIdLst:
                sourceEle = GetElementByID( root, eachSourceId )
                if sourceEle != None:
                    # find all elements by tag
                    paraLst = sourceEle.getElementsByTagName(tagLst[0])
                    for eachParaEle in paraLst:
                        resAttri = IsAttrExist( eachParaEle, self.attrLst[0] )
                        if resAttri[0] == False:
                            return [False, 'Param doesn\'t have attribute name.']
                else:
                    return [False, 'Error: can not find source.']
            
            #check all sources
            return [True, '']

    # This function is enough to test whether baked matrix is correct or not. through image comparison
    def JudgeBaseline(self, context):
        
        if len(self.attrLst) == 0:
            context.Log("Error: judging script doesn't have enough information about attributes.")
            return False
        
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
            self.status_basic = 0
            return False

        resParam = self.ParamChecker()
        
        if resParam[0] == True:
            context.Log("PASSED: Required steps executed and passed.")
        else:
            context.Log("FAILED: Param doesn't exsit.")
            context.Log(resParam[1])
        
        self.status_basic = 1
        return True
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeExemplary(self, context):
        context.Log("N/A")
        return False

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeSuperior(self, context):
        context.Log("N/A")
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
judgingObject = SimpleJudgingObject(-1000, -1000, -1000, sourceIdLst, tagLst, attrLst);