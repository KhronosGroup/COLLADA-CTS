# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx.grid
        
class FGridCellRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self):
        wx.grid.PyGridCellRenderer.__init__(self)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        if (isSelected):
            color = grid.GetSelectionBackground()
        else:
            color = attr.GetBackgroundColour()
        
        self.ColorDraw(dc, rect, color)
    
    def ColorDraw(self, dc, rect, color):
        dc.SetBackgroundMode(wx.SOLID)
        
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.SetPen(wx.Pen(color, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)
    
    def AddContext(self, grid, row, col, menu, position):
        raise NotImplementedError, "FGridCellRenderer.AddContext()"
        
    def Clicked(self, grid, row, col, position):
        raise NotImplementedError, "FGridCellRenderer.Clicked()"
