# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from Core.Gui.Grid.FTextRenderer import *

class FEnvironmentRenderer(FTextRenderer):
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, isSelected)
        
        environment = grid.GetCellValue(row, col)
        
        if (environment == None): return
        
        textArray = []
        for key in environment.keys():
            textArray.append(key + environment[key])
        textArray.sort()
        
        self.RenderText(grid, attr, dc, rect, row, col, isSelected,
                        len(textArray), textArray)
    
    def AddContext(self, grid, row, col, menu, position):
        pass
    
    def Clicked(self, grid, row, col, position):
        pass
    