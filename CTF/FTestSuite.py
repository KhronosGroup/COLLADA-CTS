# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import os
import sys

from Core.FTestSuiteGUI import MainFrame
from Core.FTestSuiteCommand import FTestSuiteCommand

os.chdir("Core");

if (len(sys.argv) == 1):
    app = wx.PySimpleApp()
    frame = MainFrame(None, wx.ID_ANY, "TestSuite")
    frame.Show()
    app.MainLoop()
else:
    args = sys.argv[1:]
    
    FTestSuiteCommand(args)
