# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
    
