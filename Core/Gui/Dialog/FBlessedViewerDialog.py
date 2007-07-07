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
                "Blessed Viewer", size = wx.Size(540, 450),
                style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        
        window = wx.SplitterWindow(self)
        
        window.SetSashGravity(0.5)
        window.SetMinimumPaneSize(20)
        
        images = FBlessedImagesPanel(window, dataSetPath)
        names = FBlessedNamesPanel(window, dataSetPath, images)
        window.SplitVertically(names, images, 200)
        
        sizer.Add(window, 1, wx.EXPAND | wx.ALL, 0)

class FBlessedNamesPanel(wx.Panel):
    def __init__(self, parent, dataSetPath, imagesPanel):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SUNKEN)
        
        self.__dataSetPath = dataSetPath
        self.__imagesPanel = imagesPanel
        self.__imagesPanel.SetChangeCallback(self.__Update)
        self.__defaultBlessedImageFilename = ""

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        # UI: Add a label for the default blessed image filename.
        defaultBlessedLabel = wx.StaticText(self, wx.ID_ANY, "  Default Blessed")
        sizer.Add(defaultBlessedLabel, 0, wx.ALIGN_LEFT | wx.ALL, 2)
        
        # UI: Add a text box with the default blessed image filename at the top.
        self.__defaultImageTextBox = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_READONLY)
        sizer.Add(self.__defaultImageTextBox, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add((1, 5), 0)

        # UI: Add a label for the blessed images list box.
        imageLabel = wx.StaticText(self, wx.ID_ANY, "  Blessed Images/Animations")
        sizer.Add(imageLabel, 0, wx.ALIGN_LEFT | wx.ALL, 2)

        # UI: Add a list box containing all the bless image filenames.
        self.__imageListBox = wx.ListBox(self, style = wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.__ImageOnClick, self.__imageListBox)
        sizer.Add(self.__imageListBox, 1, wx.EXPAND | wx.ALL, 2)
        
        self.__Update(False)
    
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
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR, BLESSED_ANIMATIONS)
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
    
    def __Update(self, onlyDefaultBless):
        
        # Update the default blessed image filename.
        defaultContainerFilename = os.path.join(self.__dataSetPath, BLESSED_DIR, BLESSED_DEFAULT_FILE)
        if (os.path.isfile(defaultContainerFilename)):
            blessFile = open(defaultContainerFilename, "rb")
            filename = blessFile.readline().strip()
            blessFile.close()
            if (filename.find(BLESSED_ANIMATIONS) == -1): # Image?
                filename = os.path.basename(filename)
            else:
                filename = os.path.basename(os.path.dirname(filename))
            self.__defaultImageTextBox.SetLabel(filename)
        else:
            self.__defaultImageTextBox.SetLabel("")
        if onlyDefaultBless: return

        # Update the image filenames list box.
        self.__imageListBox.Clear()
        for name, image in self.__GetImageList():
            self.__imageListBox.Append("[I] " + name, [image])        
        for name, images in self.__GetAnimationList():
            self.__imageListBox.Append("[A] " + name, images)
        
        # Restart the images panel
        if (self.__imageListBox.GetCount() > 0):
            self.__imageListBox.Select(0)
            self.__imagesPanel.SetImage(self.__imageListBox.GetClientData(0))
        else:
            self.__imagesPanel.Clear()
    
    def __ImageOnClick(self, e):
        e.Skip()
        selection = self.__imageListBox.GetSelection()
        if (selection == -1): return
        
        self.__imagesPanel.SetImage(self.__imageListBox.GetClientData(selection))

class FBlessedImagesPanel(wx.Panel):
    def __init__(self, parent, dataSetPath):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SUNKEN)
        
        self.__filenames = None
        self.__callback = None
        self.__animationSizer = None
        self.__dataSetPath = dataSetPath
        
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
        sizer.Add(self.__animationSizer, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 2)

        button = wx.Button(self, wx.ID_ANY, "Delete")
        buttonSizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        self.Bind(wx.EVT_BUTTON, self.__OnUnbless, button)
        
        button = wx.Button(self, wx.ID_ANY, "Default Bless")
        buttonSizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        self.Bind(wx.EVT_BUTTON, self.__OnMakeDefault, button)

        buttonSizer.Layout()
        sizer.Layout()
    
    def SetChangeCallback(self, callback):
        self.__callback = callback
    
    def __OnUnbless(self, e):
        e.Skip()
        
        # Delete the blessed image files.
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
                    FUtils.ShowWarning(self, "Unable to delete " + deleteDirectory + ".\n" +
                            "Error:\n" + str(e) + "\n Please delete directory manually.")
        
        # Verify whether this was the blessed images. In that case: clear the file.
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        defaultContainerFilename = os.path.join(blessedDir, BLESSED_DEFAULT_FILE)
        if (os.path.isfile(defaultContainerFilename)):
            blessFile = open(defaultContainerFilename, "rb")
            defaultBlessedImageFilename = blessFile.readline().strip()
            blessFile.close()

            # Need to compare absolute filenames.
            if (len(defaultBlessedImageFilename) > 0):
                defaultBlessedImageFilename = os.path.join(blessedDir, defaultBlessedImageFilename)
                defaultBlessedImageFilename = os.path.abspath(defaultBlessedImageFilename)
                isDefault = False
                for filename in self.__filenames:
                    filename = os.path.abspath(filename)
                    if (filename == defaultBlessedImageFilename):
                        isDefault = True
                        break
            
            if (isDefault):
                blessFile = open(defaultContainerFilename, "w")
                blessFile.close()
        
        if (self.__callback != None):
            self.__callback(False)
            
    def __OnMakeDefault(self, e):
        e.Skip()
        
        # Rewrite the default blessed file to include these local filenames.
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        defaultContainerFilename = os.path.join(blessedDir, BLESSED_DEFAULT_FILE)
        blessFile = open(defaultContainerFilename, "w")
        if (self.__filenames != None) and (len(self.__filenames) > 0):
            for filename in self.__filenames:
                relativeFilename = FUtils.GetRelativePath(filename, blessedDir)
                blessFile.write(relativeFilename)
                blessFile.write("\n")
        else:
            pass # Intentionally leave empty. Can we actually get here in the UI?
            
        blessFile.close()
        
        if (self.__callback != None):
            self.__callback(True)
        
