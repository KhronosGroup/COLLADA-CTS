# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path
import wx
import string
import sha as SHA1
import sys
import string
import xml
from datetime import datetime, timedelta

from stat import *
from Core.Gui.Dialog.FConfirmationDialog import *
from Core.Gui.Dialog.FWarningDialog import *

def GetExtension(filename):
    """GetExtension(filename) -> str
    
    Gets the extension of the filename. Return "" if no extension.
    
    arguments:
        filename
            string corresponding to filename to get extension from.
    
    returns:
        string corresponding to the extension of the filename.
    
    """
    try:
        return os.path.basename(filename).rsplit(".", 1)[1]
    except IndexError, e:
        return ""

def ChangeExtension(filename, newExtension):
    """ChangeExtension(filename, newExtension) -> str
    
    Replaces the extension of the filename with the given one.
    If the given filename has no extension, the new extension is
    simply appended.
    
    arguments:
        filename
            string corresponding to the filename whose extension to change.
        newExtension
            string corresponding to the new extension to append. Do not
                prepend with a period ('.').
    
    returns:
        string corresponding to the new filename.
    
    """
    try:
        # Isolate the filename
        slashIndex = filename.rfind('/')
        backslashIndex = filename.rfind('\\')
        if (backslashIndex > slashIndex):
            slashIndex = backslashIndex;

        # Look for an existing extension
        periodIndex = filename.rfind('.')
        if (periodIndex > slashIndex):
            return filename[0 : periodIndex] + "." + newExtension
        else:
            return filename + "." + newExtension
        
    except IndexError, e:
        return ""

def GetProperFilename(filename):
    """GetProperFilename(filename) -> str
    
    Gets the proper filename (the filename with the extension removed) of the
    filename.
    
    arguments:
        filename
            string corresponding to filename to get extension from.
    
    returns:
        string corresponding to proper filename of the filename.
    
    """
    return os.path.basename(filename).rsplit(".", 1)[0]

def IsImageFile(ext):
    """IsImageFile(ext) -> bool
    
    Determines if the given extension corresponds to an image file (jpg, bmp,
    or png).
    
    arguments:
        ext
            string corresponding to extension to check.
    
    returns:
        bool corresponding to whether it is an image file.
    
    """
    return (ext == "jpg") or (ext == "bmp") or (ext == "png")

def GetInvalidString():
    """GetInvalidString() -> str
    
    Returns a string consisting of the invalid characters in a filename.
    
    returns:
        string consisting of the invalid characters in a filename.
    
    """
    return "\\ / : * ? \" < > |"

def IsValidFilename(filename):
    """IsValidFilename(filename) -> bool
    
    Determines if the given filename is a valid filename. It is invalid if it
    contains any of the characters found in the string return by 
    GetInvalidString().
    
    arguments:
        filename
            string corresponding to the filename to check.
    
    returns:
        bool corresponding to whether the given filename is valid.
    
    """
    return ((filename.find("\\") == -1) and (filename.find("/") == -1) and
            (filename.find(":") == -1) and (filename.find("*") == -1) and
            (filename.find("?") == -1) and (filename.find("\"") == -1) and
            (filename.find("<") == -1) and (filename.find(">") == -1) and
            (filename.find("|") == -1))

def GetAvailableFilename(suggestion, suggestGiven = True):
    """GetAvailableFilename(suggestion) -> str
    
    Gets the next available filename given the suggestion. It returns 
    suggestion if suggestion does not correspond to a file and suggestGiven is
    True. Othewise it will return the next filename of form suggestion_(#) 
    which does not correspond to an existant file. # is a positive integer 
    starting at 0.
    
    arguments:
        suggestion
            string corresponding to the desired filename.
        suggestGiven
            bool corresponding whether to return the given suggestion. If 
            True, it will return it. If False, it will always return a 
            filename of the form suggestion_(#).
    
    returns:
        string corresponding to next available filename.
    
    """
    if ((not suggestGiven) or os.path.isfile(suggestion)):
        prefix, postfix = os.path.splitext(suggestion)
        i = 0
        while (os.path.isfile(prefix + "_(" + str(i) + ")" + postfix)):
            i = i + 1
        suggestion = prefix + "_(" + str(i) + ")" + postfix
    return suggestion

def GetAvailableDirectory(suggestion, suggestGiven = True):
    """GetAvailableDirectory(suggestion) -> str
    
    Gets the next available directory name given the suggestion. It returns 
    suggestion if suggestion does not correspond to a directory and 
    suggestGiven is True. Othewise it will return the next directory name of 
    form suggestion_(#) which does not correspond to an existant directory. # 
    is a positive integer starting at 0.
    
    arguments:
        suggestion
            string corresponding to the desired directory name.
        suggestGiven
            bool corresponding whether to return the given suggestion. If 
            True, it will return it if there is no directory with same 
            directory name. If false, it will always return a directory name of
            the form suggestion_(#).
    
    returns:
        string corresponding to next available directory name.
    
    """
    if ((not suggestGiven) or os.path.isdir(suggestion)):
        i = 0
        while (os.path.isdir(suggestion + "_(" + str(i) + ")")):
            i = i + 1
        suggestion = suggestion + "_(" + str(i) + ")"
    return suggestion

def SplitPath(filename):
    """SplitPath(filename) -> list_of_str
    
    Splits the filename into a list of string. The separation of the filename
    happens at each directory level. The drive is neglected in the list of
    strings. 
    
    Ex: 
        SplitPath("C:/Core/Common/FUtils.py") -> 
                ["Core", "Common", "FUtils.py"]
    
    arguments:
        filename
            string corresponding to absolute filename of the filename to split.
            Note that if the filename is not an absolute path, this function
            may enter an infinite loop.
    
    returns:
        a list of string corresponding to the filename separated at each
        directory level.
    
    """
    pathDrive, filename = os.path.splitdrive(filename)
    
    list = []
    while (os.path.basename(filename) != ""):
        list.append(os.path.basename(filename))
        filename = os.path.dirname(filename)
    list.reverse()
    
    return list
    

def GetHtmlRelativePath(filename, path):
    """GetHtmlRelativePath(filename, path) -> str
    
    Gets the relative path starting from path and ending at filename. Both
    must be absolute paths and on the same drive.
    
    Note: Same as GetRelativePath except the directory separator is always "/"
    because Html requires this.
    
    arguments:
        filename
            string corresponding to the absolute destination of the relative 
            path.
        path
            string corresponding to the absolute starting point of the relative
            path.
    
    returns:
        string corresponding to the relative path with "/" as directory
        separators between filename and path.
    
    """
    return "./" + GetRelativePath(filename, path).replace("\\", "/")

def GetRelativePath(filename, path):
    """GetRelativePath(filename, path) -> str
    
    Gets the relative path starting from path and ending at filename. Both
    must be on the same drive.
    
    arguments:
        filename
            string corresponding to the absolute or relative destination of the
            relative path.
        path
            string corresponding to the absolute or relative starting point of 
            the relative path.
    
    returns:
        string corresponding to the relative path between filename and path.
    
    """
    filename = os.path.normpath(os.path.abspath(filename))
    path = os.path.normpath(os.path.abspath(path))
    
    pathList = SplitPath(path)
    filenameList = SplitPath(filename)
    
    i = 0
    while ((i < len(pathList)) and (i < len(filenameList)) and 
           (pathList[i] == filenameList[i])):
        i = i + 1
    
    pathList = pathList[i:]
    filenameList = filenameList[i:]
    
    relPath = ""
    for dummy in pathList:
        relPath = os.path.join(relPath, "..")
    
    for entry in filenameList:
        relPath = os.path.join(relPath, entry)
    
    return relPath

def GetCollapsePath(filename):
    """GetCollapsePath(filename) ->str
    
    Returns the path without "..".
    
    arguments:
        filename
            string representation of the filepath
    
    return:
        the filepath without ".."
    
    """
    filenameList = SplitPath(filename)
    
    for i in range(len(filenameList) - 1, -1, -1):
        if ((i != 0) and (filenameList[i] == "..") and 
                (filenameList[i - 1] != "..")):
            filenameList = filenameList[:i - 1] + filenameList[i + 1:]
    
    return string.join(filenameList, os.sep)

def ShowWarning(parent, message):
    """ShowWarning(parent, message) -> None
    
    Displays a modal warning dialog.
    
    arguments:
        parent
            wx.Window that is the parent of the warning dialog.
        message
            string corresponding to the message to be written in the dialog.
    
    """
    alert = FWarningDialog(parent, message)
    alert.ShowModal()
    alert.Destroy()

def ShowConfirmation(parent, message, default):
    """ShowConfirmation(parent, message, default) -> bool
    
    Displays a modal confirmation dialog and returns True if the user accepted
    and False otherwise.
    
    arguments:
        parent
            wx.Window that is the parent of the confirmation dialog.
        message
            string corresponding to the message to be written in the dialog.
        default
            bool corresponding to which button is the default in the dialog. 
            True if "Yes" is the default, False if "No" is the default.
    
    returns:
        bool corresponding to whther the user accepted the confirmation. True
        if the user accepted, False otherwise.
    
    """
    confirm = FConfirmationDialog(parent, message, default)
    
    if (confirm.ShowModal() == wx.ID_NO):
        confirm.Destroy()
        return False
    else:
        confirm.Destroy()
        return True

def NormalizeRegEx(regEx):
    """NormalizeRegEx(regEx) -> str
    
    Escapes the special characters in a regular expression so it can be
    compiled properly.
    
    arguments:
        parent
            string of the regular expression where special characters are not
            escaped
    
    returns:
        string of the regular expression where special caharacters are escaped
    
    """
    regEx = regEx.replace("\\", "\\\\")
    regEx = regEx.replace(".", "\\.")
    regEx = regEx.replace("^", "\\^")
    regEx = regEx.replace("$", "\\$")
    regEx = regEx.replace("[", "\\[")
    regEx = regEx.replace("]", "\\]")
    regEx = regEx.replace("(", "\\(")
    regEx = regEx.replace(")", "\\)")
    return regEx
    
def CalculateChecksum(filename):
    """ CalculateChecksum(filename) -> str
    
    Calculates the SHA checksum of a file.
    This is used to authenticate the adopter's test suite.
    
    returns:
        string of the checksum for the given file.
        
    """
    try:
        file = open(filename, "rb")
        checksumCalculator = SHA1.new()
        for line in file:
            checksumCalculator.update(line)
        file.close()
        return checksumCalculator.hexdigest()
    except Exception, e:
        return "0000000000000000000000000000000000000000"
    
def CalculateSuiteChecksum():
    """ CalculateSuiteChecksum() -> str
    
    Calculates a checksum for every core python script file
    in the test framework.
    
    return:
        string of the checksums for the test framework script files.

    """
    
    checksum = ""
    queue = ["../ImageComparators", "."]
    while (len(queue) > 0):
        path = queue[-1]
        queue.pop()
        
        for dirEntry in os.listdir(path):
            pathname = os.path.join(path, dirEntry)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
                if (pathname.find(".svn") == -1):
                    # Add this path to our queue.
                    # Avoid useless iterations by avoiding the .svn folder.
                    queue.append(pathname)
            elif S_ISREG(mode):
                    # Process all python script files, except for the __init__.py ones.
                if (GetExtension(pathname).lower() == "py" and
                        pathname.find("__init__") == -1):
                    checksum += CalculateChecksum(pathname) + "\n"

    return checksum + "----\n"

def FindXmlChild(node, *childNames):
    """ FindXmlChild(node, *childName) -> xml.dom.Node

    Allows you to search through the children of an xml node for an element with
    a particular name. This function takes the Node to search through followed by
    a variable number of string arguments representing the names of the elements
    to search through. For example, if "root" is the node corresponding to the
    <COLLADA> element of a Collada document, you could write
      FindXmlChild(root, "asset", "contributor", "author")
    to get the <COLLADA><asset><contributor><author> element.

    return:
        The matching xml.dom.Node, or None if a matching element wasn't found.
    """
    def FindXmlChildShallow(node, childName):
        """ FindXmlChild helper function """
        if node == None:
            return None
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.nodeName == childName:
                return child
    for childName in childNames:
        node = FindXmlChildShallow(node, childName)
    return node

def GetXmlContent(node):
    """ GetXmlContent(node) -> string

    Returns a string containing the character content of an xml.dom.Node

    return:
        The character content as a string.
    """
    if node == None:
        return ""
    content = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            content.append(child.nodeValue)
    return string.join(content).strip()

def ParseDate(s):
    """ ParseDate(s) -> datetime

    This function converts a string containing the subset of ISO8601 that can be
    represented with xs:dateTime into a datetime object. As such it's suitable
    for parsing Collada's <created> and <modified> elements. The date must be of
    the form
      '-'? yyyy '-' mm '-' dd 'T' hh ':' mm ':' ss ('.' s+)? (zzzzzz)?
    See http://www.w3.org/TR/xmlschema-2/#dateTime for more info on the various parts.

    return:
        A datetime or None if the string wasn't formatted correctly.
    """
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


# NOTE: might be useful in future
#def UniqueList(list):
#    """UniqueList(list) -> list
#    
#    Returns a list that contains the same elements as the given list but only 
#    once. The first occurence it kept and subsequent ones are removed.
#    
#    arguments:
#        list
#            list of elements.
#    
#    returns:
#        list with same elements as given list but only occuring once.
#    
#    """
#    newList = []
#    for element in list:
#        if (newList.count(element) == 0):
#            newList.append(element)
#    return newList
