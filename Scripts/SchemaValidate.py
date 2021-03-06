# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import os.path
import subprocess

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Scripts.FApplication import *

class SchemaValidate (FApplication):
    """ Reintroduces SchemaValidate.exe into the testing framework as a scripted application (not hard coded as in previous revision)

        This script doubles as a framework for error logging, command line applications
    """
    __SCRIPT_EXTENSION = ".py"
    
    def __init__(self, configDict):
        """__init__() -> SchemaValidate"""
        FApplication.__init__(self, configDict)
        
        self.__workingDir = None
        self.__testCount = 0
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "MSXML 6.0"
    
    def GetOperationsList(self):
        """GetOperationsList() -> list_of_str
        
        Implements FApplication.GetOperationsList()
        
        """
        return [VALIDATE]
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        filename = ("script" + str(self.applicationIndex) + 
                SchemaValidate.__SCRIPT_EXTENSION)
        self.__script = open(os.path.join(workingDir, filename) , "w")
        
        self.WriteCrashDetectBegin(self.__script)
        
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
        if (not os.path.isfile(self.configDict["schemaValidatePath"])):
            print "MSXML 6.0 does not exist"
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
    
    def WriteValidate(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteValidate()
        
        """

        # Change the working directory to the file's directory (so executable runs correctly)
#        change_dir_string = "os.chdir(r\""+os.path.dirname(filename)+"\")\n"
#        self.__script.write(change_dir_string)

        # Write the executing command: >>schemaValidatePath file SCHEMA_LOCATION SCHEMA_NAMESPACE log
        command = ("\"" + self.configDict["schemaValidatePath"] + "\" ") 
        command = (command + "\"" + filename + "\" ")  
        command = (command + "\"" + SCHEMA_LOCATION + "\" ")
        command = (command + "\"" + SCHEMA_NAMESPACE + "\" ")
        command = (command + "\"" + logname + "\"")
        
        # Write the above command, along with crash detection
        self.WriteCrashDetect(self.__script, command)

        self.__testCount = self.__testCount + 1
        
        return [logname,]
            
    def WriteImport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport(). Schema Validation has no import.
        
        """
        pass
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender(). Schema Validation has no render.
        
        """
        pass
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_strImplements FApplication.WriteExport(). Feeling Viewer has no export.

        Implements FApplication.WriteExport(). Schema Validation has no export.

        """
        pass


