# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx

class FImageRenderArea:

    def __init__(self, x, y, width, height, filename, type):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        # string if IMAGE or LOG, list_of_str if ANIMATION
        self.__filename = filename 
        # what to display as.. possible to want to display ANIMATION as IMAGE
        self.__type = type 
    
    def GetType(self):
        return self.__type
    
    def GetRect(self):
        return wx.Rect(self.__x, self.__y, self.__width, self.__height)
    
    def GetFilename(self):
        return self.__filename