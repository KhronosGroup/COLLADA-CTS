# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import time

from Core.Gui.Grid.FTextRenderer import *

class FTimeRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, isSelected)
        
        timeRan = grid.GetCellValue(row, col)
        
        if (timeRan == None): return
        
        self.RenderWrappedText(grid, attr, dc, rect, row, col, isSelected,
                               time.asctime(timeRan))
    
    def AddContext(self, grid, row, col, menu, position):
        pass
    
    def Clicked(self, grid, row, col, position):
        pass
    