# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx

from Core.Gui.Dialog.FMessageDialog import *

class FConfirmationDialog(FMessageDialog):
    def __init__(self, parent, message, default = False):
        bottomSizer = wx.BoxSizer()
        
        FMessageDialog.__init__(self, parent, message, "Confirmation", 
                wx.ART_QUESTION, bottomSizer)
        
        yesButton = wx.Button(self, wx.ID_ANY, "&Yes")
        noButton = wx.Button(self, wx.ID_ANY, "&No")
        bottomSizer.Add(yesButton, 0, wx.ALL, 5)
        bottomSizer.Add(noButton, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.__OnYes, yesButton)
        self.Bind(wx.EVT_BUTTON, self.__OnNo, noButton)
        
        if (default):
            yesButton.SetDefault()
            yesButton.SetFocus()
        else:
            noButton.SetDefault()
            noButton.SetFocus()
        
        self.Fit()
    
    def __OnYes(self, e):
        e.Skip()
        
        if (self.IsModal()):
            self.EndModal(wx.ID_YES)
        else:
            self.SetReturnCode(wx.ID_YES)
            self.Show(False)
    
    def __OnNo(self, e):
        e.Skip()
        if (self.IsModal()):
            self.EndModal(wx.ID_NO)
        else:
            self.SetReturnCode(wx.ID_NO)
            self.Show(False)
    