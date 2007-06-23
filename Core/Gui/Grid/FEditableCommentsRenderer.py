# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from Core.Gui.Grid.FCommentsRenderer import *
    
class FEditableCommentsRenderer(FCommentsRenderer):
    def __init__(self):
        FCommentsRenderer.__init__(self)
    
    def AddContext(self, grid, row, col, menu, position):
        menu.AppendSeparator()
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, "Edit Comments")
        font = menuItem.GetFont()
        font.SetWeight(wx.BOLD)
        menuItem.SetFont(font)
        menu.AppendItem(menuItem)
        
        def OnContext(e):
            self.__EditAnnotation(grid, row, col)
            
        grid.Bind(wx.EVT_MENU, OnContext, id = id)
    
    def Clicked(self, grid, row, col, position):
        self.__EditAnnotation(grid, row, col)
    
    def __EditAnnotation(self, grid, row, col):
        grid.SetGridCursor(row, col)
        grid.MakeCellVisible(row, col)
        grid.EnableCellEditControl()
    