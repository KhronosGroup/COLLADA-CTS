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
    