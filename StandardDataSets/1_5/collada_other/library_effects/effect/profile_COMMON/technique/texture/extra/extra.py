
# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

# This sample judging object does advanced-badge extra-preservation checks.
#

import xml.sax.expatreader as Expat
import xml.sax.handler as XMLHandler
import Core.Common.FCOLLADAParser as FCOLLADAParser

class ExtraPreservationJudging:
    def __init__(self):
        self.__hasStepCrashed = None
        
    def JudgeBaseline(self, context):
        # For all badge levels: make sure nothing crashed.
        if (self.__hasStepCrashed == None):
            # Cache the often verified status.
            self.__hasStepCrashed = context.HasStepCrashed()

        if (self.__hasStepCrashed):
            context.Log("FAILED: Crashes during standard steps.")
            return False
        else:
            context.Log("PASSED: No crashes during standard steps.")
            return True
    
    def JudgeExemplary(self, context):
        return self.JudgeBaseline(context)
        
    def JudgeSuperior(self, context):
        if not self.JudgeBaseline(context): return False

        # Retrieve the filenames for all the export steps.
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False

        # Verify that these are all COLLADA documents.
        for filename in outputFilenames:
            if not FCOLLADAParser.IsCOLLADADocument(filename):
                context.Log("FAILED: Exported a non-COLLADA document.")
                return False
        
        # Process the input document
        inputFilename = context.GetInputFilename()
        reader = Expat.ExpatParser(0, 4*1024)
        try:
            contentHandler = COLLADAExtraProcessor()
            reader.setContentHandler(contentHandler)
            reader.parse(inputFilename)
            originalExtraInformation = contentHandler.GetExtras()
        except Exception, e:
            context.Log("FAILED: Crashed while parsing the test case file.")
            context.Log("        Please verify your conformance test integrity.")
            context.Log("        Exception: %s." % str(e))
            return False
            
        # Generate the comparator
        comparator = DictionaryCompare(originalExtraInformation)
            
        # Process the exported document and verify whether the extra was preserved every time.
        for filename in outputFilenames:
            try:
                contentHandler = COLLADAExtraProcessor()
                reader.setContentHandler(contentHandler)
                reader.parse(filename)
                newExtraInformation = contentHandler.GetExtras()
                if not comparator.Compare(newExtraInformation):
                    context.Log("FAILED: Extra information was not preserved.")
                    return False
                
            except Exception, e:
                context.Log("FAILED: Crashed while parsing the export file: '%s'." % filename)
                context.Log("        Exception: %s." % str(e))
                return False
                
        context.Log("PASSED: Extra information was preserved on re-export.")
        return True

# Load the extra-preservation judging script.
judgingObject = ExtraPreservationJudging();

class COLLADAExtraProcessor(XMLHandler.ContentHandler):
    
    def __init__(self):
        self.__extras = []
        self.__currentExtra = None
        self.__currentExtraElementStack = []
        self.__elementStack = []
        
    def GetExtras(self): return self.__extras
        
    # ContentHandler methods
    def startElement(self, name, attrs):
        if (len(self.__elementStack) == 0 and name != "COLLADA"):
            raise Exception("Not a COLLADA document..")

        if (self.__currentExtra != None):
            currentElement = self.__currentExtraElementStack[-1]
            newElement = {}
            self.__currentExtraElementStack.append(newElement)
            currentElement[name] = newElement
            
        elif (name == "extra"):
            # Create a new dictionary for the extra information.
            self.__currentExtra = {}
            self.__currentExtra["placement"] = self.__elementStack[:] # clones.
            self.__extras.append(self.__currentExtra)
            
            # Create a new dictionary for the extra XML tree.
            element = {}
            self.__currentExtraElementStack.append(element)
            self.__currentExtra["tree"] = element

        else:
            self.__elementStack.append(name)
            
        if (self.__currentExtra != None):
            # Record the local attributes.
            currentElement = self.__currentExtraElementStack[-1]
            attributes = {}
            for attributeName in attrs.getNames():
                attributes[attributeName] = attrs[attributeName]
            currentElement["py_test_attrs"] = attributes

    def endElement(self, name):
        if (self.__currentExtra != None):
            # We are inside an extra: are we leaving it or simply done with an inside element?
            if (len(self.__currentExtraElementStack) > 0):
                self.__currentExtraElementStack.pop()
            if (len(self.__currentExtraElementStack) == 0):
                self.__currentExtra = None

        elif (len(self.__elementStack) > 0):
            # Outside of the extras, just keep track of the current element stack.
            self.__elementStack.pop()

    def characters(self, content):
        # Record this extra bit of content.
        if (len(content) > 0 and self.__currentExtra != None):
            # Record this extra bit of content.
            currentElement = self.__currentExtraElementStack[-1]
            
            if (not currentElement.has_key("py_test_contents")):
                contents = []
            else:
                contents = currentElement["py_test_contents"]
            contents.append(content)

    def startDocument(self): pass # not interested..
    def startPrefixMapping(self, prefix, uri): pass # not interested..
    def endPrefixMapping(self, prefix): pass # not interested..
    def ignorableWhitespace(self, content): pass # not interested..
    def processingInstruction(self, target, data): pass # not interested..
    def startElementNS(self, name, qname, attrs): self.startElement(name, attrs) # not interested in NS data
    def endElementNS(self, name, qname): self.endElement(name) # not interested in NS data

class DictionaryCompare:
    def __init__(self, dict):
        self.__d = dict
        pass
        
    def Compare(self, other):
        # Iterate over the original list. Each element should exist in the second list.
        for entry in self.__d:
            originalPlacement = entry["placement"]

            found = False
            for otherEntry in other:
                if (originalPlacement == otherEntry["placement"]):
                    if (entry["tree"] == otherEntry["tree"]):
                        found = True
                        other.remove(otherEntry)
                        break
            if not found: return False
        return True
