# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx

class FImageSizer(wx.StaticBoxSizer):
    def __init__(self, parent, title, filenames, caption = None):
        imageStatic = wx.StaticBox(parent, wx.ID_ANY, title)
        
        wx.StaticBoxSizer.__init__(self, imageStatic, wx.VERTICAL)
        
        self.__filenames = filenames
        self.__parent = parent
        
        if (caption != None):
            captionSizer = wx.FlexGridSizer(cols = 2, vgap = 5, hgap = 10)
            for entry in caption:
                captionSizer.Add(
                        wx.StaticText(parent, wx.ID_ANY, entry[0] + ":"))
                captionSizer.Add(wx.StaticText(parent, wx.ID_ANY, entry[1]))
                
            self.Add(captionSizer, 0, wx.ALL, 5)
        else:
            # to make it bottom aligned
            self.Add(wx.BoxSizer(), 1, wx.ALL, 5)
        
        controlsSizer = wx.BoxSizer()
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK, wx.ART_OTHER, 
                wx.Size(16, 16))
        button = wx.BitmapButton(self.__parent, wx.ID_ANY, bmp)
        self.__parent.Bind(wx.EVT_BUTTON, self.__OnBack, button)
        controlsSizer.Add(button)
        
        self.__frameNumber = wx.StaticText(self.__parent)
        controlsSizer.Add(self.__frameNumber, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        bmp = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, 
                wx.Size(16, 16))
        button = wx.BitmapButton(self.__parent, wx.ID_ANY, bmp)
        controlsSizer.Add(button)
        self.__parent.Bind(wx.EVT_BUTTON, self.__OnForward, button)
        
        self.Add(controlsSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        image = wx.EmptyBitmap(100, 100)
        self.__bitmap = wx.StaticBitmap(self.__parent, wx.ID_ANY, image)
        self.Add(self.__bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
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
    