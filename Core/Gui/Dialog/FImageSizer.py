# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx

class FImageSizer(wx.StaticBoxSizer):
    def __init__(self, parent, title, filenames, caption = None):
        imageStatic = wx.StaticBox(parent, wx.ID_ANY, title)
        
        wx.StaticBoxSizer.__init__(self, imageStatic, wx.VERTICAL)
        
        self.__filenames = filenames
        self.__parent = parent
        
        if (caption != None):
            captionSizer = wx.FlexGridSizer(cols = 2, vgap = 2, hgap = 2)
            for entry in caption:
                if (len(entry) > 1): 
                    captionSizer.Add(wx.StaticText(parent, wx.ID_ANY, entry[0] + ":"))
                    captionSizer.Add(wx.StaticText(parent, wx.ID_ANY, entry[1]))
                else:
                    captionSizer.Add(wx.StaticText(parent, wx.ID_ANY, entry[0]))
                    captionSizer.Add(wx.StaticText(parent, wx.ID_ANY))
                
            self.Add(captionSizer, 0, wx.ALL, 2)
        else:
            # to make it bottom aligned
            self.Add(wx.BoxSizer(), 1, wx.ALL, 2)
        
        controlsSizer = wx.BoxSizer()
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK, wx.ART_OTHER, wx.Size(16, 16))
        button = wx.BitmapButton(self.__parent, wx.ID_ANY, bmp)
        self.__parent.Bind(wx.EVT_BUTTON, self.__OnBack, button)
        controlsSizer.Add(button)
        
        self.__frameNumber = wx.StaticText(self.__parent)
        controlsSizer.Add(self.__frameNumber, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, wx.Size(16, 16))
        button = wx.BitmapButton(self.__parent, wx.ID_ANY, bmp)
        controlsSizer.Add(button)
        self.__parent.Bind(wx.EVT_BUTTON, self.__OnForward, button)
        
        self.Add(controlsSizer, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        
        image = wx.EmptyBitmap(100, 100)
        self.__bitmap = wx.StaticBitmap(self.__parent, wx.ID_ANY, image)
        self.Add(self.__bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        
        self.__currentStep = 0
        self.SetImageIndex(self.__currentStep)
    
    def __OnBack(self, e):
        self.__currentStep = self.__currentStep - 1
        if (self.__currentStep < 0):
            self.__currentStep = len(self.__filenames) - 1
        
        self.SetImageIndex(self.__currentStep)
    
    def __OnForward(self, e):
        self.__currentStep = self.__currentStep + 1
        if (self.__currentStep >= len(self.__filenames)):
            self.__currentStep = 0
        
        self.SetImageIndex(self.__currentStep)
    
    def GetImageIndex(self):
        return self.__currentStep
    
    def GetCurrentFile(self):
        if (self.__currentStep < len(self.__filenames)):
            return self.__filenames[self.__currentStep]
        return None
    
    def SetImageIndex(self, index):
        self.__currentStep = index
        if (index < len(self.__filenames)):
            image = wx.Bitmap(self.__filenames[index], wx.BITMAP_TYPE_ANY)
            self.__bitmap.SetBitmap(image)
            self.__bitmap.Show(True)
            self.__frameNumber.SetLabel(str(index))
        else:
            self.__bitmap.Show(False)
            self.__frameNumber.SetLabel("x" + str(index))
        self.Layout()
    