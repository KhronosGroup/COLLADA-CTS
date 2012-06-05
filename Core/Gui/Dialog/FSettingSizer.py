# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx
import os
import os.path
import string
import copy

import Core.Common.FUtils as FUtils

from Core.Common.FConstants import *
from Core.Gui.Dialog.FChangeSettingsDialog import *
from Core.Logic.FSetting import *

class FSettingSizer(wx.StaticBoxSizer):
    # FIXME: probably want to do the setting verification in here
    __TITLE = "Settings"
    __NEW = "::New::"
    
    def __init__(self, parent, applicationMap, editable = True, 
                 callBack = None):
        self.__staticBox = wx.StaticBox(parent, wx.ID_ANY, 
                                        FSettingSizer.__TITLE)
        wx.StaticBoxSizer.__init__(self, self.__staticBox, wx.HORIZONTAL)
        self.__editable = editable
        self.__parent = parent
        self.__app = None
        self.__op = None
        self.__stepName = None
        self.__settingsDir = None
        self.__internalList = []
        self.__applicationMap = applicationMap
        self.__curHarddriveList = None
        self.__callBack = callBack
        
        comboSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__comboBox = wx.ComboBox(parent, wx.ID_ANY, "", 
                wx.DefaultPosition, wx.DefaultSize, [], 
                wx.CB_DROPDOWN | wx.CB_READONLY)
        comboSizer.Add(self.__comboBox, 1, wx.ALIGN_CENTER_VERTICAL)
        self.Add(comboSizer, 1, wx.EXPAND | wx.RIGHT, 5)
        self.__comboBox.Enable(editable)
        
        editId = wx.NewId()
        self.__editButton = wx.Button(parent, editId, "Add/Edit")
        parent.Bind(wx.EVT_BUTTON, self.__OnEdit, self.__editButton, editId)
        self.Add(self.__editButton, 0, wx.ALIGN_RIGHT | wx.LEFT, 5)
    
    def SetTitle(self, title = __TITLE):
        self.__staticBox.SetLabel(title)
    
    # FIXME: editable and enable should be the same thing
    def Enable(self, value):
        self.__comboBox.Enable(value)
        self.__editButton.Enable(value)
    
    def GetSetting(self):
        selection = self.__comboBox.GetSelection()
        if (selection == wx.NOT_FOUND): return None
        
        if (selection < len(self.__internalList)):
            return self.__internalList[selection]
        
        stringSelection = self.__comboBox.GetStringSelection()
        
        if (stringSelection == FSettingSizer.__NEW): return None
        
        return FSetting(stringSelection, self.__op, self.__app)
    
    def GetSettingName(self):
        """since it is only called in the new procedure dialog, never get <<>>"""
        stringSelection = self.__comboBox.GetStringSelection()
        if (stringSelection == ""):
            return None
        elif (stringSelection == FSettingSizer.__NEW): 
            return None
        else:
            return stringSelection
    
    # FIXME: should not need this once doing setting verification in here
    def GetOperation(self):
        return self.__op
    
    def UpdateList(self):
        newList = self.__GetList(self.__app, self.__op)
        if (newList != self.__curHarddriveList):
            for entry in newList:
                if (self.__curHarddriveList.count(entry) == 0):
                    self.__comboBox.AppendItems([entry])
            self.__curHarddriveList = newList
    
    def SetOperation(self, app, op, stepName, settingManager = None, 
            default = None):
        """default must be in the settingManager"""
        self.__staticBox.SetLabel(stepName)
        self.__app = app
        self.__op = op
        self.__stepName = stepName
        self.__internalList = []
        
        list = []
        if (settingManager != None):
            for setting in settingManager.GetSettingsGenerator(op, app):
                list.append("<<" + setting.GetShortName() + ">>")
                self.__internalList.append(setting)
        
        self.__curHarddriveList = self.__GetList(app, op)
        list = list + self.__curHarddriveList
        list.append(FSettingSizer.__NEW)
        
        self.__comboBox.Clear()
        self.__comboBox.AppendItems(list)
        
        selection = -1
        if (default != None):
            i = 0
            for setting in self.__internalList:
                if (setting == default):
                    selection = i
                    break
                i = i + 1
        
        if (selection == -1):
            if (default != None):
                defaultName = default.GetShortName()
                if (self.__IsValidSetting(app, op, defaultName)):
                    loadedSetting = FSetting(defaultName, op, app)
                    if (default == loadedSetting):
                        selection = self.__comboBox.FindString(defaultName)

        if (selection == -1):
            # The last resort: "Default" should ALWAYS exists.
            selection = self.__comboBox.FindString("Default")
            
        self.__comboBox.SetSelection(selection)
    
    def __IsValidSetting(self, app, op, name):
        settingsDir = os.path.join(os.getcwd(), SETTINGS_DIR, op, app)
        if (not os.path.isdir(settingsDir)): return False
        return os.path.isfile(
                os.path.join(settingsDir, name + "." + SETTING_EXT))
    
    def __GetList(self, app, op):
        applicationFolderName = os.path.join(os.getcwd(), SETTINGS_DIR, op, app)
        self.__settingsDir = applicationFolderName
        
        list = []
        
        # Make sure the settings folders exists.
        if not os.path.isdir(applicationFolderName):
            os.makedirs(applicationFolderName)
        
        # Read in the list of saved settings.
        for dirItem in os.listdir(applicationFolderName):
            splitted = dirItem.rsplit(".", 1)
            if ((len(splitted) != 2) or splitted[1] != SETTING_EXT): continue
            list.append(splitted[0])
            
        # Verify that we have a default setting.
        hasDefault = list.count("Default")
        if (hasDefault > 0):
            list.remove("Default") # We'll put it back, at the top, after sorting..
        else:
            # Automatically generate the default settings.
            app = self.__applicationMap[self.__app]
            settings = app.GetSettingsForOperation(self.__op)
            self.__AddSettings("Default", settings)
            
        list.sort()
        list.insert(0, "Default")
        return list
    
    def __OnEdit(self, e):
        if (self.__app == None): return
        if (self.__op == None): return
        if (self.__stepName == None): return
        
        # there is always a selection because there is FSettingSizer.__NEW
        selection = self.__comboBox.GetSelection()
        
        if (selection < len(self.__internalList)):
                settings = self.__internalList[selection]
                name = settings.GetShortName()
                settings = copy.deepcopy(settings.GetSettings())
        else:
            name = self.__comboBox.GetStringSelection()
            if (name == FSettingSizer.__NEW):
                app = self.__applicationMap[self.__app]
                settings = app.GetSettingsForOperation(self.__op)
                name = wx.EmptyString
            else:
                settings = FSetting(name, self.__op, self.__app).GetSettings()
            
        dialog = FChangeSettingsDialog(self.__parent, self.__stepName,
                settings, name, self.__editable)
        
        if (dialog.ShowModal() == wx.ID_OK):
            self.__AddSettings(dialog.title, dialog.GetSettings())

            if (not dialog.title.lower() in map(string.lower, self.__comboBox.GetStrings())):
                self.__comboBox.AppendItems([dialog.title])
                self.__curHarddriveList = self.__GetList(self.__app, self.__op)
                if (self.__callBack != None):
                    self.__callBack()
        
            newSelection = self.__comboBox.FindString(dialog.title)
            self.__comboBox.SetSelection(newSelection)        

        dialog.Destroy()
    
    def __AddSettings(self, name, settings):
        settingFilename = name + "." + SETTING_EXT
        settingFilename = os.path.join(self.__settingsDir, settingFilename)
        settingFile = open(settingFilename, "w")
        
        for setting in settings:
            settingFile.write(setting.GetPrettyName() + "\t"
                            + setting.GetCommand() + "\t"
                            + setting.GetValue() + "\n")
        
        settingFile.close()
        
        