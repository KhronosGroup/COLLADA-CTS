# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import re
import wx
import copy

from Core.Gui.Dialog.FSettingsScrolledSizer import *

class FRegExDialog(wx.Dialog):
    def __init__(self, parent, testProcedure, applicationMap):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 
                "Regular Expression Editor", size = wx.Size(600, 600),
                style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        
        window = wx.SplitterWindow(self)
        
        window.SetSashGravity(0.5)
        window.SetMinimumPaneSize(20)
        
        info = InfoPanel(window, testProcedure, applicationMap)
        tabs = TabsPanel(window, testProcedure, info)
        window.SplitVertically(tabs, info, 130)
        
        sizer.Add(window, 1, wx.EXPAND | wx.ALL, 5)
    
class TabsPanel(wx.Panel):
    def __init__(self, parent, regExManager, infoPanel):
        wx.Panel.__init__(self, parent)
        
        self.__regExManager = regExManager
        self.__infoPanel = infoPanel
        self.__oldSelection = -1
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        self.__list = wx.ListBox(self, style = wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.__OnClick, self.__list)
        self.__UpdateList()
        
        deleteButton = wx.Button(self, wx.ID_ANY, "&Delete")
        self.Bind(wx.EVT_BUTTON, self.__OnDelete, deleteButton)
        
        applyButton = wx.Button(self, wx.ID_ANY, "&Apply")
        self.Bind(wx.EVT_BUTTON, self.__OnApply, applyButton)
        
        sizer.Add(self.__list, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(deleteButton, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 5)
        sizer.Add(applyButton, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 
                  5)
    
    def __UpdateList(self):
        self.__list.Clear()
        for regExId in self.__regExManager.GetRegExIdGenerator():
            self.__list.Append("Regular Expression " + str(regExId), regExId)
    
    def __OnDelete(self, e):
        e.Skip()
        
        selection = self.__list.GetSelection()
        if (selection == -1): return
        regExId = self.__list.GetClientData(selection)
        
        if (not FUtils.ShowConfirmation(self, "Delete regular expression?", 
                True)):
            return
        
        self.__regExManager.DeleteRegEx(regExId)
        self.__UpdateList()
        
        self.__list.SetSelection(wx.NOT_FOUND)
        self.__oldSelection = -1
        self.__infoPanel.Clear()
    
    def __OnClick(self, e):
        e.Skip()
        
        selection = self.__list.GetSelection()
        if (selection == -1): return
        if (selection == self.__oldSelection): return
        self.__oldSelection = selection
        regExId = self.__list.GetClientData(selection)
        
        self.__infoPanel.SetInfo(self.__regExManager.GetRegExList(regExId),
                self.__regExManager.GetRegExSettings(regExId),
                self.__regExManager.GetIgnoredRegExList(regExId))
    
    def __OnApply(self, e):
        e.Skip()
        
        selection = self.__list.GetSelection()
        if (selection == -1): return
        regExId = self.__list.GetClientData(selection)
        
        oldRegEx = self.__regExManager.GetRegExList(regExId)
        newRegEx = self.__infoPanel.GetRegExList()
        
        oldIgnoreList = self.__regExManager.GetIgnoredRegExList(regExId)
        newIgnoreList = self.__infoPanel.GetIgnoredRegExList()
        if ((oldRegEx != newRegEx) or (oldIgnoreList != newIgnoreList)):
            i = 0
            try:
                for regEx in newRegEx:
                    re.compile(regEx)
                    i = i + 1
            except re.error, e:
                FUtils.ShowWarning(self, "Bad regular expression, page " + 
                        str(i) + ": not saved.")
                return
            
            i = 0
            try:
                for ignoredRegEx in newIgnoreList:
                    re.compile(ignoredRegEx)
                    i = i + 1
            except Exception, e:
                FUtils.ShowWarning(self, "Bad ignored regular expression, " + 
                        "page " + str(i) + ": " + "not saved.")
                return
            self.__regExManager.SetRegEx(regExId, newRegEx, newIgnoreList)
    
    
class InfoPanel(wx.Panel):
    def __init__(self, parent, testProcedure, applicationMap):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SUNKEN)
        
        self.__testProcedure = testProcedure
        self.__applicationMap = applicationMap
        
        self.__regExSizer = None
        self.__ignoreRegExSizer = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        self.Clear()
        sizer.Layout()
    
    def Clear(self):
        self.GetSizer().Clear(True)
    
    def SetInfo(self, regExList, settings, ignoredRegExList):
        self.Clear()
        sizer = self.GetSizer()
        
        scrolledSizer = FSettingsScrolledSizer(self, self.__testProcedure,
                self.__applicationMap, settings, False)
        
        regExLabel = wx.StaticText(self, wx.ID_ANY, "Regular Expression")
        self.__regExSizer = InfoPanelNotebookSizer(self, 
                                                   copy.deepcopy(regExList))
        
        ignoredLabel = wx.StaticText(self, wx.ID_ANY, 
                                     "Ignored Regular Expression")
        self.__ignoreRegExSizer = InfoPanelNotebookSizer(self, 
                copy.deepcopy(ignoredRegExList))
        
        labelStyle = wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT
        sizer.Add(scrolledSizer, 2, wx.EXPAND | wx.ALL, 5)
        sizer.Add(regExLabel, 0, labelStyle, 5)
        sizer.Add(self.__regExSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(ignoredLabel, 0, labelStyle, 5)
        sizer.Add(self.__ignoreRegExSizer, 1, wx.EXPAND | wx.ALL, 5)
        
        sizer.Layout()
        
        self.Update()
        
        if (len(regExList) > 0):
            self.__regExSizer.SetSelection(0)
        if (len(ignoredRegExList) > 0):
            self.__ignoreRegExSizer.SetSelection(0)
    
    def GetRegExList(self):
        return self.__regExSizer.GetList()
    
    def GetIgnoredRegExList(self):
        return self.__ignoreRegExSizer.GetList()


class InfoPanelNotebookSizer(wx.BoxSizer):
    def __init__(self, parent, list):
        wx.BoxSizer.__init__(self)
        
        self.__oldSelection = -1
        self.__list = list
        
        self.__listBox = wx.ListBox(parent, 
                style = wx.LB_SINGLE | wx.LB_HSCROLL)
        parent.Bind(wx.EVT_LISTBOX, self.__OnClick, self.__listBox)
        self.__textCtrl = wx.TextCtrl(parent, wx.ID_ANY, "", 
                style = wx.TE_MULTILINE)
        
        self.__listBox.Clear()
        i = 0
        for element in list:
            self.__listBox.Append("Page " + str(i), i)
            i = i + 1
        
        self.Add(self.__listBox, 0, wx.EXPAND | wx.ALL, 5)
        self.Add(self.__textCtrl, 1, wx.EXPAND | wx.ALL, 5)
    
    def SetSelection(self, index):
        self.__listBox.SetSelection(index)
        self.__Update()
    
    def GetList(self):
        if (self.__oldSelection != -1):
            oldPage = self.__listBox.GetClientData(self.__oldSelection)
            self.__list[oldPage] = self.__textCtrl.GetValue()
        return self.__list
    
    def __OnClick(self, e):
        e.Skip()
        self.__Update()
    
    def __Update(self):
        selection = self.__listBox.GetSelection()
        if (selection == -1): return
        if (selection == self.__oldSelection): return
        if (self.__oldSelection != -1):
            oldPage = self.__listBox.GetClientData(self.__oldSelection)
            self.__list[oldPage] = self.__textCtrl.GetValue()
        
        self.__oldSelection = selection
        page = self.__listBox.GetClientData(selection)
        self.__textCtrl.SetValue(self.__list[page])
    