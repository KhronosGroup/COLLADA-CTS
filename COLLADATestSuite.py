# Copyright (C) 2006-2010 Khronos Group
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
    frame = MainFrame(None, wx.ID_ANY, "COLLADA 1.4 Conformance Test Suite")
    frame.Show()
    app.MainLoop()
else:
    args = sys.argv[1:]
    
    FTestSuiteCommand(args)
