# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx

from Core.Gui.Grid.FExecutionGrid import *

class FExecutionDialog(wx.Dialog):
    def __init__(self, parent, title, testProcedure, tuples, animateAll, 
            feelingViewerPath, pythonPath, preferences):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, 
                style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | 
                        wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.CLIP_CHILDREN)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.__grid = FExecutionGrid(self, testProcedure, True, 
                feelingViewerPath, pythonPath)
        self.__grid.AppendExecutionContext()
        self.__grid.SetAnimateAll(animateAll)
        
        (mainWidth, mainHeight, mainBlessed, mainPrevious, mainDiff, 
                mainColumns) = preferences
        self.__grid.SetPreferences(mainWidth, mainHeight, mainBlessed,
                mainPrevious, mainDiff, mainColumns, False)
        
        i = 0
        for test, execution in tuples:
            self.__grid.AddExecution(i, test, execution)
            i = i + 1
        self.__grid.FullRefresh()
        
        sizer.Add(self.__grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Bind(wx.EVT_SIZE, self.__OnSize)
        self.__grid.AdjustScrollbars()
    
    def __OnSize(self, e):
        e.Skip()
        self.__grid.AdjustScrollbars()
    
