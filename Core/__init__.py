# import this before wx because of compatibility issues
import gl

import wx

# some versions of wx module use Colour instead of Color depending on locale
try:
    from wx import Color
except ImportError:
    wx.Color = wx.Colour

    