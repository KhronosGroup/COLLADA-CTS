# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

from Core.Gui.Grid.FTextRenderer import *
from Core.Logic.FJudgement import *

# used with an FExecutionGrid
class FJudgementRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):

        # "judgement" is of type FJudgement.
        judgement = grid.GetCellValue(row, col)
        if (judgement == None):
            FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, isSelected)
            return

        # The result selects the background color
        result = judgement.GetResult()
        color = wx.Color(255, 230, 128)
        if (result == FJudgement.PASSED): color = wx.Color(64, 255, 64)
        elif (result == FJudgement.FAILED): color = wx.Color(255, 64, 64)
        elif (result == FJudgement.NO_SCRIPT): color = wx.Color(218, 218, 218)
        FTextRenderer.ColorDraw(self, dc, rect, color)

        # Render the judgement log.
        textArray = judgement.GetMessage().split("\n")
        self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                        len(textArray), textArray, None, None, None, 
                        wx.Color(0, 0, 0))
    
    def AddContext(self, grid, row, col, menu, position):
        
        # "judgement" is of type FJudgement.
        judgement = grid.GetCellValue(row, col)
        if (judgement == None): return
        
        # No context menu options for now.
    
    def Clicked(self, grid, row, col, position):
        # "judgement" is of type FJudgement.
        judgement = grid.GetCellValue(row, col)
        if (judgement == None): return

        # Show the message in a standard message box.
        dialog = wx.MessageDialog(grid, judgement.GetMessage(), grid.GetColLabelValue(col))
        dialog.ShowModal()
        # Not sure what to do with the statement below..
        # (self.__GetToggleFunc(judgement[1], grid))(None)
