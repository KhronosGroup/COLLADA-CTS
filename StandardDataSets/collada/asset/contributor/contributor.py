# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This judging object does the following:
#
# JudgeBasic: Verifies that an <asset><contributor> element was exported containing an
#             <authoring_tool> tag.
# JudgeIntermediate: Same as basic badge.
# JudgeAdvanced: Same as intermediate badge.

import sys, string, os
from xml.dom import minidom, Node
from datetime import datetime, timedelta
from Core.Common.FUtils import FindXmlChild, GetXmlContent, ParseDate

# FindXmlChild wrapper that takes a list of strings instead of using varargs
def FindXmlChildList(node, childNames):
    for child in childNames:
        node = FindXmlChild(node, child)
    return node

# This is just like FindXmlChild, except that it returns a list containing all the
# child elements matching the last name given in the childNames array. So if you call
# FindXmlChildren(root, "asset", "contributor") and there are two <contributor>s,
# you'll get an array containing the two elements.
def FindXmlChildren(node, *childNames):
    result = []
    node = FindXmlChildList(node, childNames[:len(childNames)-1])
    if node == None or len(childNames) == 0:
        return result
    targetName = childNames[len(childNames)-1]
    for child in node.childNodes:
        if child.nodeType == Node.ELEMENT_NODE and child.nodeName == targetName:
            result.append(child)
    return result

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

        # Get the list of <contributor> elements
        root = minidom.parse(outputFilenames[0]).documentElement
        contributors = FindXmlChildren(root, "asset", "contributor")

        # Make sure at least one <contributor> has an <authoring_tool>
        contribWithAuthoringTool = None
        for contributor in contributors:
            if FindXmlChild(contributor, "authoring_tool") != None:
                contribWithAuthoringTool = contributor

        if contribWithAuthoringTool == None:
            context.Log("FAILED: Couldn't find an <asset><contributor><authoring_tool> element")
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
