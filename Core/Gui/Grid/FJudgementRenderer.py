# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
