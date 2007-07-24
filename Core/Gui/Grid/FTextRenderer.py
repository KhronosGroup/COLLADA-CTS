# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from Core.Gui.Grid.FGridCellRenderer import *
from Core.Gui.Grid.FImageRenderArea import *
from Core.Gui.FImageType import *

class FTextRenderer(FGridCellRenderer):
    def __init__(self):
        FGridCellRenderer.__init__(self)
    
    def RenderWrappedText(self, grid, attr, dc, rect, row, col, isSelected,
                          text, textColor = None):
        """Simple rendering of wrapped text. Assume no new lines in text."""
        dc.SetFont(attr.GetFont())
        maxWidth = rect.width - 2 # 1 pixel padding on left and right
        
        textArray = []
        words = text.split()
        if (len(words) > 0):
            textEntry = words[0]
            for i in range(1, len(words)):
                tempEntry = textEntry + " " + words[i]
                width, height = dc.GetTextExtent(tempEntry)
                if (width > maxWidth):
                    textArray.append(textEntry)
                    textEntry = words[i]
                else:
                    textEntry = tempEntry
            textArray.append(textEntry)
        
        self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                        len(textArray), textArray, textColor = textColor)
    
    def RenderText(self, grid, attr, dc, rect, row, col, isSelected, 
                   arrayLength, textArray, renderedAreas = None, 
                   dataArray = None, extraArray = None, textColor = None):
        dc.DestroyClippingRegion()
        dc.SetClippingRect(rect)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        if (isSelected):
            dc.SetTextBackground(grid.GetSelectionBackground())
            if (textColor == None):
                dc.SetTextForeground(grid.GetSelectionForeground())
            else:
                dc.SetTextForeground(textColor)
        else:
            dc.SetTextBackground(attr.GetBackgroundColour())
            if (textColor == None):
                dc.SetTextForeground(attr.GetTextColour())
            else:
                dc.SetTextForeground(textColor)
        dc.SetFont(attr.GetFont())
        
        minX = rect.x + 1
        minY = rect.y + 1
        maxY = rect.y + rect.height
        for i in range(0, arrayLength):
            textEntry = textArray[i]
            width, height = dc.GetTextExtent(textEntry)
            if (width > rect.width - 2):
                width = rect.width - 1
            if (minY + height > maxY):
                height = rect.height - minY
                if (height <= 0):
                    break
            
            if (grid.IsRectVisible(wx.Rect(minX, minY, width, height))):
                if (renderedAreas != None):
                    if (extraArray == None):
                        extra = None
                    else:
                        extra = extraArray[i]
                    renderedAreas[(row, col)].append(FImageRenderArea(
                            minX, minY, width, height, dataArray[i], extra))
                
                dc.DrawText(textEntry, minX, minY)
            
            minY = minY + height + 1
        
        dc.DestroyClippingRegion()
        
        return minY
