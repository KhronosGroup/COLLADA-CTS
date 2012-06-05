# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path
import subprocess

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FViewer (FApplication):
    """The class which represents Feeling Viewer to the testing framework."""
    
    __SCRIPT_EXTENSION = ".py"
    
    __IMPORT_CAMERA = "Rendering Camera"
    __IMPORT_ANIMATION_START = "Animation Start Time"
    __IMPORT_ANIMATION_END = "Animation End Time"
    __IMPORT_ANIMATION_FRAMES = "Animation Frames"
    __IMPORT_STILL_START = "Non-Animation Start Time"
    __IMPORT_STILL_END = "Non-Animation End Time"
    __IMPORT_STILL_FRAMES = "Non-Animation Frames"
    __IMPORT_OUTPUT_FORMAT = "Output Format"
    __IMPORT_OPTIONS = [
            ("Background Color", "-backColor", "0x00000000"),
            (__IMPORT_CAMERA, "-cam", "testCamera"),
            ("X resolution", "-width", "512"),
            ("Y resolution", "-height", "512"),
            (__IMPORT_OUTPUT_FORMAT, "", "png"),
            (__IMPORT_ANIMATION_START, "-startFrame", "0.0"),
            (__IMPORT_ANIMATION_END, "-endFrame", "2.0"),
            (__IMPORT_ANIMATION_FRAMES, "-numFrame", "15"),
            (__IMPORT_STILL_START, "-startFrame", "0.0"),
            (__IMPORT_STILL_END, "-endFrame", "0.0"),
            (__IMPORT_STILL_FRAMES, "-numFrame", "1")]
    
    def __init__(self, configDict):
        """__init__() -> FViewer"""
        FApplication.__init__(self, configDict)
        
        self.__workingDir = None
        self.__testCount = 0
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "Feeling Viewer"

    def GetOperationsList(self):
        """GetOperationsList() -> list_of_str
        
        Implements FApplication.GetOperationsList()
        
        """
        return [IMPORT]
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == IMPORT):
            options = []
            for entry in FViewer.__IMPORT_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
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
        filename = ("script" + str(self.applicationIndex) + 
                FViewer.__SCRIPT_EXTENSION)
        self.__script = open(os.path.join(workingDir, filename) , "w")
        
        self.WriteCrashDetectBegin(self.__script)
##        self.__script.write("import os\n\n" +
##                "os.chdir(\"" + 
##                self.configDict["feelingViewerPath"].replace("\\", "\\\\") + 
##                "\")\n\n")
        
        self.__testCount = 0
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
        if (not os.path.isfile(self.configDict["feelingViewerCLI"])):
            print "Feeling Viewer CLI does not exist"
            return True
        
        print ("start running " + os.path.basename(self.__script.name))
        command = ("\"" + self.configDict["pythonExecutable"] + "\" " +
                   "\"" + self.__script.name + "\"")
        
        returnValue = subprocess.call(command)
        
        if (returnValue == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
        
        return (returnValue == 0)
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport()
        
        """
        outputFormat = ".png"
        
        command = ("\"" + self.configDict["feelingViewerCLI"] + "\" ")
        for setting in settings:
            prettyName = setting.GetPrettyName()
            if (prettyName == FViewer.__IMPORT_ANIMATION_START):
                if (not isAnimated):
                    continue
                start = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS, 
                                               setting, float)
            elif (prettyName == FViewer.__IMPORT_ANIMATION_END):
                if (not isAnimated):
                    continue
                end = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS, 
                                             setting, float)
            elif (prettyName == FViewer.__IMPORT_ANIMATION_FRAMES):
                if (not isAnimated):
                    continue
                frameCount = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS,
                                                    setting, int)
            elif (prettyName == FViewer.__IMPORT_STILL_START):
                if (isAnimated):
                    continue
                start = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS, 
                                               setting, float)
            elif (prettyName == FViewer.__IMPORT_STILL_END):
                if (isAnimated):
                    continue
                end = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS, 
                                             setting, float)
            elif (prettyName == FViewer.__IMPORT_STILL_FRAMES):
                if (isAnimated):
                    continue
                frameCount = self.GetSettingValueAs(FViewer.__IMPORT_OPTIONS,
                                                    setting, int)
            elif (prettyName == FViewer.__IMPORT_OUTPUT_FORMAT):
                value = setting.GetValue().strip()
                if (value == ""):
                    value = self.FindDefault(FViewer.__IMPORT_OPTIONS, 
                                             FViewer.__IMPORT_OUTPUT_FORMAT)
                outputFormat = "." + value
                continue
            elif (prettyName == FViewer.__IMPORT_CAMERA):
                value = setting.GetValue().strip()
                # use default camera
                if (value == ""): continue
            
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FViewer.__IMPORT_OPTIONS, 
                                         setting.GetPrettyName())
            
            command = (command + setting.GetCommand() + " " + 
                       value + " ")
        
        baseName = FUtils.GetProperFilename(filename) + outputFormat
        outputFilename = os.path.join(outputDir, baseName)
        
        command = (command + "\"" + filename + 
                   "\" \"" + outputFilename + "\"")
        
        self.WriteCrashDetect(self.__script, command, logname)
        
        self.__testCount = self.__testCount + 1
        
        if (frameCount == 1):
            return [os.path.normpath(baseName),]
        
        outputList = []
        numDigit = len(str(frameCount))
        for i in range(0,frameCount):
            outputTemp = FUtils.GetProperFilename(filename)
            paddingCount = numDigit - len(str(i))
            for j in range(0, paddingCount):
                outputTemp = outputTemp + "0"
            outputTemp = outputTemp + str(i) + outputFormat
            outputList.append(os.path.normpath(outputTemp))
        
        return outputList
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender(). Feeling Viewer has no render.
        
        """
        pass
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteExport(). Feeling Viewer has no export.
        
        """
        pass
    