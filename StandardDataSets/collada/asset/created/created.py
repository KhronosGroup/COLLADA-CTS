# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This judging object does the following:
#
# JudgeBasic: Verifies that no steps crashed and that the <created> element output by
#             the tool is within 24 hours of the current time.
# JudgeIntermediate: Same as basic badge.
# JudgeAdvanced: Same as intermediate badge.

import sys, string
from xml.dom import minidom, Node
from datetime import datetime, timedelta

def findChildShallow(node, childName):
    if node == None:
        return None
    for child in node.childNodes:
        if child.nodeType == Node.ELEMENT_NODE and child.nodeName == childName:
            return child

def findChild(node, *childNames):
    for childName in childNames:
        node = findChildShallow(node, childName)
    return node

def getContent(node):
    if node == None:
        return ""
    content = []
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE:
            content.append(child.nodeValue)
    return string.join(content).strip()

# This function returns a valid UTC datetime object if the input string is formatted correctly,
# and None otherwise. The date must be of the form
#    '-'? yyyy '-' mm '-' dd 'T' hh ':' mm ':' ss ('.' s+)? (zzzzzz)?
# See http://www.w3.org/TR/xmlschema-2/#dateTime for more info on the various parts.
def parseDate(s):
    # Split the date (yyyy-mm-dd) and time by the "T" in the middle
    parts = s.split("T")
    if len(parts) != 2:
        return None
    date = parts[0]
    time = parts[1]

    # Parse the yyyy-mm-dd part
    parts = date.split("-")
    yearMultiplier = 1
    if date[0] == "-":
        yearMultiplier = -1
        parts.remove(0)
    if len(parts) != 3:
        return None
    try:
        year = yearMultiplier * int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    except ValueError:
        return None

    # Split the time and time zone by "Z", "+", or "-"
    timeZoneDelta = timedelta()
    timeZoneDeltaModifier = 1
    parts = time.split("Z")
    if len(parts) > 1:
        if parts[1] != "":
            return None
    if len(parts) == 1:
        parts = time.split("+")
    if len(parts) == 1:
        parts = time.split("-")
        timeZoneDeltaModifier = -1
    if len(parts) == 1: # Time zone not present
        return None

    time = parts[0]
    timeZone = parts[1]

    if timeZone != "":
        parts = timeZone.split(":")
        if len(parts) != 2:
            return None
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
        except ValueError:
            return None
        # The line below isn't a mistake. timedelta is initialized strangely.
        timeZoneDelta = timeZoneDeltaModifier * timedelta(0, 0, 0, 0, minutes, hours)

    parts = time.split(":")
    if len(parts) != 3:
        return None
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) # We're losing the decimal portion here, but it probably doesn't matter
    except ValueError:
        return None

    return datetime(year, month, day, hours, minutes, seconds) - timeZoneDelta

# parseDate tests
# print parseDate("-2000-01-02") # This will fail since Python's datetime doesn't support negative years
# print parseDate("2007-05-14T22:53:22Z") # Should print "2007-05-14 22:53:22"
# print parseDate("2002-10-10T12:00:00-05:00") # Should print "2002-10-10 17:00:00"
# print parseDate("2002-10-10T00:00:00+05:00") # Should print "2002-10-09 19:00:00"


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

        # Get the <created> time for the input file
        root = minidom.parse(context.GetInputFilename()).documentElement
        inputCreatedDate = parseDate(getContent(findChild(root, "asset", "created")))
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
        outputCreatedDate = parseDate(getContent(findChild(root, "asset", "created")))
        if outputCreatedDate == None:
            context.Log("FAILED: Couldn't read <created> value from the exported file.")
            return False

        if (outputCreatedDate - inputCreatedDate) < timedelta(0):
            context.Log("FAILED: <created> has an incorrect time stamp. It should be later than the <created> value in the original file.")
            context.Log("The original <created> time is " + str(inputCreatedDate))
            context.Log("The exported <created> time is " + str(outputCreatedDate))
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
