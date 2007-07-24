# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path

import Core.Common.FUtils as FUtils
from Core.Gui.Grid.FTextRenderer import *
from Core.Gui.Dialog.FCompareSetupDialog import *
from Core.Gui.FImageType import *
    
class FLogRenderer(FTextRenderer):
    def __init__(self):
        FTextRenderer.__init__(self)
        
        self.__diffCommand = ""
        
        self.__renderedAreas = {} # {(row, col) : [FImageRenderArea]}
    
    def SetDiffCommand(self, diffCommand):
        self.__diffCommand = diffCommand
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        FTextRenderer.Draw(self, grid, attr, dc, rect, row, col, 
                               isSelected)
        
        cellValue = grid.GetCellValue(row, col) 
        if (cellValue == None):
            return
        
        textArray = []
        dataArray = []
        extraArray = []
        for logEntry in cellValue:
            logFilename = logEntry[0]
            if (logFilename == None): continue
            
            textArray.append(os.path.basename(logFilename))
            dataArray.append(logFilename)
            extraArray.append(FImageType.LOG)
        
        self.__renderedAreas[(row, col)] = []
        self.RenderText(grid, attr, dc, rect, row, col, isSelected, 
                len(textArray), textArray, self.__renderedAreas, dataArray,
                extraArray)
    
    def AddContext(self, grid, row, col, menu, position):
        cellValue = grid.GetCellValue(row, col) 
        if (cellValue == None): return
        
        menu.AppendSeparator()
        
        clickedFilename = self.__GetClickedFilename(grid, row, col, position)
        
        for logEntry in cellValue:
            logFilename = logEntry[0]
            if (logFilename == None): continue # validation
            id = wx.NewId()
            menuItem = wx.MenuItem(menu, id, 
                    "Open " + os.path.basename(logFilename))
            if (logFilename == clickedFilename):
                font = menuItem.GetFont()
                font.SetWeight(wx.BOLD)
                menuItem.SetFont(font)
            menu.AppendItem(menuItem)
            grid.Bind(wx.EVT_MENU, self.__GetOpenFunc(logFilename), id = id)
        for logEntry in cellValue:
            logFilename = logEntry[0]
            if (logFilename == None): continue # validation
            id = wx.NewId()
            menuItem = wx.MenuItem(menu, id, 
                    "Compare " + os.path.basename(logFilename))
            menu.AppendItem(menuItem)
            grid.Bind(wx.EVT_MENU, self.__GetCompareFunc(logEntry, grid), 
                      id = id)
    
    def __GetOpenFunc(self, log):
        def Open(e):
            # XXX: this is windows only
            os.startfile("\"" + log  + "\"")
        return Open
    
    def __GetCompareFunc(self, logEntry, grid):
        # almost same compare function as in FImageRenderer
        def Compare(e):
            if (self.__diffCommand == ""):
                FUtils.ShowWarning(grid.GetParent(), 
                                   "No diff program selected")
                return
            
            dialog = FCompareSetupDialog(grid, FCompareSetupDialog.LOG, 
                    logEntry[3], logEntry[2], logEntry[1])
            if (dialog.ShowModal() == wx.ID_OK):
                command = self.__diffCommand.replace("%base", 
                        "\"" + os.path.abspath(logEntry[0]) + "\"")
                command = command.replace("%mine", 
                        "\"" + os.path.abspath(dialog.GetPath()) + "\"")
                os.system("\"" + command + "\"")
        return Compare
    
    def __GetClickedFilename(self, grid, row, col, position):
        if (not self.__renderedAreas.has_key((row, col))): return None
        
        position = grid.CalcUnscrolledPosition(position)
        for renderedArea in self.__renderedAreas[(row, col)]:
            rect = renderedArea.GetRect()
            if (rect.Inside(position)):
                return renderedArea.GetFilename()
    
    def Clicked(self, grid, row, col, position):
        filename = self.__GetClickedFilename(grid, row, col, position)
        if (filename != None):
            (self.__GetOpenFunc(filename))(None)
    