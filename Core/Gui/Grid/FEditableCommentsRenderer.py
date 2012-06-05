# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

from Core.Gui.Grid.FCommentsRenderer import *
    
class FEditableCommentsRenderer(FCommentsRenderer):
    def __init__(self):
        FCommentsRenderer.__init__(self)
    
    def AddContext(self, grid, row, col, menu, position):
        menu.AppendSeparator()
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, "Edit Comments")
        font = menuItem.GetFont()
        font.SetWeight(wx.BOLD)
        menuItem.SetFont(font)
        menu.AppendItem(menuItem)
        
        def OnContext(e):
            self.__EditAnnotation(grid, row, col)
            
        grid.Bind(wx.EVT_MENU, OnContext, id = id)
    
    def Clicked(self, grid, row, col, position):
        self.__EditAnnotation(grid, row, col)
    
    def __EditAnnotation(self, grid, row, col):
        grid.SetGridCursor(row, col)
        grid.MakeCellVisible(row, col)
        grid.EnableCellEditControl()
    