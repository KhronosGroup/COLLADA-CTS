# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path
import shutil
import Core.Common.FUtils as FUtils

from stat import *
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FMaya_UIRender (FApplication):
    """The class which represents Maya 7.0 to the testing framework.
    
    Note that this has only been tested on Maya 7.0 and will probably not work
    on other versions.
    
    """
    
    __PLUGIN = ("COLLADA")
    
    __MEL_SCRIPT_EXTENSION = ".mel"
    __SCRIPT_EXTENSION = ".py"
    
    __IMPORT_OPTIONS = [
            ("Import document up-axis", "importUpAxis", "0"),
            ("Import document units", "importUnits", "0")]

    __EXPORT_OPTIONS = [
            ("Bake transforms", "bakeTransforms", "0"),
            ("Relative paths", "relativePaths", "0"),
            ("Bake lighting", "bakeLighting", "0"),
            ("Export camera as lookat", "exportCameraAsLookat", "0"),
            ("Export polygons as triangles", "exportTriangles", "0"),
            ("Sampling", "isSampling", "0"),
            ("Curve-Contrain", "curveConstrainSampling", "0"),
            ("Sampling Function", "samplingFunction", ""),
            ("Static curve removal", "removeStaticCurves", "1"),
            ("Export polygon meshes", "exportPolygonMeshes", "1"),
            ("Export lights", "exportLights", "1"),
            ("Export cameras", "exportCameras", "1"),
            ("Export joints and skin", "exportJointsAndSkin", "1"),
            ("Export animations", "exportAnimations", "1"),
            ("Export invisible nodes", "exportInvisibleNodes", "0"),
            ("Export default cameras", "exportDefaultCameras", "0"),
            ("Export normals", "exportNormals", "1"),
            ("Export texture coordinates", "exportTexCoords", "1"),
            ("Export per-vertex colors", "exportVertexColors", "1"),
            ("Export per-vertex color animations", "exportVertexColorAnimations", "1"),
            ("Export geometric tangents", "exportTangents", "0"),
            ("Export texture tangents", "exportTexTangents", "1"),
            ("Export materials only", "exportMaterialsOnly", "0"),
            ("Export constraints", "exportConstraints", "1"),
            ("Export physics", "exportPhysics", "1"),
            ("Exclusion set mode", "exclusionSetMode", "0"),
            ("Exclusion set", "exclusionSets", ""),
            ("Export external references", "exportXRefs", "1"),
            ("De-Reference external references", "dereferenceXRefs", "0"),
            ("XFov", "cameraXFov", "0"),
            ("YFov", "cameraYFov", "1")]

    __RENDER_CAMERA = "Camera"
    __RENDER_RENDERER = "Renderer"
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
            (__RENDER_CAMERA, "- NOT USED -", "|testCamera"),
            (__RENDER_WIDTH, "- NOT USED -", "300"),
            (__RENDER_HEIGHT, "- NOT USED -", "300"),
            (__RENDER_ANIMATION_START, "setAttr defaultRenderGlobals.startFrame ", "1"),
            (__RENDER_ANIMATION_END, "setAttr defaultRenderGlobals.endFrame ", "45"),
            (__RENDER_ANIMATION_STEP, "setAttr defaultRenderGlobals.byFrameStep ", "3"),
            (__RENDER_STILL_START, "setAttr defaultRenderGlobals.startFrame ", "1"),
            (__RENDER_STILL_END, "setAttr defaultRenderGlobals.endFrame ", "1"),
            (__RENDER_STILL_STEP, "setAttr defaultRenderGlobals.byFrameStep ", "1")]

    def __init__(self, configDict):
        """__init__() -> FMaya_UIRender"""
        FApplication.__init__(self, configDict)
        self.__melScript = None
        self.__currentFilename = None
        self.__currentImportProperName = None
        self.__testImportCount = 0
        self.__workingDir = None
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "Maya - UIRender"
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        options = []
        
        # Retrieve the list of options for this operation.
        optionList = None
        if operation == IMPORT: optionList = FMaya_UIRender.__IMPORT_OPTIONS
        elif operation == EXPORT: optionList = FMaya_UIRender.__EXPORT_OPTIONS
        elif operation == RENDER: optionList = FMaya_UIRender.__RENDER_OPTIONS

        # Return a correctly-processed list of FSettingEntry's.
        if optionList != None:
            for entry in optionList:
                options.append(FSettingEntry(*entry))
        return options
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        melFilename = ("script" + str(self.applicationIndex) + FMaya_UIRender.__MEL_SCRIPT_EXTENSION)
        self.__melScript = open(os.path.join(workingDir, melFilename) , "w")
        
        self.__melScript.write(
                "int $descriptor;\n" +
                "catch(`loadPlugin \"" + 
                FMaya_UIRender.__PLUGIN.replace("\\", "\\\\") + "\"`);\n" +
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
        self.__workingDir = workingDir
        self.__renderFolders = []
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
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
            
        # Maya has a tendency to dump images where I don't want them to be.
        # Look for images in the sub-folders of the output folder and move them to the output folder.
        for renderFolder in self.__renderFolders:
            subFolders = [renderFolder]
            while (len(subFolders) > 0):
                subFolder = subFolders[-1]
                subFolders.pop()
                
                for dirEntry in os.listdir(subFolder):
                    pathname = os.path.join(subFolder, dirEntry)
                    mode = os.stat(pathname)[ST_MODE]
                    if S_ISDIR(mode):
                        # Add this sub-folder to our queue.
                        subFolders.append(pathname)
                    elif S_ISREG(mode):
                        # Process all python script files, except for the __init__.py ones.
                        if FUtils.GetExtension(pathname).lower() == "png":
                            shutil.move(pathname, os.path.join(renderFolder, dirEntry))
        self.__renderFolders = []
        
        return (returnValueImport == 0)
            
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated):
        """WriteImport(filename, logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteImport(). Assumes a COLLADA, maya binary,
        or maya ascii file is being imported.
        
        """
        baseName = FUtils.GetProperFilename(filename)
        self.__currentImportProperName = baseName
        output = (os.path.join(outputDir, baseName)).replace("\\", "/")
        filename = filename.replace("\\", "/")
        self.__currentFilename = output + ".mb"
        
        # Generate the import options string.
        options = ""
        for setting in settings:
            value = setting.GetValue().strip()
            if len(value) == 0:
                value = self.FindDefault(FMaya_UIRender.__IMPORT_OPTIONS, setting.GetPrettyName())
            options = (options + setting.GetCommand() + "=" + value + ";")
        
        # Generate the import MEL command.
        extension = FUtils.GetExtension(filename).lower()        
        if (extension == "mb"): 
            command = ("catch(`file -type \"mayaBinary\" -o \"" + filename + "\"`);\n")
        elif (extension == "ma"): 
            command = ("catch(`file -type \"mayaAscii\" -o \"" + filename + "\"`);\n")
        else: 
            command = ("catch(`file -type \"COLLADA importer\" -op \"" + options + "\" -o \"" + filename + "\"`);\n")

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
    
    def WriteRender(self, logname, outputDir, settings, isAnimated):
        """WriteRender(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
        baseName = self.__currentImportProperName
        output = os.path.normpath(os.path.join(outputDir, baseName))
        outputDir = os.path.dirname(output)
                
        self.__melScript.write(
                "$logname = \"" + logname.replace("\\", "/") + "\";\n" +
                "$descriptor = `cmdFileOutput -o $logname`;\n")

        # Set render globals example:
        # Maya node types: renderGlobals, hardwareRenderGlobals, 
        # setAttr hardwareRenderGlobals.frameBufferFormat 0

        for setting in settings:
            
            # Start by parsing the value.
            value = setting.GetValue().strip()
            if (len(value) == 0):
                value = self.FindDefault(FMaya_UIRender.__RENDER_OPTIONS, setting.GetPrettyName())

            prettyName = setting.GetPrettyName()
            if (prettyName == FMaya_UIRender.__RENDER_ANIMATION_START):
                if not isAnimated: continue
                start = int(value)
            elif (prettyName == FMaya_UIRender.__RENDER_ANIMATION_END):
                if not isAnimated: continue
                end = int(value)
            elif (prettyName == FMaya_UIRender.__RENDER_ANIMATION_STEP):
                if not isAnimated: continue
                step = int(value)
                
            elif (prettyName == FMaya_UIRender.__RENDER_STILL_START):
                if isAnimated: continue
                start = int(value)
            elif (prettyName == FMaya_UIRender.__RENDER_STILL_END):
                if isAnimated: continue
                end = int(value)
            elif (prettyName == FMaya_UIRender.__RENDER_STILL_STEP):
                if isAnimated: continue
                step = int(value)
                
            # Record these settings for later.                
            elif (prettyName == FMaya_UIRender.__RENDER_WIDTH):
                width = value
                continue
            elif (prettyName == FMaya_UIRender.__RENDER_HEIGHT):
                height = value
                continue
            elif (prettyName == FMaya_UIRender.__RENDER_CAMERA):
                camera = value
                continue
            
            self.__melScript.write(setting.GetCommand() + " " + value + ";\n")
        
        self.__melScript.write("setAttr defaultRenderGlobals.imageFormat 32;\n") # where 32 is PNG.
        self.__melScript.write("setAttr -type \"string\" defaultRenderGlobals.imageFilePrefix \"" + str(baseName) + "\";\n")
        self.__melScript.write("setAttr defaultRenderGlobals.animation " + str(isAnimated).lower() + ";\n")
        self.__melScript.write("setAttr defaultRenderGlobals.putFrameBeforeExt true;\n")
        self.__melScript.write("workspace -renderType \"images\" \"" + outputDir.replace("\\", "/") + "\";\n")
        self.__melScript.write("catch(`hwRender -camera \"" + camera + "\" -width " + width + " -height " + height + "`);\n\n")
        self.__melScript.write("cmdFileOutput -c $descriptor;\nfixNewlines $logname;\n\n")
                
        # Record this folder for image look-ups, because Maya spreads images in unexpected ways.
        self.__renderFolders.append(outputDir)
        
        outputList = []
        if not isAnimated:
            outputList.append(os.path.normpath(output + ".png"))
        else:
            numDigit = len(str(end))
            for i in range(start, end + 1, step):
                outputList.append(os.path.normpath(output + "." + str(i) + ".png"))

        return outputList
    
    def WriteExport(self, logname, outputDir, settings, isAnimated):
        """WriteImport(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
        basename = self.__currentImportProperName + ".dae"
        output = os.path.join(outputDir, self.__currentImportProperName)
        output = output.replace("\\", "/")
        
        options = ""
        for setting in settings:
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FMaya_UIRender.__EXPORT_OPTIONS, 
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
    