# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
    