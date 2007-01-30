# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx

import Core.Common.FUtils as FUtils

class FPreferenceDialog(wx.Dialog):
    __DIALOG_TITLE = "Preferences"
    
    def __init__(self, parent, allColumns, shownColumns, showBlessed = False,
            showPrevious = False, width = 100, height = 100, diffPath = ""):
        """Creates this dialog.
        
        arguments:
            parent -- the parent frame for this dialog.
            allColumns -- list of 2-tuples. The first being an index and the
                    second is a string. The string is what is shown to the
                    user. The reason for the index is because FExecutionGrid
                    uses it. In FPreferenceDialog, the index will merely follow
                    the string as the user types. This list is for all the
                    columns.
            shownColumns -- see allColumns for explanation of the list of
                    2-tuples. This list is for only the shown columns.
            showBlessed -- True if show blessed checkbox is to be checked by 
                    default.
            showPrevious -- True if show previous checkbox is to be checked by
                    default.
            width -- integer corresponding to default value of width.
            height -- integer corresponding to default value of height.
            diffPath -- string corresponding to default value of diff path.
        
        """
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 
                           FPreferenceDialog.__DIALOG_TITLE)
        
        self.__ID_DIFF_BROWSE = wx.NewId()
        self.__ID_OK = wx.NewId()
        self.__ID_CANCEL = wx.NewId()
        self.__ID_SHOW = wx.NewId()
        self.__ID_HIDE = wx.NewId()
        self.__ID_UP = wx.NewId()
        self.__ID_DOWN = wx.NewId()
        
        self.__blessed = None
        self.__previous = None
        self.__width = None
        self.__height = None
        self.__diff = None
        self.__hiddenList = None
        self.__shownList = None
        
        self.__shownColumns = shownColumns[:] # create a copy
        self.__hiddenColumns = []
        
        for column in allColumns:
            if (not column in self.__shownColumns):
                self.__hiddenColumns.append(column)
        
        outterSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(outterSizer)
        
        previewSizer = self.__GetPreviewSizer(showBlessed, showPrevious, width,
                                              height)
        diffSizer = self.__GetDiffSizer(parent, diffPath)
        columnSizer = self.__GetColumnSizer(allColumns)
        
        bottomSizer = self.__GetBottomSizer()
        
        outterSizer.Add(previewSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(diffSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(columnSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(bottomSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.Fit()
    
    def GetShowBlessed(self):
        return self.__blessed.IsChecked()
    
    def GetShowPrevious(self):
        return self.__previous.IsChecked()
    
    def GetThumbnailSize(self):
        return (int(self.__width.GetValue()), int(self.__height.GetValue()))
    
    def GetDiffPath(self):
        value = self.__diff.GetValue()
        if (value == ""): return value
        
        if (value.find("%base") == -1):
            value = value + " %base"
        if (value.find("%mine") == -1):
            value = value + " %mine"
        return value
    
    def GetColumns(self):
        return self.__shownColumns
    
    def __OnOk(self, e):
        e.Skip()
        if (not self.__width.GetValue().isdigit()):
            FUtils.ShowWarning(self, "Width is not a number")
            return
        if (not self.__height.GetValue().isdigit()):
            FUtils.ShowWarning(self, "Height is not a number")
            return
        
        if (self.IsModal()):
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Show(False)
    
    def __OnCancel(self, e):
        e.Skip()
        if (self.IsModal()):
            self.EndModal(wx.ID_CANCEL)
        else:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Show(False)
        e.Skip()
    
    def __OnShow(self, e):
        e.Skip()
        selection = self.__hiddenList.GetSelection()
        if (selection == -1): return
        
        string = self.__hiddenList.GetString(selection)
        data = self.__hiddenList.GetClientData(selection)
        
        self.__shownColumns.append((data, string))
        self.__shownList.Append(string, data)
        
        self.__hiddenColumns.pop(selection)
        self.__hiddenList.Delete(selection)
    
    def __OnHide(self, e):
        e.Skip()
        selection = self.__shownList.GetSelection()
        if (selection == -1): return
        
        string = self.__shownList.GetString(selection)
        data = self.__shownList.GetClientData(selection)
        
        self.__hiddenColumns.append((data, string))
        self.__hiddenList.Append(string, data)
        
        self.__shownColumns.pop(selection)
        self.__shownList.Delete(selection)
    
    def __OnUp(self, e):
        e.Skip()
        selection = self.__shownList.GetSelection()
        if (selection == -1): return
        if (selection == 0): return # can't move up anymore
        
        switchIndex = selection - 1
        
        selectedPair = self.__shownColumns[selection]
        self.__shownColumns[selection] = self.__shownColumns[switchIndex]
        self.__shownColumns[switchIndex] = selectedPair
        
        self.__shownList.Insert(selectedPair[1], switchIndex, selectedPair[0])
        self.__shownList.Delete(selection + 1)
        self.__shownList.SetSelection(switchIndex)
    
    def __OnDown(self, e):
        e.Skip()
        selection = self.__shownList.GetSelection()
        if (selection == -1): return
        if (selection == len(self.__shownColumns) - 1): 
            return # can't more down anymore
        
        switchIndex = selection + 1
        
        switchPair = self.__shownColumns[switchIndex]
        self.__shownColumns[switchIndex] = self.__shownColumns[selection]
        self.__shownColumns[selection] = switchPair
        
        self.__shownList.Insert(switchPair[1], selection, switchPair[0])
        self.__shownList.Delete(selection + 2)
        self.__shownList.SetSelection(switchIndex)
        
      #  print "switching " + str(selection) + " with " + str(switchIndex)
    
    def __OnDiffBrowse(self, e):
        e.Skip()
        fileChooser = wx.FileDialog(self, "Find Diff Program", 
                "", "",  
                "", 
                wx.OPEN | wx.HIDE_READONLY)
        if (fileChooser.ShowModal() == wx.ID_OK):
            self.__diff.SetValue("\"" + fileChooser.GetPath() + "\"")
    
    def __GetPreviewSizer(self, showBlessed, showPrevious, width, height):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        additionalPreviewSizer = self.__GetAdditionalPreviewSizer(showBlessed,
                                                                  showPrevious)
        previewSizeSizer = self.__GetPreviewSizeSizer(width, height)
        
        sizer.Add(additionalPreviewSizer, 1, wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(previewSizeSizer, 1, wx.EXPAND | wx.LEFT, 5)
        
        return sizer
    
    def __GetAdditionalPreviewSizer(self, showBlessed, showPrevious):
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Additional Previews:")
        outterSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.__blessed = wx.CheckBox(self, wx.ID_ANY, "Show Blessed")
        self.__previous = wx.CheckBox(self, wx.ID_ANY, "Show Previous")
        if (showBlessed):
            self.__blessed.SetValue(wx.CHK_CHECKED)
        if (showPrevious):
            self.__previous.SetValue(wx.CHK_CHECKED)
        
        sizer.Add(self.__blessed, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.__previous, 0, wx.EXPAND | wx.ALL, 5)
        
        outterSizer.Add(sizer, 1, wx.EXPAND)
        
        return outterSizer
    
    def __GetPreviewSizeSizer(self, width, height):
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Previews Size:")
        outterSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        
        sizer = wx.GridSizer(2, 2, 5, 5)
        
        labelX = wx.StaticText(self, wx.ID_ANY, "Width: ")
        self.__width = wx.TextCtrl(self, wx.ID_ANY, str(width))
        labelY = wx.StaticText(self, wx.ID_ANY, "Height: ")
        self.__height = wx.TextCtrl(self, wx.ID_ANY, str(height))
        
        sizer.Add(labelX, 0, wx.ALIGN_RIGHT)
        sizer.Add(self.__width, 1)
        sizer.Add(labelY, 0, wx.ALIGN_RIGHT)
        sizer.Add(self.__height, 1)
        
        outterSizer.Add(sizer, 1, wx.EXPAND)
        
        return outterSizer
    
    def __GetDiffSizer(self, parent, diffPath):
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Diff Viewer")
        sizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        
        innerSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        label = wx.StaticText(self, wx.ID_ANY, "Diff Command: ")
        self.__diff = wx.TextCtrl(self, wx.ID_ANY, diffPath)
        diffBrowse = wx.Button(self, self.__ID_DIFF_BROWSE, "Browse")
        self.Bind(wx.EVT_BUTTON, self.__OnDiffBrowse, diffBrowse, 
                  self.__ID_DIFF_BROWSE)
        
        descLabel = wx.StaticText(self, wx.ID_ANY, 
                "Use %base and %mine in command for inputs into the external" +
                " program. Will add %base and %mine at end if not found.")
        descLabel.SetOwnForegroundColour(wx.BLUE)
        
        innerSizer.Add(label, 0, wx.EXPAND | wx.ALL, 5)
        innerSizer.Add(self.__diff, 1, wx.EXPAND | wx.ALL, 5)
        innerSizer.Add(diffBrowse, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(innerSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(descLabel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        return sizer
        
    def __GetColumnSizer(self, allColumns):
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Grid Columns")
        outterSizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)
        
        shownLabel =  wx.StaticText(self, wx.ID_ANY, "Shown columns")
        self.__shownList = wx.ListBox(self, wx.ID_ANY)
        for pair in self.__shownColumns:
            self.__shownList.Append(pair[1], pair[0])
        shownSizer = wx.BoxSizer(wx.VERTICAL)
        shownSizer.Add(shownLabel, 0, wx.ALIGN_CENTER)
        shownSizer.Add(self.__shownList, 1, wx.EXPAND | wx.ALL, 5)
        
        hiddenLabel =  wx.StaticText(self, wx.ID_ANY, "Hidden columns")
        self.__hiddenList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition)
        for pair in self.__hiddenColumns:
            self.__hiddenList.Append(pair[1], pair[0])
        hiddenSizer = wx.BoxSizer(wx.VERTICAL)
        hiddenSizer.Add(hiddenLabel, 0, wx.ALIGN_CENTER)
        hiddenSizer.Add(self.__hiddenList, 1, wx.EXPAND | wx.ALL, 5)
        
        showButton = wx.Button(self, self.__ID_SHOW, "<<")
        hideButton = wx.Button(self, self.__ID_HIDE, ">>")
        upButton = wx.Button(self, self.__ID_UP, "< Move Up")
        downButton = wx.Button(self, self.__ID_DOWN, "< Move Down")
        self.Bind(wx.EVT_BUTTON, self.__OnShow, showButton, self.__ID_SHOW)
        self.Bind(wx.EVT_BUTTON, self.__OnHide, hideButton, self.__ID_HIDE)
        self.Bind(wx.EVT_BUTTON, self.__OnUp, upButton, self.__ID_UP)
        self.Bind(wx.EVT_BUTTON, self.__OnDown, downButton, self.__ID_DOWN)
        
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(showButton, 0, wx.EXPAND | wx.ALIGN_CENTER)
        buttonSizer.Add(hideButton, 0, wx.EXPAND | wx.ALIGN_CENTER)
        buttonSizer.Add(upButton, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.TOP, 10)
        buttonSizer.Add(downButton, 0, wx.EXPAND | wx.ALIGN_CENTER)
        
        outterSizer.Add(shownSizer, 1, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        outterSizer.Add(hiddenSizer, 1, wx.EXPAND | wx.ALL, 5)
        
        return outterSizer
    
    def __GetBottomSizer(self):
        """Returns the Sizer used to confirm or cancel this dialog."""
        okButton = wx.Button(self, self.__ID_OK, "Ok")
        cancelButton = wx.Button(self, self.__ID_CANCEL, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.__OnOk, okButton, self.__ID_OK)
        self.Bind(wx.EVT_BUTTON, self.__OnCancel, cancelButton, 
                  self.__ID_CANCEL)
        
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(okButton, 0, wx.ALIGN_LEFT)
        bottomSizer.Add(cancelButton, 0, wx.ALIGN_RIGHT)
        
        return bottomSizer
    
# Used to start up this dialog without the entire application.
##allColumns = [(1, "Test Filename"), (1, "Annotations"), (1, "Blessed Image"), 
##              (1, "Input"), (1, "[3DSMax 7] Import"), (1, "[3DSMax 7] Render"),
##              (1, "[3DSMax 7] Export"), (1, "[3DSMax 7] Import"), 
##              (1, "[3DSMax 7] Render"), (1, "Result"), 
##              (1, "Different from Previous"), (1, "Logs"), (1, "Date Ran"),
##              (1, "Category"), (1, "Subcategory"), (1, "Configurations"), 
##              (1, "Environment")]
##shownColumns = [(1, "Test Filename"), (1, "Annotations"), (1, "Blessed Image"), 
##                (1, "[3DSMax 7] Render"), (1, "[3DSMax 7] Render"),
##                (1, "Result"), (1, "Different from Previous")]
##            
##class MainFrame(wx.MDIParentFrame):
##    def __init__(self, parent, id, title):
##        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
##                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
##                
##        dialog = FPreferenceDialog(self, allColumns, shownColumns)
##        if (dialog.ShowModal() == wx.ID_OK):
##            print dialog.GetThumbnailSize()
##            print dialog.GetColumns()
##            print dialog.GetShowBlessed()
##            print dialog.GetShowPrevious()
##            print dialog.GetDiffPath()
##        
##app = wx.PySimpleApp()
##frame = MainFrame(None,-1, "Test")
##app.MainLoop()