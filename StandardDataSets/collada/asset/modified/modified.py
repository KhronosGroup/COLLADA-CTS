# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This judging object does the following:
#
# JudgeBasic: Verifies that no steps crashed and that the <modified> element output by
#             the tool is within 24 hours of the current time.
# JudgeIntermediate: Same as basic badge.
# JudgeAdvanced: Same as intermediate badge.

import sys, string, os
from xml.dom import minidom, Node
from datetime import datetime, timedelta
from Core.Common.FUtils import FindXmlChild, GetXmlContent, ParseDate

class JudgingObject:
    def __init__(self):
        self.basicResult = None # Cached result to avoid duplication of work
        
    def JudgeBasicImpl(self, context):
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            return False

        # Get the output file
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False

        # Get the <modified> time for the output file
        root = minidom.parse(outputFilenames[0]).documentElement
        modifiedDate = ParseDate(GetXmlContent(FindXmlChild(root, "asset", "modified")))
        if modifiedDate == None:
            context.Log("FAILED: Couldn't read <modified> value from the exported file.")
            return False

        now = datetime.utcnow()
        if abs(modifiedDate - now) > timedelta(1):
            context.Log("FAILED: <modified> has an incorrect time stamp. It should be within 24 hours of the current time.")
            context.Log("<modified> is " + str(modifiedDate))
            context.Log("The current time is " + str(now))
            return False
        
        context.Log("PASSED: Required steps executed and passed.")
        return True
      
    def JudgeBasic(self, context):
        if self.basicResult == None:
            self.basicResult = self.JudgeBasicImpl(context)
        return self.basicResult

    def JudgeIntermediate(self, context):
        return self.JudgeBasic(context)
            
    def JudgeAdvanced(self, context):
        return self.JudgeIntermediate(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = JudgingObject();
