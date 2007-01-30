# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os
import os.path
import subprocess

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *

class FApplication:
    """Abstract class for specific applications for testing framework."""
    
    def __init__(self, configDict):
        """__init__() -> FApplication
        
        Creates the FApplication. (It should be called by any implemenations of
        application specific scripts.)
        
        arguments:
            configDict
                dictionary with values from the configuration file for the
                application specific scripts.
        
        """
        self.applicationIndex = -1
        self.configDict = configDict
    
    def SetApplicationIndex(self, applicationIndex):
        """SetApplicationIndex(applicationIndex) -> None
        
        Sets the application index. (It should *not* be overriden by any
        implemenations of application specific scripts)
        
        arguments:
            applicationIndex
                integer corresponding to the position of the application in the
                order of operations for the test procedure.
        
        """
        self.applicationIndex = applicationIndex
    
    def SetTestProcedureDir(self, testProcedureDir):
        """SetTestProcedureDir(testProcedureDir) -> None
        
        Sets the test procedure directory. This will be used to keep watch over
        I/O operations to detect crashes. (It should *not* be overriden by any
        implemenations of application specific scripts)
        
        arguments:
            testProcedureDir
                string representing absolute file path for the test procedure.
        
        """
        self.__testProcedureDir = testProcedureDir
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Returns the name for this application which will be displayed to the
        user. It must be unique. (It must be overriden by any implementations 
        of application specific scripts.)
        
        returns:
            string representing the name of the application.
        
        """
        raise NotImplementedError, "Application.GetPrettyName()"
    
    def GetOperationsList(self):
        """GetOperationsList() -> list_of_str
        
        Returns the operations that are available in this application. They
        operations are represented by the strings defined in FConstants. (It 
        *may* be overriden by any implementations of application specific 
        scripts.)
        
        returns:
            list of string representing the operations available.
        
        """
        return [IMPORT, EXPORT, RENDER]
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Returns the settings for the DCC with respect to the given operation.
        These will be used as the default settings. (It must be overriden by
        any implementations of application specific scripts.)
        
        arguments:
            operation
                constant (defined in FConstants) representing the operation
                whose settings are being requested.
        
        returns:
            list of FSettingEntry for the specified operation
        
        """
        raise NotImplementedError, "Application.GetSettingsForOperation()"
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Called before using the application specific script to run tests. Any 
        initialization that is needed to run a test should be done here. It is
        mostly for setting up the scripts that will be used to run the actual
        DCC. (It must be overriden by any implementations of application 
        specific scripts.)
        
        arguments:
            workingDir
                string corresponding to the directory that the script files 
                should be placed. This is a temporay directory and files placed
                in here should not be assumed to remain across different
                runnings of tests.
        
        """
        raise NotImplementedError, "Application.BeginScript()"
    
    def EndScript(self):
        """EndScript() -> None
        
        Called after all writing of operations are done but before calling
        RunScript. Any finalizations needed for running a test should be done 
        here. It is mostly for closing the scripts that will be used to run
        the actual DCC. (It must be overriden by any implementations of
        application specific scripts.)
        
        """
        raise NotImplementedError, "Application.EndScript()"
    
    def RunScript(self):
        """RunScript() -> None
        
        Runs the script that will be used to run the actual DCC. (It must be
        overriden by any implementations of application specific scripts.)
        
        """
        raise NotImplementedError, "Application.RunScript()"
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated):
        """WriteImport(filename, logname, outputDir, settings, isAnimated) -> list_of_str
        
        Writes the import operation to the script that will be used to run
        the actual DCC. (It must be overriden by any implementations of
        application specific scripts.)
        
        arguments:
            filename
                string corresponding to the absolute filename for the file to 
                import.
            logname
                string corresponding to the absolute filename for the log file
                for this operation. The file has been created already.
            outputDir
                string corresponding to the absolute path for where the outputs
                should be placed. This directory has been created already.
            settings
                list of FSettingEntry what the user has specified for the
                running of these tests. They will be the same as those given
                in GetSettingsForOperation but with the possbility that the
                values are changed.
            isAnimated
                boolean representing whether the given filename is considered
                an animated scene. It is animated if "Animation" or "animation"
                appears in the data set name, subcategory, or category of the 
                data set.
        
        returns:
            list of string representing the locations of all the output files.
            These should be relative to outputDir. It should not include the
            log files.
        
        """
        raise NotImplementedError, "Application.WriteImport()"
    
    def WriteRender(self, logname, outputDir, settings, isAnimated):
        """WriteRender(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Writes the render operation to the script that will be used to run
        the actual DCC. It assumes that WriteImport has been called. (It must 
        be overriden by any implementations of application specific scripts.)
        
        arguments:
            logname
                string corresponding to the absolute filename for the log file
                for this operation. The file has been created already.
            outputDir
                string corresponding to the absolute path for where the outputs
                should be placed. This directory has been created already.
            settings
                list of FSettingEntry what the user has specified for the
                running of these tests. They will be the same as those given
                in GetSettingsForOperation but with the possbility that the
                values are changed.
            isAnimated
                boolean representing whether the given filename is considered
                an animated scene. It is animated if "Animation" or "animation"
                appears in the data set name, subcategory, or category of the 
                data set.
        
        returns:
            list of string representing the locations of all the output files.
            These should be relative to outputDir. It should not include the
            log files.
        
        """
        raise NotImplementedError, "Application.WriteRender()"
    
    def WriteExport(self, logname, outputDir, settings, isAnimated):
        """WriteImport(logname, outputDir, settings, isAnimated) -> list_of_str
        
        Writes the export operation to the script that will be used to run
        the actual DCC. It assumes that WriteImport has been called. (It must 
        be overriden by any implementations of application specific scripts.)
        
        arguments:
            logname
                string corresponding to the absolute filename for the log file
                for this operation. The file has been created already.
            outputDir
                string corresponding to the absolute path for where the outputs
                should be placed. This directory has been created already.
            settings
                list of FSettingEntry what the user has specified for the
                running of these tests. They will be the same as those given
                in GetSettingsForOperation but with the possbility that the
                values are changed.
            isAnimated
                boolean representing whether the given filename is considered
                an animated scene. It is animated if "Animation" or "animation"
                appears in the data set name, subcategory, or category of the 
                data set.
        
        returns:
            list of string representing the locations of all the output files.
            These should be relative to outputDir. It should not include the
            log files.
        
        """
        raise NotImplementedError, "Application.WriteExport()"
    
    def AddToScript(self, operation, filename, logname, outputDir, settings, 
                    isAnimated):
        """AddToScript(operation, filename, logname, outputDir, settings, isAnimated) -> list_of_str
        
        Calls the appropriate Write* method with the correct parameters to 
        write the operation specified. (It should *not* be overriden by any
        implemenations of application specific scripts)
        
        arguments:
            operation
                constant (defined in FConstants) representing the operation to
                write.
            filename
                string corresponding to the absolute filename for the file to 
                import.
            logname
                string corresponding to the absolute filename for the log file
                for this operation. The file has been created already.
            outputDir
                string corresponding to the absolute path for where the outputs
                should be placed. This directory has been created already.
            settings
                list of FSettingEntry what the user has specified for the
                running of these tests. They will be the same as those given
                in GetSettingsForOperation but with the possbility that the
                values are changed.
            isAnimated
                boolean representing whether the given filename is considered
                an animated scene. It is animated if "Animation" or "animation"
                appears in the data set name, subcategory, or category of the 
                data set.
        
        returns:
            list of string representing the locations of all the output files.
            These should be relative to outputDir. It should not include the
            log files.
        
        """
        if (operation == IMPORT):
            return self.WriteImport(filename, logname, outputDir, settings, 
                                    isAnimated)
        elif (operation == RENDER):
            return self.WriteRender(logname, outputDir, settings, isAnimated)
        elif (operation == EXPORT):
            return self.WriteExport(logname, outputDir, settings, isAnimated)
    
    def RunApplication(self, command, workingDir):
        """RunApplication(command, workingDir) -> int
        
        Runs the command in another process. (It should *not* be overriden by 
        any implemenations of application specific scripts)
        
        If detectCrash is "True" in the configuration file, then it will run 
        the command with the timeout specified in the configuration file. The 
        timeout is the amount of time without I/O that is allowed before 
        considering that there is a crash and then will kill the process. The
        return value will be 1 if a crash was detected and needed to kill 
        the command. The return value will be the return value of the command 
        if it finished.
        
        If detectCrash is not "True" in the configuration file, it will run and
        wait for the command to return. The return value will be 0.
        
        arguments:
            command
                string representing the command to execute.
            workingDir
                string corresponding to the directory that the script files 
                should be placed. This is a temporay directory and files placed
                in here should not be assumed to remain across different
                runnings of tests.
        
        """
        dccFilename = os.path.join(workingDir, "temporaryDCCProcess.py")
        dccFilename = FUtils.GetAvailableFilename(dccFilename)
        
        file = open(dccFilename, "w")
        self.WriteCrashDetectBegin(file)
        self.WriteCrashDetect(file, command)
        if (self.configDict["detectCrash"] == "True"):
            file.write("sys.exit(p.poll())\n")
        file.close()
        
        returnValue = subprocess.call("\"" + 
                self.configDict["pythonExecutable"] + "\" \"" + dccFilename + 
                "\"")
        
        os.remove(dccFilename)
        return returnValue
    
    def WriteCrashDetectBegin(self, file):
        """WriteCrashDetectBegin(file) -> None
        
        Writes the header code needed to use WriteCrashDetect to the file
        specified. (It should *not* be overriden by any implemenations of 
        application specific scripts)
        
        arguments:
            file
                file object to write to
        
        """
        if (self.configDict["detectCrash"] == "True"):
            file.write(
                    # XXX: only works for win32
                    "import win32api\n" +
                    "import subprocess\n" +
                    "import time\n" +
                    "import os\n" +
                    "import sys\n\n" +
                    "def GetDirectoryStatistics(path):\n" +
                    "    fileCount = 0\n" +
                    "    dirCount = 0\n" +
                    "    size = 0\n" +
                    "    for root, dirs, files in os.walk(path):\n" +
                    "        fileCount = fileCount + len(files)\n" +
                    "        dirCount = dirCount + len(dirs)\n" +
                    "        for file in files:\n" +
                    "            size = size + os.path.getsize(os.path.join" +
                            "(root, file))\n" +
                    "    return (size, fileCount, dirCount)\n\n"
                    )
        else:
            file.write(
                    "import subprocess\n" +
                    "import os\n\n")
    
    def WriteCrashDetect(self, file, command, logFilename = None):
        """WriteCrashDetect(file, command, logFilename = None) -> None
        
        Writes the command to the file using the log file specified. (It should
        *not* be overriden by any implemenations of application specific 
        scripts)
        
        If detectCrash is "True" in the configuration file, then it will write
        it in a crash safe way using the timeout also specified in the
        configuration file. The timeout is the amount of time without I/O that 
        is allowed before considering that there is a crash and then will kill 
        the process. 
        
        If detectCrash is not "True" in the configuration file, it will write
        it so that it executes the command and waits until it returns.
        
        arguments:
            file
                file object to write to
            command
                string representing the command to write
            logFilename
                string representing the file path of the log name. None if no
                log file should be use. In that case, it will dump it to 
                stdout.
        
        """
        if (logFilename == None):
            logWritten = "None"
        else:
            logWritten = "\"" + logFilename.replace("\\","\\\\") + "\""
        file.write(
                "logFilename = " + logWritten + "\n" +
                "if (logFilename == None):\n" + 
                "    log = None\n" +
                "else:\n" +
                "    log = open(logFilename, \"a\")\n"
                )
        
        if (self.configDict["detectCrash"] == "True"):
            file.write(
                    # XXX: only works for win32
                    "p = subprocess.Popen('" + command.replace("\\", "\\\\") + 
                            "', stdout = log, stderr = subprocess.STDOUT)\n" +
                    "watcher = subprocess.Popen('\"" + 
                            os.path.abspath(FILEWATCHER).replace("\\", "\\\\") + "\" \"" + 
                            self.__testProcedureDir.replace("\\", "\\\\") + 
                            "\" " + self.configDict["ioTimeoutMilli"] +
                            "')\n" +
                    "while ((p.poll() == None) and " +
                            "(watcher.poll() == None)):\n" +
                    "    time.sleep(1)\n" +
                    "if (watcher.poll() == None):\n" +
                    "    handle = win32api.OpenProcess(1, 0, watcher.pid)\n" +
                    "    win32api.TerminateProcess(handle, 0)\n" +
                    "    win32api.CloseHandle(handle)\n" +
                    "if (p.poll() == None):\n" +
                    "    handle = win32api.OpenProcess(1, 0, p.pid)\n" +
                    "    win32api.TerminateProcess(handle, 0)\n" +
                    "    win32api.CloseHandle(handle)\n" +
                    "    if (log != None):\n" +
                    "        log.close()\n" +
                    "    sys.exit(1)\n" +
                    "if (log != None):\n" +
                    "    log.close()\n\n"
                    )
        else:
            file.write(
                    "subprocess.call('" + command.replace("\\", "\\\\") + 
                            "', stdout = log, stderr = subprocess.STDOUT)\n\n"
                    )
    
    def GetSettingValueAs(self, list, setting, typeCast):
        """GetSettingValueAs(list, setting, typeCast) -> typeCast
        
        Gets the value of a setting. (It should *not* be overriden by any 
        implemenations of application specific scripts)
        
        If the value in the setting is not "", then it will return that value
        as the type defined by typeCast. If it is "", then it will get the
        default value from the list of settings defined in list.
        
        arguments:
            list
                list of 3-tuples: first is the pretty name, second the command,
                and third the value
            setting
                FSetting to get value from
            typeCast
                the type to cast to. There must be a global function defined, 
                in the form typeCast(), that will cast a str to the type
        
        """
        value = setting.GetValue().strip()
        if (value != ""):
            try:
                value = typeCast(value)
            except ValueError, e:
                value = ""
        if (value == ""):
            value = self.FindDefault(list, setting.GetPrettyName())
            value = typeCast(value)
        
        return value
    
    def FindDefault(self, list, prettyName):
        """FindDefault(list, prettyName) -> str
        
        Gets the value for prettyName in the list of setting specified. (It 
        should *not* be overriden by any implemenations of application specific
        scripts)
        
        arguments:
            list
                list of 3-tuples: first is the pretty name, second the command,
                and third the value
            prettyName:
                str representing the prettyName of the setting to get value for
        
        """
        for entry in list:
            if (entry[0] == prettyName):
                return entry[2]
        raise LookupError, "Cannot find pretty name: " + prettyName
    