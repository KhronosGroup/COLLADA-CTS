# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

from Core.Gui.Grid.FTextRenderer import *

# used with an FExecutionGrid
class FResultRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        
        # Retrieve the result object.
        if (value != None) and (value[0] != None):
            execution = value[0]
            result = execution.GetResult()
        else: result = None

        if (result != None):
            # Render a green/red cell with the result text.
            result = execution.GetResult()
            
            if (result != None) and (result.GetResult()): cellColor = wx.Color(0, 255, 0)
            else: cellColor = wx.Color(255, 0, 0)
            FTextRenderer.ColorDraw(self, dc, rect, cellColor)
            textArray = result.GetTextArray()
            
            self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                            len(textArray), textArray, None, None, None, 
                            wx.Color(0, 0, 0))
        else:
            # Render a plain white cell
            FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, isSelected)
    
    def AddContext(self, grid, row, col, menu, position):
        value = grid.GetCellValue(row, col)
        if (value != None) and (value[0] != None):
            execution = value[0]
            result = execution.GetResult()
        else: result = None
        if (result == None): return
        
        # Add a result toggle menu item
        menu.AppendSeparator()
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, "Toggle Result")
        font = menuItem.GetFont()
        font.SetWeight(wx.BOLD)
        menuItem.SetFont(font)
        menu.AppendItem(menuItem)
        grid.Bind(wx.EVT_MENU, self.__GetToggleFunc(grid, value), id = id)
    
    def __GetToggleFunc(self, grid, value): # value: (execution, test, id)
        def Toggle(e):
            # Toggle the execution results.
            grid.PartialRefreshRemove(value[1], value[2])
            value[0].ToggleResult()
            grid.PartialRefreshAdd(value[1], value[0], value[2])
            grid.PartialRefreshDone()
        return Toggle
    
    def Clicked(self, grid, row, col, position):
        value = grid.GetCellValue(row, col)
        if (value != None) and (value[0] != None):
            execution = value[0]
            result = execution.GetResult()
        else: result = None
        if (result == None): return

        # Toggle the results.
        (self.__GetToggleFunc(grid, value))(None)
    