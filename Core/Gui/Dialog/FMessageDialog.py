# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx

class FMessageDialog(wx.Dialog):
    def __init__(self, parent, message, title, iconName, bottomSizer):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, 
                style = wx.CAPTION | wx.SYSTEM_MENU)
        
        outterSizer = wx.BoxSizer(wx.VERTICAL)
        
        topSizer = wx.BoxSizer()
        icon = wx.ArtProvider.GetBitmap(iconName, wx.ART_MESSAGE_BOX, (32,32))
        icon = wx.StaticBitmap(self, wx.ID_ANY, icon)
        textCtrl = self.__GetText(message)
        topSizer.Add(icon, 0, wx.ALL, 5)
        topSizer.Add(textCtrl, 1, wx.EXPAND | wx.ALL, 10)
        
        outterSizer.Add(topSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(bottomSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.SetSizer(outterSizer)
        self.Fit()
        self.Centre(wx.BOTH | wx.CENTRE_ON_SCREEN)
        
        self.Bind(wx.EVT_BUTTON, self.__OnCancel, id = wx.ID_CANCEL)
    
    def __GetText(self, message):
        displayWidth, displayHeight = wx.GetDisplaySize()
        displayWidth = displayWidth * 3 / 4
        displayHeight = displayHeight * 3 / 4
        label = wx.StaticText(self, wx.ID_ANY, message)
        # this works only if wxWidgets 2.6.2 or higher
        #label.Wrap(displayWidth)
        labelWidth, labelHeight = label.GetSize()
        
        if ((labelWidth < displayWidth) and (labelHeight < displayHeight)):
            return label
        
        label.Destroy()
        
        if (labelWidth < displayWidth):
            # consider area for horizontal scrollbar
            textCtrlWidth = min(labelWidth + 30, displayWidth)
            textCtrlHeight = min(labelHeight, displayHeight)
        else: # wraps because of long words, so add a few lines to make nicer
            textCtrlWidth = displayWidth
            lines = labelWidth / displayWidth + 1
            textCtrlHeight = min(labelHeight + (15 * lines), displayHeight)
        
        textCtrl = wx.TextCtrl(self, wx.ID_ANY, message,
                size = wx.Size(textCtrlWidth, textCtrlHeight),
                style = wx.TE_MULTILINE | wx.TE_READONLY)
        textCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        
        return textCtrl
    
    def __OnCancel(self, e):
        pass # don't cancel
    