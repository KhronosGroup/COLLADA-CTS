# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx

class FDiffImageDialog(wx.Dialog):
    def __init__(self, parent, image1, image2):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Image Diff")
        
        outterSizer = wx.FlexGridSizer(2, 2, 5, 5)
        
        absLabel = wx.StaticText(self, wx.ID_ANY, "Absolute Difference")
        relLabel = wx.StaticText(self, wx.ID_ANY, "Relative Difference")
        
        outterSizer.Add(absLabel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        outterSizer.Add(relLabel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        absImage, relImage = self.__GetDifferences(image1, image2)
        bitmap = wx.StaticBitmap(self, wx.ID_ANY, absImage.ConvertToBitmap())
        outterSizer.Add(bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bitmap = wx.StaticBitmap(self, wx.ID_ANY, relImage.ConvertToBitmap())
        outterSizer.Add(bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.SetSizer(outterSizer)
        self.Fit()
    
    def __GetDifferences(self, image1, image2):
        maxHeight = max(image1.GetHeight(), image2.GetHeight())
        minHeight = min(image1.GetHeight(), image2.GetHeight())
        maxWidth = max(image1.GetWidth(), image2.GetWidth())
        minWidth = min(image1.GetWidth(), image2.GetWidth())
        
        absImage = wx.EmptyImage(maxHeight, maxWidth)
        absImage.SetRGBRect(wx.Rect(0, 0, maxWidth, maxHeight), 255, 255, 255)
        
        maxDifference = 0
        
        for i in range(minWidth):
            for j in range(minHeight):
                image1Red = image1.GetRed(i, j)
                image1Green = image1.GetGreen(i, j)
                image1Blue = image1.GetBlue(i, j)
                image2Red = image2.GetRed(i, j)
                image2Green = image2.GetGreen(i, j)
                image2Blue = image2.GetBlue(i, j)
                
                redDifference = abs(image1Red - image2Red)
                greenDifference = abs(image1Green - image2Green)
                blueDifference = abs(image1Blue - image2Blue)
                
                totalDifference = (redDifference + greenDifference + 
                                   blueDifference)
                if (totalDifference > maxDifference):
                    maxDifference = totalDifference
                
                absImage.SetRGB(i, j, redDifference, greenDifference, 
                        blueDifference)
        
        relImage = wx.EmptyImage(maxHeight, maxWidth)
        relImage.SetRGBRect(wx.Rect(0, 0, maxWidth, maxHeight), 255, 255, 255)
        
        if (maxDifference == 0):
            maxDifference = 0
        else:
            maxDifference = 255.0 / maxDifference 
        
        for i in range(minWidth):
            for j in range(minHeight):
                difference = (absImage.GetRed(i, j) + absImage.GetGreen(i, j) + 
                              absImage.GetBlue(i, j))
                
                relDifference = difference * maxDifference
                relImage.SetRGB(i, j, relDifference, relDifference, 
                                relDifference)
        
        return (absImage, relImage)
    