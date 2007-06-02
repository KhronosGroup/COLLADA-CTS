# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import os.path

from Core.Common.FConstants import *

class FMenuBar(wx.MenuBar):
    '''The menu bar used for the test suite.'''
    ID_NEW = wx.NewId()
    ID_OPEN = wx.NewId()
    ID_SAVEAS = wx.NewId()
    ID_EXPORT_ALL = wx.NewId()
    ID_EXPORT_SELECTED = wx.NewId()
    ID_CLOSE = wx.NewId()
    ID_EXIT = wx.NewId()
    ID_PREFERENCES = wx.NewId()
    ID_ADD_TEST = wx.NewId()
    ID_RUN_SELECTED = wx.NewId()
    ID_RUN_ALL = wx.NewId()
    ID_RUN_UNRAN = wx.NewId()
    ID_UPDATE = wx.NewId()
    ID_HELP = wx.NewId()
    ID_ABOUT = wx.NewId()
    ID_ANIMATE = wx.NewId()
    ID_RELOAD = wx.NewId()
    ID_REGEX = wx.NewId()
    ID_SELECT_ALL = wx.NewId()
    ID_EXPORT_ALL_CSV = wx.NewId()
    
    def __init__(self, frame, createToolbar):
        wx.MenuBar.__init__(self)
        self.__frame = frame
        
        self.__passedCtrl = None
        self.__failedCtrl = None
        self.__totalCtrl = None
        self.__badgesEarnedLabel = None
        
        self.Append(self.__CreateFileMenu(), "&File")
        self.Append(self.__CreateTestMenu(), "&Test")
        self.Append(self.__CreateHelpMenu(), "&Help")
        
        if (createToolbar):
            self.__toolbar = self.__CreateToolBar(frame)
        else:
            self.__toolbar = None
        
        self.Bind(FMenuBar.ID_ANIMATE, self.__OnAnimate)
        
        self.__DisableAll()
    
    def __OnAnimate(self, e):
        id = e.GetId()
        value = e.IsChecked()
        self.__toolbar.ToggleTool(id, value)
        self.Check(id, value)
    
    def Bind(self, id, op):
        self.__frame.Bind(wx.EVT_MENU, op, id = id)
        self.Enable(id, True)
        if (self.__toolbar != None):
            self.__toolbar.Bind(wx.EVT_TOOL, op, id = id)
            self.__toolbar.EnableTool(id, True)
        
    def UnBind(self, id):
        self.__frame.Bind(wx.EVT_MENU, None, id)
        self.Enable(id, False)
        if (self.__toolbar != None):
            self.__toolbar.Bind(wx.EVT_TOOL, None, id = id)
            self.__toolbar.EnableTool(id, False)
    
    def SetPassed(self, value):
        self.__passedCtrl.SetValue(str(value))
    
    def SetFailed(self, value):
        self.__failedCtrl.SetValue(str(value))
    
    def SetTotal(self, value):
        self.__totalCtrl.SetValue(str(value))
        
    def SetBadgesEarned(self, badgesEarned):
        badgesEarnedCount = len(badgesEarned)
        if (badgesEarnedCount == 0):
            self.__badgesEarnedLabel.SetLabel("  No badges earned.")
        else:
            text = "  Badges earned: "
            for i in range(badgesEarnedCount):
                text += badgesEarned[i]
                if (i < badgesEarnedCount - 1): text += ", "
            self.__badgesEarnedLabel.SetLabel(text)
    
    def __DisableAll(self):
        self.Enable(FMenuBar.ID_NEW, False)
        self.Enable(FMenuBar.ID_OPEN, False)
        self.Enable(FMenuBar.ID_SAVEAS, False)
        self.Enable(FMenuBar.ID_RELOAD, False)
        self.Enable(FMenuBar.ID_EXPORT_ALL, False)
        self.Enable(FMenuBar.ID_EXPORT_ALL_CSV, False)
        self.Enable(FMenuBar.ID_EXPORT_SELECTED, False)
        self.Enable(FMenuBar.ID_CLOSE, False)
        self.Enable(FMenuBar.ID_EXIT, False)
        
        self.Enable(FMenuBar.ID_PREFERENCES, False)
        
        self.Enable(FMenuBar.ID_ADD_TEST, False)
        self.Enable(FMenuBar.ID_RUN_SELECTED, False)
        self.Enable(FMenuBar.ID_RUN_ALL, False)
        self.Enable(FMenuBar.ID_RUN_UNRAN, False)
        self.Enable(FMenuBar.ID_SELECT_ALL, False)
        self.Enable(FMenuBar.ID_UPDATE, False)
        self.Enable(FMenuBar.ID_ANIMATE, False)
        self.Enable(FMenuBar.ID_REGEX, False)
        
        self.Enable(FMenuBar.ID_HELP, False)
        self.Enable(FMenuBar.ID_ABOUT, False)
        
        if (self.__toolbar != None):
            self.__toolbar.EnableTool(FMenuBar.ID_NEW, False)
            self.__toolbar.EnableTool(FMenuBar.ID_OPEN, False)
            self.__toolbar.EnableTool(FMenuBar.ID_SAVEAS, False)
            self.__toolbar.EnableTool(FMenuBar.ID_ADD_TEST, False)
            self.__toolbar.EnableTool(FMenuBar.ID_RUN_SELECTED, False)
            self.__toolbar.EnableTool(FMenuBar.ID_UPDATE, False)
            self.__toolbar.EnableTool(FMenuBar.ID_HELP, False)
            self.__toolbar.EnableTool(FMenuBar.ID_ANIMATE, False)
    
    def __AddTool(self, toolbar, image, id, shortName, longName):
        icon = wx.ArtProvider.GetBitmap(image, wx.ART_TOOLBAR, (16,16))
        toolbar.AddSimpleTool(id, icon, shortName, longName)
    
    def __AddCheckToolFromDisk(self, toolbar, filename, id, shortName, 
                               longName):
        icon = wx.Bitmap(filename)
        toolbar.AddCheckTool(id, icon, icon, shortName, longName)
    
    def __AddToolFromDisk(self, toolbar, filename, id, shortName, longName):
        icon = wx.Bitmap(filename)
        toolbar.AddSimpleTool(id, icon, shortName, longName)
    
    def __CreateToolBar(self, frame):
        toolbar = frame.CreateToolBar()
            
        self.__AddTool(toolbar, wx.ART_NEW, FMenuBar.ID_NEW, 
                       "New Test Procedure", "Creates a new test procedure")
        self.__AddTool(toolbar, wx.ART_FILE_OPEN, FMenuBar.ID_OPEN, 
                       "Open Test Procedure", "Opens a saved test procedure")
        self.__AddTool(toolbar, wx.ART_FILE_SAVE_AS, FMenuBar.ID_SAVEAS, 
                       "Save Test Procedure As", 
                       "Saves current test procedure as specified name")
        
        toolbar.AddSeparator()
        self.__AddToolFromDisk(toolbar, 
                os.path.join(IMAGES_DIR, "addTest.bmp"), FMenuBar.ID_ADD_TEST, 
               "Add Test", 
                "Creates new tests and add to current test procedure")
        self.__AddToolFromDisk(toolbar, 
                os.path.join(IMAGES_DIR, "runTest.bmp"), 
                FMenuBar.ID_RUN_SELECTED, "Run Selected", 
                "Run the selected tests")
        self.__AddToolFromDisk(toolbar, 
                os.path.join(IMAGES_DIR, "results.bmp"), FMenuBar.ID_UPDATE,
                "AutoUpdate Results", "Automatically updates all " + 
                "results not overriden against blessed.")
        
        toolbar.AddSeparator()
        self.__AddCheckToolFromDisk(toolbar, 
                os.path.join(IMAGES_DIR, "animate.bmp"), FMenuBar.ID_ANIMATE,
                "Animate Selected Only", "Only animates the selected tests")
        
        toolbar.AddSeparator()
        self.__AddTool(toolbar, wx.ART_HELP, FMenuBar.ID_HELP, 
                       "Help", "Opens help document")
        
        toolbar.AddSeparator()
        toolbar.AddControl(wx.StaticText(toolbar, wx.ID_ANY, "           "))
        
        toolbar.AddControl(wx.StaticText(toolbar, wx.ID_ANY, "   Total "))
        self.__totalCtrl = wx.TextCtrl(toolbar, wx.ID_ANY, "??", 
                size = (40, -1), style = wx.TE_READONLY)
        toolbar.AddControl(self.__totalCtrl)
        
        toolbar.AddControl(wx.StaticText(toolbar, wx.ID_ANY, "   Passed "))
        self.__passedCtrl = wx.TextCtrl(toolbar, wx.ID_ANY, "??", 
                size = (40, -1), style = wx.TE_READONLY)
        self.__passedCtrl.SetBackgroundColour(wx.Color(0, 255, 0))
        toolbar.AddControl(self.__passedCtrl)
        
        toolbar.AddControl(wx.StaticText(toolbar, wx.ID_ANY, "   Failed "))
        self.__failedCtrl = wx.TextCtrl(toolbar, wx.ID_ANY, "??", 
                size = (40, -1), style = wx.TE_READONLY)
        self.__failedCtrl.SetBackgroundColour(wx.Color(255, 0, 0))
        toolbar.AddControl(self.__failedCtrl)
        
        self.__badgesEarnedLabel = wx.StaticText(toolbar, wx.ID_ANY, "  Badges earned - ")
        toolbar.AddControl(self.__badgesEarnedLabel)
        
        toolbar.Realize()
        
        return toolbar
    
    def __CreateFileMenu(self):
        filemenu = wx.Menu()
        filemenu.Append(FMenuBar.ID_NEW, "&New Test Procedure\tCtrl+N", 
                        "Creates a new test procedure")
        filemenu.Append(FMenuBar.ID_OPEN, "&Open Test Procedure\tCtrl+O", 
                        "Opens a saved test procedure")
        filemenu.AppendSeparator()
        
        filemenu.Append(FMenuBar.ID_SAVEAS, "&Save Test Procedure As\tCtrl+S", 
                        "Saves current test procedure as specified name")
        filemenu.Append(FMenuBar.ID_EXPORT_ALL, "&Export All to HTML", 
                        "Exports the current test procedure to HTML")
        filemenu.Append(FMenuBar.ID_EXPORT_SELECTED, "Export Selected to HTML", 
                        "Exports the selected tests of current run to HTML")
        filemenu.Append(FMenuBar.ID_EXPORT_ALL_CSV, "Export All to &CSV",
                        "Exports the current test procedure to CSV")
        filemenu.AppendSeparator()
        
        filemenu.Append(FMenuBar.ID_PREFERENCES, "&Preferences", 
                        "Edit preferences for the test suite user interface")
        filemenu.AppendSeparator()
        
        filemenu.Append(FMenuBar.ID_CLOSE, "&Close", 
                        "Close the test procedure")
        filemenu.Append(FMenuBar.ID_RELOAD, "&Reload", 
                "Closes and reopens the test procedure to update the " +
                "display with value from the harddrive.")
        filemenu.AppendSeparator()
        filemenu.Append(FMenuBar.ID_EXIT, "&Exit", "Terminate this program")
        
        return filemenu
    
    def __CreateTestMenu(self):
        testmenu = wx.Menu()
        testmenu.Append(FMenuBar.ID_ADD_TEST, "Add Tests\tCtrl+T", 
                        "Creates new tests and add to current run")
        testmenu.AppendSeparator()
        testmenu.Append(FMenuBar.ID_RUN_SELECTED, "Run Selected\tCtrl+R", 
                        "Run the selected tests")
        testmenu.Append(FMenuBar.ID_RUN_ALL, "Run All", 
                        "Run all tests")
        testmenu.Append(FMenuBar.ID_RUN_UNRAN, "Run Remaining", 
                        "Run all tests that have not be ran")
        testmenu.AppendSeparator()
        testmenu.Append(FMenuBar.ID_SELECT_ALL, "Select All\tCtrl+A", 
                        "Selects all the tests")
        testmenu.AppendSeparator()
        testmenu.Append(FMenuBar.ID_ANIMATE, "Animate Selected Only", 
            "Animates only the selected tests.", wx.ITEM_CHECK)
        testmenu.Append(FMenuBar.ID_UPDATE, "AutoUpdate Results", 
            "Automatically updates all results not overriden against blessed.")
        testmenu.AppendSeparator()
        testmenu.Append(FMenuBar.ID_REGEX, "Regular Expression Editor",
                "Opens the regular expression editor")
        
        return testmenu
    
    def __CreateHelpMenu(self):
        helpmenu = wx.Menu()
        helpmenu.Append(FMenuBar.ID_HELP, "&Help", 
                        "Opens help document")
        helpmenu.AppendSeparator()
        helpmenu.Append(FMenuBar.ID_ABOUT, "&About", 
                        "Information about this application")
        
        return helpmenu
    