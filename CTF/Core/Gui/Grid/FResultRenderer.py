# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from Core.Gui.Grid.FTextRenderer import *

# used with an FExecutionGrid
class FResultRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        result = grid.GetCellValue(row, col)
        
        if ((result == None) or (result[0] == None)):
            FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, 
                                   isSelected)
            return
        
        result = result[0]
        if (result.GetResult()):
            FTextRenderer.ColorDraw(self, dc, rect, wx.Color(0, 255, 0))
        else:
            FTextRenderer.ColorDraw(self, dc, rect, wx.Color(255, 0, 0))
        textArray = result.GetTextArray()
        
        self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                        len(textArray), textArray, None, None, None, 
                        wx.Color(0, 0, 0))
    
    def AddContext(self, grid, row, col, menu, position):
        result = grid.GetCellValue(row, col)
        if (result == None): return
        if (result[0] == None): return
        
        menu.AppendSeparator()
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, "Toggle Result")
        font = menuItem.GetFont()
        font.SetWeight(wx.BOLD)
        menuItem.SetFont(font)
        menu.AppendItem(menuItem)
        grid.Bind(wx.EVT_MENU, self.__GetToggleFunc(result[1], grid), id = id)
    
    def __GetToggleFunc(self, execution, grid):
        def Toggle(e):
            execution.ToggleResult()
            
            grid.RefreshTable()
        return Toggle
    
    def Clicked(self, grid, row, col, position):
        result = grid.GetCellValue(row, col)
        if (result == None): return
        if (result[0] == None): return
        (self.__GetToggleFunc(result[1], grid))(None)
    