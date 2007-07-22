# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path
import wx

import Core.Common.FUtils as FUtils

class FImageData:
    __HEIGHT_SPACING = 2
    __WIDTH_SPACING = 2 # if > 8, will need to shrink on default preview
    __BITMAP_WIDTH = 100
    __BITMAP_HEIGHT = 100
    
    def __init__(self, test, execution, step, id, simplified):
        # Copy the parameters locally
        self.__test = test
        self.__execution = execution
        self.__gridId = id
        
        # Cache some of the information.
        self.__blessedFilenames = test.GetBlessed()
        
        if (step >= 0): # Steps output
            self.__filenameList = execution.GetOutputLocation(step)
        elif (step == -1): # Input file.
            self.__filenameList = [test.GetAbsFilename()]
        elif (step == -2): # Blessed file.
            self.__filenameList = self.__blessedFilenames
            
        self.__defaultFilename = self.__filenameList[-1]
        self.__defaultImage = None
        
        if (simplified or step < 0): self.__previousFilenameList = None
        else: self.__previousFilenameList = test.GetPreviousOutputLocation(step)
        
        if (self.__execution != None and step >= 0):
            self.__errorCount = execution.GetErrorCount(step)
            self.__warningCount = execution.GetWarningCount(step)
            self.__logFilename = execution.GetLog(step)
            executionDir = execution.GetExecutionDir()
        else:
            self.__errorCount = None
            self.__warningCount = None
            self.__logFilename = None
            executionDir = None
        
        if (executionDir != None): self.__executionName = os.path.basename(executionDir)
        else: self.__executionName = None
        
        self.__defaultImage = self.GetImage(-1)
    
    def GetExecutionName(self):
        return self.__executionName
    
    def GetBlessedFilenames(self):
        if (self.__blessedFilenames == None): return [None,]
        else: return self.__blessedFilenames
    
    def GetBlessedImages(self):
        if (self.__blessedFilenames == None): 
            return [self.__GetEmptyImage("(No Blessed)"),]
            
        images = []
        for name in self.__blessedFilenames:
            images.append(self.__GetImage(name))
        return images
    
    def GetDefaultFilename(self):
        return self.__defaultFilename
    
    def GetDefaultImage(self):
        return self.__defaultImage
    
    def GetFilenames(self):
        return self.__filenameList
    
    def GetImages(self):
        images = []
        for name in self.__filenameList:
            images.append(self.__GetImage(name))
        return images
    
    def GetPreviousFilenames(self):
        if (self.__previousFilenameList == None): 
            return [None,]
        
        return self.__previousFilenameList
    
    def GetPreviousImages(self):
        if (self.__previousFilenameList == None): 
            return [self.__GetEmptyImage("(No Previous)"),]
        
        images = []
        for name in self.__previousFilenameList:
            images.append(self.__GetImage(name))
        return images
    
    def GetFilename(self, fileNumber): # fileNumber 0 indexing
        return self.__filenameList[fileNumber]
    
    def GetImage(self, imageNumber): # imageNumber 0 indexing
        return self.__GetImage(self.__filenameList[imageNumber])
    
    def GetBlessedImage(self, imageNumber): # imageNumber 0 indexing
        return self.__GetImage(self.__blessedFilenames[imageNumber])
    
    def GetPreviousImage(self, imageNumber): # imageNumber 0 indexing
        return self.__GetImage(self.__previousFilenameList[imageNumber])
    
    def GetTest(self):
        return self.__test
        
    def GetExecution(self):
        return self.__execution
    
    def GetGridId(self):
        return self.__gridId
    
    def GetLogFilename(self):
        if (self.__logFilename == None):
            raise ValueError, "<FImageData> Log file never initialized"
        
        return self.__logFilename
    
    def GetErrorCount(self):
        return self.__errorCount
    
    def GetWarningCount(self):
        return self.__warningCount
    
    def GetFilenameCount(self):
        return len(self.__filenameList)
    
    def __GetEmptyImage(self, text):
        bitmap = wx.EmptyBitmap(FImageData.__BITMAP_WIDTH, 
                                FImageData.__BITMAP_HEIGHT)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        
        dc.SetPen(wx.BLACK_PEN)
        bitmapWidth = FImageData.__BITMAP_WIDTH - 2
        bitmapHeight = FImageData.__BITMAP_HEIGHT - 2
        dc.DrawRectangle(0, 0, bitmapWidth, bitmapHeight)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextBackground(wx.WHITE)
        dc.SetTextForeground(wx.BLACK)
        
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        dc.SetFont(font)
        
        width, height = dc.GetTextExtent(text)
        
        dc.DrawText(text, (bitmapWidth - width)/2, (bitmapHeight - height)/2)
        
        return bitmap.ConvertToImage()
    
    def __GetImage(self, filename):
        if (not os.path.isfile(filename)): 
            return wx.ImageFromBitmap(wx.ArtProvider.GetBitmap(
                    wx.ART_MISSING_IMAGE, wx.ART_OTHER, (48, 48)))
        
        if (self.__IsRecognizable(filename)):
            return wx.Image(filename, wx.BITMAP_TYPE_ANY)
        
        bitmap = wx.EmptyBitmap(FImageData.__BITMAP_WIDTH, 
                                FImageData.__BITMAP_HEIGHT)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        
        dc.SetPen(wx.BLACK_PEN)
        bitmapWidth = FImageData.__BITMAP_WIDTH - 2
        bitmapHeight = FImageData.__BITMAP_HEIGHT - 2
        dc.DrawRectangle(0, 0, bitmapWidth, bitmapHeight)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextBackground(wx.WHITE)
        dc.SetTextForeground(wx.BLACK)
        
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        dc.SetFont(font)
        
        ext = FUtils.GetExtension(filename)
        if (ext == "dae"):
            text = "Collada File"
        elif (ext == "max"):
            text = "Max File"
        elif (ext == "ma"):
            text = "Maya Ascii File"
        elif (ext == "mb"):
            text = "Maya Binary File"
        else:
            text = ext + " File"
        width1, height1 = dc.GetTextExtent(text)
        width2, height2 = dc.GetTextExtent("(No Preview)")
        width = max(width1, width2)
        height = height1 + height2 + FImageData.__HEIGHT_SPACING
        
        textY = (bitmapHeight - height)/2
        
        dc.DrawText(text, (bitmapWidth - width1)/2, textY)
        dc.DrawText("(No Preview)", (bitmapWidth - width2)/2 , 
                textY + height1 + FImageData.__HEIGHT_SPACING)
        
        return bitmap.ConvertToImage()
    
    def __IsRecognizable(self, filename):
        extension = FUtils.GetExtension(filename)
        return FUtils.IsImageFile(extension)
    