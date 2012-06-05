# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FDebug (FApplication):
    """The class which represents mimic to the testing framework.
    
    """
    
    __SCRIPT_EXTENSION = ".py"
    
    def __init__(self, configDict):
        """__init__() -> FDebug"""
        FApplication.__init__(self, configDict)
        self.__script = None
        self.__currentFilename = None
        self.__currentImageName = None
        self.__currentImportProperName = None
        self.__testImportCount = 0
        self.__testRenderCount = 0
        self.__workingDir = None
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "Debug 1.0"
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == IMPORT):
            return []
        elif (operation == EXPORT):
            return []
        elif (operation == RENDER): 
            return []
        else:
            return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        pyFilename = ("script" + str(self.applicationIndex) + 
                FDebug.__SCRIPT_EXTENSION)
        self.__script = open(os.path.join(workingDir, pyFilename), "w")
        self.WriteCrashDetectBegin(self.__script)
        
        self.__testImportCount = 0
        self.__testRenderCount = 0
        self.__workingDir = workingDir
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
        self.__script.close()
    
    def RunScript(self):
        """RunScript() -> None
        
        Implements FApplication.RunScript()
        
        """
        returnValue = 0
                
        return (returnValue == 0)
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated):
        """WriteImport(filename, logname, outputDir, settings, isAnimated) -> list_of_str
                
        """
        print "Write Import filename: %s  logname: %s  outputDir: %s" % (filename, logname, outputDir)        
        return ["foo.dae"]
        
    
    def WriteRender(self, logname, outputDir, settings, isAnimated):
        """WriteRender(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
        print "Render logname: %s  outputDir: %s" % (logname, outputDir)        
        return ["foo.dae"]

    
    def WriteExport(self, logname, outputDir, settings, isAnimated):
        """WriteImport(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
        print "Write Export logname: %s  outputDir: %s" % (logname, outputDir)        
        return ["foo.dae"]
