# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
            ("Output Size", "outputSize", "[300,300]"),
            (__RENDER_FILE_TYPE, "", "png"),
            ("Renderer", "renderer", "#production"),
            ("Progress Bar", "progressbar", "false"),
            ("Anti-Aliasing", "antiAliasing", "false"),
            ("Enable Pixel Sampler", "enablePixelSampler", "false"),
            ("Quite", "quiet", "true"),
            ("Radiosity", "useRadiosity", "false"),
            ("Dither True Color", "ditherTrueColor", "false"),
            ("Dither Paletted", "ditherPaletted", "false")]
    
    __EXPORT_OPTIONS = [("Normals", "normals","1"),
                        ("Triangles", "triangles", "1"),
                        ("XRefs", "xrefs", "1"),
                        ("Tangents", "tangents", "0"),
                        ("Sample animation", "sampleAnim", "0"),
                        ("Single <animation>", "singleAnim", "1"),
                        ("Bake Matrices", "bakeMatrices", "0"),
                        ("Y Up", "convertYUp", "0"),
                        ("Object Space", "objectSpace", "1"),
                        ("Fixed FX", "mixedFX", "0"),
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
            return []
        elif (operation == EXPORT):
            options = []
            for entry in FMax.__EXPORT_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        elif (operation == RENDER): 
            options = []
            for entry in FMax.__RENDER_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
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
        
        returnValue = self.RunApplication(self.configDict["maxPath"] + 
                " -U MAXScript \"" + self.__script.name + "\"", 
                self.__workingDir)
        
        if (returnValue == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
        
        if (hadConfig):
            shutil.copy2(tempFilename, filename)
            os.remove(tempFilename)
        elif (os.path.isfile(filename)):
            os.remove(filename)
        
        return (returnValue == 0)
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated):
        """WriteImport(filename, logname, outputDir, settings, isAnimated) -> list_of_str
        
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
            command = "    loadMaxFile my_importfilename quiet:true\n"
        else:
            command = "    importFile my_importfilename #noprompt\n"
        
        self.__script.write(
                "logfilename = \"" + logname.replace("\\", "\\\\") + "\"\n" +
                "openLog logfilename mode:\"w\" outputOnly:true\n" +
                "try (\n" +
                "    resetmaxfile #noprompt\n" +
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
    
    def WriteRender(self, logname, outputDir, settings, isAnimated):
        """WriteRender(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
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
    
    def WriteExport(self, logname, outputDir, settings, isAnimated):
        """WriteImport(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
        baseName = self.__currentImportProperName + ".dae"
        output = (os.path.join(outputDir, baseName)).replace("\\", "\\\\")
        
        cfgFilename = os.path.normpath(
                self.configDict["maxColladaExporterFilename"])
        cfgFilename = cfgFilename.replace("\\", "\\\\")
        
        options = ""
        for setting in settings:
            options = (options + setting.GetCommand() + "=" + 
                       setting.GetValue() + "\\n")
        
        self.__script.write(
                "logfilename = \"" + logname.replace("\\", "\\\\") + "\"\n" +
                "openLog logfilename mode:\"w\" outputOnly:true\n" +
                "try (\n" +
                "    cfgfile_ptr = createfile \"" + cfgFilename + "\"\n" +
                "    format \"" + options + "\" to:cfgfile_ptr\n" +
                "    outfile_name  = \"" + output + "\"\n" +
                "    exportFile outfile_name #noprompt\n" +
                "    close cfgfile_ptr\n"
                "    print \"Export succeeded with " + output + "\"\n" +
                ") catch (\n" +
                "    print \"Export error     with " + output + "\"\n" +
                ")\n" + 
                "flushLog()\n" +
                "closeLog()\n\n")
        
        return [os.path.normpath(baseName),]
    