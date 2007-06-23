# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os
import os.path
import shutil
import time
import types

import Core.Common.FUtils as FUtils
import Core.Common.FGlobals as FGlobals
import Core.Common.FCOLLADAParser as FCOLLADAParser
from Core.Common.FConstants import *
from Core.Common.FSerializable import *
from Core.Common.FSerializer import *
from Core.Logic.FExecution import *
from Core.Logic.FResult import *

class FTest(FSerializable, FSerializer):
    YES = "Yes"
    NO = "No"
    NA = "N/A"
    def __init__(self, dataSetPath, testId, settings):
        """Creates the FTest.
        
        It is ready to be saved after constructor is called.
        
        arguments:
            dataSetPath -- The relative path of the data set for the test 
            starting from the working directory  (the one from os.getcwd()).
        
        """
        FSerializable.__init__(self)
        FSerializer.__init__(self)
        
        self.__filename = None
        for entry in os.listdir(dataSetPath):
            fullEntry = os.path.join(dataSetPath, entry)
            if (os.path.isfile(fullEntry)):

                # Don't grab the python post-processing script,
                # but any other file with the same name as the last folder.
                if (FUtils.GetExtension(fullEntry).upper() != "PY" and
                        FUtils.GetProperFilename(fullEntry) == os.path.basename(dataSetPath)):
                    self.__filename = fullEntry
                    
        if (self.__filename == None):
            raise ValueError, "Invalid Data Set: " + dataSetPath
        
        self.__testDir = None
        self.__testId = testId
        self.__previousExecution = None
        self.__currentExecution = None
        self.__currentExecutionDir = ""
        self.__defaultComments = ""
        self.__settings = settings
        self.__dataSetPath = dataSetPath
        filePath = os.path.dirname(os.path.abspath(dataSetPath))

        self.RefreshCOLLADA()

        # valid while running, otherwise None
        self.__beforePreviousExecution = None 
        self.__crashIndices = None
        self.__isRecovered = False

    def SetTestDirectory(self, testDir):
        """Sets the directory for the test and creates all the necessary
        members from it.
        
        This is done outside of the constructor so that saving can be done
        directly after the constructor for efficiency. Note that the
        FTest initialization is not complete until this method is called.
        
        arguments:
            testDir -- the directory path for which the test procedure
            can save its files. This should be relative to the working 
            directory (the one from os.getcwd()).
        
        """
        self.__testDir = testDir
    
    def InitializeFromLoad(self, filename):
        self.__testDir = os.path.dirname(filename)
        self.__isRecovered = False
        self.__UpdateExecution()
        
        # Backward compatibility: if they are missing, read in the keyword/comment from the DAE document.
        if (not self.__dict__.has_key("_FTest__colladaKeyword")
            or not self.__dict__.has_key("_FTest__colladaComment")):
            self.RefreshCOLLADA()
    
    def __UpdateExecution(self):
        self.__previousExecution = None
        self.__currentExecution = None
        self.__currentExecutionDir = ""
        
        self.__currentExecutionDir, previousDir = (self.
                                                    __FindLatestExecutionDir())
        if (self.__currentExecutionDir == None):
            self.__currentExecutionDir = ""
            return
        
        executionPath = os.path.join(self.__currentExecutionDir, 
                                     EXECUTION_FILENAME)
        if (os.path.isfile(executionPath)):
            self.__currentExecution = self.Load(os.path.abspath(executionPath))
        else:
            self.__isRecovered = True
            shutil.rmtree(self.__currentExecutionDir)
            self.__UpdateExecution()
            return
        
        if (previousDir != None):
            executionPath = os.path.join(previousDir, EXECUTION_FILENAME)
            self.__previousExecution = self.Load(
                    os.path.abspath(executionPath))
    
    def IsRecovered(self):
        return self.__isRecovered
    
    def __FindLatestExecutionDir(self):
        entries = os.listdir(self.__testDir)
        if (len(entries) == 0): return (None, None)
        
        entries.sort()
        entries.reverse()
        
        finalEntry = None
        secondFinalEntry = None
        for entry in entries:
            if (entry.find(EXECUTION_PREFIX) == 0):
                if (finalEntry == None):
                    finalEntry = entry
                    continue
                if (secondFinalEntry == None):
                    secondFinalEntry = entry
                    break
        
        if (finalEntry == None): return (None, None)
        if (secondFinalEntry == None): 
            return (os.path.join(self.__testDir, finalEntry), None)
        
        finalEntryPrefix = finalEntry[:finalEntry.find("(") + 1]
        secondFinalEntryPrefix = secondFinalEntry[:secondFinalEntry.find("(") +
                                                  1]
        
        if (finalEntryPrefix == secondFinalEntryPrefix):
            searchPrefix = finalEntryPrefix
        else:
            searchPrefix = secondFinalEntryPrefix
        
        # must take into account that not all number have same digit count
        numIndex = len(searchPrefix)
        maxExecution = -1
        secondMaxExecution = -1
        for entry in entries:
            if (not os.path.isdir(os.path.join(self.__testDir, entry))): 
                continue
            if (entry.find(searchPrefix) == 0):
                number = entry[numIndex:-1]
                try:
                    intNumber = int(number)
                    if (intNumber > secondMaxExecution):
                        if (intNumber > maxExecution):
                            secondMaxExecution = maxExecution
                            maxExecution = intNumber
                        else:
                            secondMaxExecution = intNumber
                except ValueError, e:
                    print "<FTest> Invalid execution found: " + entry
                    print e
            elif (entry < searchPrefix):
                break
        
        if (finalEntryPrefix == secondFinalEntryPrefix):
            final = os.path.join(self.__testDir, 
                            searchPrefix + str(maxExecution) + ")")
            second = os.path.join(self.__testDir,
                            searchPrefix + str(secondMaxExecution) + ")")
        else:
            final = os.path.join(self.__testDir, finalEntry)
            second = os.path.join(self.__testDir, 
                            searchPrefix + str(maxExecution) + ")")
        
        return (final, second)
    
    def GetHistory(self):
        sortedExecutionFilenames = self.__GetHistoryFilenames()
        
        executions = []
        # have to take into account the ones that are already in memory
        i = 0
        if (self.__currentExecution != None):
            executions.append(self.__currentExecution)
            i = 1
        if (self.__previousExecution != None):
            executions.append(self.__previousExecution)
            i = 2
        for executionFilename in sortedExecutionFilenames[i:]:
            executionPath = os.path.join(executionFilename, EXECUTION_FILENAME)
            executions.append(self.Load(executionPath))
        
        return executions
    
    def __GetHistoryFilenames(self):
        entries = os.listdir(self.__testDir)
        if (len(entries) == 0): return []
        
        executionFilenames = []
        maxDigits = 0
        for entry in entries:
            if (entry.find(EXECUTION_PREFIX) == 0):
                executionFilenames.append(entry)
                number = entry[entry.find("(") + 1:-1]
                if (len(number) > maxDigits):
                    maxDigits = len(number)
        
        executionPaddedFilenames = []
        for i in range(len(executionFilenames)):
            executionFilename = executionFilenames[i]
            prefixEnd = executionFilename.find("(") + 1
            number = executionFilename[prefixEnd:-1]
            if (len(number) < maxDigits):
                difference = maxDigits - len(number)
                padding = ""
                for j in range(difference):
                    padding = padding + "0"
                number = padding + number
                executionFilename = (executionFilename[:prefixEnd] + number + 
                                     executionFilename[-1])
            
            executionPaddedFilenames.append((executionFilename, i))
        
        executionPaddedFilenames.sort()
        
        sortedExecutionFilenames = []
        for tuple in executionPaddedFilenames:
            full = os.path.join(self.__testDir, executionFilenames[tuple[1]])
            sortedExecutionFilenames.append(os.path.normpath(full))
        
        sortedExecutionFilenames.reverse() # want most recent first
        return sortedExecutionFilenames
    
    def GetTestDir(self):
        return self.__testDir
    
    def GetCurrentExecution(self):
        return self.__currentExecution
    
    def GetCurrentExecutionDir(self):
        return self.__currentExecutionDir;
    
    def GetBlessed(self):
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR);
        if (not os.path.isdir(blessedDir)): return None
        
        defaultFile = os.path.join(blessedDir, BLESSED_DEFAULT_FILE)
        if (not os.path.isfile(defaultFile)): return None
        
        blessedFilenames = []
        f = open(defaultFile)
        blessed = f.readline()[:-1] # remove \n
        while (blessed):
            blessed = os.path.join(blessedDir, blessed)
            if (os.path.isfile(blessed)): 
                blessedFilenames.append(blessed)
            blessed = f.readline()[:-1]
        f.close()
        
        if (blessedFilenames == []):
            try:
                os.remove(defaultFile)
            except Exception, e:
                print "<FTest> can't remove default file... continuing"
            return None
        
        return blessedFilenames
    
    def DefaultBless(self, filename):
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        if (not os.path.isdir(blessedDir)):
            os.mkdir(blessedDir)
        
        f = open(os.path.join(blessedDir, BLESSED_DEFAULT_FILE), "w")
        
        ext = FUtils.GetExtension(filename)
        blessedDir = os.path.join(blessedDir, ext)
        if (not os.path.isdir(blessedDir)):
            os.mkdir(blessedDir)
        
        blessedFilename, compareResults = self.__HasBlessed(filename)
        if ((blessedFilename != None) and (blessedFilename != "")):
            f.write(os.path.join(ext, os.path.basename(blessedFilename)) + 
                    "\n")
            f.close()
            return
        
        blessedFilename = FUtils.GetAvailableFilename(
                os.path.join(blessedDir, os.path.basename(filename)))
        f.write(os.path.join(ext, os.path.basename(blessedFilename)) + "\n")
        f.close()
        shutil.copy2(filename, blessedFilename)
    
    def Bless(self, filename):
        if (self.GetBlessed() != None):
            blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
            blessedDefault = os.path.join(blessedDir, BLESSED_DEFAULT_FILE)
            
            ext = FUtils.GetExtension(filename)
            blessedDir = os.path.join(blessedDir, ext)
            if (not os.path.isdir(blessedDir)):
                os.mkdir(blessedDir)
            
            blessed, compareResults = self.__HasBlessed(filename)
            if ((blessed != None) and (blessed != "")): return
            
            copiedFilename = FUtils.GetAvailableFilename(
                    os.path.join(blessedDir, os.path.basename(filename)))
            shutil.copy2(filename, copiedFilename)
            return
        
        # since there is no default, make it
        self.DefaultBless(filename)
    
    def BlessAnimation(self, filenames):
        if (self.GetBlessed() != None):
            blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
            blessedDefault = os.path.join(blessedDir, BLESSED_DEFAULT_FILE)
            
            blessedDir = os.path.join(blessedDir, BLESSED_ANIMATIONS)
            if (not os.path.isdir(blessedDir)):
                os.mkdir(blessedDir)
            
            blessed, compareResults = self.__HasBlessedAnimation(filenames)
            if ((blessed != None) and (blessed != "")): return
            
            directory = FUtils.GetAvailableDirectory(
                    os.path.join(blessedDir, "type"), False)
            os.mkdir(directory)
            
            digits = len(str(len(filenames)))
            i = 0
            for filename in filenames:
                padding = digits - len(str(i))
                basename = ""
                for j in range(padding):
                    basename = basename + "0"
                basename += str(i) + "." + FUtils.GetExtension(filename)
                shutil.copy2(filename, os.path.join(directory, basename))
                i = i + 1
            
            return
        
        # since there is no default, make it
        self.DefaultBlessAnimation(filenames)
    
    def DefaultBlessAnimation(self, filenames):
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        if (not os.path.isdir(blessedDir)):
            os.mkdir(blessedDir)
        
        f = open(os.path.join(blessedDir, BLESSED_DEFAULT_FILE), "w")
        
        blessedAnimationDir = os.path.join(blessedDir, BLESSED_ANIMATIONS)
        if (not os.path.isdir(blessedAnimationDir)):
            os.mkdir(blessedAnimationDir)
        
        blessed, compareResults = self.__HasBlessedAnimation(filenames)
        if ((blessed != None) and (blessed != "")):
            for blessedFilename in blessed:
                f.write(FUtils.GetRelativePath(blessedFilename, blessedDir) + 
                        "\n")
            f.close()
            return
        
        directory = FUtils.GetAvailableDirectory(
                os.path.join(blessedAnimationDir, "type"), False)
        os.mkdir(directory)
        
        digits = len(str(len(filenames)))
        i = 0
        for filename in filenames:
            padding = digits - len(str(i))
            basename = ""
            for j in range(padding):
                basename = basename + "0"
            basename += str(i) + "." + FUtils.GetExtension(filename)
            newFilename = os.path.join(directory, basename)
            shutil.copy2(filename, newFilename)
            f.write(FUtils.GetRelativePath(newFilename, blessedDir) + "\n")
            i = i + 1
        f.close()
    
    def __SearchBlessHash(self, testProcedure):
        blessedHash = os.path.join(self.__dataSetPath, BLESSED_DIR, 
                BLESSED_EXECUTIONS, BLESSED_EXECUTIONS_HASH)
        
        if (not os.path.isfile(blessedHash)): return None
        
        f = open(blessedHash, "r")
        line = f.readline()
        while (line):
            appOpString, folder = line.split("\t",1)
            if (appOpString == testProcedure.GetAppOpString()):
                f.close()
                return folder[:-1] # remove newline
            line = f.readline()
        
        f.close()
        return None
    
    def __HasBlessedExecution(self, folder, execution):
        for executionDir in os.listdir(folder):
            executionDir = os.path.join(folder, executionDir)
            if (os.path.isdir(executionDir)):
                executionFile = os.path.join(executionDir, EXECUTION_FILENAME)
                if os.path.isfile(executionFile):
                    blessedExecution = self.Load(executionFile)
                    if (blessedExecution == execution):
                        return True
        return False
    
    def __GetLastBlessedExecution(self, folder):
        max = -1
        maxFilename = ""
        for entry in os.listdir(folder):
            executionDir = os.path.join(folder, entry)
            if (os.path.isdir(executionDir)):
                executionFile = os.path.join(executionDir, EXECUTION_FILENAME)
                if os.path.isfile(executionFile):
                    num = int(entry[len("blessed_("):-1])
                    if (num > max):
                        max = num
                        maxFilename = executionFile
        
        if (maxFilename != ""):
            return self.Load(executionFile)
        else:
            return None
    
    # TODO: maybe implemented default bless execution
    def GetBlessedExecution(self, testProcedure):
        folder, blessedHash, blessedDir = self.__GetBlessedExecutionFolder(
                                                                testProcedure)
        if (folder == None): return None
        return self.__GetLastBlessedExecution(folder)
    
    def __GetBlessedExecutionFolder(self, testProcedure):
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR)
        if (not os.path.isdir(blessedDir)):
            os.mkdir(blessedDir)
        
        blessedDir = os.path.join(blessedDir, BLESSED_EXECUTIONS)
        if (not os.path.isdir(blessedDir)):
            os.mkdir(blessedDir)
        
        blessedHash = os.path.join(blessedDir, BLESSED_EXECUTIONS_HASH)
        if (not os.path.isfile(blessedHash)):
            f = open(blessedHash, "w")
            f.close()
        
        folder = self.__SearchBlessHash(testProcedure)
        
        return (folder, blessedHash, blessedDir)
    
    def BlessExecution(self, testProcedure, execution):
        if (execution == None):
            raise ValueError, "No execution"
        
        folder, blessedHash, blessedDir = self.__GetBlessedExecutionFolder(
                                                                testProcedure)
        
        if (folder == None):
            f = open(blessedHash, "a")
            folder = FUtils.GetAvailableDirectory(
                    os.path.join(blessedDir, "type"), False)
            f.write(testProcedure.GetAppOpString() + "\t" + folder + "\n")
            f.close()
            
            os.mkdir(folder)
        
        if (self.__HasBlessedExecution(folder, execution)): return
        
        executionDir = FUtils.GetAvailableDirectory(
                os.path.join(folder, "blessed"), False)
        os.mkdir(executionDir)
        clonedExecution = execution.Clone(executionDir)
        self.Save(clonedExecution, 
                  os.path.join(executionDir, EXECUTION_FILENAME))
    
    def __HasBlessedAnimation(self, filenames):
        """__HasBlessedAnimation(filename) -> bool
        
        Determines if there is a blessed animation matching the filenames 
        given.
        
        arguments:
            filenames
                list of str representing filenames of the images in an 
                animation to test agains the blessed animations.
        
        returns:
            pair representing if there was a matching blessed animation. The 
            pair has the following forms depending on if there is a blessed 
            animation, if there is a matching blessed animations, and if there 
            are no matching blessed animations:
                (None, None) if there are no blessed animations available
                ("", [[FCompareResult,...],...]) if there are blessed 
                    animations but none of them match the given files. The
                    inner lists represent the different blessed animations and
                    the FCompareResult within these lists is the result given 
                    by the FImageComparator on a single image of the animation.
                ([str,...], [[FCompareResult,...],]) if there are blessed 
                    animations and at least one of them matches the given 
                    files. The single inner list represents the blessed 
                    animation that is the first match and the FCompareResult 
                    within this list is the result given by the 
                    FImageComparator on a single image of the animation.
        
        """
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR, 
                                  BLESSED_ANIMATIONS)
        if (os.path.isdir(blessedDir)):
            allCompareResults = []
            for directory in os.listdir(blessedDir):
                blessedArray = []
                fullDirectory = os.path.join(blessedDir, directory)
                storedFilenames = []
                for filename in os.listdir(fullDirectory):
                    fullFilename = os.path.join(fullDirectory, filename)
                    if (os.path.isfile(fullFilename)):
                        storedFilenames.append(fullFilename)
                storedFilenames.sort()
                
                if (len(filenames) != len(storedFilenames)): continue
                
                compareResults = []
                foundFalse = False
                for i in range(len(filenames)):
                    compareResult = FGlobals.imageComparator.CompareImages(
                            filenames[i], storedFilenames[i])
                    compareResults.append(compareResult)
                    if (not compareResult.GetResult()):
                        foundFalse = True
                    else:
                        blessedArray.append(storedFilenames[i])
                if (foundFalse): 
                    allCompareResults.append(compareResults)
                    continue
                
                return (blessedArray, [compareResults])
            return ("", allCompareResults)
        return (None, None)
    
    def __HasBlessed(self, filename):
        """__HasBlessed(filename) -> bool
        
        Determines if there is a blessed image matching the filename given.
        
        arguments:
            filename
                str representing filename of image to test against the blessed.
        
        returns:
            pair representing if there was a matching blessed image. The pair
            has the following forms depending on if there is a blessed image,
            if there is a matching blessed image, and if there are no matching 
            blessed images:
                (None, None) if there are no blessed images available
                ("", [FCompareResult,...]) if there are blessed images but none
                    of them match the given file. The FCompareResult is the 
                    result given by the FImageComparator.
                (str, [FCompareResult,]) if there are blessed images and at 
                    least one of them matches the given file.The FCompareResult
                    returned is the one for the matching blessed image. It
                    takes the first matching blessed image it finds.
        
        """
        ext = FUtils.GetExtension(filename)
        blessedDir = os.path.join(self.__dataSetPath, BLESSED_DIR, ext)
        if (os.path.isdir(blessedDir)):
            compareResults = []
            for filename1 in os.listdir(blessedDir):
                fullFilename = os.path.join(blessedDir, filename1)
                if (not os.path.isfile(fullFilename)): 
                    continue
                compareResult = FGlobals.imageComparator.CompareImages(
                        filename, fullFilename)
                if (compareResult.GetResult()):
                    return (os.path.join(blessedDir, filename1), 
                            [compareResult,])
                compareResults.append(compareResult)
            return ("", compareResults)
        return (None, None)
    
    def HasCurrentExecution(self):
        return (self.__currentExecution != None)
    
    def DeleteCurrentExecution(self):
        dirToDelete = self.__currentExecutionDir
        
        if (dirToDelete == ""):
            raise ValueError, "No current execution."
        #TODO: try, catch this and all other shutil
        shutil.rmtree(dirToDelete)
        self.__isRecovered = False
        self.__UpdateExecution()
    
    def GetCurrentResult(self):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetResult()
    
    def __CompileResult(self, testProcedure, execution):
        if (execution == None): return
        
        # Prepare the result structure.
        result = FResult()
        
        history = self.__GetHistoryFilenames()
        try:
            currentIndex = history.index(execution.GetExecutionDir())
            previousIndex = currentIndex + 1
            if (previousIndex >= len(history)):
                previous = None
            else:
                previousPath = os.path.join(history[previousIndex], 
                                            EXECUTION_FILENAME)
                previous = self.Load(previousPath)
        except ValueError, e:
            print "<FTest> execution not in history"
            previous = None
        
        if ((previous != None) and (previous.GetResult() != None) and
                (previous.GetResult().IsOverriden()) and
                (previous == execution)):
            result.Override(previous.GetResult().GetResult())
        else:
            # checks the executions
            folder = self.__SearchBlessHash(testProcedure)
            if ((folder != None) and 
                    (self.__HasBlessedExecution(folder, execution))):
                result.SetPassFromExecution(True)
        
        # checks the individual outputs
        passed = True
        for step, app, op, setting in testProcedure.GetStepGenerator():
            outputs = execution.GetOutputLocation(step)
            if (outputs == None):
                result.AppendOutput(FResult.IGNORED_NONE)
            elif (type(outputs) is types.ListType and op != VALIDATE):
                failed = False
                for entry in outputs:
                    if (not os.path.isfile(entry)):
                        result.AppendOutput(FResult.FAILED_MISSING)
                        failed = True
                        passed = False
                        break
                
                if (not failed):
                    if (len(outputs) == 1): # still
                        ext = FUtils.GetExtension(outputs[0])
                        if (FUtils.IsImageFile(ext)):
                            blessed, compareResults = self.__HasBlessed(
                                    outputs[0])
                            if (blessed == None):
                                result.AppendOutput(
                                        FResult.IGNORED_NO_BLESS_IMAGE)
                            else:
                                message = FGlobals.imageComparator.GetMessage(
                                        compareResults)
                                if (blessed == ""):
                                    result.AppendOutput(FResult.FAILED_IMAGE,
                                            message)
                                    passed = False
                                else:
                                    result.AppendOutput(FResult.PASSED_IMAGE,
                                            message)
                        else:
                            result.AppendOutput(FResult.IGNORED_TYPE)
                    else: # animation
                        blessed, compareResults = self.__HasBlessedAnimation(
                                outputs)
                        if (blessed == None):
                            result.AppendOutput(
                                    FResult.IGNORED_NO_BLESS_ANIMATION)
                        else:
                            message = FGlobals.imageComparator.GetMessage(
                                    compareResults)
                            if (blessed == ""):
                                result.AppendOutput(FResult.FAILED_ANIMATION,
                                        message)
                                passed = False  
                            else:
                                result.AppendOutput(FResult.PASSED_ANIMATION,
                                        message)
            else: # validation
                if (execution.GetErrorCount(step) == 0):
                    result.AppendOutput(FResult.PASSED_VALIDATION)
                else:
                    result.AppendOutput(FResult.FAILED_VALIDATION)
                    passed = False
        result.SetPassFromOutput(passed)

        execution.SetResult(result)
        
    def UpdateResult(self, testProcedure, execution):
        self.__CompileResult(testProcedure, execution)
        self.Save(execution, os.path.abspath(
                os.path.join(execution.GetExecutionDir(), EXECUTION_FILENAME)))
        
    def GetDataSetPath(self):
        return self.__dataSetPath
    
    def GetTestId(self):
        return self.__testId
        
    def GetFilename(self):
        return self.__filename # Added for performance reasons.
    
    def GetBaseFilename(self):
        return os.path.basename(self.__filename)
       
    def GetAbsFilename(self):
        return os.path.abspath(self.__filename)
        
    def GetSeparatedFilename(self):
        out = self.__filename.lstrip('\\/.')
        out = out.replace("\\", " ")
        return out.replace("/", " ")

    def GetSettings(self):
        return self.__settings
    
    def IsAnimated(self):
        return ((self.__filename.find("Animation") != -1) or
                (self.__filename.find("animation") != -1))
    
    def GetPreviousOutputLocation(self, opNumber):
        if (self.__previousExecution == None): return None
        
        return self.__previousExecution.GetOutputLocation(opNumber)
    
    def GetCurrentComments(self):
        if (self.__currentExecution == None): return self.__defaultComments
        
        return self.__currentExecution.GetComments()
    
    def SetDefaultComments(self, value):
        self.__defaultComments = value
        self.Save(self, os.path.abspath(
                os.path.join(self.__testDir, TEST_FILENAME)))
    
    def GetCurrentOutputLocation(self, opNumber):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetOutputLocation(opNumber)
    
    def IsCurrentOutputGood(self, opNumber):
        return self.__currentExecution.IsOutputGood(opNumber)
    
    def GetCurrentErrorCount(self, opNumber):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetErrorCount(opNumber)
    
    def GetCurrentWarningCount(self, opNumber):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetWarningCount(opNumber)
    
    def GetCurrentTimeRan(self):
        if (self.__currentExecution == None): 
            return FExecution().GetTimeRan()
        
        return self.__currentExecution.GetTimeRan()
    
    def GetCurrentLogs(self):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetLogs()
    
    def GetCurrentLog(self, opNumber):
        if (self.__currentExecution == None): return None
        
        return self.__currentExecution.GetLog(opNumber)
    
    def GetCurrentDiffFromPrevious(self):
        if (self.__currentExecution == None): 
            return FExecution().GetDiffFromPrevious()
        
        return self.__currentExecution.GetDiffFromPrevious()
    
    def GetCurrentEnvironment(self):
        if (self.__currentExecution == None): return {}
        
        return self.__currentExecution.GetEnvironment()
        
    def RefreshCOLLADA(self):
        # If the given file is a COLLADA document, parse in the keywords and comments.
        if FCOLLADAParser.IsCOLLADADocument(self.__filename):
            (self.__colladaKeyword, self.__colladaComment) = FCOLLADAParser.GetKeywordAndComment(self.__filename)
        else:
            (self.__colladaKeyword, self.__colladaComment) = ("", "")

    def GetCOLLADAKeyword(self):
        return self.__colladaKeyword

    def GetCOLLADAComment(self):
        return self.__colladaComment

    def Prepare(self):
        self.__beforePreviousExecution = self.__previousExecution
        self.__previousExecution = self.__currentExecution
        self.__crashIndices = []
        
        postfix = "%0.4d_%0.2d_%0.2d_(" %(time.localtime()[0:3])
        filename = os.path.join(self.__testDir, EXECUTION_PREFIX + postfix)
        i = 0
        while (os.path.isdir(filename + str(i) + ")")):
            i = i + 1
        
        self.__currentExecutionDir = filename + str(i) + ")"
        self.__currentExecution = FExecution(self.__currentExecutionDir)
        try:
            os.mkdir(self.__currentExecutionDir)
        except OSError, e:
            print "<FTest> could not make the execution directory"
            print e
    
    def Validate(self, step):
        self.__currentExecution.Validate(step)
    
    def Run(self, appPython, step, op, inStep):
        self.__currentExecution.Run(appPython, step, op, inStep, 
                self.__filename, self.__settings[step].GetSettings(), 
                self.IsAnimated())
    
    def CancelRun(self):
        self.__currentExecution = self.__previousExecution
        self.__previousExecution = self.__beforePreviousExecution
        self.__beforePreviousExecution = None
        self.__crashIndices = None
        try:
            shutil.rmtree(self.__currentExecutionDir)
        except OSError, e:
            print "<FTest> can't delete executionDir, keep trying" 
            
            while(os.path.isdir(self.__currentExecutionDir)):
                try:
                    time.sleep(5)
                    shutil.rmtree(self.__currentExecutionDir)
                except OSError, e:
                    print "<FTest> trying again in 5 seconds"
            print "<FTest> succeeded in deleting"
        
        if (self.__currentExecution != None):
            self.__currentExecutionDir = (self.__currentExecution.
                                                            GetExecutionDir())
        else:
            self.__currentExecutionDir = None
    
    def Crash(self, step):
        self.__crashIndices.append(step)
    
    def Validate(self, testProcedure):
        self.__currentExecution.Validate(self.__filename, testProcedure, self.__testId)

    def Compile(self, testProcedure):
        self.__beforePreviousExecution = None
        self.__currentExecution.Compile(self.__filename, self.__crashIndices)
        self.__crashIndices = None
        executionDir = os.path.abspath(
                os.path.join(self.__currentExecutionDir, EXECUTION_FILENAME))
        
        if (self.__previousExecution == None):
            self.__currentExecution.SetDiffFromPrevious(FTest.NA)
            prevComments = self.__defaultComments
        else:
            if (self.__currentExecution == self.__previousExecution):
                self.__currentExecution.SetDiffFromPrevious(FTest.NO)
            else:
                self.__currentExecution.SetDiffFromPrevious(FTest.YES)
            prevComments = self.__previousExecution.GetComments()
        
        if (prevComments != ""):
            if (prevComments.find("<From Previous Execution>") != 0):
                prevComments = "<From Previous Execution> " + prevComments
            
            self.__currentExecution.SetComments(prevComments)
        
        self.__CompileResult(testProcedure, self.__currentExecution)
        
    def Judge(self, testProcedure):
        self.__currentExecution.Judge(self.__filename, testProcedure, self.__testId)

    def Conclude(self, testProcedure):        
        # update requires DiffFromPrevious to be set; update saves also
        self.Save(self.__currentExecution, os.path.abspath(
                os.path.join(self.__currentExecution.GetExecutionDir(), EXECUTION_FILENAME)))
