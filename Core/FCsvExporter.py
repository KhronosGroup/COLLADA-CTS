# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import os.path
import shutil
import types
import time

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Core.Logic.FJudgement import *
from Core.Logic.FJudgementCompiler import *

class FCsvExporter:
    __REPLACE_TEST_PROCEDURE_COUNT = "???Replace with test procedure count???"
    __REPLACE_HTML_COUNT = "???Replace with HTML count???"
    __REPLACE_PASSED_COUNT = "???Replace with passed count???"
    __REPLACE_FAILED_COUNT = "???Replace with failed count???"
    __REPLACE_WARNINGS_COUNT = "???Replace with warnings count???"
    __REPLACE_ERRORS_COUNT = "???Replace with errors count???"
    __REPLACE_BADGES_EARNED = "???Replace with badges earned statement???"
    
    def __init__(self):
        self.__mainDir = None
        self.__filesDir = None
        self.__passedTestsCount = 0
        self.__failedTestsCount = 0
        self.__warningCount = 0
        self.__errorCount = 0
        self.__judgementCompiler = FJudgementCompiler()

    #path should be absolute
    def ToCsv(self, path, testProcedure, showBlessed, showPrevious, width,
               height, keys = None):
        file = open(path, "w")
        checksumFile = open(FUtils.ChangeExtension(path, "sha"), "w")
        checksumFile.write(FUtils.CalculateSuiteChecksum())
        
        file.write("\nTest Procedure:,%s\n\n" % (testProcedure.GetName()))    
        file.write("Statistics: \n" +
                "# of tests in test procedure:," + FCsvExporter.__REPLACE_TEST_PROCEDURE_COUNT + "\n" + 
                "# of tests:," + FCsvExporter.__REPLACE_HTML_COUNT + "\n" + 
                "# of tests passed:," + FCsvExporter.__REPLACE_PASSED_COUNT + "\n" + 
                "# of tests failed:," + FCsvExporter.__REPLACE_FAILED_COUNT + "\n" + 
                "# of tests warning:," + FCsvExporter.__REPLACE_WARNINGS_COUNT + "\n" + 
                "# of tests errors:," + FCsvExporter.__REPLACE_ERRORS_COUNT + "\n" +
                "Badges earned:," + FCsvExporter.__REPLACE_BADGES_EARNED + "\n\n")
        file.write("Test Id,Categories,Description,Test Filename,Blessed,")    
        for step, app, op, settings in testProcedure.GetStepGenerator():
            if (op == VALIDATE and op not in OPS_NEEDING_APP):
                file.write("<" + str(step) + ">" + " " + op + ",")
            else:
                file.write("<" + str(step) + ">" + " " + op + " (" + app + "),")
        file.write("Results,")
        for i in range(len(FGlobals.badgeLevels)):
            file.write(FGlobals.badgeLevels[i] + ",")
        file.write("Different From Previous,Time,Environment,Comments\n")    

        self.__filesDir = FUtils.GetProperFilename(path) + CSV_POSTFIX
        self.__filesDir = os.path.join(os.path.dirname(path), self.__filesDir)
        self.__filesDir = self.__GetAvailableDir(self.__filesDir)
        
     #   os.mkdir(self.__filesDir)
        
        self.__mainDir = os.path.dirname(path)
        self.__passedTestsCount = 0
        self.__failedTestsCount = 0
        self.__warningCount = 0
        self.__errorCount = 0
        
        testCount = 0
        if (keys == None):
            for test in testProcedure.GetTestGenerator():
                self.__AddTest(file, checksumFile, testProcedure, test, showBlessed, 
                              showPrevious, width, height)
                testCount = testCount + 1
        else:
            for key in keys:
                self.__AddTest(file, checksumFile, testProcedure, testProcedure.GetTest(key), 
                               showBlessed, showPrevious, width, height)
                testCount = testCount + 1
        
        file.close()
        
        # Replace the statement tokens by their real values.
        badgesEarnedStatement = self.__judgementCompiler.GenerateStatement()
        if (len(badgesEarnedStatement) == 0): badgesEarnedStatement = "None"
        replaceDict = {
                FCsvExporter.__REPLACE_TEST_PROCEDURE_COUNT : str(testProcedure.GetTestCount()),
                FCsvExporter.__REPLACE_HTML_COUNT : str(testCount),
                FCsvExporter.__REPLACE_PASSED_COUNT : str(self.__passedTestsCount),
                FCsvExporter.__REPLACE_FAILED_COUNT : str(self.__failedTestsCount),
                FCsvExporter.__REPLACE_WARNINGS_COUNT : str(self.__warningCount),
                FCsvExporter.__REPLACE_ERRORS_COUNT : str(self.__errorCount),
                FCsvExporter.__REPLACE_BADGES_EARNED : badgesEarnedStatement }
        
        tempFilename = FUtils.GetAvailableFilename(path + ".temp")
        f = open(tempFilename, "w")
        csvFile = open(path)
        line = csvFile.readline()
        while (line):
            for key in replaceDict.keys():
                if (line.count(key) != 0):
                    line = line.replace(key, replaceDict[key], 1)
                    replaceDict.pop(key)
                    break
            f.write(line)
            line = csvFile.readline()
        csvFile.close()
        f.close()
        
        shutil.copy2(tempFilename, path)
        os.remove(tempFilename)
    
    def __GetAvailableDir(self, suggestion):
        if (os.path.isdir(suggestion)):
            i = 0
            while (os.path.isdir(suggestion + "_(" + str(i) + ")")):
                i = i + 1
            suggestion = suggestion + "_(" + str(i) + ")"
        return suggestion
    
    def __GetOutputTag(self, exportedDir, test, step, 
                exportedBlessed, showBlessed, showPrevious, width, height):
        errorCount = test.GetCurrentErrorCount(step)
        warningCount = test.GetCurrentWarningCount(step)
        
        if (errorCount != None):
            self.__errorCount = self.__errorCount + errorCount
        if (warningCount != None):
            self.__warningCount = self.__warningCount + warningCount
        
        tag = ""
        
        outputList = test.GetCurrentOutputLocation(step)
        if ((outputList == None) or (len(outputList) == 0)):
            tag = tag + " "
        elif (not type(outputList) is types.ListType): # validation
            name = os.path.basename(outputList)
            exportedFilename = os.path.join(exportedDir, str(step) + "_" + 
                    name)
            
            if (os.path.isfile(outputList)):
         #       shutil.copy2(outputList, exportedFilename)
                if (errorCount > 0):
                    status = "Failed"
                else:
                    status = "Passed"
                tag = (tag +  status + 
                        " - " + str(warningCount) + " Warnings " + 
                        " - " + str(errorCount) + " Errors")
            else:
                tag = tag + "Missing File"
        else:
            if (showPrevious):
                exportedPrevious = self.__ExportImageList(exportedDir,
                        test.GetPreviousOutputLocation(step), str(step) + "p_")
            else:
                exportedPrevious = None
            
            exportedFilename = self.__ExportImageList(exportedDir, outputList,
                    str(step) + "_")
            if (exportedFilename == None):
                tag = tag + "Missing File"
        
        logName = test.GetCurrentLog(step)
        if (logName != None):  # equals None if not ran
            name = os.path.basename(logName)
            exportedLog = os.path.join(exportedDir, str(step) + "_" + name)
            if (os.path.isfile(logName)):
        #        shutil.copy2(logName, exportedLog)
                tag = (tag + 
#                        FUtils.GetRelativePath(exportedLog, self.__mainDir) + 
#                        " - " + str(warningCount) + " Warnings" + 
                        str(warningCount) + " Warnings" + 
                        " - " + str(errorCount) + " Errors")
            else:
                tag = tag + "Missing Log File"
        
        return tag
    
    def __ExportImageList(self, exportedDir, filenameList, prefix):
        exportedList = None
        if ((filenameList != None) and (len(filenameList) != 0)):
            exportedList = []
            for filename in filenameList:
                name = os.path.basename(filename)
                exportedFrame = os.path.join(exportedDir, prefix + name)
                if (os.path.isfile(filename)):
            #        shutil.copy2(filename, exportedFrame)
                    exportedList.append(exportedFrame)
                else:
                    exportedList.append(None)
        return exportedList
    
    def __AddTest(self, file, checksumFile, testProcedure, test, 
                  showBlessed, showPrevious, width, height):

	print "ID: %s" % (test.GetCOLLADAId())
        file.write(test.GetCOLLADAId() + ",")
        file.write(test.GetCOLLADAKeyword() + ",")
        file.write(test.GetCOLLADASubject() + ",")
        file.write(test.GetSeparatedFilename() + ",")  

        execution = test.GetCurrentExecution()
        exportedDir = os.path.join(self.__filesDir, "Test" + str(test.GetTestId()),
            FUtils.GetProperFilename(test.GetBaseFilename()))
        exportedDir = self.__GetAvailableDir(exportedDir)
        
        exportedBlessed = self.__ExportImageList(exportedDir, 
                test.GetBlessed(), "blessed_")
        
        file.write(",")
        
        for step, app, op, settings in testProcedure.GetStepGenerator():
            if (not showBlessed):
                exportedBlessed = None
            
            file.write(self.__GetOutputTag(exportedDir, test, step,
                    exportedBlessed, showBlessed, showPrevious, width, height) + ",")
        
        # Write out the local results
        result = test.GetCurrentResult()
        if (result == None):
            resultTag = ""
        else:
            if (result.GetResult()):
                self.__passedTestsCount = self.__passedTestsCount + 1
                resultTag = ""
            else:
                self.__failedTestsCount = self.__failedTestsCount + 1
                resultTag = ""
            
            for entry in result.GetTextArray():
                resultTag = resultTag + " " + entry + " "
        file.write(resultTag + ",");

        # Write out the judging results
        for i in range(len(FGlobals.badgeLevels)):
            if (execution == None):
                file.write("NO EXECUTION,")
            else:
                badgeLevel = FGlobals.badgeLevels[i]
                badgeResult = execution.GetJudgementResult(badgeLevel)
                self.__judgementCompiler.ProcessJudgement(i, badgeResult)
                if (badgeResult == FJudgement.PASSED):
                    file.write("PASSED,")
                elif (badgeResult == FJudgement.FAILED):
                    file.write("FAILED,")
                elif (badgeResult == FJudgement.MISSING_DATA):
                    file.write("MISSING DATA,")
                elif (badgeResult == FJudgement.NO_SCRIPT):
                    file.write("NO SCRIPT,")        
        
        if (test.GetCurrentTimeRan() == None):
            timeString = ""
        else:
            timeString = time.asctime(test.GetCurrentTimeRan())
        
        if (test.GetCurrentDiffFromPrevious() == ""):
            diff = ""
        else:
            diff = str(test.GetCurrentDiffFromPrevious())

        environmentDict = test.GetCurrentEnvironment()
        environment = ""
        for key in environmentDict.keys():
            environment = environment + key + environmentDict[key] + " "
        if (environment == ""):
            environment = ""
        
        comments = test.GetCurrentComments()
        if (comments == ""):
            comments = ""
        
        file.write(diff + "," + timeString + "," + environment + "," + comments)
        file.write("\n")
        
        # Append checksum.
        if (execution != None):
            checksum = execution.GetChecksum()
            checksumFile.write(checksum + "\n")

