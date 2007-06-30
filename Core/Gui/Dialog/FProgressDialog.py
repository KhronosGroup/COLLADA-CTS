# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import os.path

EVT_COMMAND_FPROGRESS_GAUGE = wx.NewEventType()
EVT_COMMAND_FPROGRESS_MESSAGE = wx.NewEventType()
EVT_COMMAND_FPROGRESS_DONE = wx.NewEventType()
EVT_COMMAND_FPROGRESS_MKCLEAR = wx.NewEventType()
EVT_COMMAND_FPROGRESS_MKADD = wx.NewEventType()

EVT_FPROGRESS_GAUGE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_GAUGE, 1)
EVT_FPROGRESS_MESSAGE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_MESSAGE, 1)
EVT_FPROGRESS_DONE = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_DONE, 1)
EVT_FPROGRESS_MKCLEAR = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_MKCLEAR, 1)
EVT_FPROGRESS_MKADD = wx.PyEventBinder(EVT_COMMAND_FPROGRESS_MKADD, 1)

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
        
class FProgressMarkerClearEvent(wx.PyCommandEvent):
    def __init__(self, id):
        wx.PyCommandEvent.__init__(self, EVT_COMMAND_FPROGRESS_MKCLEAR, id)

class FProgressMarkerAddEvent(wx.PyCommandEvent):
    def __init__(self, id, marker):
        wx.PyCommandEvent.__init__(self, EVT_COMMAND_FPROGRESS_MKADD, id)
        self.__marker = marker
    
    def GetMarker(self):
        return self.__marker;

class FProgressDialog(wx.Dialog):
    def __init__(self, parent, maxGauge, description = ""):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Please Wait", style = wx.CAPTION | wx.RESIZE_BORDER)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        
        label = wx.StaticText(self, wx.ID_ANY, description)
        sizer.Add(label, 0, wx.ALL, 5)
        
        # Create the progress bar and the marker label
        self.__gauge = wx.Gauge(self, wx.ID_ANY, maxGauge)
        sizer.Add(self.__gauge, 0, wx.EXPAND | wx.ALL, 5)
        
        self.__markerLabel = wx.StaticText(self, wx.ID_ANY, " -> Script markers: 0/0")
        sizer.Add(self.__markerLabel, 0, wx.EXPAND | wx.ALL, 2)

        # Below comes the log
        self.__textCtrl = wx.TextCtrl(self, style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.__textCtrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        sizer.Add(self.__textCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        # At the very bottom, at the cancel button
        self.__cancelButton = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.__OnCancel, self.__cancelButton)
        sizer.Add(self.__cancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Events to track
        self.Bind(EVT_FPROGRESS_GAUGE, self.__OnGauge)
        self.Bind(EVT_FPROGRESS_MESSAGE, self.__OnMessage)
        self.Bind(EVT_FPROGRESS_DONE, self.__OnDone)
        self.Bind(EVT_FPROGRESS_MKADD, self.__OnMarkerAdd)
        self.Bind(EVT_FPROGRESS_MKCLEAR, self.__OnMarkerClear)
        self.Bind(wx.EVT_CLOSE, self.__OnClose)
        self.Bind(wx.EVT_TIMER, self.__OnTimer)            
    
        # Set-up the timer.
        self.__timerCount = 0
        self.__timer = wx.Timer(self)
        self.__timer.Start(500) # 500ms

        self.__cancelFunc = None
        self.__markers = []
        self.__nextMarker = None

    def SetGaugeMax(self, value):
        self.__gauge.SetRange(value)
    
    def SetCancelFunc(self, func):
        self.__cancelFunc = func
        
    def __OnClose(self, e):
        self.__timer.Stop()
        del self.__timer
        self.Destroy()
    
    def __OnDone(self, e):
        self.EndModal(wx.CANCEL)
    
    def __OnCancel(self, e):
        self.__cancelButton.Enable(False)
        if (self.__cancelFunc != None):
            self.__cancelFunc(self)
    
    def __OnGauge(self, e):
        self.__gauge.SetValue(e.GetNewGaugeValue())
    
    def __OnMarkerClear(self, e):
        self.__markers = []
        self.__markerLabel.SetLabel(" -> Script markers: 0/0")
        self.__nextMarker = None
        
    def __OnMarkerAdd(self, e):
        # Intentionally do not update the label: that will pointlessly flicker the UI.
        self.__markers.append(e.GetMarker())
        self.__nextMarker = None
        
    def __OnMessage(self, e):
        self.__textCtrl.AppendText(e.GetMessage() + "\n")
        
    def __OnTimer(self, e):
        markerCount = len(self.__markers)
        if markerCount != 0:
            
            if self.__nextMarker == None:
                self.__nextMarker = 0 # At the very least, we need to refresh the label.                
            elif not self.__CheckMarker(self.__nextMarker):
                if (self.__nextMarker < markerCount - 1):
                    if self.__CheckMarker(self.__nextMarker + 1):
                        # This happens: some marker got skipped.
                        self.__nextMarker = self.__nextMarker + 2
                        # Otherwise, the next markers haven't happened yet.
                    else: return
                else: return

            # Binary search within the [nextMarker, markerCount[ range.
            start = self.__nextMarker
            end = markerCount - 1
            mid = (start + end) / 2
            while end > start:
                if self.__CheckMarker(mid): start = mid + 1
                else: end = mid
                mid = (start + end) / 2
                
            # Update the UI and remember the next marker to check.
            self.__markerLabel.SetLabel(" -> Script markers: %d/%d" % (mid + 1, markerCount))
            self.__nextMarker = mid

    def __CheckMarker(self, marker):
        """ Returns whether a given marker file path contains files. """
        filename = self.__markers[marker]
        return os.path.exists(filename)

