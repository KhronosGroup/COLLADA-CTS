# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This judging object does the following:
#
# JudgeBaseline: Verifies that an <asset><contributor> element was exported containing an
#             <authoring_tool> tag.
# JudgeExemplary: Same as basic badge.
# JudgeSuperior: Same as intermediate badge.

import sys, string
from xml.dom import minidom, Node
from Core.Common.FUtils import FindXmlChild, GetXmlContent
from StandardDataSets.scripts import JudgeAssistant

# This is just like FindXmlChild, except that it returns a list containing all the
# child elements matching the last name given in the childNames array. So if you call
# FindXmlChildren(root, "asset", "contributor") and there are two <contributor>s,
# you'll get a list containing the two elements.
def FindXmlChildren(node, *childNames):
    result = []
    node = FindXmlChild(node, *childNames[:len(childNames)-1])
    if node == None or len(childNames) == 0:
        return result
    targetName = childNames[len(childNames)-1]
    for child in node.childNodes:
        if child.nodeType == Node.ELEMENT_NODE and child.nodeName == targetName:
            result.append(child)
    return result

class JudgingObject:
    def __init__(self):
        self.__assistant = JudgeAssistant.JudgeAssistant()
        self.basicResult = None # Cached result to avoid duplication of work
        
    def JudgeBasicImpl(self, context):
        self.__assistant.CheckCrashes(context)
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])
        if not self.__assistant.GetResults(): return False

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
        
        context.Log("PASSED: <contributor> present.")
        return True
      
    def JudgeBaseline(self, context):
        if self.basicResult == None:
            self.basicResult = self.JudgeBasicImpl(context)
        return self.basicResult

    def JudgeExemplary(self, context):
        return self.JudgeBaseline(context)
            
    def JudgeSuperior(self, context):
        return self.JudgeExemplary(context)
       
judgingObject = JudgingObject();
