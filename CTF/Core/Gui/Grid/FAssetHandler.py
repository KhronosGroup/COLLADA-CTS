# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import xml.sax.saxutils

class FAssetHandler(xml.sax.saxutils.XMLGenerator):
    def __init__(self, file):
        xml.sax.saxutils.XMLGenerator.__init__(self, file)
        self.__tags = []
    
    def startDocument(self):
        pass #override
    
    def startElement(self, tag, attributes):
        if ((len(self.__tags) == 0) and (tag != "asset")): return
        self.__tags.append(tag)
        
        xml.sax.saxutils.XMLGenerator.startElement(self, tag, attributes)
    
    def characters(self, data):
        if (len(self.__tags) == 0): return
        
        xml.sax.saxutils.XMLGenerator.characters(self, data)
    
    def endElement(self, tag):
        if (len(self.__tags) == 0): return
        
        if (tag != self.__tags[-1]): 
            raise ValueError, "Invalid XML file"
        
        self.__tags.pop()
        xml.sax.saxutils.XMLGenerator.endElement(self, tag)
    