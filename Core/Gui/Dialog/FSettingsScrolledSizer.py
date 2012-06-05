# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx
import wx.lib.scrolledpanel

from Core.Gui.Dialog.FSettingSizer import *
from Core.Common.FConstants import *

class FSettingsScrolledSizer(wx.BoxSizer):
    def __init__(self, parent, testProcedure, applicationMap, settings = None, 
                 editable = True):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        
        self.__settingSizers = []
        
        title = wx.StaticText(parent, wx.ID_ANY, "Test Settings")
        scrolledPanel = wx.lib.scrolledpanel.ScrolledPanel(parent, wx.ID_ANY, 
                style=wx.SUNKEN_BORDER)
        
        self.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.Add(scrolledPanel, 1, wx.EXPAND | wx.TOP, 5)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        for step, app, op, setting in testProcedure.GetStepGenerator():
            sizer = FSettingSizer(scrolledPanel, applicationMap, editable, 
                                  self.__OnUpdateList)
            if (settings == None):
                default = testProcedure.GetGlobalSetting(step)
            else:
                default = settings[step]
            
            if (op == VALIDATE and op not in OPS_NEEDING_APP):
                sizer.SetOperation(">>", op, ">>" + op)
                sizer.Enable(False)
            else:
                sizer.SetOperation(app, op, "[" + app + "]" + op, 
                               testProcedure.GetSettingManager(), default)
            topSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 5)
            self.__settingSizers.append(sizer)
        
        padSizer = wx.BoxSizer(wx.VERTICAL)
        padSizer.Add(topSizer, 1, wx.EXPAND | wx.ALL, 5)
        
        scrolledPanel.SetSizer(padSizer)
        scrolledPanel.SetAutoLayout(True)
        scrolledPanel.SetupScrolling(scroll_x = False)
    
    def IsSettingOk(self):
        for settingSizer in self.__settingSizers:
            if (settingSizer.GetOperation() == VALIDATE): continue
            
            if (settingSizer.GetSettingName() == None):
                return False
        return True
    
    def GetSettings(self):
        settings = []
        for settingSizer in self.__settingSizers:
            settings.append(settingSizer.GetSetting())
        return settings
    
    def __OnUpdateList(self):
        for sizer in self.__settingSizers:
            sizer.UpdateList()
    