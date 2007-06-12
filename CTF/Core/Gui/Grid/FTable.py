# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx.grid
import types

class FTable(wx.grid.PyGridTableBase):
    __NAME = 0
    __POSITION = 1
    __SIZE = 2
    __RENDERER = 3
    __EDITOR = 4
    __ATTR = 5
    
    def __init__(self, grid):
        wx.grid.PyGridTableBase.__init__(self)
        self.__grid = grid
        self.__sortingKey = None
        self.__sortingDirection = None
        
        self.__rows = {}    # form {rkey : position}  # in future, include size
        # form {ckey : {name, position, size, renderer, editor, attr}}
        self.__columns = {} 
        self.__data = {}    # form {rkey : {ckey : data}}
        self.__rowsKey = [] # rkeys corresponding to shown value in table
        self.__colsKey = [] # ckeys corresponding to shown value in table
    
    def Clear(self):
        for row in self.__rows.keys():
            for col in self.__columns.keys():
                if (self.__columns[col][FTable.__RENDERER] == None):
                    self.__data[row][col] = ""
                else:
                    self.__data[row][col] = None
    
    def GetNumberRows(self):
        return len(self.__rows)
    
    def GetNumberCols(self):
        """GetNumberCols() -> integer
        
        Returns the number of visible columns.
        
        """
        return len(self.__colsKey)
    
    def GetColLabelValue(self, col):
        return self.__columns[self.__colsKey[col]][FTable.__NAME]
    
    def AppendColumn(self, key, colName, size, renderer = None, editor = None):
        if (key in self.__columns.keys()):
            raise KeyError, "Duplicate col key"
        
        if (renderer == None):
            for row in self.__data.keys():
                self.__data[row][key] = ""
            renderer = wx.grid.GridCellStringRenderer()
        else:
            for row in self.__data.keys():
                self.__data[row][key] = None
        
        attr = wx.grid.GridCellAttr()
        attr.SetOverflow(self.__grid.GetDefaultCellOverflow())
        attr.SetRenderer(renderer)
        
        if (editor == None):
            attr.SetReadOnly(True)
        else:
            attr.SetEditor(editor)
        
        self.__columns[key] = { FTable.__NAME: colName,
                                FTable.__POSITION : None, 
                                FTable.__SIZE : size,
                                FTable.__RENDERER : renderer,
                                FTable.__EDITOR : editor,
                                FTable.__ATTR : attr }
    
    def AppendRow(self, key):
        if (key in self.__rows.keys()):
            raise KeyError, "Duplicate row key"
        
        self.__data[key] = {}
        for col in self.__columns.keys():
            if (self.__columns[col][FTable.__RENDERER] == None):
                self.__data[key][col] = ""
            else:
                self.__data[key][col] = None
        
        rowsCount = self.GetNumberRows()
        self.__rows[key] = rowsCount
        self.__rowsKey.append(key)
    
    def DeleteRow(self, key):
        if (not key in self.__rows.keys()):
            raise KeyError, "Key not in table"
        
        self.__data.pop(key)
        
        for i in range(self.__rows[key], self.GetNumberRows() - 1):
            nextKey = self.__rowsKey[i + 1]
            self.__rowsKey[i] = nextKey
            self.__rows[nextKey] = i
        
        self.__rows.pop(key)
        self.__rowsKey.pop()
    
    def SetColumnOrder(self, columns):
        """SetColumnOrder(columns) -> None
        
        Sets the visible columns and their ordering. columns is a list of keys
        to be shown in that order. The keys correspond to those added using 
        AppendColumn.
        
        Since badge levels may be added/removed in the configuration file
        and this information comes from the serializer, we remove any unknown
        column key when opening the test procedure. This may result in added
        hidden columns.
        
        """

        # Validate the columns list.
        # 
        # Since this information comes from a serialization
        # and the badge levels may have changed
        # We need to compensate for deleted/new columns.
        hasWhinedOnce = False;
        columnsToRemove = []
        for column in columns:
            if not column in self.__columns.keys():
                if not hasWhinedOnce:
                    print "WARNING: Grid columns have changed. Attempting to compensate."
                    print "         File->Preferences may contain hidden columns."
                    hasWhinedOnce = True
                columnsToRemove.append(column)
        for column in columnsToRemove:
            columns.remove(column)
        
        # Use this (serialized) column order.
        self.__colsKey = columns
        for cKey in self.__columns.keys():
            column = self.__columns[cKey]
            if (column[FTable.__POSITION] != None):
                column[FTable.__ATTR].IncRef()
                column[FTable.__POSITION] = None
        for i in range(len(self.__colsKey)):
            cKey = self.__colsKey[i]
            column = self.__columns[cKey]
            column[FTable.__POSITION] = i
            self.SetColSize(cKey, column[FTable.__SIZE])
            self.__grid.SetColAttr(i, column[FTable.__ATTR])
    
    def SetColSize(self, cKey, width):
        self.__columns[cKey][FTable.__SIZE] = width
    
    def GetColSize(self, cKey):
        return self.__columns[cKey][FTable.__SIZE]
    
    def InsertData(self, rKey, cKey, data):
        self.__data[rKey][cKey] = data
    
    def GetValue(self, row, col):
        return self.__data[self.__rowsKey[row]][self.__colsKey[col]]
    
    def IsEmptyCell(self, row, col):
        try:
            return not self.__data[self.__rowsKey[row]][self.__colsKey[col]]
        except IndexError:
            return True
        
    def GetRowKey(self, row):
        return self.__rowsKey[row]    
    
    def GetRow(self, rKey):
        return self.__rows[rKey]
    
    def GetCol(self, cKey):
        return self.__columns[cKey][FTable.__POSITION]
    
    def GetColKey(self, col):
        return self.__colsKey[col]
    
    def SetValue(self, row, col, value):
        self.__data[self.__rowsKey[row]][self.__colsKey[col]] = value
    
    # SafeCmp -- a safe cmp function for sort
    #     Fixes issue in SortColumn when data[0][rKey] is initialized 
    #     with a test run and data[0][0] is not.
    def SafeCmp(self,a, b):
        c_a = a[0]
        c_b = b[0]
        
        if hasattr(a[0],"__getitem__"):
            c_a = a[0][0]
            
        if hasattr(b[0],"__getitem__"):
            c_b = b[0][0]
            
        return cmp(c_a,c_b)
    
    
    def SortColumn(self, col, ascending):
        cKey = self.__colsKey[col]
        
        self.__sortingKey = cKey
        self.__sortingDirection = ascending
        
        tempList = []
        for rKey in self.__data.keys():
            tempList.append((self.__data[rKey][cKey], rKey))
        
        if (len(self.__data) == 0): return
        
        if (type(self.__data[0][cKey]) == types.TupleType):
            # compare only the first element
            cmpFunction = lambda x, y: self.SafeCmp(x, y)
        else:
            cmpFunction = lambda x, y: cmp(x[0], y[0])
        
        if (ascending):
            tempList.sort(cmpFunction)
        else:
            tempList.sort(cmpFunction, reverse = True)
        
        for row in range(len(tempList)):
            entry = tempList[row]
            rKey = entry[1]
            
            self.__rows[rKey] = row
            self.__rowsKey[row] = rKey
    
    def IsSortedColumn(self, col):
        cKey = self.__colsKey[col]
        return cKey == self.__sortingKey
    
    def GetSortingDirection(self):
        return self.__sortingDirection
    
    