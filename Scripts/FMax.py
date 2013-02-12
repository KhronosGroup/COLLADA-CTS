# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import os.path
import shutil

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FMax (FApplication):
    """The class which represents 3DS Max 7 to the testing framework.
    
    Note that this has only been tested on 3DS Max 7 and will probably not work
    on other versions.
    
    """
    
    __IMPORT_OPTIONS = [("Import Units", "importUnits","1"),
                        ("Import Up-axis", "importUpAxis", "1")]
    
    __RENDER_ANIMATION_START = "Animation Start Frame"
    __RENDER_ANIMATION_END = "Animation End Frame"
    __RENDER_ANIMATION_STEP = "Animation Step Interval"
    __RENDER_STILL_START = "Non-Animation Start Frame"
    __RENDER_STILL_END = "Non-Animation End Frame"
    __RENDER_STILL_STEP = "Non-Animation Step Interval"
    __RENDER_FILE_TYPE = "Output Filetype"
    __RENDER_OPTIONS = [
            ("Camera", "camera", "$testCamera"),
            ("Frame", "frame", "1"),
            (__RENDER_ANIMATION_START, "fromframe", "1"),
            (__RENDER_ANIMATION_END, "toframe", "45"),
            (__RENDER_ANIMATION_STEP, "nthframe", "3"),
            (__RENDER_STILL_START, "fromframe", "1"),
            (__RENDER_STILL_END, "toframe", "1"),
            (__RENDER_STILL_STEP, "nthframe", "1"),
            ("Output Size", "outputSize", "[512,512]"),
            (__RENDER_FILE_TYPE, "", "png"),
            ("Renderer", "renderer", "#production"),
            ("Progress Bar", "progressbar", "false"),
            ("Anti-Aliasing", "antiAliasing", "false"),
            ("Enable Pixel Sampler", "enablePixelSampler", "false"),
            ("Quiet", "quiet", "true"),
            ("Radiosity", "useRadiosity", "false"),
            ("Dither True Color", "ditherTrueColor", "false"),
            ("Dither Paletted", "ditherPaletted", "false")]
    
    __EXPORT_OPTIONS = [("Normals", "normals","1"),
                        ("Triangles", "triangles", "1"),
                        ("XRefs", "xrefs", "0"),
                        ("Tangents", "tangents", "1"),
                        ("Enable Animations", "animations", "1"),
                        ("Sample Animation", "sampleAnim", "0"),
                        ("Create Animation Clip", "createClip", "0"),
                        ("Bake Matrices", "bakeMatrices", "0"),
                        ("Relative Paths", "relativePaths", "1"),
                        ("Animation Start", "animStart", "0"),
                        ("Animation End", "animEnd", "100")]
    
    __EXTENSION = ".max"
    __SCRIPT_EXTENSION = ".ms"
    
    def __init__(self, configDict):
        """__init__() -> FMax"""
        FApplication.__init__(self, configDict)
        self.__script = None
        self.__currentImportProperName = None
        self.__testCount = 0
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "3DSMax 7"
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == IMPORT):
            return [FSettingEntry(*entry) for entry in FMax.__IMPORT_OPTIONS]
        elif (operation == EXPORT):
            return [FSettingEntry(*entry) for entry in FMax.__EXPORT_OPTIONS]
        elif (operation == RENDER): 
            return [FSettingEntry(*entry) for entry in FMax.__RENDER_OPTIONS]
        else:
            return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        filename = ("script" + str(self.applicationIndex) + 
                    FMax.__SCRIPT_EXTENSION)
        self.__script = open(os.path.join(workingDir, filename) , "w")
        self.__workingDir = workingDir
        self.__testCount = 0
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
        self.__script.write("quitMax #noPrompt\n")
        self.__script.close()
    
    def RunScript(self):
        """RunScript() -> None
        
        Implements FApplication.RunScript()
        
        """
        if (not os.path.isfile(self.configDict["maxPath"])):
            print "Max does not exist"
            return True
        
        filename = os.path.normpath(
                self.configDict["maxColladaExporterFilename"])
        
        hadConfig = os.path.isfile(filename)
        if (hadConfig):
            i = 0
            tempFilename = filename
            while (os.path.isfile(tempFilename)):
                tempFilename = filename + str(i)
                i = i + 1
            shutil.copy2(filename, tempFilename)
        
        """Calls 3DS MAX to run the script."""
        print ("start running " + os.path.basename(self.__script.name))
        # print "XXXX"
        
        returnValue = self.RunApplication(self.configDict["maxPath"] + 
                " -U MAXScript \"" + self.__script.name + "\"", 
                self.__workingDir)
        
        if (returnValue == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
        
        try:
            if (hadConfig):
                shutil.copy2(tempFilename, filename)
                os.remove(tempFilename)
            elif (os.path.isfile(filename)):
                os.remove(filename)
        except Exception, e:
            pass
        
        return (returnValue == 0)
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport()
        
        """
        self.__testCount = self.__testCount + 1
        baseName = FUtils.GetProperFilename(filename)
        self.__currentImportProperName = baseName
        
        baseName = baseName + FMax.__EXTENSION
        output = (os.path.join(outputDir, baseName)).replace("\\", "\\\\")
        writeableDir = os.path.dirname(filename).replace("\\", "\\\\")
        writeableFilename = filename.replace("\\", "\\\\")
        if (FUtils.GetExtension(filename) == FMax.__EXTENSION[1:]):
            command = "    loadMaxFile my_importfilename useFileUnits:true quiet:true\n"
        else:
            command = "    importFile my_importfilename #noprompt using:OpenCOLLADAImporter\n"
            
        cfgFilename = os.path.normpath(
                self.configDict["maxColladaExporterFilename"])
        cfgFilename = cfgFilename.replace("\\", "\\\\")
        
        options = "".join(["    setINISetting \"%s\" \"ColladaMax\" \"%s\" \"%s\"\n"
                           % (cfgFilename,setting.GetCommand(),setting.GetValue())
                           for setting in settings])
        
        self.__script.write(
                "logfilename = \"" + logname.replace("\\", "\\\\") + "\"\n" +
                "openLog logfilename mode:\"w\" outputOnly:true\n" +
                "try (\n" +
                "    resetmaxfile #noprompt\n" + 
                options +
                "    sysInfo.currentdir = \"" + writeableDir + "\"\n" +
                "    my_importfilename = \"" + writeableFilename + "\"\n" +
                command + 
                "    saveMaxFile \"" + output + "\"\n" +
                "    print \"Import succeeded with " + writeableFilename + 
                "\"\n" +
                ") catch (\n" +
                "    print \"Import error     with " + writeableFilename + 
                "\"\n" +
                ")\n" + 
                "flushLog()\n" +
                "closeLog()\n\n")
        
        return [os.path.normpath(baseName),]
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
        # print ("cameraRig:  " + str(cameraRig))
        command = "try (\n    render "
        for setting in settings:
            prettyName = setting.GetPrettyName()
            if (prettyName == FMax.__RENDER_ANIMATION_START):
                if (not isAnimated):
                    continue
                start = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FMax.__RENDER_ANIMATION_END):
                if (not isAnimated):
                    continue
                end = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FMax.__RENDER_ANIMATION_STEP):
                if (not isAnimated):
                    continue
                step = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FMax.__RENDER_STILL_START):
                if (isAnimated):
                    continue
                start = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FMax.__RENDER_STILL_END):
                if (isAnimated):
                    continue
                end = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FMax.__RENDER_STILL_STEP):
                if (isAnimated):
                    continue
                step = self.GetSettingValueAs(FMax.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FMax.__RENDER_FILE_TYPE):
                value = setting.GetValue().strip()
                if (value == ""):
                    value = self.FindDefault(FMax.__RENDER_OPTIONS, 
                                             FMax.__RENDER_FILE_TYPE)
                renderType = "." + value
                baseName = (self.__currentImportProperName + renderType)
                outputFilename = os.path.join(outputDir, baseName)
                outputFilename = outputFilename.replace("\\", "\\\\")
                
                command = command + "outputfile:\"" + outputFilename + "\" "
                continue
            
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FMax.__RENDER_OPTIONS, 
                                         setting.GetPrettyName())

            # print ("prettyName: " + prettyName +" value: " + value)
            
            command = (command + setting.GetCommand() + ":" + value + " ")
        
        command = (
                "logfilename = \"" + logname.replace("\\", "\\\\") + "\"\n" +
                "openLog logfilename mode:\"w\" outputOnly:true\n" +
                command + "\n" +
                "    print \"Render succeeded with " + outputFilename + 
                "\"\n" +
                ") catch (\n" +
                "    print \"Render error     with " + outputFilename + 
                "\"\n" +
                ")\n" + 
                "flushLog()\n" +
                "closeLog()\n\n")
        
        self.__script.write(command)
        
        framesList = range(start, end + 1, step)
        if (len(framesList) < 2):
            return [os.path.normpath(baseName),]
        
        outputList = []
        for i in framesList:
            paddingCount = 4 - len(str(i))
            outputTemp = self.__currentImportProperName
            for j in range(0, paddingCount):
                outputTemp = outputTemp + "0"
            outputTemp = outputTemp + str(i) + renderType
            outputList.append(os.path.normpath(outputTemp))
        return outputList
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
        baseName = self.__currentImportProperName + ".dae"
        output = (os.path.join(outputDir, baseName)).replace("\\", "\\\\")
        
        cfgFilename = os.path.normpath(
                self.configDict["maxColladaExporterFilename"])
        cfgFilename = cfgFilename.replace("\\", "\\\\")
        
        options = "".join(["    setINISetting \"%s\" \"ColladaMax\" \"%s\" \"%s\"\n"
                           % (cfgFilename,setting.GetCommand(),setting.GetValue())
                           for setting in settings])
        
        self.__script.write(
                "logfilename = \"" + logname.replace("\\", "\\\\") + "\"\n" +
                "openLog logfilename mode:\"w\" outputOnly:true\n" +
                "try (\n" + 
                options +
                "    outfile_name  = \"" + output + "\"\n" +
                "    exportFile outfile_name #noprompt using:OpenCOLLADAExporter\n" +
                "    print \"Export succeeded with " + output + "\"\n" +
                ") catch (\n" +
                "    print \"Export error     with " + output + "\"\n" +
                ")\n" + 
                "flushLog()\n" +
                "closeLog()\n\n")
        
        return [os.path.normpath(baseName),]
    