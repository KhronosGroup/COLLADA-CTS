# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import OpenGL.GL
import OpenGL.GLUT
import os
import os.path
import shutil
import sys
import time
import types

import Core.Common.FUtils as FUtils
import Core.Common.FGlobals as FGlobals
from Core.Common.FConstants import *
from Core.Common.FSerializable import *
from Core.Common.FSerializer import *
from Core.Logic.FJudgement import *
from Core.Logic.FJudgementContext import *
from Core.Logic.FResult import *

class FExecution(FSerializable, FSerializer):
    def __init__(self, executionDir = None):
        """Creates the FExecution."""
        FSerializable.__init__(self)
        FSerializer.__init__(self)
        
        self.__executionDir = executionDir
        self.__outputLocations = []
        self.__outputFilenames = []
        self.__logLocations = []
        self.__logFilenames = []
        self.__errorCounts = []
        self.__warningCounts = []
        self.__timeRan = None
        self.__environment = {}
        self.__validationList = []
        self.__diffFromPrevious = ""
        self.__comments = ""
        self.__result = None
        self.__initializedSteps = []
        self.__crashIndices = []
        self.__judgingResults = {}
        self.__judgingLogs = {}
        self.__checksum = ""

    # executionDir must be absolute path and it should be empty!
    def Clone(self, executionDir):
        newExecution = FExecution(executionDir)
        newExecution.__outputFilenames = self.__outputFilenames
        newExecution.__logFilenames = self.__logFilenames
        newExecution.__errorCounts = self.__errorCounts
        newExecution.__warningCounts = self.__warningCounts
        newExecution.__timeRan = self.__timeRan
        newExecution.__environment = self.__environment
        newExecution.__comments = self.__comments
        newExecution.__crashIndices = self.__crashIndices
        newExecution.__judgingResults = self.__judgingResults
        newExecution.__judgingLogs = self.__judgingLogs
        newExecution.__checksum = self.__checksum
        newExecution.__ResetOutputLocations()
        newExecution.__ResetLogLocations()
        
        for directory in os.listdir(self.__executionDir):
            fullPath = os.path.join(self.__executionDir, directory)
            destFullPath = os.path.normpath(os.path.abspath(
                    os.path.join(executionDir, directory)))
            if (os.path.isdir(fullPath)):
                shutil.copytree(fullPath, destFullPath)
        
        return newExecution
    
    # currently only checks warning count, error count, and bmp and jpg files
    def __eq__(self, other):
        if other is None: return False
        
        if (self.__comments != other.__comments): return False
        if (self.__environment != other.__environment): return False
        if (self.__crashIndices != other.__crashIndices): return False
        if (self.__judgingResults != other.__judgingResults): return False
        if (self.__checksum != other.__checksum): return False
        
        # Do not compare judging logs.
        # Do not compare time ran.
        
        if (len(self.__errorCounts) != len(other.__errorCounts)): return False
        for i in range(len(self.__errorCounts)):
            if (self.__errorCounts[i] != other.__errorCounts[i]): return False
        
        if (len(self.__warningCounts) != len(other.__warningCounts)): 
            return False
        for i in range(len(self.__warningCounts)):
            if (self.__warningCounts[i] != other.__warningCounts[i]): 
                return False

        # Do not compare log locations.
        
        if (len(self.__outputLocations) != len(other.__outputLocations)): 
            return False
        for i in range(len(self.__outputLocations)):
            # validation
            if ((type(self.__outputLocations[i]) is types.StringType) and
                    (type(other.__outputLocations[i]) is types.StringType)):
                continue
            if ((self.__outputLocations[i] == None) and 
                    (other.__outputLocations[i] == None)):
                continue
            if ((self.__outputLocations[i] == None) or
                    (other.__outputLocations[i] == None)):
                return False
            if (len(self.__outputLocations[i]) != 
                    len(other.__outputLocations[i])): return False
            for j in range(len(self.__outputLocations[i])):
                #todo what happens if file not there
                ext = FUtils.GetExtension(self.__outputLocations[i][j])
                if (FUtils.IsImageFile(ext)):
                    compareResult = FGlobals.imageComparator.CompareImages(
                            self.__outputLocations[i][j], 
                            other.__outputLocations[i][j])
                    if (not compareResult.GetResult()): return False
        
        return True
    
    def GetExecutionDir(self):
        return self.__executionDir
    
    def __ResetOutputLocations(self):
        self.__outputLocations = []
        step = 0
        for filenameList in self.__outputFilenames:
            if (type(filenameList) is types.ListType):
                newLocation = []
                for outputName in filenameList:
                    newLocation.append(os.path.join(self.__executionDir, 
                            STEP_PREFIX + str(step), outputName))
                self.__outputLocations.append(newLocation)
            else:
                self.__outputLocations.append(os.path.join(self.__executionDir,
                        STEP_PREFIX + str(step), filenameList))
            step = step + 1
    
    def __ResetLogLocations(self):
        self.__logLocations = []
        step = 0
        for logFilename in self.__logFilenames:
            if (logFilename == None):
                self.__logLocations.append(None)
            else:
                self.__logLocations.append(os.path.join(self.__executionDir, 
                        STEP_PREFIX + str(step), logFilename))
            step = step + 1
    
    def InitializeFromLoad(self, filename):
        # FResult was updated to contain messages in Khronos svn r15.
        if ((self.__result != None) and self.__result.BackwardCompatibility()):
            self.Save(self, filename)

        # For backward compatibility: if the judging information is missing, create
        # empty dictionaries.
        if not self.__dict__.has_key("_FExecution__judgingResults"): self.__judgingResults = {}
        if not self.__dict__.has_key("_FExecution__judgingLogs"): self.__judgingLogs = {}
        if not self.__dict__.has_key("_FExecution__checksum"): self.__checksum = ""
        
        if (self.__executionDir == os.path.dirname(filename)): return
        
        self.__executionDir = os.path.dirname(filename)
        self.__ResetOutputLocations()
        self.__ResetLogLocations()
        
        self.Save(self, filename)

    def __AddOutputLocation(self, step, newFilenameList, logFilename):
        self.__outputFilenames.append(newFilenameList)
        self.__logFilenames.append(logFilename)
        if (logFilename == None):
            self.__logLocations.append(None)
        else:
            self.__logLocations.append(os.path.join(self.__executionDir, 
                STEP_PREFIX + str(step), logFilename))
        
        if (newFilenameList == None):
            self.__outputLocations.append(None)
        else:
            newLocation = []
            for filename in newFilenameList:
                newLocation.append(os.path.join(self.__executionDir, 
                        STEP_PREFIX + str(step), filename))
            self.__outputLocations.append(newLocation)
    
    def GetOutputLocation(self, opNumber):
        #FIXME: should not be perfoming this check
        if (opNumber >= len(self.__outputLocations)): return None
        
        return self.__outputLocations[opNumber]
    
    def IsOutputGood(self, opNumber):
        for outputLocation in self.__outputLocations[opNumber]:
            if (not os.path.isfile(outputLocation)):
                return False
        return True
    
    def ToggleResult(self):
        self.__result.Override(not self.__result.GetResult())
        self.Save(self, os.path.abspath(
                os.path.join(self.__executionDir, EXECUTION_FILENAME)))
    
    def GetResult(self):
        return self.__result
    
    def SetResult(self, result):
        self.__result = result
        for indices in self.__crashIndices:
            self.__result.ReplaceOutput(indices, FResult.CRASH)
    
    def GetErrorCount(self, opNumber):
        return self.__errorCounts[opNumber]
    
    def GetWarningCount(self, opNumber):
        return self.__warningCounts[opNumber]
    
    def GetTimeRan(self):
        return self.__timeRan
    
    def GetLogs(self):
        return self.__logLocations
    
    def GetLog(self, opNumber):
        return self.__logLocations[opNumber]
    
    def SetDiffFromPrevious(self, value):
        self.__diffFromPrevious = value
    
    def GetDiffFromPrevious(self):
        return self.__diffFromPrevious
    
    def GetComments(self):
        return self.__comments
        
    def GetChecksum(self):
        return self.__checksum
    
    def SetComments(self, comments):
        self.__comments = comments
        executionDir = os.path.normpath(
                os.path.join(self.__executionDir, EXECUTION_FILENAME))
        self.Save(self, executionDir)
    
    def GetEnvironment(self):
        return self.__environment
        
    def GetJudgementResult(self, badge):
        if (self.__judgingResults.has_key(badge)):
            return self.__judgingResults[badge]
        else:
            # This is negative in order to force the adopter to
            # run the appropriate test all at once.
            return FJudgement.MISSING_DATA
            
    def GetJudgementLog(self, badge):
        if (self.__judgingLogs.has_key(badge)):
            return self.__judgingLogs[badge]
        else:
            return ""
    
    def Validate(self, step):
        if (self.__validationList.count(step) == 0):
            self.__validationList.append(step)
            self.__AddOutputLocation(step, None, None)
                
    def __InitializeRun(self, appPython, step, op, inStep, filename, settings, 
                        isAnimated, markerCallBack):
        stepName = STEP_PREFIX + str(step)
        outDir = os.path.abspath(os.path.join(self.__executionDir, stepName))            
        logFilename = stepName + "." + LOG_EXT
        logAbsFilename = os.path.join(outDir, stepName + "." + LOG_EXT)
        
        try:
            os.mkdir(outDir)
        except OSError, e:
            print "<FExecution> could not make the step directory"
            print e
        
#        open(logAbsFilename, "w").close() # create the file
        
        self.__timeRan = time.localtime()
        
        # need to do this before glGetString will return something
        if (OpenGL.GLUT.glutGet(OpenGL.GLUT.GLUT_ELAPSED_TIME) == 0):
            OpenGL.GLUT.glutInit(sys.argv)
        
        winId = OpenGL.GLUT.glutCreateWindow("")
        self.__environment["GL_VENDOR: "] = OpenGL.GL.glGetString(
                                                        OpenGL.GL.GL_VENDOR)
        self.__environment["GL_RENDERER: "] = OpenGL.GL.glGetString(
                                                        OpenGL.GL.GL_RENDERER)
        OpenGL.GLUT.glutDestroyWindow(winId)
        
        if ((inStep == 0) or (self.__outputLocations[inStep] == None)):
            curInputFile = os.path.abspath(filename)
        else:
            curInputFile = os.path.abspath(self.__outputLocations[inStep][-1])
        
        output = appPython.AddToScript(op, curInputFile, logAbsFilename, 
                outDir, settings, isAnimated)
        self.__AddOutputLocation(step, output, logFilename)
        
        if markerCallBack != None and len(output) > 0:
            # Some annoying scripts don't give us valid paths.
            if not os.path.isabs(output[0]):
                markerCallBack(False, os.path.join(outDir, output[0]))
            else: markerCallBack(False, output[0])
    
    def Run(self, appPython, step, op, inStep, filename, settings, isAnimated, markerCallBack):
        # First run: calculate the check-sum.
        if (len(self.__checksum) == 0):
            self.__checksum = FUtils.CalculateChecksum(filename)
        
        # Run the test steps.
        if (self.__initializedSteps.count(step) == 0):
            self.__InitializeRun(appPython, step, op, inStep, filename, settings, isAnimated, markerCallBack)
            self.__initializedSteps.append(step)
        else:
            stepName = STEP_PREFIX + str(step)
            outDir = os.path.abspath(
                    os.path.join(self.__executionDir, stepName))
            logFilename = stepName + "." + LOG_EXT
            logAbsFilename = os.path.join(outDir, stepName + "." + LOG_EXT)
            
            if ((inStep == 0) or (self.__outputLocations[inStep] == None)):
                curInputFile = os.path.abspath(filename)
            else:
                curInputFile = os.path.abspath(self.__outputLocations[inStep][-1])
            
            output = appPython.AddToScript(op, curInputFile, logAbsFilename, outDir, settings, isAnimated)

            if markerCallBack != None and len(output) > 0:
                # Some annoying scripts don't give us valid paths.
                if not os.path.isabs(output[0]):
                    markerCallBack(False, os.path.join(outDir, output[0]))
                else: markerCallBack(False, output[0])
                

    def Validate(self, filename, testProcedure, testId):
        
        # Execute the validation steps.
        for step in self.__validationList:
            if (step != 0):
                lastOutputs = self.GetOutputLocation(step - 1)
                if (lastOutputs != None):
                    # only validates the last one
                    documentFilename = lastOutputs[-1]
                else:
                    documentFilename = None
            
            if (documentFilename != None):
                documentFilename = os.path.abspath(documentFilename)
            
            stepName = STEP_PREFIX + str(step)
            outDir = os.path.abspath(
                    os.path.join(self.__executionDir, stepName))
            logFilename = stepName + "." + LOG_EXT
            logAbsFilename = os.path.join(outDir, logFilename)
            
            try:
                os.mkdir(outDir)
            except OSError, e:
                print "<FExecution> could not make the step directory"
                print e
            
            if ((documentFilename != None) and 
                    (FUtils.GetExtension(documentFilename).lower() == "dae")):
                os.system("SchemaValidate.exe \"" + documentFilename + "\" \"" + 
                        SCHEMA_LOCATION + "\" \"" + SCHEMA_NAMESPACE + 
                        "\" \"" + logAbsFilename + "\"")
            else:
                logFile = open(logAbsFilename, "w")
                logFile.write("Error: Not a Collada file.\n")
                logFile.close()
            self.__outputFilenames[step] = logFilename
            self.__outputLocations[step] = logAbsFilename
            
            errors, warnings = self.__ParseValidation(logAbsFilename)
            self.__errorCounts[step] = errors
            self.__warningCounts[step] = warnings

    def Compile(self, filename, crashIndices):
        self.__crashIndices = crashIndices
        
        for logLocation in self.__logLocations:
            errors, warnings = self.__ParseLog(logLocation)
            self.__errorCounts.append(errors)
            self.__warningCounts.append(warnings)
    
    def Judge(self, filename, testProcedure, testId):
        # Look for a judging script
        scriptFilename = FUtils.ChangeExtension(filename, "py")
        try:
            # Set-up the judging script context.
            context = FJudgementContext(testProcedure, testId)

            if (os.path.exists(scriptFilename)):
                
                # Parse, compile and execute the judging script.
                judgingDictionary = { 'testProducedure' : testProcedure, 'judgingObject' : None };
                execfile(scriptFilename, judgingDictionary, judgingDictionary);
                if (judgingDictionary.has_key('judgingObject')):
                    judgingObject = judgingDictionary['judgingObject']
                    
                    # We have a juding object.
                    # Look for and process all the wanted badge levels.
                    for i in range(len(FGlobals.badgeLevels)):
                        badgeLevel = FGlobals.badgeLevels[i]
                        judgingLevel = "Judge" + badgeLevel
                        if (judgingObject.__class__.__dict__.has_key(judgingLevel)):
                            judgingFunction = judgingObject.__class__.__dict__[judgingLevel]
                            if (callable(judgingFunction)):

                                # Run this judging function.
                                judgement = judgingFunction(judgingObject, context)

                                # Process the judgement
                                if judgement: self.__judgingResults[badgeLevel] = FJudgement.PASSED
                                else: self.__judgingResults[badgeLevel] = FJudgement.FAILED
                                judgingLog = context.GetLog()
                                if len(judgingLog) > 0: self.__judgingLogs[badgeLevel] = judgingLog
                                elif judgement: self.__judgingLogs[badgeLevel] = "Judgement passed."
                                else: self.__judgingLogs[badgeLevel] = "Judgement failed."
                                context.ResetLog()

                            else:
                                self.__judgingResults[badgeLevel] = FJudgement.MISSING_DATA
                                self.__judgingLogs[badgeLevel] = "Invalid judging script. '" + judgingLevel + "' is not a function."
                        else:
                            self.__judgingResults[badgeLevel] = FJudgement.NO_SCRIPT
                            self.__judgingLogs[badgeLevel] = "Judging script does not include the '" + badgeLevel + "' badge."
                        
                    # We need that checksum too!
                    self.__checksum += "\n" + FUtils.CalculateChecksum(scriptFilename)
                    
                else:
                    for i in range(len(FGlobals.badgeLevels)):
                        badgeLevel = FGlobals.badgeLevels[i]
                        self.__judgingResults[badgeLevel] = FJudgement.MISSING_DATA
                        self.__judgingLogs[badgeLevel] = "Invalid judging script. Did not create the judging object."
            else:
                for i in range(len(FGlobals.badgeLevels)):
                    badgeLevel = FGlobals.badgeLevels[i]
                    self.__judgingResults[badgeLevel] = FJudgement.NO_SCRIPT
                    self.__judgingLogs[badgeLevel] = "No judging script provided."
            
        except Exception, e:
            print "------------------------------------------------------------"
            print "<FExecution> could not run judging script: '" + os.path.basename(scriptFilename) + "'."
            print "Error message: '", e, "'."
        

    def __ParseValidation(self, logLocation):
        if (logLocation == None): return (0, 0)
        
        errors = 0
        warnings = 0
        log = open(logLocation)
        line = log.readline()
        while (line):
            if (line[:7] == "Warning"):
                warnings = warnings + 1
            elif (line[:5] == "Error"):
                errors = errors + 1
            line = log.readline()
        log.close()
        return (errors, warnings)
    
    def __ParseLog(self, logLocation):
        if (logLocation == None): return (0, 0)
        
        errors = 0
        warnings = 0
        try:
            log = open(logLocation)
            line = log.readline()
            while (line):
                line = line.lower()
                errors = errors + line.count("error")
                warnings = warnings + line.count("warning")
                line = log.readline()
            log.close()
        except Exception, e:
            errors = errors + 1 # Make sure we fail then.
            pass
            
        return (errors, warnings)
    