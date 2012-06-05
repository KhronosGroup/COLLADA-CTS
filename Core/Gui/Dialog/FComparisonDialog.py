# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx
import os.path

import Core.Common.FUtils as FUtils
from Core.Gui.Dialog.FDiffImageDialog import *
from Core.Gui.Dialog.FImageSizer import *

class FComparisonDialog(wx.Dialog):
    def __init__(self, parent, title1, filename1, title2, filename2, 
                 blessed = None):
        
        if (filename2 == None and blessed == None):
            wx.MessageBox("Unable to compare: please provide a compare-against image set or some blessed images.")
            return
        elif (filename2 == None):
            # If a second set of files is not provided, compare against the blessed one.
            filename2 = blessed
            blessed = None
            
        self.__maxFrameCount = max(len(filename1), len(filename2))
        if (blessed != None):
            self.__maxFrameCount = max(self.__maxFrameCount, len(blessed))
        
        if (len(filename1) == 1):
            title = str(os.path.basename(filename1[0])) + " Comparison"
        else:
            title = "Animation Comparison"
        
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        
        self.__blessedSizer = None
        self.__image1Sizer = None
        self.__image2Sizer = None
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        compSizer = self.__GetComparisonSizer(title1, filename1, 
                title2, filename2, blessed)
        
        sizer.Add(compSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.Fit()
    
    def __GetComparisonSizer(self, title1, filename1, title2, filename2, 
                             blessed):
        outterSizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        if (blessed != None):
            self.__blessedSizer = self.__GetImageSizer(blessed, "Blessed")
            sizer.Add(self.__blessedSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.__image1Sizer = self.__GetImageSizer(filename1, "Image 1", title1)
        self.__image2Sizer = self.__GetImageSizer(filename2, "Image 2", title2)
        
        sizer.Add(self.__image1Sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.__image2Sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        outterSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        controlsSizer = wx.BoxSizer()
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK, wx.ART_OTHER, 
                wx.Size(32, 32))
        button = wx.BitmapButton(self, wx.ID_ANY, bmp)
        self.Bind(wx.EVT_BUTTON, self.__OnBack, button)
        controlsSizer.Add(button)
        
        label = wx.StaticText(self, wx.ID_ANY, "ALL")
        controlsSizer.Add(label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, 
                wx.Size(32, 32))
        button = wx.BitmapButton(self, wx.ID_ANY, bmp)
        controlsSizer.Add(button)
        self.Bind(wx.EVT_BUTTON, self.__OnForward, button)
        
        outterSizer.Add(controlsSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        bottomSizer = wx.BoxSizer()
        if (blessed != None):
            blessedButton = wx.Button(self, wx.ID_ANY, "Diff Blessed")
            self.Bind(wx.EVT_BUTTON, self.__OnDiffBlessed, blessedButton)
            bottomSizer.Add(blessedButton, 0, wx.ALL, 5)
        imageButton = wx.Button(self, wx.ID_ANY, "Diff Image2")
        self.Bind(wx.EVT_BUTTON, self.__OnDiffImage, imageButton)
        bottomSizer.Add(imageButton, 0, wx.ALL, 5)
        
        outterSizer.Add(bottomSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        return outterSizer

    def __OnDiffImage(self, e):
        filename1 = self.__image1Sizer.GetCurrentFile()
        if (filename1 == None): return
        filename2 = self.__image2Sizer.GetCurrentFile()
        if (filename2 == None): return
        
        image1 = wx.Image(filename1, wx.BITMAP_TYPE_ANY)
        image2 = wx.Image(filename2, wx.BITMAP_TYPE_ANY)
        
        if (image1.Ok() and image2.Ok()):
            dialog = FDiffImageDialog(self, image1, image2)
            dialog.ShowModal()
    
    def __OnDiffBlessed(self, e):
        filename1 = self.__image1Sizer.GetCurrentFile()
        if (filename1 == None): return
        filename2 = self.__blessedSizer.GetCurrentFile()
        if (filename2 == None): return
        
        image1 = wx.Image(filename1, wx.BITMAP_TYPE_ANY)
        image2 = wx.Image(filename2, wx.BITMAP_TYPE_ANY)
        
        if (image1.Ok() and image2.Ok()):
            dialog = FDiffImageDialog(self, image1, image2)
            dialog.ShowModal()

    def __GetImageSizer(self, filename, type, caption = None):
        if (len(filename) > 1):
            title = type + "(Animation)"
        else:
            title = type + " (" + os.path.basename(filename[0]) + ")"
        return FImageSizer(self, title, filename, caption)
    
    def __OnBack(self, e):
        if (self.__blessedSizer != None):
            curIndex = self.__blessedSizer.GetImageIndex() - 1
            if (curIndex < 0):
                curIndex = self.__maxFrameCount - 1
            self.__blessedSizer.SetImageIndex(curIndex)
        
        curIndex = self.__image1Sizer.GetImageIndex() - 1
        if (curIndex < 0):
            curIndex = self.__maxFrameCount - 1
        self.__image1Sizer.SetImageIndex(curIndex)
        
        curIndex = self.__image2Sizer.GetImageIndex() - 1
        if (curIndex < 0):
            curIndex = self.__maxFrameCount - 1
        self.__image2Sizer.SetImageIndex(curIndex)
    
    def __OnForward(self, e):
        if (self.__blessedSizer != None):
            curIndex = self.__blessedSizer.GetImageIndex() + 1
            if (curIndex >= self.__maxFrameCount):
                curIndex = 0
            self.__blessedSizer.SetImageIndex(curIndex)
        
        curIndex = self.__image1Sizer.GetImageIndex() + 1
        if (curIndex >= self.__maxFrameCount):
            curIndex = 0
        self.__image1Sizer.SetImageIndex(curIndex)
        
        curIndex = self.__image2Sizer.GetImageIndex() + 1
        if (curIndex >= self.__maxFrameCount):
            curIndex = 0
        self.__image2Sizer.SetImageIndex(curIndex)
