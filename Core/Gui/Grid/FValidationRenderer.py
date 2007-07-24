# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os

from Core.Gui.Grid.FTextRenderer import *
from Core.Gui.FImageType import *
from Core.Common.FConstants import *

class FValidationRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
        self.__renderedAreas = {} # {(row, col) : [outputFilename]}
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        validationData = grid.GetCellValue(row, col) 
        
        if ((validationData == None) or (validationData[2] == None)):
            FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, 
                                   isSelected)
            return
        
        outputFilename = validationData[2]
        errors = validationData[0]
        warnings = validationData[1]
        
        textArray = []
        dataArray = []
        extraArray = []
        if (errors > 0):
            FTextRenderer.ColorDraw(self, dc, rect, wx.Color(255, 0, 0))
            textArray.append("Failed")
        elif (warnings > 0):
            FTextRenderer.ColorDraw(self, dc, rect, wx.Color(255, 255, 0))
            textArray.append("Passed")
        else:
            FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, 
                                   isSelected)
            textArray.append("Passed")
        dataArray.append(outputFilename)
        extraArray.append(FImageType.VALIDATION)
        
        textArray.append(str(warnings) + " warnings")
        dataArray.append(outputFilename)
        extraArray.append(FImageType.VALIDATION)
        textArray.append(str(errors) + " errors")
        dataArray.append(outputFilename)
        extraArray.append(FImageType.VALIDATION)
        
        self.__renderedAreas[(row, col)] = []
        self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                len(textArray), textArray, self.__renderedAreas, dataArray,
                extraArray, wx.Color(0, 0, 0))
    
    def __GetOpenFunc(self, file):
        # FApplications return a list, which doesn't work for a single log       
        if VALIDATE in OPS_NEEDING_APP:
            file2 = file[0]
        else:
            file2 = file
        
        def Open(e):
            # XXX: this is windows only
            os.startfile("\"" + file2  + "\"")
        return Open
    
    def __GetRenderedArea(self, grid, row, col, position):
        position = grid.CalcUnscrolledPosition(position)
        for renderedArea in self.__renderedAreas[(row, col)]:
            rect = renderedArea.GetRect()
            if (rect.Inside(position)):
                return renderedArea
    
    def AddContext(self, grid, row, col, menu, position):
        validationData = grid.GetCellValue(row, col) 
        if ((validationData == None) or (validationData[2] == None)): return
        
        menu.AppendSeparator()
        
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, "View Report")
        font = menuItem.GetFont()
        font.SetWeight(wx.BOLD)
        menuItem.SetFont(font)
        menu.AppendItem(menuItem)
        grid.Bind(wx.EVT_MENU, self.__GetOpenFunc(validationData[2]), id = id)
    
    def Clicked(self, grid, row, col, position):
        if (not self.__renderedAreas.has_key((row, col))): return
        
        renderedArea = self.__GetRenderedArea(grid, row, col, position)
        if (renderedArea != None):
            filename = renderedArea.GetFilename()
            (self.__GetOpenFunc(filename))(None)
    