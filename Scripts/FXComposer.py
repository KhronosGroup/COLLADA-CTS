# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# Originally written by Brendan Rehon, SCEA (brendan_rehon@playstation.sony.com)

import os
import os.path
import re
import subprocess
import shutil

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FXComposer (FApplication):
    """ Introduces FX Composer 2 into the testing framework
    """
    __SCRIPT_EXTENSION = ".py"
    __EXTENSION = ".dae"
    
    __HEX_PATTERN = "^0x[\dabcdef]{8}$" # Describes a valid RGBA hex pattern

    __RENDER_PORT = "Render Port"
    __RENDER_BACKGROUND = "Background Color"
    __RENDER_CAMERA = "Camera"
    
    __RENDER_ANIMATION_START = "Animation Start Frame"
    __RENDER_ANIMATION_END = "Animation End Frame"
    __RENDER_ANIMATION_FRAMES = "Animation Frames"
    
    __RENDER_STILL_START = "Non-Animation Start Time"
    __RENDER_STILL_END = "Non-Animation End Time"
    __RENDER_STILL_FRAMES = "Non-Animation Frames"
    
    __RENDER_OUTPUT_FORMAT = "Output Format"
    
    __RENDER_WIDTH = "X resolution"
    __RENDER_HEIGHT = "Y resolution"

    __RENDER_PORT_OPTIONS = ["OpenGL", "Direct3D9"]
    __RENDER_PORT_OGL = 0
    __RENDER_PORT_D3D = 1

    __RENDER_OPTIONS = [
        (__RENDER_PORT, "", __RENDER_PORT_OPTIONS[__RENDER_PORT_OGL]), 
        (__RENDER_BACKGROUND, "", "0xFFFFFFFF"), 
        (__RENDER_CAMERA, "", "testCamera"), 
        
        (__RENDER_ANIMATION_START, "", "0.0"), 
        (__RENDER_ANIMATION_END, "", "2.0"), 
        (__RENDER_ANIMATION_FRAMES, "", "15"), 
        
        (__RENDER_STILL_START, "", "0.0"), 
        (__RENDER_STILL_END, "", "0.0"), 
        (__RENDER_STILL_FRAMES, "", "1"), 
        
        (__RENDER_WIDTH, "", "300"), 
        (__RENDER_HEIGHT, "", "300"), 
        (__RENDER_OUTPUT_FORMAT, "", "png")]
    
    
    def __init__(self, configDict):
        """__init__() -> FXComposer"""
        FApplication.__init__(self, configDict)
        self.__script = None
        self.__workingDir = None
        self.__testCount = 0
        self.__hex_prog = re.compile(self.__HEX_PATTERN)
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "NVIDIA FX Composer 2"
    
    def GetOperationsList(self):
        """GetOperationsList() -> list_of_str
        
        Implements FApplication.GetOperationsList()
        
        """
        return [IMPORT, RENDER, EXPORT]
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == RENDER):
            options = []
            for entry in FXComposer.__RENDER_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        else:
            return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        filename = ("script" + str(self.applicationIndex) + 
                FXComposer.__SCRIPT_EXTENSION)
        self.__script = open(os.path.join(workingDir, filename) , "w")

        # Write FXC specific script imports
        self.__script.write(
            "from fxcapi import *\n"+
            "from FXComposer.Scene.Commands import *\n"+
            "from FXComposer.UI.Animation import *\n"+ # For animation playback
            "from FXComposer.IDE.Services import *\n\n"+
            "import os, re\n\n"+
            "CTS_DEFAULT_CAMERAS = re.compile(r\"(Top)|(Front)|(Right)|(Perspective)$\")\n\n"
            
            # Define functions to overcome FXC's Python script limit from the command line
            
            # SaveFile: Save imported assets to a COLLADA file.
            # @param  path  location to save the COLLADA file
            # @param  name  name of the COLLADA file
            # @param  log   error log
            "def ctsSaveFile(path, name, log):\n"+
            "    try:\n"+
            "        FXProjectService.Instance.SaveAssetCollection(FXRuntime.Instance.Library.ActiveAssetCollection, FXUri(path))\n"+
            "    except:\n"+
            "        log.write(\"Error: %s failed to save!\\n\" % name)\n"+
            "    else:\n"+
            "        log.write(\"%s saved successfully.\\n\" % name)\n\n"+
            
            # ImportFile: Import a pre-existing COLLADA file into FXC and then save a copy.
            # @see SaveFile
            # @param  path     the import COLLADA file's location
            # @param  name     name of the saved COLLADA file
            # @param  logname  error log's filepath
            # @param  output   location to save the COLLADA file
            # @return a boolean flag that is true iff the COLLADA file successfully imports
            "def ctsImportFile(path,name,logname,output):\n"+
            "    FXProjectService.Instance.ResetProject()\n"+
            "    import_error_log = open(logname,'w')\n"+
            "    import_successful = True\n"+
            "    try:\n"+
            "        FXProjectService.Instance.AddDocument(FXUri(path))\n"+
            "    except:\n"+
            "        import_error_log.write(\"Error: %s failed to load!\\n\" % name)\n"+
            "        print \"Error: %s failed to load!\" % name\n"+
            "        import_successful = False\n"+
            "    else:\n"+
            "        import_error_log.write(\"%s loaded successfully.\\n\" % name)\n"+
            "        ctsSaveFile(output,name,import_error_log)\n"
            "    import_error_log.close()\n"+
            "    return import_successful\n\n"+
            
            # BindToTestLight: Bind all materials to the first light found in the active scene.
            # @param  scene  the active scene
            "def ctsBindToTestLight(scene):\n"+
            "    lightlist = []\n"+
            "    [lightlist.append(x) for x in scene.FindItems(FXLightInstance)]\n"+
            "    if len(lightlist) > 0:\n"+
            "        top_light = lightlist[0]\n"+
            "        FXDefaultLightBinding.BindMaterialsToLightInstance(top_light.Uri,top_light)\n\n"+
            
            # GetTestCamera: Find a render camera whose name matches the render camera test setting
            #                If there is no match, use the first non-default camera found in the scene.
            #                If there are only default lights in the scene, use the default freeform camera.
            # @param  scene        the active scene
            # @param  camera_name  the render camera test setting to match
            # @param  log          error log
            # @return the render camera
            "def ctsGetTestCamera(scene,camera_name,log):\n"+
            "    test_candidates = []\n"+
            "    [test_candidates.append(x) for x in scene.FindItems(FXCameraInstance) if CTS_DEFAULT_CAMERAS.match(x.Name) == None]\n"+
            "    if test_candidates == []:\n"+
            "        log.write(\"Warning: Can't find user specified camera. Using default perspective camera instead.\\n\")\n"+
            "        return scene.GetDefaultCamera(FXCameraType.Freeform)\n"+
            "    else:\n"+
            "        templist = [test_candidates.pop()]\n"+
            "        [templist.append(x) for x in test_candidates if x.ParentNode.Name.lower().startswith(camera_name) or x.Camera.Name.lower().startswith(camera_name)]\n"+
            "        return templist.pop()\n\n"+
            
            # SetupTestCamera: Find a suitable render camera for the test and bind it to a render port.
            # @see GetTestCamera
            # @param  port  the render port
            "def ctsSetupTestCamera(port,scene,camera_name,log):\n"+
            "    testcamera = ctsGetTestCamera(scene,camera_name,log)\n"+
            "    if testcamera != None:\n"+
            "        port.CurrentCamera = testcamera\n\n"+
            
            # SetupRender: Bind the test lights, set the background color and dimensions of the render port, 
            #              hide all non-geometry (lights, grid, HUD), and activate the render port.
            # @see BindToTestLight
            # @param  port             the render port
            # @param  scene            the active scene
            # @param  width            desired render port width
            # @param  height           desired render port height
            # @param  backgroundColor  desired render port background color 
            "def ctsSetupRender(port,scene,width,height,backgroundColor):\n"+
            "    ctsBindToTestLight(scene)\n"+
            "    FxcScene.ShowGrid(scene, 0)\n"+
            "    FxcScene.ShowCameras(scene, 0)\n"+ 
            "    FxcScene.ShowLights(scene, 0)\n"+ 
            "    FxcRender.EnableRenderPortHud(port, 0)\n"+
            "    FxcScene.SetBackgroundColor(FXMatrix.Vector4(backgroundColor[0],backgroundColor[1],backgroundColor[2],backgroundColor[3]))\n"+
            "    FxcRender.SetActiveRenderPort(port)\n"+
            "    FxcRender.SetRenderPortSize(port,width,height)\n\n"+
            
            # Clamp: A standard clamp function -- clamp value x into the range [min_val,max_val].
            # @param  x        value to clamp
            # @param  min_val  minimum
            # @param  max_val  maximum
            # @return the clamped value
            "def ctsClamp(x,min_val,max_val):\n"+
            "    curr_val = x\n"
            "    if curr_val > max_val:\n"+
            "        curr_val = max_val\n"+
            "    elif curr_val < min_val:\n"+
            "        curr_val = min_val\n"+
            "    return curr_val\n\n"+
            
            # GetOutputFile: Format a render file name into the form [filename]0*x.[extension] where x is the frame number 
            # @param  filename     the output file's path or basename
            # @param  numDigits    the maximum number digits required to write the largest frame number (in absolute value)
            # @param  frame        an integer representing current frame number
            # @param  frameNumber  a string representing the frame number iff the scene is animated
            # @param  extension    the output file's extensions (.png, .bmp, etc)
            # @return the formatted output file name
            "def ctsGetOutputFile(filename,numDigit,frame,frameNumber,extension):\n"
            "    out_file = filename\n" +
            "    paddingCount = numDigit - len(str(frame))\n"+
            "    for j in range(paddingCount):\n"+
            "        out_file = out_file + '0'\n"+          
            "    return out_file + frameNumber + extension\n\n"+
            
            # RenderFrames: Render out all the frames.
            # @see GetOutputFile
            # @param  port          the active renderport
            # @param  frameCount    number of frames to render out
            # @param  filename      the output files' path + basename
            # @param  cts_start     start of the animation (via CTS test setting)
            # @param  cts_end       end of the animation (via CTS test setting)
            # @param  outputFormat  the output files' file format extension (.png, .bmp, etc]
            "def ctsRenderFrames(port,frameCount,cts_start,cts_end,filename,outputFormat):\n"+
            "    starttime, endtime = FxcAnimationPlayback.GetStartFrame(), FxcAnimationPlayback.GetEndFrame()\n"+
            "    numDigits = len(str(frameCount))\n"+
            "    for frame in range(frameCount):\n"+
            # Prepare a safe value for linear interpolation
            "        if frameCount > 1:\n"+
            "            safe_fc = float(frameCount-1)\n"+
            "            safe_fn = str(frame)\n"+
            "        else:\n"+
            "            safe_fc = 1.0\n"+
            "            safe_fn = \"\"\n"+
            "        lerp = frame/safe_fc\n"
            "        currtime = ctsClamp(cts_start*(1.0-lerp)+cts_end*lerp,starttime,endtime)\n"+
            "        FxcAnimationPlayback.SetCurrentFrame(currtime)\n"+
            "        ForceRedraw()\n"+
            "        outfile = ctsGetOutputFile(filename,numDigits,frame,safe_fn,outputFormat)\n"+
            "        FxcRender.SaveRenderPortImage(port, outfile)\n\n"+
            
            # InvalidSceneOrPort: Assuming an invalid scene and/or render port, specifically report the error.
            # @param  port   the possibly invalid render port (i.e. it wasn't found)
            # @param  scene  the possibly invalid active scene (i.e. it wasn't found)
            # @param  log    error log (from the render stage)
            "def ctsInvalidSceneOrPort(scene,port,log):\n"+
            "    if scene is None:\n"+
            "        log.write(\"Error: Could not find render scene.\\n\")\n"+
            "    if port is None:\n"+
            "        log.write(\"Error: Could not find render port.\\n\")\n\n"+
            
            "FxcCommand.BeginGroup(\"FXC Conformance Test Import and Rendering\")\n")
        
        self.__testCount = 0
        self.__workingDir = workingDir
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
        self.__script.write(
            "FxcCommand.EndGroup()\n"+
#            Undo everything the regression script just did.
#            "Undo()\n"+
            "FXProjectService.Instance.ResetProject()\n\n"+
            "try:\n"+
            "    Fxc.Exit()\n"
            "except:\n"+
            "    print \"An unexpected error occurred while closing. Please close FXC 2.0 manually.\"\n")
        
        self.__script.close()
    
    def RunScript(self):
        """RunScript() -> None
        
        Implements FApplication.RunScript()
        
        """
        if (not os.path.isfile(self.configDict["FXComposerPath"])):
            print "NVIDIA FX Composer 2 does not exist"
            return True

        file_name = os.path.basename(self.__script.name)
        
        print ("start running " + file_name)
        
        command = ("\"" + self.configDict["FXComposerPath"] + 
                   "\" \"" + self.__script.name + "\"")
        
        returnValue = self.RunApplication(command, self.__workingDir)
        
        if (returnValue == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
        
        return (returnValue == 0)
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport().
        
        """
        self.__testCount = self.__testCount + 1
        name_only = FUtils.GetProperFilename(filename)
        self.__currentImportProperName = name_only
        output = (os.path.join(outputDir, name_only))+self.__EXTENSION
        
        self.__script.write(
            "if ctsImportFile(r\""+filename+"\",\""+name_only+"\",r\""+logname+"\",r\""+output+"\"):\n"+
            "    print \""+name_only+"\",\"loaded.\"\n"
            )
        
        return [output, ]
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
        
        name_only = self.__currentImportProperName
        
        for setting in settings:
            
            prettyName = setting.GetPrettyName()

            #   Non-animation: start, end and total number of frames
            if (prettyName == FXComposer.__RENDER_ANIMATION_START):
                if (not isAnimated):
                    continue
                start = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                               setting, float)
            elif (prettyName == FXComposer.__RENDER_ANIMATION_END):
                if (not isAnimated):
                    continue
                end = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                             setting, float)
            elif (prettyName == FXComposer.__RENDER_ANIMATION_FRAMES):
                if (not isAnimated):
                    continue
                frameCount = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                                    setting, int)
            #   Animation: start, end and total number of frames
            elif (prettyName == FXComposer.__RENDER_STILL_START):
                if (isAnimated):
                    continue
                start = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                               setting, float)
            elif (prettyName == FXComposer.__RENDER_STILL_END):
                if (isAnimated):
                    continue
                end = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                             setting, float)
            elif (prettyName == FXComposer.__RENDER_STILL_FRAMES):
                if (isAnimated):
                    continue
                frameCount = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                                    setting, int)
            #   Render image dimensions: width and height
            elif (prettyName == FXComposer.__RENDER_WIDTH):
                width = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                                    setting, int)
            elif (prettyName == FXComposer.__RENDER_HEIGHT):
                height = self.GetSettingValueAs(FXComposer.__RENDER_OPTIONS, 
                                                    setting, int)
            #   Render image format
            elif (prettyName == FXComposer.__RENDER_OUTPUT_FORMAT):
                value = setting.GetValue().strip()
                if (value == ""):
                    value = self.FindDefault(FXComposer.__RENDER_OPTIONS, 
                                             FXComposer.__RENDER_OUTPUT_FORMAT)
                outputFormat = "." + value
            #   Render camera
            elif (prettyName == FXComposer.__RENDER_CAMERA):
                value = setting.GetValue().strip()
                if (value == ""):
                    value = self.FindDefault(FXComposer.__RENDER_OPTIONS, 
                                             FXComposer.__RENDER_CAMERA)
                outputCamera = value.lower()
            #   Render background: a hex value 0x[R][G][B][A] where [*] is a byte
            elif (prettyName == FXComposer.__RENDER_BACKGROUND):
                
                value = setting.GetValue().strip().lower()
                
                # If the string is not a hex pattern, use the default
                if not self.__hex_prog.match(value):
                    value = self.FindDefault(FXComposer.__RENDER_OPTIONS, 
                                             FXComposer.__RENDER_BACKGROUND)
                
                # Strip opening characters
                value = value[value.find("0x")+2:]
                
                backgroundColor = []
                # Populate RGBA values as floats in [0,1]
                [backgroundColor.append(int(value[i-2:i], 16)/255.0) for i in [2, 4, 6, 8]]
                
            #   Render port
            elif (prettyName == FXComposer.__RENDER_PORT):
                value = setting.GetValue().strip()
                #   Since render port names are very specific, intelligently find closest match
                vallow = value.lower() 
                if vallow.find("d3d") != -1 or vallow.find("direct") != -1:
                    value = FXComposer.__RENDER_PORT_OPTIONS[FXComposer.__RENDER_PORT_D3D]
                elif vallow.find("gl") != -1 or vallow.find("open") != -1 :
                    value = FXComposer.__RENDER_PORT_OPTIONS[FXComposer.__RENDER_PORT_OGL]
                #    If blank, use the default port option
                elif vallow == "":
                    value = self.FindDefault(FXComposer.__RENDER_OPTIONS, 
                                             FXComposer.__RENDER_PORT)
                #    Otherwise, assume the user knows what they're doing
                outputPort = value
        
        outputList = []
        
        # Rendered file list (you'll see this routine in other CTS scripts)
        if frameCount == 1:
            outputList.append(os.path.join(outputDir, name_only + outputFormat))
        else:
            numDigit = len(str(frameCount))
            for i in range(0, frameCount):
                outputTemp = name_only
                paddingCount = numDigit - len(str(i))
                for j in range(0, paddingCount):
                    outputTemp = outputTemp + "0"
                outputTemp = outputTemp + str(i) + outputFormat
                outputList.append(os.path.join(outputDir, outputTemp))
        
        self.__script.write(
            # Resume script after importing  the COLLADA file after a try-except-else statement
            "    render_error_log = open(r\""+logname+"\",'w')\n"+
            "    port = FxcRender.FindRenderPort(\""+outputPort+"\")\n"+
            "    scene = FXSceneService.Instance.ActiveScene\n\n"+
                      
            "    if scene != None and port != None:\n"+
            "        ctsSetupTestCamera(port,scene,r\""+str(outputCamera)+"\",render_error_log)\n"+
            "        ctsSetupRender(port,scene,"+str(width)+","+str(height)+","+str(backgroundColor)+")\n"+        
            "        ctsRenderFrames(port,"   +str(frameCount)+","+str(start)+","+str(end)
                                       +",r\""+os.path.join(outputDir, name_only)+"\",\""+outputFormat+"\")\n"+
            "        render_error_log.write(\""+name_only+" has successfully rendered.\\n\")\n"+
            "    else:\n"+
            "        ctsInvalidSceneOrPort(scene,port,render_error_log)\n"+
            "    render_error_log.close()\n\n")
    
        return outputList
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_strImplements FApplication.WriteExport(). Feeling Viewer has no export.

        Implements FApplication.WriteExport().

        """
        
        name_only = self.__currentImportProperName
        output = (os.path.join(outputDir, name_only))+self.__EXTENSION
        
        self.__script.write(
        "    output_error_log = open(r\""+logname+"\",'w')\n"+
        "    ctsSaveFile(r\""+output+"\",\""+name_only+"\",output_error_log)\n"+
        "    output_error_log.close()\n"
        )
        
        return [output, ]


