# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx
import wx.grid

from Core.Gui.Grid.FGridCellRenderer import *
from Core.Gui.Grid.FTable import *

class FGrid(wx.grid.Grid):
    __SCROLL_PAGE_DOWN = 0
    __SCROLL_PAGE_UP = 1
    __SCROLL_DOWN = 2
    __SCROLL_UP = 3
    __SCROLL_LEFT = 4
    __SCROLL_RIGHT = 5
    __SCROLL_ABS_TOP = 6
    __SCROLL_ABS_BOTTOM = 7
    __SCROLL_ABS_LEFT = 8
    __SCROLL_ABS_RIGHT = 9
    
    def __init__(self, gridParent):
        wx.grid.Grid.__init__(self, gridParent, wx.ID_ANY)
        self.SetRowLabelSize(0)
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)
        self.SetDefaultCellOverflow(False)
        self.EnableDragCell(True) # to get the dragging events
        
        self.__gridParent = gridParent
        self.__startRow = -1
        self.__table = FTable(self)
        self.__context = []
        
        self.SetTable(self.__table, True)
        
        # to make the scrollbars refresh properly
        self.Bind(wx.EVT_SIZE, self.__OnSize)
        self.__gridParent.Bind(wx.EVT_SIZE, self.__OnFrameSize)
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.__OnLabelClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.__OnCellClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__OnCellDClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.__OnCellRightClick)
        self.Bind(wx.grid.EVT_GRID_COL_SIZE, self.__OnColSize)
        self.Bind(wx.grid.EVT_GRID_CELL_BEGIN_DRAG, self.__OnCellDrag)
        self.Bind(wx.EVT_KEY_UP, self.__OnKeyUp)
        self.Bind(wx.EVT_KEY_DOWN, self.__OnKeyDown)
        self.GetGridColLabelWindow().Bind(wx.EVT_PAINT, self.__OnLabelPaint)
        
        newId = wx.NewId()
        self.__timer = wx.Timer(self, newId)
        self.Bind(wx.EVT_TIMER, self.__OnUpdateAnimation, self.__timer, newId)
        self.__timer.Start(70, False)
        self.__animations = {}
    
    def AppendContext(self, message, function):
        self.__context.append((message, function))
    
    def AppendColumn(self, key, colName, size, renderer = None, editor = None):
        """AppendColumn(key, colName, size[, renderer[, editor]]) -> None
        
        Appends a column to the end of the grid. key is the key to reference
        the column by. renderer and editors will be used for all rows in this
        column. Note that this appends a column to the grid, but it does not
        actually show it because calling SetColumnOrder with the specified
        key.
        
        """
        self.__table.AppendColumn(key, colName, size, renderer, editor)
    
    def AppendRow(self, key):
        self.__table.AppendRow(key)
        msg = wx.grid.GridTableMessage(self.__table, 
                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
        self.ProcessTableMessage(msg)
    
    def DeleteRow(self, key):
        self.__table.DeleteRow(key)
        msg = wx.grid.GridTableMessage(self.__table, 
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 
                self.__table.GetNumberRows(), 1)
        self.ProcessTableMessage(msg)
    
    def SetColumnOrder(self, columns):
        """SetColumnOrder(columns) -> None
        
        Sets the visible columns and their ordering. columns is a list of keys
        to be shown in that order. The keys correspond to those added using 
        AppendColumn. A KeyError is raised if invalid key.
        
        """
        oldColsCount = self.__table.GetNumberCols()
        self.__table.SetColumnOrder(columns)
        newColsCount = self.__table.GetNumberCols()
        
        self.BeginBatch()
        
        if (oldColsCount > newColsCount): # deleted
            msg = wx.grid.GridTableMessage(self.__table, 
                    wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, newColsCount, 
                    oldColsCount - newColsCount)
            self.ProcessTableMessage(msg)
        elif (oldColsCount < newColsCount): # added
            msg = wx.grid.GridTableMessage(self.__table, 
                    wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED, 
                    newColsCount - oldColsCount)
            self.ProcessTableMessage(msg)
        
        for i in range(newColsCount):
            wx.grid.Grid.SetColSize(self, i, 
                    self.__table.GetColSize(self.__table.GetColKey(i)))
        
        msg = wx.grid.GridTableMessage(self.__table, 
                wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.ProcessTableMessage(msg)
        
        self.EndBatch()
    
    def InsertData(self, rKey, cKey, data):
        self.__table.InsertData(rKey, cKey, data)
        
    def ClearRow(self, rKey):
        for col in range(self.__table.GetNumberCols()):
            cKey = self.__table.GetColKey(col)
            self.__table.ClearData(rKey, cKey)

    def SetColSize(self, cKey, width):
        self.__table.SetColSize(cKey, width)
        
        position = self.__table.GetCol(cKey)
        if (position != None): # is visible
            wx.grid.Grid.SetColSize(self, position, width)

    def GetCellValue(self, row, col):
        return self.__table.GetValue(row, col)
    
    def SetCellValue(self, row, col, value):
        self.__table.SetValue(row, col, value)
        
    def IsRowSelected(self, row):
        return self.IsInSelection(row, 1)
    
    def SortColumn(self, col, ascending):
        if (self.__startRow != -1):
            startRowKey = self.__table.GetRowKey(self.__startRow)
            
        selectedKeys = self.GetSelectedKeys()
        
        self.__table.SortColumn(col, ascending)
        
        if (self.__startRow != -1):
            self.__startRow = self.__table.GetRow(startRowKey)
        
        wx.grid.Grid.ClearSelection(self)
        for key in selectedKeys:
            self.SelectRow(self.__table.GetRow(key), True)
        
        msg = wx.grid.GridTableMessage(self.__table, 
                wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.ProcessTableMessage(msg)
        self.ForceRefresh()
    
    def GetSelectedKeys(self):
        selectedKeys = []
        for row in self.GetSelectedRows():
            selectedKeys.append(self.__table.GetRowKey(row))
        
        return selectedKeys
    
    #inspired from http://wiki.wxpython.org/index.cgi/DrawingOnGridColumnLabel
    def __OnLabelPaint(self, e):
        labelsWindow = self.GetGridColLabelWindow()
        dc = wx.PaintDC(labelsWindow)
        clientRect = labelsWindow.GetClientRect()
        font = dc.GetFont()
        
        # For each column, draw it's rectangle, it's column name,
        # and it's sort indicator, if appropriate:
        #totColSize = 0
        # Thanks Roger Binns
        totColSize = -self.GetViewStart()[0]*self.GetScrollPixelsPerUnit()[0] 
        for col in range(self.__table.GetNumberCols()):
            # Render the column header
            dc.SetBrush(wx.Brush("WHEAT", wx.TRANSPARENT))
            dc.SetTextForeground(wx.BLACK)
            colSize = self.GetColSize(col)
            rect = (totColSize,0,colSize,self.GetColLabelSize())
            
            dc.DestroyClippingRegion()
            dc.DrawRectangle(rect[0] - (col<>0 and 1 or 0), rect[1],
                             rect[2] + (col<>0 and 1 or 0), rect[3])
            totColSize += colSize
            
            title = self.__table.GetColLabelValue(col)
            
            if self.__table.IsSortedColumn(col):
                # For selected columns: bold the header and
                # render an arrow-head for the sort direction.
                font.SetWeight(wx.BOLD)
                left = rect[0] + rect[2]/2 - 3
                top = rect[1] + rect[3] - 8
                
                dc.SetBrush(wx.Brush("WHEAT", wx.SOLID))
                if (not self.__table.GetSortingDirection()):
                    dc.DrawPolygon([(left,top), (left+6,top), (left+3,top+4)])
                else:
                    dc.DrawPolygon(
                            [(left+3,top), (left+6, top+4), (left, top+4)])
            else:
                font.SetWeight(wx.NORMAL)
            
            # Prepare the DC and fit the label to the allowable size.
            if len(title) > 0:
                dc.SetFont(font)
                paddedRect = (rect[0] + 2, rect[1], rect[2] - 4, rect[3] - 4) # Pad for a nicer UI.
                dc.SetClippingRect(paddedRect)
                allowableTitle = title;
                (width, height) = dc.GetTextExtent(allowableTitle)
                if width > paddedRect[2]:
                    alignment = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL

                    # Title is too long. Shorten and use '..' as appropriate.
                    currentLength = len(title)
                    while width > paddedRect[2] and currentLength > 0:
                        currentLength = currentLength / 2
                        allowableTitle = title[:currentLength] + ".."
                        (width, height) = dc.GetTextExtent(allowableTitle)

                    # Now test using re-added characters.
                    testString = allowableTitle
                    while width < paddedRect[2]:
                        allowableTitle = testString
                        currentLength = currentLength + 1
                        testString = title[:currentLength] + ".."
                        (width, height) = dc.GetTextExtent(allowableTitle)
                else:
                    alignment = wx.ALIGN_CENTER
                
                # Draw the column header label.
                dc.DrawLabel(allowableTitle, paddedRect, alignment)
    
    def __OnColSize(self, e):
        col = e.GetRowOrCol()
        newSize = self.GetColSize(col)
        self.__table.SetColSize(self.__table.GetColKey(col), newSize)
    
    def __OnCellClick(self, e):
        selectedRow = e.GetRow()
        if (e.ControlDown()):
            if (self.IsRowSelected(selectedRow)):
                self.DeselectRow(selectedRow)
            else:
                self.SelectRow(selectedRow, True)
                
            self.__startRow = selectedRow
            return
        
        if (e.ShiftDown()):
            if (self.__startRow == -1):
                self.SelectRow(selectedRow, False)
                self.__startRow = selectedRow
            else:
                wx.grid.Grid.ClearSelection(self)
                for rowCount in range(min(self.__startRow, selectedRow),
                                      max(self.__startRow, selectedRow) + 1):
                    self.SelectRow(rowCount, True)
                    
            return
        
        self.SelectRow(selectedRow, False)
        self.__startRow = selectedRow
    
    def SelectAll(self):
        # wx.grid.Grid.SelectAll does not work with GetSelectedRows
        for row in range(self.GetNumberRows()):
            self.SelectRow(row, True)
    
    def ClearSelection(self):
        wx.grid.Grid.ClearSelection(self)
        self.__startRow = -1
    
    def __OnCellDrag(self, e):
        e.Veto()
    
    def __OnCellDClick(self, e):
        selectedRow = e.GetRow()
        selectedCol = e.GetCol()
        
        cellRenderer = self.GetCellRenderer(selectedRow, selectedCol)
        if (isinstance(cellRenderer, FGridCellRenderer)):
            position = e.GetPosition()
            position.y = position.y - self.GetColLabelSize()
            cellRenderer.Clicked(self, selectedRow, selectedCol, position)
    
    def __OnCellRightClick(self, e):
        row = e.GetRow()
        if (not self.IsRowSelected(row)):
            self.SelectRow(row)
        
        self.__startRow = row
        
        menu = wx.Menu()
        for context in self.__context:
            if (context[0] == None):
                menu.AppendSeparator()
                continue
            
            id = wx.NewId()
            menu.Append(id, context[0])
            self.Bind(wx.EVT_MENU, context[1], id = id)
        
        cellRenderer = self.GetCellRenderer(row, e.GetCol())
        if (isinstance(cellRenderer, FGridCellRenderer)):
            position = e.GetPosition()
            position.y = position.y - self.GetColLabelSize()
            cellRenderer.AddContext(self, row, e.GetCol(), menu, position)
        
        self.PopupMenu(menu, e.GetPosition())
        menu.Destroy()
        return

    def __OnLabelClick(self, e):
        column = e.GetCol()
        if (self.__table.IsSortedColumn(column) and 
                self.__table.GetSortingDirection()):
            self.SortColumn(column, False)
        else:
            self.SortColumn(column,  True)
        
    def __OnSize(self, e):
        e.Skip()
        self.__gridParent.SendSizeEvent()
    
    def __OnFrameSize(self, e):
        e.Skip()
        try:
            self.AdjustScrollbars()
        except Exception, e:
            pass   # when grid is being destroyed, it also generates event
    
    def __OnKeyDown(self, e):
        key = e.GetKeyCode()
        if ((key == wx.WXK_UP) or (key == wx.WXK_NUMPAD_UP)):
            self.__Scroll(FGrid.__SCROLL_UP)
        elif ((key == wx.WXK_DOWN) or (key == wx.WXK_NUMPAD_DOWN)):
            self.__Scroll(FGrid.__SCROLL_DOWN)
        elif ((key == wx.WXK_LEFT) or (key == wx.WXK_NUMPAD_LEFT)):
            self.__Scroll(FGrid.__SCROLL_LEFT)
        elif ((key == wx.WXK_RIGHT) or (key == wx.WXK_NUMPAD_RIGHT)):
            self.__Scroll(FGrid.__SCROLL_RIGHT)
        elif ((key == wx.WXK_PAGEUP) or (key == wx.WXK_PRIOR)):
            self.__Scroll(FGrid.__SCROLL_PAGE_UP)
        elif ((key == wx.WXK_PAGEDOWN) or (key == wx.WXK_NEXT)):
            self.__Scroll(FGrid.__SCROLL_PAGE_DOWN)
        elif ((key == wx.WXK_RETURN) or (key == wx.WXK_NUMPAD_ENTER)):
            if (e.ControlDown()):
                e.Skip()
            else:
                # block moving the grid cursor down
                self.DisableCellEditControl()
        elif (key == wx.WXK_TAB):
            # block it from tabbing to next cell
            return 
        elif (key == wx.WXK_HOME):
            if (e.ControlDown()):
                self.__Scroll(FGrid.__SCROLL_ABS_TOP)
            else:
                self.__Scroll(FGrid.__SCROLL_ABS_LEFT)
        elif (key == wx.WXK_END):
            if (e.ControlDown()):
                self.__Scroll(FGrid.__SCROLL_ABS_BOTTOM)
            else:
                self.__Scroll(FGrid.__SCROLL_ABS_RIGHT)
        elif (key == wx.WXK_SPACE):
            # block it from skipping onto next cell or toggling selection
            return 
        elif (key == wx.WXK_F2):
            # block enabling edit control with the grid cursor
            pass
        else:
            e.Skip()
    
    # modified from scrolwin.cpp in wxWidgets
    def __Scroll(self, type):
        xViewStart, yViewStart = self.GetViewStart()
        xClientSize, yClientSize = self.GetClientSizeTuple()
        xVirtualSize, yVirtualSize = self.GetGridWindow().GetVirtualSize()
        xScrollPixels, yScrollPixels = self.GetScrollPixelsPerUnit()
        
        xScrollOld = self.GetScrollPos(wx.HORIZONTAL)
        yScrollOld = self.GetScrollPos(wx.VERTICAL)
        
        if (xScrollPixels == 0):
            xClientSize = 0
            xVirtualSize = -1
        else:
            xClientSize = xClientSize / xScrollPixels
            xVirtualSize = xVirtualSize / xScrollPixels
        if (yScrollPixels == 0):
            yClientSize = 0
            yVirtualSize = -1
        else:
            yClientSize = yClientSize / yScrollPixels
            yVirtualSize = yVirtualSize / yScrollPixels
        
        if (type == FGrid.__SCROLL_PAGE_UP):
            yDest = yViewStart - (5 * yClientSize / 6)
            if (yDest == -1):
                self.Scroll(-1, 0)
            else:
                self.Scroll(-1, yDest)
        elif (type == FGrid.__SCROLL_PAGE_DOWN):
            self.Scroll(-1, yViewStart + (5 * yClientSize / 6))
        elif (type == FGrid.__SCROLL_UP):
            self.Scroll(-1, yViewStart - 1)
        elif (type == FGrid.__SCROLL_DOWN):
            self.Scroll(-1, yViewStart + 1)
        elif (type == FGrid.__SCROLL_LEFT):
            self.Scroll(xViewStart - 1, -1)
        elif (type == FGrid.__SCROLL_RIGHT):
            self.Scroll(xViewStart + 1, -1)
        elif (type == FGrid.__SCROLL_ABS_TOP):
            self.Scroll(-1, 0)
        elif (type == FGrid.__SCROLL_ABS_BOTTOM):
            self.Scroll(-1, yVirtualSize - yClientSize)
        elif (type == FGrid.__SCROLL_ABS_LEFT):
            self.Scroll(0, -1)
        elif (type == FGrid.__SCROLL_ABS_RIGHT):
            self.Scroll(xVirtualSize - xClientSize, -1)
        
        xScrollNew = self.GetScrollPos(wx.HORIZONTAL)
        if (xScrollOld != xScrollNew):
            e = wx.ScrollWinEvent(wx.wxEVT_SCROLLWIN_THUMBTRACK, xScrollNew,
                                  wx.HORIZONTAL)
            e.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(e)
        
        yScrollNew = self.GetScrollPos(wx.VERTICAL)
        if (yScrollOld != yScrollNew):
            e = wx.ScrollWinEvent(wx.wxEVT_SCROLLWIN_THUMBTRACK, yScrollNew,
                                  wx.VERTICAL)
            e.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(e)
    
    def __OnKeyUp(self, e):
        # override wxGrid updating its internal selection
        if (e.GetKeyCode() != wx.WXK_SHIFT):
            e.Skip()
    
    def IsRectVisible(self, rect):
        viewX, viewY =  self.GetViewStart()
        scrollX, scrollY = self.GetScrollPixelsPerUnit()
        sizeX, sizeY = self.GetClientSizeTuple()
        clientRect = wx.Rect(viewX * scrollX, viewY * scrollY, sizeX, sizeY)
        
        return rect.Intersects(clientRect)
    
    def AddAnimation(self, row, col, id, animation):
        self.__animations[(row, col, id)] = animation
        self.__OnUpdateAnimation(None)
    
    def DeleteAnimation(self, row, col, id):
        # may be deleted by __OnUpdateAnimation when animation left visibility
        if (self.__animations.has_key((row, col, id))):
            self.__animations.pop((row, col, id))
    
    def __OnUpdateAnimation(self, e):
        dc = wx.ClientDC(self.GetGridWindow())
        self.PrepareDC(dc)
        
        for key in self.__animations.keys():
            row, col, id = key
            if (not self.IsRectVisible(self.CellToRect(row, col))):
                self.__animations.pop(key)
                continue
            
            animation = self.__animations[key]
            animation.Update(dc)
    
# used to test this class
##class MainFrame(wx.Frame):
##    def __init__(self, parent, title):
##        wx.Frame.__init__(self, parent, -1, title, size = (640, 480))
##        grid = FGrid(self)
##        self.__grid = grid
##        
##        grid.AppendContext("Show All Columns", self.__OnShowAllColumns)
##        
##        grid.AppendColumn(1, "Filename")
##        grid.AppendColumn(2, "Thumbnails") 
##        grid.AppendColumn(3, "Result")
##        grid.AppendColumn(4, "A really really really long name")
##        grid.AppendColumn(5, "Blah")
##        grid.AppendColumn(6, "Foo")
##        grid.AppendColumn(7, "Bar")
##        grid.AppendColumn(8, "Hello")
##        grid.AppendColumn(9, "Test")
##        
##        grid.AppendRow(1)
##        grid.AppendRow(2)
##        grid.AppendRow(3)
##        grid.AppendRow(4)
##        
##        grid.InsertData(1, 1, "A")
##        grid.InsertData(2, 1, "G")
##        grid.InsertData(3, 1, "E")
##        grid.InsertData(4, 1, "A")
##        
##        grid.InsertData(1, 2, "Z(A)")
##        grid.InsertData(2, 2, "X(G)")
##        grid.InsertData(3, 2, "Y(E)")
##        grid.InsertData(4, 2, "A(A)")
##        
##        grid.InsertData(1, 3, "F(A)")
##        grid.InsertData(2, 3, "D(G)")
##        grid.InsertData(3, 3, "H(E)")
##        grid.InsertData(4, 3, "A(A)")
##        
##        grid.DeleteRow(4)
##        
##        grid.SetColumnOrder([1,])
##        grid.SortColumn(0, True)
##        grid.SetColumnOrder([2,])
##      #  grid.SetColumnOrder([9, 8, 3, 1])
##        
##    def __OnShowAllColumns(self, e):
##        self.__grid.SetColumnOrder([1,2,3,4,5,6,7,8,9])
##    
##app = wx.PySimpleApp()
##frame = MainFrame(None, "Test")
##frame.Show()
##app.MainLoop()