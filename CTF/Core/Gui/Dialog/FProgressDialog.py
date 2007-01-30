# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx

EVT_COMMAND_FPROGRESS_GAUGE = wx.NewEventType()
EVT_COMMAND_FPROGRESS_MESSAGE = wx.NewEventType()
EVT_COMMAND_FPROGRESS_DONE = wx.NewEventType()
EVT_FPROGRESS_GAUGE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_GAUGE, 1)
EVT_FPROGRESS_MESSAGE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_MESSAGE, 1)
EVT_FPROGRESS_DONE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_DONE, 1)

class FProgressGaugeEvent(wx.PyCommandEvent):
    def __init__(self, id, newGaugeValue):
        wx.PyCommandEvent.__init__(self, EVT_COMMAND_FPROGRESS_GAUGE, id)
        self.__newGaugeValue = newGaugeValue
    
    def GetNewGaugeValue(self):
        return self.__newGaugeValue

class FProgressMessageEvent(wx.PyCommandEvent):
    def __init__(self, id, message):
        wx.PyCommandEvent.__init__(self, EVT_COMMAND_FPROGRESS_MESSAGE, id)
        self.__message = message
    
    def GetMessage(self):
        return self.__message

class FProgressDoneEvent(wx.PyCommandEvent):
    def __init__(self, id):
        wx.PyCommandEvent.__init__(self, EVT_COMMAND_FPROGRESS_DONE, id)

class FProgressDialog(wx.Dialog):
    def __init__(self, parent, maxGauge, description = ""):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Please Wait", 
                style = wx.CAPTION | wx.RESIZE_BORDER)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        label = wx.StaticText(self, wx.ID_ANY, description)
        sizer.Add(label, 0, wx.ALL, 5)
        
        self.__gauge = wx.Gauge(self, wx.ID_ANY, maxGauge)
        sizer.Add(self.__gauge, 0, wx.EXPAND | wx.ALL, 5)
        
        self.__textCtrl = wx.TextCtrl(self, 
                style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.__textCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        sizer.Add(self.__textCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        self.__cancelButton = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.__OnCancel, self.__cancelButton)
        sizer.Add(self.__cancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.Bind(EVT_FPROGRESS_GAUGE, self.__OnGauge)
        self.Bind(EVT_FPROGRESS_MESSAGE, self.__OnMessage)
        self.Bind(EVT_FPROGRESS_DONE, self.__OnDone)
        
        self.__cancelFunc = None
    
    def SetGaugeMax(self, value):
        self.__gauge.SetRange(value)
    
    def SetCancelFunc(self, func):
        self.__cancelFunc = func
    
    def __OnDone(self, e):
        self.EndModal(wx.CANCEL)
    
    def __OnCancel(self, e):
        self.__cancelButton.Enable(False)
        if (self.__cancelFunc != None):
            self.__cancelFunc(self)
    
    def __OnGauge(self, e):
        self.__gauge.SetValue(e.GetNewGaugeValue())
    
    def __OnMessage(self, e):
        self.__textCtrl.AppendText(e.GetMessage() + "\n")
    
##import time
##import threading
##class MyThread(threading.Thread):
##    def __init__(self, dialog, maxValue):
##        threading.Thread.__init__(self)
##        self.__maxValue = maxValue + 1
##        dialog.SetCancelFunc(self.__OnCancel)
##        self.__dialog = dialog
##        self.__dialogId = dialog.GetId()
##        self.__cancelled = False
##    
##    def run(self):
##        i = -1
##        while (not self.__cancelled):
##            if (i > self.__maxValue):
##                i = -1
##            print self.__dialog.IsModal()
##            wx.PostEvent(self.__dialog, 
##                         FProgressGaugeEvent(self.__dialogId, i))
##            wx.PostEvent(self.__dialog, 
##                         FProgressMessageEvent(self.__dialogId, 
##                                               "changed gauge to " + str(i)))
##            i = i + 1
##            time.sleep(1)
##        
##        wx.PostEvent(self.__dialog, FProgressDoneEvent(self.__dialogId))
##    
##    def __OnCancel(self, dialog):
##        self.__cancelled = True
##    
##class MainFrame(wx.MDIParentFrame):
##    def __init__(self, parent, id, title):
##        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
##                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
##        
##        maxGauge = 3
##        
##        dialog = FProgressDialog(self, maxGauge, "Running Tests. Please wait.")
##        myThread = MyThread(dialog, maxGauge)
##        myThread.start()
##        print "showing modal"
##        dialog.ShowModal()
##        print "finished showing Modal"
##        myThread.join()
##        print "joined"
##        dialog.Destroy()
##    
##app = wx.PySimpleApp()
##frame = MainFrame(None,-1, "Test")
##app.MainLoop()
