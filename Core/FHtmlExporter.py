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
import Core.Common.FGlobals as FGlobals
from Core.Common.FConstants import *
from Core.Logic.FJudgement import *
from Core.Logic.FJudgementCompiler import *

class FHtmlExporter:
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
    
    # path should be absolute
    def ToHtml(self, path, testProcedure, showBlessed, showPrevious, width,
               height, keys = None):
        file = open(path, "w")
        checksumFilename = FUtils.ChangeExtension(path, "sha")
        checksumFile = open(checksumFilename, "w")
        checksumFile.write(FUtils.CalculateSuiteChecksum())
        
        file.write(
                "<html>\n" +
                "<head>\n" + 
                "    <title>" + testProcedure.GetName() + "</title>\n" +
                "</head>\n" +
                "<body>\n" +
                "    <h1><center>" + testProcedure.GetName() + 
                        "</center></h1>\n" +
                "    <b><u>Statistics:</b></u>" +
                "    <table>\n" +
                "        <tr>\n" +
                "            <td># of tests in test procedure:</td>\n" +
                "            <td>" + 
                        FHtmlExporter.__REPLACE_TEST_PROCEDURE_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "        <tr>\n" +
                "            <td># of tests in HTML:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_HTML_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "        <tr>\n" +
                "            <td># of tests passed in HTML:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_PASSED_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "        <tr>\n" +
                "            <td># of tests failed in HTML:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_FAILED_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "            <td># of tests warning in HTML:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_WARNINGS_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "            <td># of tests errors in HTML:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_ERRORS_COUNT + 
                        "</td>\n" +
                "        </tr>\n" +
                "        </tr>\n" +
                "            <td>Badges earned:</td>\n" +
                "            <td>" + FHtmlExporter.__REPLACE_BADGES_EARNED + 
                        "</td>\n" +
                "        </tr>\n" +                "    </table>\n" +
                "    <br><br>\n" +
                # TODO:take with respect to how user positions the columns
                "    <center><table border=\"1\" cellspacing=\"0\" " +
                        "cellpadding=\"5\" bordercolor=\"gray\">\n" +
                "        <tr>\n" +
                "            <th>\n" +
                "                Test Id\n" +
                "            </th>\n" +
                "            <th>\n" +
                "                Categories\n" +
                "            </th>\n" +
                "            <th>\n" +
                "                Description\n" +
                "            </th>\n" +
                "            <th>\n" +
                "                Test Filename\n" +
                "            </th>\n" +
                "            <th>\n" +
                "                Blessed\n" +
                "            </th>\n")
        
        
        for step, app, op, settings in testProcedure.GetStepGenerator():
            if (op == VALIDATE and op not in OPS_NEEDING_APP):
                file.write(
                    "            <th>\n" +
                    "                <" + str(step) + "> " + op + "\n" +
                    "            </th>\n")
            else:
                file.write(
                    "            <th>\n" +
                    "                <" + str(step) + "> " + op + "(" + app + 
                            ")\n" +
                    "            </th>\n")
                    
        file.write(
                "            <th><div style=\"width: 300\">\n" +
                "                Result\n" +
                "            </div></th>\n");
                
        for i in range(len(FGlobals.badgeLevels)):
            file.write(
                "            <th>" + FGlobals.badgeLevels[i] + "</td>")
        
        file.write(
                "            <th>\n" +
                "                Different From Previous\n" +
                "            </th>\n" +
                "            <th><div style=\"width: 100\">\n" +
                "                Time\n" +
                "            </div></th>\n" +
                "            <th>\n" +
                "                Environment\n" +
                "            </th>\n" +
                "            <th>\n" +
                "                Comments\n" +
                "            </th>\n" +
                "        </tr>\n")
        
        self.__filesDir = FUtils.GetProperFilename(path) + HTML_POSTFIX
        self.__filesDir = os.path.join(os.path.dirname(path), self.__filesDir)
        self.__filesDir = self.__GetAvailableDir(self.__filesDir)
        
        os.mkdir(self.__filesDir)
        
        self.__mainDir = os.path.dirname(path)
        self.__passedTestsCount = 0
        self.__failedTestsCount = 0
        self.__warningCount = 0
        self.__errorCount = 0

        # Prepare the badges earned results.
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
        
        file.write(
                "    </table></center>\n" +
                "</body>\n" +
                "</html>\n")
        file.close()
        checksumFile.close()
        
        # Replace the statement tokens by their real values.
        badgesEarnedStatement = self.__judgementCompiler.GenerateStatement()
        if (len(badgesEarnedStatement) == 0): badgesEarnedStatement = "None"
        replaceDict = {
                FHtmlExporter.__REPLACE_TEST_PROCEDURE_COUNT : str(testProcedure.GetTestCount()),
                FHtmlExporter.__REPLACE_HTML_COUNT : str(testCount),
                FHtmlExporter.__REPLACE_PASSED_COUNT : str(self.__passedTestsCount),
                FHtmlExporter.__REPLACE_FAILED_COUNT : str(self.__failedTestsCount),
                FHtmlExporter.__REPLACE_WARNINGS_COUNT : str(self.__warningCount),
                FHtmlExporter.__REPLACE_ERRORS_COUNT : str(self.__errorCount),
                FHtmlExporter.__REPLACE_BADGES_EARNED : badgesEarnedStatement }
        
        tempFilename = FUtils.GetAvailableFilename(path + ".temp")
        f = open(tempFilename, "w")
        htmlFile = open(path)
        line = htmlFile.readline()
        while (line):
            for key in replaceDict.keys():
                if (line.count(key) != 0):
                    line = line.replace(key, replaceDict[key], 1)
                    replaceDict.pop(key)
                    break
            f.write(line)
            line = htmlFile.readline()
        htmlFile.close()
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
    
    def __GetSingleImageTag(self, mainDir, filename, width, height, 
                link = None):
        if (filename == None):
            return "Missing&nbsp;File"
        
        filename = FUtils.GetHtmlRelativePath(filename, mainDir)
        ext = FUtils.GetExtension(filename)
        
        if (link == None):
            link = filename
        else:
            link = FUtils.GetHtmlRelativePath(link, mainDir)
        
        tag = "<a href=\"" + link + "\"><img "
        
        if (FUtils.IsImageFile(ext)):
            tag = tag + "src=\"" + filename + "\" border=\"0\" "
        elif (ext == "dae"):
            tag = tag + "alt=\"Collada File\" border=\"1\" "
        elif (ext == "max"):
            tag = tag + "alt=\"Max File\" border=\"1\" "
        elif (ext == "mb"):
            tag = tag + "alt=\"Maya Binary File\" border=\"1\" "
        elif (ext == "ma"):
            tag = tag + "alt=\"Maya Ascii File\" border=\"1\" "
        else:
            tag = tag + "alt=\"Ext: " + ext + "\" border=\"1\" "
        
        return (tag + "" + "width=\"" + str(width) + 
               "\" height=\"" + str(height) + "\"></a>")
    
    # filename can't be None
    def __GetImageTag(self, exportedBlessed, exportedPrevious, 
            filename, spacing, width, height, showBlessed = False, 
            showPrevious = False):
        
        tag = spacing
        
        if (((exportedBlessed == None) or (len(exportedBlessed) == 1)) and 
                ((exportedPrevious == None) or (len(exportedPrevious) == 1)) 
                and (len(filename) == 1)):
            link = None
        else:
            animationFilename = os.path.join(self.__filesDir, "animation.html")
            animationFilename = FUtils.GetAvailableFilename(animationFilename)
            
            f = open(animationFilename, "w")
            htmlInMemory = (
                    "<html>\n" +
                    "<head>\n" +
                    "    <title>Animation</title>\n" +
                    "</head>\n" +
                    "<body>\n" +
                    "    <table>\n" +
                    "        <tr>\n")
            
            if ((showBlessed) and (exportedBlessed != None)):
                htmlInMemory = htmlInMemory + "        <th>Blessed</th>\n"
            if ((showPrevious) and (exportedPrevious != None)):
                htmlInMemory = htmlInMemory + "        <th>Previous</th>\n"
            
            htmlInMemory = (htmlInMemory + "        <th>Current</th>\n" +
                    "        </tr>\n")
            
            maxRows = len(filename)
            if ((showBlessed) and (exportedBlessed != None)):
                maxRows = max(maxRows, len(exportedBlessed))
            if ((showPrevious) and (exportedPrevious != None)):
                maxRows = max(maxRows, len(exportedPrevious))
            
            for i in range(maxRows):
                htmlInMemory = htmlInMemory + "        <tr>\n"
                
                if ((showBlessed) and (exportedBlessed != None)):
                    if (i < len(exportedBlessed)):
                        htmlInMemory = (htmlInMemory +
                            "            <td>\n" +
                            "                " + 
                            self.__GetSingleImageTag(self.__filesDir,
                                    exportedBlessed[i], width, height) + "\n" +
                            "            </td>\n")
                    else:
                        htmlInMemory = (htmlInMemory + 
                                "           <td>&nbsp;</td>")
                
                if ((showPrevious) and (exportedPrevious != None)):
                    if (i < len(exportedPrevious)):
                        htmlInMemory = (htmlInMemory +
                            "            <td>\n" +
                            "                " + 
                            self.__GetSingleImageTag(self.__filesDir,
                                    exportedPrevious[i], width, height) + 
                            "\n" +
                            "            </td>\n")
                    else:
                        htmlInMemory = (htmlInMemory + 
                                "           <td>&nbsp;</td>")
                
                if (i < len(filename)):
                    htmlInMemory = (htmlInMemory +
                        "            <td>\n" +
                        "                " + 
                        self.__GetSingleImageTag(self.__filesDir,
                                filename[i], width, height) + 
                        "\n" +
                        "            </td>\n")
                else:
                    htmlInMemory = (htmlInMemory + 
                            "           <td>&nbsp;</td>")
                
                htmlInMemory = htmlInMemory + "        </tr>\n"
            
            f.write(htmlInMemory + "    </table>\n</body>\n</html>\n")
            
            f.close()
            
            link = animationFilename
        
        if (showBlessed):
            if (exportedBlessed == None):
                tag = (tag + "<img alt=\"No Blessed\" " + 
                       "border=\"1\" width=\"" + str(width) + "\" height=\"" + 
                       str(height) + "\">&nbsp;")
            else:
                tag = (tag + self.__GetSingleImageTag(self.__mainDir, 
                        exportedBlessed[-1], width, height, link) + "&nbsp;")
        
        if (showPrevious):
            if (exportedPrevious == None):
                tag = (tag + "<img alt=\"No Previous\" " + 
                       "border=\"1\" width=\"" + str(width) + "\" height=\"" + 
                       str(height) + "\">&nbsp;")
            else:
                tag = (tag + self.__GetSingleImageTag(self.__mainDir, 
                        exportedPrevious[-1], width, height, link) + "&nbsp;")
        
        tag = (tag + self.__GetSingleImageTag(self.__mainDir, filename[-1], 
                width, height, link))
        
        return tag
    
    def __GetOutputTag(self, exportedDir, test, step, 
                exportedBlessed, showBlessed, showPrevious, width, height):
        errorCount = test.GetCurrentErrorCount(step)
        warningCount = test.GetCurrentWarningCount(step)
        
        if (errorCount != None):
            self.__errorCount = self.__errorCount + errorCount
        if (warningCount != None):
            self.__warningCount = self.__warningCount + warningCount
        
        # None (not ran) is considered < 0 in python
        if (errorCount > 0):
            tag = "            <td bgcolor=\"#FF0000\">\n"
        elif (warningCount > 0):
            tag = "            <td bgcolor=\"#FFFF00\">\n"
        else:
            tag = "            <td bgcolor=\"#FFFFFF\">\n"
        
        outputList = test.GetCurrentOutputLocation(step)
        if ((outputList == None) or (len(outputList) == 0)):
            tag = tag + "                &nbsp;\n"
        elif (not type(outputList) is types.ListType): # validation
            name = os.path.basename(outputList)
            exportedFilename = os.path.join(exportedDir, str(step) + "_" + 
                    name)
            
            if (os.path.isfile(outputList)):
                shutil.copy2(outputList, exportedFilename)
                if (errorCount > 0):
                    status = "Failed"
                else:
                    status = "Passed"
                tag = (tag + "                <a href=\"" + 
                        FUtils.GetHtmlRelativePath(exportedFilename, 
                                self.__mainDir) + 
                        "\"> " + status + "<br>" + 
                        str(warningCount) + "&nbsp;Warnings<br>" + 
                        str(errorCount) + "&nbsp;Errors</a>\n")
            else:
                tag = tag + "                Missing&nbsp;File\n"
        else:
            if (showPrevious):
                exportedPrevious = self.__ExportImageList(exportedDir,
                        test.GetPreviousOutputLocation(step), str(step) + "p_")
            else:
                exportedPrevious = None
            
            exportedFilename = self.__ExportImageList(exportedDir, outputList,
                    str(step) + "_")
            if (exportedFilename == None):
                tag = tag + "                Missing&nbsp;File<br>\n"
            else:
                tag = (tag + self.__GetImageTag(exportedBlessed, 
                        exportedPrevious, exportedFilename, "                ",
                        width, height, showBlessed, showPrevious) + "<br>\n")
        
        logName = test.GetCurrentLog(step)
        if (logName != None):  # equals None if not ran
            name = os.path.basename(logName)
            exportedLog = os.path.join(exportedDir, str(step) + "_" + name)
            if (os.path.isfile(logName)):
                shutil.copy2(logName, exportedLog)
                tag = (tag + "                <a href=\"" + 
                        FUtils.GetHtmlRelativePath(exportedLog, 
                                self.__mainDir) + 
                        "\"> " + str(warningCount) + "&nbsp;Warnings<br>" + 
                        str(errorCount) + "&nbsp;Errors</a>\n")
            else:
                tag = tag + "                Missing&nbsp;Log&nbsp;File\n"
        
        tag = tag + "            </td>\n"
        return tag
    
    def __ExportImageList(self, exportedDir, filenameList, prefix):
        exportedList = None
        if ((filenameList != None) and (len(filenameList) != 0)):
            exportedList = []
            for filename in filenameList:
                name = os.path.basename(filename)
                exportedFrame = os.path.join(exportedDir, prefix + name)
                if (os.path.isfile(filename)):
                    try:
                        shutil.copy2(filename, exportedFrame)
                    except IOError, e:
                        print ("Unable to copy " + filename + " to " +  
                                exportedFrame + ", " + "probably due to " +
                                "filename too long. Skipping.")
                    exportedList.append(exportedFrame)
                else:
                    exportedList.append(None)
        return exportedList
    
    def __AddTest(self, file, checksumFile, testProcedure, test, 
                  showBlessed, showPrevious, width, height):
                      
        # Retrieve the COLLADA asset information and write it out.
        colladaId = test.GetCOLLADAId()
        if len(colladaId) == 0: colladaId = "&nbsp;"
        colladaKeyword = test.GetCOLLADAKeyword()
        if len(colladaKeyword) == 0: colladaKeyword = "&nbsp;"
        colladaSubject = test.GetCOLLADASubject()
        if len(colladaSubject) == 0: colladaSubject = "&nbsp;"
        
        file.write(
                "        <tr>\n" +
                "            <td>\n" +
                "                " + colladaId + "\n" +
                "            </td>\n" +
                "            <td>\n" +
                "                " + colladaKeyword + "\n" +
                "            </td>\n" +
                "            <td>\n" +
                "                " + colladaSubject + "\n" +
                "            </td>\n")
        
        exportedDir = os.path.join(self.__filesDir, "Test" + str(test.GetTestId()),
            FUtils.GetProperFilename(test.GetBaseFilename()))
        exportedDir = self.__GetAvailableDir(exportedDir)
        os.makedirs(exportedDir)
        
        origTag = "            <td>\n"
        origFile = test.GetAbsFilename()
        exportedOrig = self.__ExportImageList(exportedDir, [origFile], "orig_")
        if ((exportedOrig == None) or (exportedOrig[0] == None)):
            origTag = (origTag + 
                    "                " + test.GetSeparatedFilename() + "\n")
        else:
            origTag = (origTag + 
                    "                <a href=\"" + 
                    FUtils.GetHtmlRelativePath(exportedOrig[0], self.__mainDir)
                     + "\">" + test.GetBaseFilename() + "</a>\n")
        origTag = origTag + "            </td>\n"
        file.write(origTag)
        
        blessedTag = "            <td>\n"
        exportedBlessed = self.__ExportImageList(exportedDir, 
                test.GetBlessed(), "blessed_")
        
        if (exportedBlessed == None):
            blessedTag = blessedTag + "                &nbsp;\n"
        else:
            blessedTag = ((blessedTag + self.__GetImageTag(None, None, 
                           exportedBlessed, "                ", width, 
                           height)) + "\n")
        
        blessedTag = blessedTag + "            </td>\n"
        file.write(blessedTag)
        
        for step, app, op, settings in testProcedure.GetStepGenerator():
            if (not showBlessed):
                exportedBlessed = None
            
            file.write(self.__GetOutputTag(exportedDir, test, step,
                    exportedBlessed, showBlessed, showPrevious, width, height))
        
        # Write out the local results.
        result = test.GetCurrentResult()
        if (result == None):
            resultTag = "            <td>\n"
            resultTag = resultTag + "                &nbsp;\n"
        else:
            if (result.GetResult()):
                self.__passedTestsCount = self.__passedTestsCount + 1
                resultTag = "            <td bgcolor=\"#00FF00\">\n"
            else:
                self.__failedTestsCount = self.__failedTestsCount + 1
                resultTag = "            <td bgcolor=\"#FF0000\">\n"
            
            for entry in result.GetTextArray():
                resultTag = (resultTag + "                &nbsp;" + entry + 
                             "<br>\n")
        file.write(resultTag + "            </td>\n")

        # Write out the judging results
        execution = test.GetCurrentExecution()
        for i in range(len(FGlobals.badgeLevels)):
            if (execution == None):
                file.write("            <td>NO EXECUTION</td>")
            else:
                badgeLevel = FGlobals.badgeLevels[i]
                badgeResult = execution.GetJudgementResult(badgeLevel)
                self.__judgementCompiler.ProcessJudgement(i, badgeResult)
                if (badgeResult == FJudgement.PASSED):
                    file.write("            <td>PASSED</td>")
                elif (badgeResult == FJudgement.FAILED):
                    file.write("            <td>FAILED</td>")
                elif (badgeResult == FJudgement.MISSING_DATA):
                    file.write("            <td>MISSING DATA</td>")
                elif (badgeResult == FJudgement.NO_SCRIPT):
                    file.write("            <td>NO SCRIPT</td>")
        
        # Write out the environment information
        if (test.GetCurrentTimeRan() == None):
            timeString = "&nbsp;"
        else:
            timeString = time.asctime(test.GetCurrentTimeRan())
        
        if (test.GetCurrentDiffFromPrevious() == ""):
            diff = "&nbsp;"
        else:
            diff = str(test.GetCurrentDiffFromPrevious())
        
        environmentDict = test.GetCurrentEnvironment()
        environment = ""
        for key in environmentDict.keys():
            environment = environment + key + environmentDict[key] + "<br><br>"
        if (environment == ""):
            environment = "&nbsp;"
        
        comments = test.GetCurrentComments()
        if (comments == ""):
            comments = "&nbsp;"
        
        file.write(
                "            <td>\n" +
                "                " + diff + "\n" +
                "            </td>\n" +
                "            <td>\n" +
                "                " + timeString + "\n" +
                "            </td>\n" +
                "            <td>\n" +
                "                " + environment + "\n" +
                "            </td>\n" +
                "            <td>\n" +
                "                " + comments + "\n" +
                "            </td>\n" +
                "        </tr>\n")
                
        # Append checksum.
        if (execution != None):
            checksum = execution.GetChecksum()
            checksumFile.write(checksum + "\n")

