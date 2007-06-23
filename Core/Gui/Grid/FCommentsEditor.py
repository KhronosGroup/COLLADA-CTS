# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx.grid
    
class FCommentsEditor(wx.grid.PyGridCellEditor):
    def __init__(self):
        wx.grid.PyGridCellEditor.__init__(self)
        self.__textCtrl = None
        self.__startValue = ""
    
    def Create(self, parent, id, evtHandler):
        """Must Override."""
        self.__textCtrl = wx.TextCtrl(parent, id, "", style = wx.TE_MULTILINE)
        self.SetControl(self.__textCtrl)
        if (evtHandler):
            self.__textCtrl.PushEventHandler(evtHandler)
    
    def SetSize(self, rect):
        self.__textCtrl.SetDimensions(rect.x, rect.y, rect.width + 2,
                rect.height + 2, wx.SIZE_ALLOW_MINUS_ONE)
    
    def Show(self, show, attr):
        self.base_Show(show, attr)
    
    def PaintBackground(self, rect, attr):
        # override to reduce flicker
        pass
    
    def BeginEdit(self, row, col, grid):
        """Must Override."""
        self.__startValue = grid.GetCellValue(row, col)[0]
        self.__textCtrl.SetValue(self.__startValue)
        self.__textCtrl.SetInsertionPointEnd()
        self.__textCtrl.SetFocus()
        self.__textCtrl.SetSelection(0, self.__textCtrl.GetLastPosition())
    
    def EndEdit(self, row, col, grid):
        """Must Override."""
        newValue = self.__textCtrl.GetValue()
        if (self.__startValue != newValue):
            cellValue = grid.GetCellValue(row, col)
            test = cellValue[1]
            execution = cellValue[2]
            if (execution == None):
                test.SetDefaultComments(newValue)
            else:
                execution.SetComments(newValue)
            
            grid.SetCellValue(row, col, (newValue, cellValue[1], cellValue[2]))
            return True
        return False
    
    def Reset(self):
        """Must Override."""
        self.__textCtrl.SetValue(self.__startValue)
        self.__textCtrl.SetInsertionPointEnd()
    
    def IsAcceptedKey(self, evt):
        # don't allow any keys to start editor
        return False
    
    def Clone(self):
        """Must Override."""
        return FCommentsEditor()
    