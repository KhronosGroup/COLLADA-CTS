# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import copy
import os
import os.path
import re
import shutil

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Core.Common.FSerializable import *
from Core.Common.FSerializer import *
from Core.Logic.FDataSetParser import *
from Core.Logic.FKeySupplier import *
from Core.Logic.FRegExManager import *
from Core.Logic.FSetting import *
from Core.Logic.FSettingManager import *
from Core.Logic.FTest import *

class FTestProcedure(FSerializable, FSerializer, FRegExManager, 
                     FDataSetParser):
    def __init__(self, procedureTree):
        """Creates the FTestProcedure.
        
        It assumes that the procedureDir exists already and will use that
        directory to create more directories. It is ready to be saved after 
        constructor is called.
        
        arguments:
            procedureTree -- a list of 2-tuples that contain a string 
            representation of an application and a list of string 
            representations of operations. For example:
                [("App1", [("op1","setting1"), 
                           ("op2","setting2"), 
                           ("op3","setting3")]),
                 ("App2", [("op1","setting4"), 
                           ("op3","setting5")]),
                 ("App1", [("op3","setting6"), 
                           ("op2","setting7"), 
                           ("op1","setting8")])]
        
        """
        FSerializable.__init__(self)
        FSerializer.__init__(self)
        FRegExManager.__init__(self)
        FDataSetParser.__init__(self)
        
        self.__procedureTree = procedureTree
        self.__procedureDir = None
        self.__name = None
        self.__dccWorkingDir = None
        # FIXME: don't think there's a point for both testList and supplier
        self.__testList = {}
        self.__globalSettings = []
        self.__settingManager = FSettingManager()
        self.__supplier = FKeySupplier()
        self.__cancelRun = False
        self.__version = VERSION
        
        for app in range(len(self.__procedureTree)):
            appString = self.__procedureTree[app][0]
            for op in range(len(self.__procedureTree[app][1])):
                if (appString != None):
                    opString = self.__procedureTree[app][1][op][0]
                    settingString = self.__procedureTree[app][1][op][1]
                    if (settingString != None):
                        setting = FSetting(self.__procedureTree[app][1][op][1], 
                                           opString, appString)
                        self.__globalSettings.append(setting)
                        
                        self.__settingManager.AddSetting(opString, appString, 
                                                         setting)
                    else:
                        self.__globalSettings.append(None)
                else:
                    self.__globalSettings.append(None)
    
    def GetRecoveredTestIds(self):
        message = ""
        for test in self.GetTestGenerator():
            if (test.IsRecovered()):
                message = message + "Test" + str(test.GetTestId()) + "\n"
        return message[:-1]
    
    def AddRegEx(self, settings, regEx, ignoredRegEx = [""]):
        FRegExManager.AddRegEx(self, settings, regEx, ignoredRegEx)
        self.Save(self, 
                  os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
    
    def DeleteRegEx(self, index):
        FRegExManager.DeleteRegEx(self, index)
        self.Save(self, 
                  os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
    
    def SetRegEx(self, index, regEx, ignoredRegEx):
        FRegExManager.SetRegEx(self, index, regEx)
        FRegExManager.SetIgnoredRegEx(self, index, ignoredRegEx)
        self.Save(self, 
                  os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
    
    def CheckForNewTests(self, regExId):
        newDataSets = []
        dir = FUtils.NormalizeRegEx(os.path.normpath(MAIN_FOLDER))
        
        ignoredPatterns = []
        for i in self.GetIgnoredRegExPageGenerator(regExId):
            ignoredPatterns.append(re.compile("(" + dir + ")(/|\\\\)(" + 
                    self.GetIgnoredRegEx(regExId, i) + ")$"))
        
        for regExPage in self.GetRegExPageGenerator(regExId):
            pattern = re.compile("(" + dir + ")(/|\\\\)(" + 
                    self.GetRegEx(regExId, regExPage) + ")$")
            tempDataSets = []
            for dataSetDir in DATA_SET_DIRS:
                self.__CheckForNewTestsRecurse(dataSetDir, pattern, 
                        self.GetRegExSettings(regExId), tempDataSets, 
                        ignoredPatterns)
            newDataSets = newDataSets + tempDataSets
        
        return newDataSets
    
    def __CheckForNewTestsRecurse(self, path, pattern, settings, newDataSets,
            ignoredPatterns):
        file, dirs = self.GetValidFileAndDirs(path)
        
        if (file != None):
            file = os.path.normpath(os.path.dirname(file))
            match = pattern.match(file)
            if (match != None):
                if (match.group() == file):
                    found = False
                    for test in self.GetTestGenerator():
                        if ((test.GetDataSetPath() == file) and 
                                test.GetSettings() == settings):
                            found = True
                            break
                    if (not found):
                        ignoredMatchFlag = False
                        for ignoredPattern in ignoredPatterns:
                            ignoredMatch = ignoredPattern.match(file)
                            if ((ignoredMatch != None) and 
                                    (ignoredMatch.group() == file)):
                                ignoredMatchFlag = True
                                break
                        if (not ignoredMatchFlag):
                            newDataSets.append(file)
            return
        
        for dir in dirs:
            self.__CheckForNewTestsRecurse(dir, pattern, settings, newDataSets,
                    ignoredPatterns)
    
    def StepEquals(self, other):
        return self.__procedureTree == other.__procedureTree
    
    def GetAppOpString(self):
        string = ""
        for step, app, op, setting in self.GetStepGenerator():
            if (op == VALIDATE and op not in OPS_NEEDING_APP):
                string = string + "[" + op + "]"
            else:
                string = string + "[" + app + "," + op + "]"
        return string
    
    def SetProcedureDirectory(self, procedureDir):
        """Sets the directory for the procedure and creates all the necessary
        members from it.
        
        This is done outside of the constructor so that saving can be done
        directly after the constructor for efficiency. Note that the
        FTestProcedure initialization is not complete until this method is
        called.
        
        arguments:
            procedureDir -- the directory path for which the test procedure
            can save its files. This should be relative to the working 
            directory (the one from os.getcwd()).
        
        """
        self.__Initialize(procedureDir)
        try:
            os.mkdir(self.__dccWorkingDir)
        except OSError, e:
            print "<FTestProcedure> could not make the working directory"
            print e
    
    def InitializeFromLoad(self, filename):
        procedureDir = os.path.dirname(filename)
        self.__Initialize(procedureDir)
        self.__testList = {}
        
        testPrefix = os.path.join(self.__procedureDir, TEST_PREFIX)
        for key in self.__supplier.GetKeyGenerator():
            testFilename = os.path.join(testPrefix + str(key), TEST_FILENAME)
            if (os.path.isfile(testFilename)):
                test = self.Load(testFilename)
                self.__testList[key] = test
            else:
                self.__supplier.ReturnKey(key)
        
        if (FRegExManager.BackwardCompatibility(self)):
            self.Save(self, 
                    os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
        
        # pre 1.3
        if (not "_FTestProcedure__version" in self.__dict__.keys()):
            FRegExManager.BackwardCompatibilityPath(self)
            self.__version = VERSION
            self.Save(self, 
                    os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
    
    def __Initialize(self, procedureDir):
        self.__procedureDir = procedureDir
        self.__name = os.path.basename(procedureDir)
        self.__dccWorkingDir = os.path.join(self.__procedureDir, DCC_WORK)
    
    def GetName(self):
        return self.__name
    
    def GetSettingManager(self):
        return self.__settingManager
    
    def GetGlobalSetting(self, step):
        return self.__globalSettings[step]
    
    def AddTest(self, dataSetPath, settings = None):
        testId = self.__supplier.NextKey()
        testDir = os.path.join(self.__procedureDir, TEST_PREFIX + str(testId))
        try:
            os.mkdir(testDir)
        except OSError, e:
            print "<FTestProcedure> could not make test directory"
            print e
        
        if (settings == None):
            settings = self.__globalSettings
        
        test = FTest(dataSetPath, testId, copy.copy(settings))
        self.Save(test, os.path.join(testDir, TEST_FILENAME))
        test.SetTestDirectory(testDir)
        self.__testList[testId] = test
        
        i = 0
        for app in range(len(self.__procedureTree)):
            appString = self.__procedureTree[app][0]
            for op in range(len(self.__procedureTree[app][1])):
                opString = self.__procedureTree[app][1][op][0]
                if (settings[i] != None): # not validation
                    self.__settingManager.AddSetting(opString, appString, 
                                                 settings[i])
                i = i + 1
        
        # FIXME: when update the way saving, abstract this
        # don't save the testList since it is read from file structure!
        cachedList = self.__testList
        self.__testList = {}
        self.Save(self, 
                  os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
        self.__testList = cachedList
        
        return testId
    
    def RemoveTest(self, key):
        deletedSettings = self.__testList[key].GetSettings()
        
        for regExId in self.GetRegExIdGenerator():
            if (deletedSettings == self.GetRegExSettings(regExId)):
                ignoredRegEx = self.GetIgnoredRegExList(regExId)
                if (len(ignoredRegEx) == 0):
                    ignoredRegEx.append("")
                
                displayedFilename = FUtils.GetRelativePath(
                        self.__testList[key].GetDataSetPath(), MAIN_FOLDER)
                regExPath = FUtils.NormalizeRegEx(displayedFilename)
                newIgnored = ignoredRegEx[-1]
                if (newIgnored != ""):
                    newIgnored = newIgnored + "|"
                newIgnored = newIgnored + regExPath
                if (len(newIgnored) < 30000):
                    ignoredRegEx[-1] = newIgnored
                else:
                    ignoredRegEx.append(regExPath)
                self.SetIgnoredRegEx(regExId, ignoredRegEx)
        
        testDir = os.path.join(self.__procedureDir, TEST_PREFIX + str(key))
        shutil.rmtree(testDir)
        self.__supplier.ReturnKey(key)
        self.__testList.pop(key)
        
        for step, appString, opString, dummy in self.GetStepGenerator():
            if (deletedSettings[step] != None): # not validation
                otherSteps = []
                for (step2, appString2, opString2, 
                        dummy2) in self.GetStepGenerator():
                    if ((appString2 == appString) and (opString2 == opString)):
                        otherSteps.append(step2)
                
                found = False
                for stepIndex in otherSteps:
                    if (deletedSettings[step] == 
                            self.__globalSettings[stepIndex]):
                        found = True
                        break
                if (found): continue
                
                for test in self.GetTestGenerator():
                    for stepIndex in otherSteps:
                        testSettings = test.GetSettings()
                        if (deletedSettings[step] == testSettings[stepIndex]):
                            found = True
                            break
                if (found): continue
                
                self.__settingManager.DeleteSetting(opString, appString,
                        deletedSettings[step])
        
        # FIXME: when update the way saving, abstract this
        # don't save the testList since it is read from file structure!
        cachedList = self.__testList
        self.__testList = {}
        self.Save(self, 
                  os.path.join(self.__procedureDir, TEST_PROCEDURE_FILENAME))
        self.__testList = cachedList
    
    def GetDirectory(self):
        return self.__procedureDir
    
    def GetTest(self, key):
        return self.__testList[key]
    
    def GetTestCount(self):
        return len(self.__testList)
    
    def GetTestGenerator(self):
        for key in self.__testList.keys():
            yield self.__testList[key]
                
    def GetStepGenerator(self):
        """Get the generator for the test procedure.
        
        Upon yield, it returns an index to the operation, the string 
        representation of the application, and the string representation of the
        operation. It does so in order of the list.
        
        """
        i = 0
        for app in range(len(self.__procedureTree)):
            for op in range(len(self.__procedureTree[app][1])):
                yield (i, self.__procedureTree[app][0], 
                       self.__procedureTree[app][1][op][0],
                       self.__procedureTree[app][1][op][1])
                i = i + 1
    
    def __RunTestsAux(self, appPython, appIndex, maxAppIndex, testIds, 
                      applicationMap, callBack):
        if (self.__cancelRun): return None
        
        steps = []
        for step, op in self.__GetOpGenerator(appIndex):
            if (op != VALIDATE or op in OPS_NEEDING_APP):
                steps.append(step)
        
        if (callBack != None):
            callBack(appIndex, maxAppIndex, 
                    "Creating script for steps: " + str(steps) + ".")
        appPython.BeginScript(os.path.abspath(self.__dccWorkingDir))
        
        for testId in testIds:
            for step, op in self.__GetOpGenerator(appIndex):
                if (op == VALIDATE and op not in OPS_NEEDING_APP):
                    self.__testList[testId].Validate(step)
                else:
                    self.__testList[testId].Run(appPython, step, op, 
                                            self.__GetInputStep(step))
        
        appPython.EndScript()
        
        if (self.__cancelRun): return None
        
        if (callBack != None):
            callBack(appIndex, maxAppIndex, 
                    "Running script for steps: " + str(steps) + ".")
        
        return appPython.RunScript()
    
    # callBack takes 2 parameters: current, max, message
    def RunTests(self, testIds, applicationMap, callBack = None):
        maxAppIndex = 0
        for appIndex, stepIndex, app in self.__GetAppGenerator():
            maxAppIndex = maxAppIndex + 1
        maxAppIndex = maxAppIndex + 3 # validation, compiling, judging..
        
        if (callBack != None):
            callBack(0, maxAppIndex, "Preparing " + str(len(testIds)) + 
                     " executions for running...")
        
        for testId in testIds:
            self.__testList[testId].Prepare()
        
        self.__cancelRun = False
        for appIndex, stepIndex, app in self.__GetAppGenerator():
            if (self.__cancelRun): break
            
            if (app == None):
                for testId in testIds:
                    self.__testList[testId].Validate(stepIndex)
                continue
            
            if (not applicationMap.has_key(app)):
                print ("!!! <FTestProcedure> Application specific python " +
                       "script missing. Can't do anything about it, so not " +
                       "stop running tests.")
                break
            
            appPython = applicationMap[app]
            appPython.SetApplicationIndex(appIndex)
            appPython.SetTestProcedureDir(self.__procedureDir)
            
            savedTestIds = testIds
            
            while (True):
                result = self.__RunTestsAux(appPython, appIndex, maxAppIndex, 
                                            testIds, applicationMap, callBack)
                if ((result == None) or (result == True)):
                    break
                
                # there was a crash: find last correct
                for i in range(len(testIds) - 1, -2, -1):
                    if (i == -1): break
                    
                    testId = testIds[i]
                    found = False
                    for step, op in self.__GetOpGenerator(appIndex):
                        if (op == VALIDATE):
                            continue
                        if (self.__testList[testId].IsCurrentOutputGood(step)):
                            found = True
                            break
                    if (found):
                        break
                
                if (callBack != None):
                    callBack(appIndex, maxAppIndex, 
                            "There was a crash. Checking for which case.")
                
                if (len(testIds) > 1):
                    while (True):
                        i = i + 1
                        if (i >= len(testIds)): break
                        result = self.__RunTestsAux(appPython, appIndex, 
                                maxAppIndex, [testIds[i],], applicationMap, 
                                callBack)
                        if ((result == None) or (result == False)):
                            break
                else:
                    i = i + 1
                if (i < len(testIds)):
                    print "test" + str(testIds[i]) + " crashed!!!"
                    for step, op in self.__GetOpGenerator(appIndex):
                        if (op != VALIDATE or op in OPS_NEEDING_APP):
                            self.__testList[testIds[i]].Crash(step)
                
                i = i + 1 # skip the broken one
                if (i >= len(testIds)): break
                
                if (callBack != None):
                    callBack(appIndex, maxAppIndex, 
                            "There was a crash. Rerunning.")
                
                testIds = testIds[i:]
            
            testIds = savedTestIds
        
        if (self.__cancelRun):
            callBack(None, None, "Cancelling...")
            for testId in testIds:
                self.__testList[testId].CancelRun()
                callBack(None, None, "Reverted test" + str(testId) + ".")
            return
        
        self.__cancelRun = True
        
        if (callBack != None):
            callBack(appIndex + 1, maxAppIndex, "Performing validation steps.")

        for testId in testIds:
            self.__testList[testId].Validate(self)

        if (callBack != None):
            callBack(appIndex + 2, maxAppIndex, "Compiling executions.")
        
        for testId in testIds:
            self.__testList[testId].Compile(self)
            
        if (callBack != None):
            callBack(appIndex + 2, maxAppIndex, "Performing badge judging.")
 
        for testId in testIds:
            self.__testList[testId].Judge(self)

        if (callBack != None):
            callBack(appIndex + 2, maxAppIndex, "Finalizing executions.")

        for testId in testIds:
            self.__testList[testId].Conclude(self)

    def CancelRun(self, callBack = None):
        if (callBack != None):
            if (self.__cancelRun):
                callBack(None, None, "Cannot canel anymore.")
            else:
                callBack(None, None, "Cancelling at next available moment.")
        self.__cancelRun = True
    
    def __GetInputStep(self, currentStep):
        inputStep = 0
        for step, app, op, setting in self.GetStepGenerator():
            if (step >= currentStep):
                break
            if (op == EXPORT):
                inputStep = step
        return inputStep
    
    def __GetAppGenerator(self):
        """Get the generator for only the applications.
        
        Upon yield, it returns an index to the application as well as the 
        string representation of the application. It does so in order of the
        list.
        
        """
        appCount = 0
        stepCount = 0
        for app in range(len(self.__procedureTree)):
            yield (appCount, stepCount, self.__procedureTree[app][0])
            appCount = appCount + 1
            for op in range(len(self.__procedureTree[app][1])):
                stepCount = stepCount + 1
    
    def __GetOpGenerator(self, appIndex):
        """Get the generator for only the operations in one application.
        
        Upon yield, it returns an index to the operation (relative to the first
        operation in the list) as well as the string representation of the 
        operation. It does so in order of the list.
        
        arguments:
            appIndex -- The index of the application to get the generator for.
        
        """
        i = 0;
        for j in range(appIndex):
            i = i + len(self.__procedureTree[j][1])
        
        for op in self.__procedureTree[appIndex][1]:
            yield (i, op[0])
            i = i + 1
    