# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FMimic (FApplication):
    """The class which represents mimic to the testing framework.
    
    """
    
    __SCRIPT_EXTENSION = ".py"
    
    def __init__(self, configDict):
        """__init__() -> FMimic"""
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
        return "Mimic 1.0"
    
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
                FMimic.__SCRIPT_EXTENSION)
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
        if (not os.path.isfile(self.configDict["mimicPath"])):
            print "Mimic does not exist"
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
                
        """
        outputFormat = ".png"
        
        command = ("\"" + self.configDict["mimicPath"] + "\" ")
            
        
        baseName = FUtils.GetProperFilename(filename)
        self.__currentImportProperName = baseName
        outputFilename = os.path.join(outputDir, baseName + "_out" + ".dae")
        self.__currentFilename = outputFilename
        imageFilename = os.path.join(outputDir, "result" + outputFormat)
        self.__currentImagename = imageFilename
        command = (command + "\"" + filename + 
                   "\" \"" + outputFilename + "\" \"" + imageFilename + "\"")
        
        print "***Importting: %s" % (filename)
	print "   Command %s" % (command)        
        self.WriteCrashDetect(self.__script, command, logname)
        
        self.__testImportCount = self.__testImportCount + 1
        
        return [os.path.normpath(outputFilename)]
        
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender()
        
        """
	print "***Render outputDir: %s" % (outputDir)

	outputFormat = ".png"        
        command = ("\"" + self.configDict["mimicRenderPath"] + "\" ")
                    
        baseName = self.__currentImportProperName;
        
        outputFilename = os.path.join(outputDir, baseName + "_out" + ".dae")
        imageFilename = os.path.join(outputDir, "result" + outputFormat)
        self.__currentImagename = imageFilename
        command = (command + "\"" + self.__currentFilename + 
                   "\" \"" + outputFilename + "\" \"" + imageFilename + "\"")

	print "   Command %s" % (command)        
        self.WriteCrashDetect(self.__script, command, logname)
        
        self.__testRenderCount = self.__testRenderCount + 1        
        return [os.path.normpath(imageFilename),]

    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteExport()
        
        """
	outputFormat = ".png"        
        command = ("\"" + self.configDict["mimicPath"] + "\" ")
             
        print "***Export outputDir: %s" % (outputDir)     
        baseName = self.__currentImportProperName;
        
        outputFilename = os.path.join(outputDir, baseName + "_out" + ".dae")
        imageFilename = os.path.join(outputDir, baseName + outputFormat)
        self.__currentImagename = imageFilename
        command = (command + "\"" + self.__currentFilename + 
                   "\" \"" + outputFilename + "\" \"" + imageFilename + "\"")
        
	print "   Command %s" % (command)        
        self.WriteCrashDetect(self.__script, command, logname)
        
        return [os.path.normpath(outputFilename)]
