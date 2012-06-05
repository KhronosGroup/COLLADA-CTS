# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
    