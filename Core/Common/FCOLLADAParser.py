# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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

def GetKeywordAndComment(filename):
    """GetKeywordAndComment(filename) -> (str,str)
    
    Retrieves the <keywords> and <comments> the extension of the filename.
    Return ("","") if the filename is invalid or the information was not found.
    
    This implementation is quick, dirty, not XML-aware and is not meant
    to be used in critical situations.
    
    arguments:
        filename
            string corresponding to a COLLADA document filename.
    
    returns:
        (string, string) where the first string corresponds to
        the <keywords> element content and the second string corresponds to
        the <comments> element content.
    
    """
    keyword = ""
    comment = ""
    reader = Expat.ExpatParser(0, 16*1024)

    try:
        contentHandler = GetKeywordAndCommentProcessor()
        reader.setContentHandler(contentHandler)
        reader.parse(filename)
        
        # In theory, you should never get here:
        # the EarlyExitException should always be triggered.
        keyword = contentHandler.GetKeyword()
        comment = contentHandler.GetComment()
        reader.close()
    
    except EarlyExitException, e:
        keyword = contentHandler.GetKeyword()
        comment = contentHandler.GetComment()
        
    except Exception, e:
        pass
        
    return (keyword, comment)

class EarlyExitException(Exception):
    """ [INTERNAL] This exception is used to kill the SAX parser
        once we have found the information we were looking for. """
        
class GetKeywordAndCommentProcessor(XMLHandler.ContentHandler):
    
    def __init__(self):
        self.__keyword = ""
        self.__comment = ""
        self.__elementStack = []
        
    def GetKeyword(self): return self.__keyword
    def GetComment(self): return self.__comment
        
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
            if (len(self.__elementStack) == 4 and
                    self.__elementStack[0] == "COLLADA" and
                    self.__elementStack[1] == "asset" and
                    self.__elementStack[2] == "contributor" and
                    self.__elementStack[3] == "comments"):
                        
                # Only retrieve the first available contributor's comment.
                if (len(self.__comment) == 0): self.__comment = content.strip(' \t')
                
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
