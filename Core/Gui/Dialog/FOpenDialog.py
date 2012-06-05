# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import os.path
import wx

from Core.Common.FConstants import *

class FOpenDialog(wx.Dialog):
    __DIALOG_TITLE = "Open Test Procedure"
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, FOpenDialog.__DIALOG_TITLE)
        
        self.__ID_OK = wx.NewId()
        self.__ID_CANCEL = wx.NewId()
        self.__ID_PROCEDURE = wx.NewId()
        self.__ID_PROCEDURE = wx.NewId()
        
        self.__commentsCtrl = None
        self.__proceduresCtrl = None
        
        outterSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(outterSizer)
        
        procedureSizer = self.__GetProcedureSizer()
        commentSizer = self.__GetCommentsSizer()
        bottomSizer = self.__GetBottomSizer()
        
        outterSizer.Add(procedureSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(commentSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(bottomSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.Fit()
    
    def GetPath(self):
        selection = self.__proceduresCtrl.GetStringSelection()
        if (selection == ""): return None
        
        return os.path.abspath(os.path.join(
                RUNS_FOLDER, self.__proceduresCtrl.GetStringSelection(), 
                TEST_PROCEDURE_FILENAME))
    
    def __OnOk(self, e):
        if (self.__proceduresCtrl.GetStringSelection() == ""): return
        
        if (self.IsModal()):
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Show(False)
    
    def __OnCancel(self, e):
        if (self.IsModal()):
            self.EndModal(wx.ID_CANCEL)
        else:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Show(False)
    
    def __OnClick(self, e):
        file = os.path.join(RUNS_FOLDER, 
                self.__proceduresCtrl.GetStringSelection(), 
                TEST_PROCEDURE_COMMENTS)
        comments = ""
        if (os.path.isfile(file)):
            f = open(file)
            line = f.readline()
            while (line):
                comments = comments + line
                line = f.readline()
            f.close()
        
        self.__commentsCtrl.SetValue(comments)
    
    def __OnDClick(self, e):
        self.__OnOk(e)
    
    def __GetProcedureSizer(self):
        """Retuns the Sizer used to display test procedures."""
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Available Test Procedures")
        sizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)
        
        choices = []
        if (os.path.isdir(RUNS_FOLDER)):
            for entry in os.listdir(RUNS_FOLDER):
                if (os.path.isfile(os.path.join(
                        RUNS_FOLDER, entry, TEST_PROCEDURE_FILENAME))):
                    choices.append(entry)
        
        self.__proceduresCtrl = wx.ListBox(self, self.__ID_PROCEDURE, 
                size = wx.Size(300, 140), choices = choices,
                style = wx.LB_SINGLE | wx.LB_SORT)
        self.Bind(wx.EVT_LISTBOX, self.__OnClick, self.__proceduresCtrl, 
                  self.__ID_PROCEDURE)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.__OnDClick, 
                  self.__proceduresCtrl, self.__ID_PROCEDURE)
        
        sizer.Add(self.__proceduresCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        return sizer
    
    def __GetCommentsSizer(self):
        """Returns the Sizer used for comments."""
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Test Procedure Comments")
        sizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)
        
        self.__commentsCtrl = wx.TextCtrl(self, wx.ID_ANY, "", 
                size = wx.Size(300, 60), 
                style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.__commentsCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        sizer.Add(self.__commentsCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        return sizer
    
    def __GetBottomSizer(self):
        """Returns the Sizer used to confirm or cancel this dialog."""
        okButton = wx.Button(self, self.__ID_OK, "Ok")
        wx.EVT_BUTTON(self, self.__ID_OK, self.__OnOk)
        cancelButton = wx.Button(self, self.__ID_CANCEL, "Cancel")
        wx.EVT_BUTTON(self, self.__ID_CANCEL, self.__OnCancel)
        
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(okButton, 0, wx.ALIGN_LEFT)
        bottomSizer.Add(cancelButton, 0, wx.ALIGN_RIGHT)
        
        return bottomSizer

# Used to start up this dialog without the entire application.
##class MainFrame(wx.MDIParentFrame):
##    def __init__(self, parent, id, title):
##        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
##                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
##                
##        dialog = FOpenDialog(self)
##        if (dialog.ShowModal() == wx.ID_OK):
##            print dialog.GetPath()
##            print "ok"
##        else:
##            print "cancelled"
##        
##app = wx.PySimpleApp()
##frame = MainFrame(None,-1, "Test")
##app.MainLoop()
