# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx.grid

from Core.Gui.Grid.FTextRenderer import *
    
class FCommentsRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
        
        self.__stringRenderer = wx.grid.GridCellStringRenderer()
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, isSelected)
        
        self.RenderWrappedText(grid, attr, dc, rect, row, col, isSelected,
                        grid.GetCellValue(row, col)[0])
    
    def AddContext(self, grid, row, col, menu, position):
        pass
    
    def Clicked(self, grid, row, col, position):
        pass
    