# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FMaya (FApplication):
    """The class which represents Maya 7.0 to the testing framework.
    
    Note that this has only been tested on Maya 7.0 and will probably not work
    on other versions.
    
    """
    
    __PLUGIN = ("COLLADA")
    
    __MEL_SCRIPT_EXTENSION = ".mel"
    __SCRIPT_EXTENSION = ".py"

    __EXPORT_OPTIONS = [
            ("Bake transforms", "bakeTransforms", "0"),
            ("Relative paths", "relativePaths", "0"),
            ("Bake lighting", "bakeLighting", "0"),
            ("Export camera as lookat", "exportCameraAsLookat", "0"),
            ("Export polygons as triangles", "exportTriangles", "0"),
            ("Sampling", "isSampling", "0"),
            ("Curve-Contrain", "curveConstrainSampling", "0"),
            ("Sampling Function", "samplingFunction", ""),
            ("Export polygon meshes", "exportPolygonMeshes", "1"),
            ("Export lights", "exportLights", "1"),
            ("Export cameras", "exportCameras", "1"),
            ("Export joints and skin", "exportJointsAndSkin", "1"),
            ("Export animations", "exportAnimations", "1"),
            ("Export invisible nodes", "exportInvisibleNodes", "0"),
            ("Export normals", "exportNormals", "1"),
            ("Export texture coordinates", "exportTexCoords", "1"),
            ("Export per-vertex colors", "exportVertexColors", "1"),
            ("Export geometric tangents", "exportTangents", "0"),
            ("Export texture tangents", "exportTexTangents", "1"),
            ("Export constraints", "exportConstraints", "1"),
            ("Export physics", "exportPhysics", "1"),
            ("Exclusion set mode", "exclusionSetMode", "0"),
            ("Exclusion set", "exclusionSets", ""),
            ("Export references", "exportXRefs", "1"),
            ("De-Reference", "dereferenceXRefs", "0"),
            ("XFov", "cameraXFov", "0"),
            ("YFov", "cameraYFov", "1")]
    
    __RENDER_ANIMATION_START = "Animation Start Frame"
    __RENDER_ANIMATION_END = "Animation End Frame"
    __RENDER_ANIMATION_STEP = "Animation Step Interval"
    __RENDER_STILL_START = "Non-Animation Start Frame"
    __RENDER_STILL_END = "Non-Animation End Frame"
    __RENDER_STILL_STEP = "Non-Animation Step Interval"
    __RENDER_WIDTH = "X resolution"
    __RENDER_HEIGHT = "Y resolution"
    __RENDER_ARD = "Device Aspect Ratio (empty to ignore)"
    __RENDER_FORMAT = "Output Filetype"
    __RENDER_OPTIONS = [
            ("Camera", "-cam", "\"|testCamera\""),
            ("Renderer", "-r", "ctfHw"),
            (__RENDER_WIDTH, "-x", "512"),
            (__RENDER_HEIGHT, "-y", "512"),
            (__RENDER_ARD, "-ard", "1.0"),
            (__RENDER_ANIMATION_START, "-s", "1"),
            (__RENDER_ANIMATION_END, "-e", "45"),
            (__RENDER_ANIMATION_STEP, "-b", "3"),
            (__RENDER_STILL_START, "-s", "1"),
            (__RENDER_STILL_END, "-e", "1"),
            (__RENDER_STILL_STEP, "-b", "1"),
            (__RENDER_FORMAT, "-of", "png")]

    def __init__(self, configDict):
        """__init__() -> FMaya"""
        FApplication.__init__(self, configDict)
        self.__melScript = None
        self.__script = None
        self.__currentFilename = None
        self.__currentImportProperName = None
        self.__testImportCount = 0
        self.__testRenderCount = 0
        self.__workingDir = None
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "Maya 7.0"
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == IMPORT):
            return []
        elif (operation == EXPORT):
            options = []
            for entry in FMaya.__EXPORT_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        elif (operation == RENDER): 
            options = []
            for entry in FMaya.__RENDER_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        else:
            return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        melFilename = ("script" + str(self.applicationIndex) + 
                FMaya.__MEL_SCRIPT_EXTENSION)
        pyFilename = ("script" + str(self.applicationIndex) + 
                FMaya.__SCRIPT_EXTENSION)
        self.__melScript = open(os.path.join(workingDir, melFilename) , "w")
        self.__script = open(os.path.join(workingDir, pyFilename), "w")
        self.WriteCrashDetectBegin(self.__script)
        
        self.__melScript.write(
                "int $descriptor;\n" +
                "catch(`loadPlugin \"" + 
                FMaya.__PLUGIN.replace("\\", "\\\\") + "\"`);\n" +
                "catch(`file -f -new`);\n\n" +
                "proc fixNewlines(string $filename) {\n" +
                "    $tempFilename = $filename + \".temp\";\n" +
                "\n" +
                "    $file=`fopen $filename \"r\"`;\n" +
                "    $tempFile=`fopen $tempFilename \"w\"`;\n" +
                "\n" +
                "    string $nextLine = `fgetline $file`;\n" +
                "    while (size($nextLine) > 0) { \n" +
                "        fprint $tempFile `substitute \"\\n\" " + 
                "$nextLine \"\\r\\n\"`;\n" +
                "        $nextLine = `fgetline $file`;\n" +
                "    }\n" +
                "    fclose $tempFile;\n" +
                "    fclose $file;\n" +
                "\n" +
                "    sysFile -delete $filename;\n" +
                "    sysFile -rename $filename $tempFilename;\n" +
                "}\n\n")
        
        self.__testImportCount = 0
        self.__testRenderCount = 0
        self.__workingDir = workingDir
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
        self.__script.close()
        self.__melScript.close()
    
    def RunScript(self):
        """RunScript() -> None
        
        Implements FApplication.RunScript()
        
        """
        if (not os.path.isfile(self.configDict["mayaPath"])):
            print "Maya does not exist"
            return True
        
        command = ("\"" + self.configDict["mayaPath"] + 
                   "\" -batch -script \"" + self.__melScript.name + "\"")
        
        # quotes around command is awkward, but seems like the only way works
        print ("start running " + os.path.basename(self.__melScript.name))
        returnValueImport = self.RunApplication(command, self.__workingDir)
        if (returnValueImport == 0):
            print "finished running " + os.path.basename(self.__melScript.name)
        else:
            print "crashed running " + os.path.basename(self.__melScript.name)
        
        # quotes around command is awkward, but seems like the only way works
        print ("start running " + os.path.basename(self.__script.name))
        command = ("\"" + self.configDict["pythonExecutable"] + "\" " +
                   "\"" + self.__script.name + "\"")
                
        returnValueRender = subprocess.call(command)
        
        if (returnValueRender == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
        
        return ((returnValueImport == 0) and (returnValueRender == 0))
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport(). Assumes a COLLADA, maya binary,
        or maya ascii file is being imported.
        
        """
        baseName = FUtils.GetProperFilename(filename)
        self.__currentImportProperName = baseName
        output = (os.path.join(outputDir, baseName)).replace("\\", "/")
        filename = filename.replace("\\", "/")
        self.__currentFilename = output + ".mb"
        
        extension = os.path.basename(filename).rsplit(".", 1)[1]
        
        if (extension == "mb"): 
            command = ("catch(`file -type \"mayaBinary\" -o \"" + filename + 
                       "\"`);\n")
        elif (extension == "ma"): 
            command = ("catch(`file -type \"mayaAscii\" -o \"" + filename + 
                       "\"`);\n")
        else: 
            command = ("catch(`file -type \"COLLADA importer\" -o \"" + 
                       filename + "\"`);\n")
        
        self.__melScript.write(
                "$logname = \"" + logname.replace("\\", "/") + "\";\n" +
                "$descriptor = `cmdFileOutput -o $logname`;\n" +
                "catch(`file -f -new`);\n" +
                command +
                "catch(`file -rename \"" + output + "\"`);\n" +
                "catch(`file -save -type \"mayaBinary\"`);\n" +
                "cmdFileOutput -c $descriptor;\n" + 
                "fixNewlines $logname;\n\n")
        
        self.__testImportCount = self.__testImportCount + 1
        
        return [os.path.normpath(baseName + ".mb"),]
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
        baseName = self.__currentImportProperName
        output = os.path.normpath(os.path.join(outputDir, baseName))
        outputDir = os.path.dirname(output)
        
        command = "Render -rd \"" + outputDir + "\" "
        for setting in settings:
            prettyName = setting.GetPrettyName()
            if (prettyName == FMaya.__RENDER_ANIMATION_START):
                if (not isAnimated):
                    continue
                start = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FMaya.__RENDER_ANIMATION_END):
                if (not isAnimated):
                    continue
                end = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FMaya.__RENDER_ANIMATION_STEP):
                if (not isAnimated):
                    continue
                step = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FMaya.__RENDER_STILL_START):
                if (isAnimated):
                    continue
                start = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FMaya.__RENDER_STILL_END):
                if (isAnimated):
                    continue
                end = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FMaya.__RENDER_STILL_STEP):
                if (isAnimated):
                    continue
                step = self.GetSettingValueAs(FMaya.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FMaya.__RENDER_ARD):
                if (setting.GetValue().strip() == ""):
                    continue
            elif (prettyName == FMaya.__RENDER_FORMAT):
                outputFormat = setting.GetValue().strip()
                if (outputFormat == ""):
                    outputFormat = self.FindDefault(FMaya.__RENDER_OPTIONS, 
                                                    FMaya.__RENDER_FORMAT)
            
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FMaya.__RENDER_OPTIONS, 
                                         setting.GetPrettyName())
            
            command = (command + setting.GetCommand() + " " + value + " ")
        
        command = (command + 
                   " -im \"" + baseName + "\" \"" + 
                   os.path.normpath(self.__currentFilename) + "\"")
        
        self.WriteCrashDetect(self.__script, command, logname)
        
        outputList = []
        numDigit = len(str(end))
        for i in range(start, end + 1, step):
            outputTemp = baseName
            paddingCount = numDigit - len(str(i))
            for j in range(0, paddingCount):
                outputTemp = outputTemp + "0"
            outputTemp = outputTemp + str(i) + "." + outputFormat
            outputList.append(os.path.normpath(outputTemp))
            
            self.__script.write(
                    "oldFilename = \"" + 
                            (output + "." + outputFormat).replace("\\", "\\\\")
                            + "." + str(i) + "\"\n"
                    "try:\n" +
                    "    os.rename(oldFilename, '" + os.path.join(outputDir, 
                    os.path.basename(outputTemp)).replace("\\", "\\\\") + 
                    "')\n" +
                    "except Exception, e:\n" +
                    "    log = open('" + logname.replace("\\", "\\\\") + 
                            "', \"a\")\n" +
                    "    log.write(\"\\nError: unable to rename: \" + " +
                            "oldFilename + \"\\n\")" +
                    "\n    log.write(str(e) + \"\\n\")\n" +
                    "    log.close()\n\n")
        
        self.__testRenderCount = self.__testRenderCount + 1
        
        return outputList
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
        basename = self.__currentImportProperName + ".dae"
        output = os.path.join(outputDir, self.__currentImportProperName)
        output = output.replace("\\", "/")
        
        options = ""
        for setting in settings:
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FMaya.__EXPORT_OPTIONS, 
                                         setting.GetPrettyName())
            
            options = (options + setting.GetCommand() + "=" + 
                       value + ";")
        
        self.__melScript.write(
                "$logname = \"" + logname.replace("\\", "/") + "\";\n" +
                "$descriptor = `cmdFileOutput -o $logname`;\n" +
                "catch(`file -op \"" + options + 
                "\" -typ \"COLLADA exporter\" -pr -ea \"" + output + 
                "\"`);\n" +
                "cmdFileOutput -c $descriptor;\n" + 
                "fixNewlines $logname;\n\n")  
        
        return [os.path.normpath(basename),]
    