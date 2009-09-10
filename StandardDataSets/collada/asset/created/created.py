# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This judging object does the following:
#
# JudgeBasic: Verifies that no steps crashed and that the <created> time output by
#             the tool is the same or later than the <created> time in the original file.
# JudgeIntermediate: Same as basic badge.
# JudgeAdvanced: Same as intermediate badge.

import sys, string, os
from xml.dom import minidom, Node
from datetime import datetime, timedelta
from Core.Common.FUtils import FindXmlChild, GetXmlContent, ParseDate
from StandardDataSets.scripts import JudgeAssistant

class JudgingObject:
    def __init__(self):
        self.__assistant = JudgeAssistant.JudgeAssistant()
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        
    def CheckDate(self, context):
        self.__assistant.CheckCrashes(context)
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])
        if not self.__assistant.GetResults(): return False

        # Get the <created> time for the input file
        root = minidom.parse(context.GetInputFilename()).documentElement
        inputCreatedDate = ParseDate(GetXmlContent(FindXmlChild(root, "asset", "created")))
        if inputCreatedDate == None:
            context.Log("FAILED: Couldn't read <created> value from test input file.")
            return False
        
        # Get the output file
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False

        # Get the <created> time for the output file
        root = minidom.parse(outputFilenames[0]).documentElement
        outputCreatedDate = ParseDate(GetXmlContent(FindXmlChild(root, "asset", "created")))
        if outputCreatedDate == None:
            context.Log("FAILED: Couldn't read <created> value from the exported file.")
            return False

        if (outputCreatedDate - inputCreatedDate) < timedelta(0):
            context.Log("FAILED: <created> has an incorrect time stamp. It should be later than the <created> value in the original file.")
            context.Log("The original <created> time is " + str(inputCreatedDate))
            context.Log("The exported <created> time is " + str(outputCreatedDate))
            return False
        
        context.Log("PASSED: <created> element is correct.")
        return True
      
    def JudgeBaseline(self, context):
        self.status_baseline = self.CheckDate(context)          
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
judgingObject = JudgingObject();
