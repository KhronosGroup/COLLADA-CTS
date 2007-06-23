# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import sys
import wx

# meant to be started without the CTF, so it doesn't know about Core
from Gui.Dialog.FImageSizer import *

class FAnimationPanel(wx.Panel):
    
    """
    wx.Panel that contains an FImageSizer, which can be displayed in a frame to
    make a simple viewer for animations.
    """
    
    def __init__(self, parent, filenames):
        """__init__(parent, filenames) -> FAnimationPanel
        
        Creates a FAnimationPanel.
        
        arguments:
            parent
                wx.Window that is the parent of this wx.Panel.
            filenames
                list of string that correspond to absolute filenames of the
                images that form the animation.
        
        """
        wx.Panel.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        animationSizer = FImageSizer(self, wx.EmptyString, filenames, None)
        
        sizer.Add(animationSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.Fit()

class FAnimationViewer(wx.Frame):
    
    """
    A simple viewer for a series of image files that compose an animation. It 
    displays simple controls such as next frame and previous frame.
    """
    
    def __init__(self, parent, id, title, filenames):
        """__init__(parent, id, title, filenames) -> FAnimationViewer
        
        Creates and shows the FAnimationViewer.
        
        arguments:
            parent
                wx.Window that is the parent of this wx.Frame. None if this is
                be be the top-level Frame.
            id
                int corresponding to id of this wx.Frame
            title
                string corresponding to the title of this wx.Frame. It is shown
                in the title bar.
            filenames
                list of string that correspond to absolute filenames of the
                images that form the animation.
        
        """
        wx.Frame.__init__(self, parent, id, title)
        panel = FAnimationPanel(self, filenames)
        self.Fit()
        self.Show()

# Entry point.
if (len(sys.argv) > 1):
    app = wx.PySimpleApp()
    filenames = []
    for i in range(1, len(sys.argv)):
        filenames.append(sys.argv[i])
    frame = FAnimationViewer(None, wx.ID_ANY, "Animation", filenames)
    app.MainLoop()
