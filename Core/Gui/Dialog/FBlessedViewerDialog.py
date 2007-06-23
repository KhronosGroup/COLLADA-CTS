# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import os
import os.path
import shutil


import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Core.Gui.Dialog.FImageSizer import *

class FBlessedViewerDialog(wx.Dialog):
    def __init__(self, parent, dataSetPath):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 
                "Blessed Viewer", size = wx.Size(600, 600),
                style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        
        window = wx.SplitterWindow(self)
        
        window.SetSashGravity(0.5)
        window.SetMinimumPaneSize(20)
        
        images = FBlessedImagesPanel(window)
        names = FBlessedNamesPanel(window, dataSetPath, images)
        window.SplitVertically(names, images, 200)
        
        sizer.Add(window, 1, wx.EXPAND | wx.ALL, 5)

class FBlessedNamesPanel(wx.Panel):
    def __init__(self, parent, dataSetPath, imagesPanel):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SUNKEN)
        
        self.__dataSetPath = dataSetPath
        self.__imagesPanel = imagesPanel
        self.__imagesPanel.SetUnblessCallback(self.__Update)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        imageLabel = wx.StaticText(self, wx.ID_ANY, "Blessed Images")
        self.__imageListBox = wx.ListBox(self, 
                style = wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.__ImageOnClick, self.__imageListBox)
        
        animationLabel = wx.StaticText(self, wx.ID_ANY, "Blessed Animations")
        self.__animationListBox = wx.ListBox(self, 
                style = wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.__AnimationOnClick, 
                  self.__animationListBox)
        
        sizer.Add(imageLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(self.__imageListBox, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(animationLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(self.__animationListBox, 1, wx.EXPAND | wx.ALL, 5)    
        
        self.__Update()
    
    # returns [(imageName, imagePath),]
    def __GetImageList(self):
        blessedImages = []
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        if (os.path.isdir(blessedDir)):
            for ext in os.listdir(blessedDir):
                if (ext[0] == "."): continue # mostly for .svn folders
                if (ext == BLESSED_EXECUTIONS): continue
                extBlessedDir = os.path.join(blessedDir, ext)
                if (os.path.isdir(extBlessedDir)):
                    for filename in os.listdir(extBlessedDir):
                        fullFilename = os.path.join(extBlessedDir, filename)
                        if (os.path.isfile(fullFilename)):
                            blessedImages.append((filename, fullFilename))
        return blessedImages
    
    # returns [(animationName, [imagePath1,]), ]
    def __GetAnimationList(self):
        blessedAnimations = []
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR, 
                                  BLESSED_ANIMATIONS)
        if (os.path.isdir(blessedDir)):
            for directory in os.listdir(blessedDir):
                if (directory[0] == "."): continue # mostly for .svn folders
                fullDirectory = os.path.join(blessedDir, directory)
                storedFilenames = []
                for filename in os.listdir(fullDirectory):
                    fullFilename = os.path.join(fullDirectory, filename)
                    if (os.path.isfile(fullFilename)):
                        storedFilenames.append(fullFilename)
                storedFilenames.sort()
                blessedAnimations.append((directory, storedFilenames))
        
        return blessedAnimations
    
    def __Update(self):
        self.__imageListBox.Clear()
        for name, image in self.__GetImageList():
            self.__imageListBox.Append(name, [image])
        
        self.__animationListBox.Clear()
        for name, images in self.__GetAnimationList():
            self.__animationListBox.Append(name, images)
        
        self.__imagesPanel.Clear()
    
    def __ImageOnClick(self, e):
        e.Skip()
        selection = self.__imageListBox.GetSelection()
        if (selection == -1): return
        self.__animationListBox.SetSelection(wx.NOT_FOUND)
        
        self.__imagesPanel.SetImage(
                self.__imageListBox.GetClientData(selection))
    
    def __AnimationOnClick(self, e):
        e.Skip()
        selection = self.__animationListBox.GetSelection()
        if (selection == -1): return
        self.__imageListBox.SetSelection(wx.NOT_FOUND)
        
        self.__imagesPanel.SetImage(
                self.__animationListBox.GetClientData(selection))


class FBlessedImagesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SUNKEN)
        
        self.__filenames = None
        self.__callback = None
        self.__animationSizer = None
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        self.Clear()
        sizer.Layout()
    
    def Clear(self):
        sizer = self.GetSizer()
        
        # for some reason Clear() does not destroy the static box
        if (self.__animationSizer != None):
            sizer.Detach(self.__animationSizer)
            self.__animationSizer.DeleteWindows()
            self.__animationSizer.GetStaticBox().Destroy()
            self.__animationSizer = None
        self.GetSizer().Clear(True)
        self.GetSizer().Layout()
    
    def SetImage(self, filenames):
        sizer = self.GetSizer()
        self.Clear()
        
        self.__filenames = filenames
        
        self.__animationSizer = FImageSizer(self, wx.EmptyString, filenames, None)
        sizer.Add(self.__animationSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        button = wx.Button(self, wx.ID_ANY, "Unbless")
        sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.__OnUnbless, button)
        
        sizer.Layout()
    
    def SetUnblessCallback(self, callback):
        self.__callback = callback
    
    def __OnUnbless(self, e):
        e.Skip()
        
        for filename in self.__filenames:
            os.remove(filename)
            foundFile = False
            for element in os.listdir(os.path.dirname(filename)):
                if (element != ".svn"):
                    foundFile = True
                    break
            if (not foundFile):
                deleteDirectory = os.path.abspath(os.path.dirname(filename))
                try:
                    shutil.rmtree(deleteDirectory)
                except OSError, e:
                    FUtils.ShowWarning(self, "Unable to delete " + 
                            deleteDirectory + ".\nError:\n" + str(e) + 
                            "\n Please delete directory manually.")
        
        if (self.__callback != None):
            self.__callback()
