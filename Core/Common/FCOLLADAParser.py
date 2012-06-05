# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path
import xml.sax.expatreader as Expat
import xml.sax.handler as XMLHandler
import Core.Common.FUtils as FUtils

def IsCOLLADADocument(filename):
    """ IsCOLLADADocument(filename) -> Boolean
    
    Retrieves whether the file identified by the given filename contains
    a COLLADA document. The extension of the filename is used for this purpose.
    'DAE' and 'XML' are the supported extensions.
        
    arguments:
        filename
            string corresponding to a filename
    
    returns:
        Boolean indicated whether the given filename contains a COLLADA document.
        
    """
    extension = FUtils.GetExtension(filename)
    extension = extension.upper()
    if extension == "DAE" or extension == "XML": return True
    else: return False

def GetCOLLADAAssetInformation(filename):
    """GetCOLLADAAssetInformations(filename) -> (str,str)
    
    Retrieves the <keywords> and <comments> the extension of the filename.
    Return ("","") if the filename is invalid or the information was not found.
    
    This implementation is quick, dirty, not XML-aware and is not meant
    to be used in critical situations.
    
    arguments:
        filename
            string corresponding to a COLLADA document filename.
    
    returns:
        (string, string, string) where the first string corresponds to
        the <title> element content, the second string corresponds to
        the <subject> element content and the third string corresponds to
        the <keywords> element content.
    
    """
    keyword = ""
    title = ""
    subject = ""
    reader = Expat.ExpatParser(0, 4*1024)

    try:
        contentHandler = COLLADAAssetProcessor()
        reader.setContentHandler(contentHandler)
        reader.parse(filename)
        
        # In theory, you should never get here:
        # the EarlyExitException should always be triggered.
        keyword = contentHandler.GetKeyword()
        title = contentHandler.GetTitle()
        subject = contentHandler.GetSubject()
        reader.close()
    
    except EarlyExitException, e:
        keyword = contentHandler.GetKeyword()
        title = contentHandler.GetTitle()
        subject = contentHandler.GetSubject()
        
    except Exception, e:
        pass
        
    return (title, subject, keyword)

class EarlyExitException(Exception):
    """ [INTERNAL] This exception is used to kill the SAX parser
        once we have found the information we were looking for. """
        
class COLLADAAssetProcessor(XMLHandler.ContentHandler):
    
    def __init__(self):
        self.__keyword = ""
        self.__title = ""
        self.__subject = ""
        self.__elementStack = []
        
    def GetKeyword(self): return self.__keyword
    def GetSubject(self): return self.__subject
    def GetTitle(self): return self.__title
        
    # ContentHandler methods
    def startElement(self, name, attrs):
        if (len(self.__elementStack) == 0 and 
                name != "COLLADA"):
            raise EarlyExitException("Not a COLLADA document..")

        elif (len(self.__elementStack) == 1 and
                name != "asset"):
            raise EarlyExitException("The <asset> element that we are interested in should always be first. Otherwise, it is considered missing.")

        self.__elementStack.append(name)

    def endElement(self, name):
        if (len(self.__elementStack) > 0):

            # check for early exit..
            if (len(self.__elementStack) == 2 and
                    self.__elementStack[0] == "COLLADA" and
                    self.__elementStack[1] == "asset"):
                raise EarlyExitException("Correctly closing the <asset> element. We don't care about the rest of the information.")

            self.__elementStack.pop()

    def characters(self, content):
        if (len(content) > 0):
            if (len(self.__elementStack) == 3 and
                    self.__elementStack[0] == "COLLADA" and
                    self.__elementStack[1] == "asset" and
                    self.__elementStack[2] == "title"):
                        
                # Retrieve the one title.
                self.__title = content.strip(' \t')

            elif (len(self.__elementStack) == 3 and
                    self.__elementStack[0] == "COLLADA" and
                    self.__elementStack[1] == "asset" and
                    self.__elementStack[2] == "subject"):
                
                # Retrieve the one subject.
                self.__subject = content.strip(' \t')
                
            elif (len(self.__elementStack) == 3 and
                    self.__elementStack[0] == "COLLADA" and
                    self.__elementStack[1] == "asset" and
                    self.__elementStack[2] == "keywords"):
                
                # The 1.4.1 schema is vague about this: assume there may
                # zero or one <keywords> element in the top-level <asset>
                self.__keyword = content.strip(' \t')


    def startDocument(self): pass # not interested..
    def startPrefixMapping(self, prefix, uri): pass # not interested..
    def endPrefixMapping(self, prefix): pass # not interested..
    def ignorableWhitespace(self, content): pass # not interested..
    def processingInstruction(self, target, data): pass # not interested..
    def startElementNS(self, name, qname, attrs): self.startElement(name, attrs) # not interested in NS data
    def endElementNS(self, name, qname): self.endElement(name) # not interested in NS data
