import wx

from Core.Gui.Dialog.FMessageDialog import *

class FWarningDialog(FMessageDialog):
    def __init__(self, parent, message):
        bottomSizer = wx.BoxSizer()
        
        FMessageDialog.__init__(self, parent, message, "Alert", wx.ART_WARNING, 
                          bottomSizer)
        
        okButton = wx.Button(self, wx.ID_ANY, "OK")
        bottomSizer.Add(okButton, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.__OnOk, okButton)
        
        okButton.SetDefault()
        okButton.SetFocus()
        
        self.Fit()
    
    def __OnOk(self, e):
        e.Skip()
        
        if (self.IsModal()):
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Show(False)