# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx.wizard

import Core.Common.FUtils as FUtils
from Core.Gui.Dialog.FSettingsScrolledSizer import *

class FAppSettingsDialog(wx.wizard.WizardPageSimple):
    def __init__(self, parent, testProcedure, applicationMap):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        
        self.__settingsSizer = FSettingsScrolledSizer(self, testProcedure,
                                                      applicationMap)
        self.SetSizer(self.__settingsSizer)
        
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.__OnPageChanging)
    
    def __OnPageChanging(self, e):
        if (not self.__settingsSizer.IsSettingOk()):
            FUtils.ShowWarning(self, "There's an invalid setting.")
            e.Veto()
        else:
            e.Skip()
    
    def GetSettings(self):
        return self.__settingsSizer.GetSettings()
    
# Used to start up this dialog without the entire application.
##import wx
##from FTestProcedure import *
##class MainFrame(wx.MDIParentFrame):
##    def __init__(self, parent, id, title):
##        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
##                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
##        
##        run = [('3DSMax 7', [('Import', 'Default'), 
##                             ('Render', 'Default'),
##                             ('Export', 'Default')]), 
##               ('3DSMax 7', [('Import', 'Default'),
##                             ('Render', 'Default')])]
##        #run = [('3DSMax 7', ['Import',])]
##        wiz = wx.wizard.Wizard(self, -1, "Add a Test")
##        page1 = FAppSettingsDialog(wiz,FTestProcedure(run)) # this is broken
##        wiz.FitToPage(page1)
##        wiz.RunWizard(page1)
##        
##        print page1.GetSettings()
##        
##app = wx.PySimpleApp()
##frame = MainFrame(None,-1, "Test")
##app.MainLoop()
##