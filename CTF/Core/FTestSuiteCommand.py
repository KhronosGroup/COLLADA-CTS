# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from Core.FCsvExporter import *
from Core.FHtmlExporter import *
from Core.FTestSuite import *
from Core.Common.FConstants import *

class FTestSuiteCommand(FTestSuite):
    def __init__(self, args):
        FTestSuite.__init__(self)
        print ("")
        
        self.__file = None
        self.__runAll = False
        self.__csvFile = None
        self.__htmlFile = None
        self.__diffHtmlFile = None
        self.__showBlessed = False
        self.__showPrevious = False
        self.__width = 100
        self.__height = 100
        self.__addMissingTests = False
        self.__statistics = None
        self.__killErrorReports = False
        
        while (len(args) != 0):
            if (args[0] == "-help"):
                self.__PrintUsage()
                return
            elif (args[0] == "-file"):
                if (len(args) == 1):
                    print "<Argument Error>: Missing argument after -file"
                    return
                else:
                    self.__file = args[1]
                    args = args[2:]
            elif (args[0] == "-runAll"):
                self.__runAll = True
                args = args[1:]
            elif (args[0] == "-killErrorReports"):
                self.__killErrorReports = True
                args = args[1:]
            elif (args[0] == "-showBlessed"):
                self.__showBlessed = True
                args = args[1:]
            elif (args[0] == "-addMissingTests"):
                self.__addMissingTests = True
                args = args[1:]
            elif (args[0] == "-showPrevious"):
                self.__showPrevious = True
                args = args[1:]
            elif (args[0] == "-previewWidth"):
                if (len(args) == 1):
                    print ("<Argument Error>: Missing argument after " +
                           "-previewWidth")
                    return
                else:
                    self.__width = args[1]
                    args = args[2:]
            elif (args[0] == "-previewHeight"):
                if (len(args) == 1):
                    print ("<Argument Error>: Missing argument after " +
                           "-previewHeight")
                    return
                else:
                    self.__height = args[1]
                    args = args[2:]
            elif (args[0] == "-statistics"):
                if (len(args) == 1):
                    print ("<Argument Error>: Missing argument after " +
                           "-statistics")
                    return
                else:
                    self.__statistics = args[1]
                    args = args[2:]
            elif (args[0] == "-csv"):
                if (len(args) == 1):
                    print "<Argument Error>: Missing argument after -csv"
                    return
                else:
                    self.__csvFile = args[1]
                    args = args[2:]
            elif (args[0] == "-html"):
                if (len(args) == 1):
                    print "<Argument Error>: Missing argument after -html"
                    return
                else:
                    self.__htmlFile = args[1]
                    args = args[2:]
            elif (args[0] == "-diffHtml"):
                if (len(args) == 1):
                    print "<Argument Error>: Missing argument after -diffHtml"
                    return
                else:
                    self.__diffHtmlFile = args[1]
                    args = args[2:]
            else:
                print "<Tag Error>: unknown tag: " + args[0]
                print "FTestSuite.py -help for usage."
                return
        
        self.__ApplyCommands()
    
    def __ApplyCommands(self):
        if (self.__file == None): 
            print ">> No file specified."
            return
        
        procedureDir = os.path.normpath(os.path.join(RUNS_FOLDER, self.__file))
        if (os.path.isdir(procedureDir)):
            testProcedure = self.Load(
                    os.path.join(procedureDir, TEST_PROCEDURE_FILENAME))
            
            if (testProcedure != None):
                for regExId in testProcedure.GetRegExIdGenerator():
                    dataSets = testProcedure.CheckForNewTests(regExId)
                    if (len(dataSets) == 0): continue
                    
                    settings = testProcedure.GetRegExSettings(regExId)
                    for dataSet in dataSets:
                        if (self.__addMissingTests):
                            testProcedure.AddTest(dataSet, settings)
                            print ("Added missing data set for Regular " +
                                    "Expression " + str(regExId) + ": " + 
                                    dataSet)
                        else:
                            print ("Ignored missing data set for Regular " +
                                    "Expression " + str(regExId) + ": " + 
                                    dataSet)
                
                print ">> Procedure loaded: " + self.__file
            else:
                print ">> Error in procedure loading: " + self.__file
                return
        else:
            print ">> No procedure as: " + self.__file
            return
        
        if (self.__runAll):
            testsToRun = []
            for test in testProcedure.GetTestGenerator():
                testsToRun.append(test.GetTestId())
            if (len(testsToRun) == 0): return
            
            testProcedure.RunTests(testsToRun, self.applicationMap)
            print ">> Ran all tests."
        
        if (self.__statistics != None):
            statisticsFile = open(self.__statistics, "w")
            
            passedCount = 0
            failedCount = 0
            totalCount = 0
            
            for test in testProcedure.GetTestGenerator():
                totalCount = totalCount + 1
                result = test.GetCurrentResult()
                if (result != None):
                    if (result.GetResult()):
                        passedCount = passedCount + 1
                    else:
                        failedCount = failedCount + 1
            
            statisticsFile.write("Failed: " + str(failedCount) + "\n")
            statisticsFile.write("Passed: " + str(passedCount) + "\n")
            statisticsFile.write("Total: " + str(totalCount) + "\n")
            statisticsFile.close()
        
        if (self.__csvFile != None):
            FCsvExporter().ToCsv(self.__csvFile, testProcedure, 
                    self.__showBlessed, self.__showPrevious, self.__width,
                    self.__height)
            print ">> Exported all tests to CSV."
            print "       - Show Blessed: " + str(self.__showBlessed)
            print "       - Show Previous: " + str(self.__showPrevious)
        
        if (self.__htmlFile != None):
            FHtmlExporter().ToHtml(self.__htmlFile, testProcedure, 
                    self.__showBlessed, self.__showPrevious, self.__width,
                    self.__height)
            print ">> Exported all tests to HTML."
            print "       - Show Blessed: " + str(self.__showBlessed)
            print "       - Show Previous: " + str(self.__showPrevious)
        
        if (self.__diffHtmlFile != None):
            keys = []
            for test in testProcedure.GetTestGenerator():
                if (test.GetCurrentDiffFromPrevious() != FTest.NO):
                    keys.append(test.GetTestId())
            FHtmlExporter().ToHtml(self.__diffHtmlFile, testProcedure,
                    self.__showBlessed, self.__showPrevious, self.__width,
                    self.__height, keys)
            print ">> Exported all different from previous tests to HTML."
            print "       - Show Blessed: " + str(self.__showBlessed)
            print "       - Show Previous: " + str(self.__showPrevious)
        
        if (self.__killErrorReports):
            os.system(KILLER + " dwwin")
            print ">> Killed all dwwin.exe."
            os.system(KILLER + " SendDmp")
            print ">> Killed all SendDmp.exe."

    def __PrintUsage(self):
        print """
Usage: FTestSuite.py [tags]

If tags is emtpy, it will launch the GUI. If tags is not empty, it will use 
commandline and not show the GUI. Tags can be in any order and there can be
only one of each (it will not check for this). The following tags are valid.

-help
    Displays this message and exits regardless of other tags.

-file [procedureName]
    Opens the test procedure specified if it exists. It must be located in the 
    TestProcedures directory to be detected. This must be a tag in order for 
    the following tags to work.

-addMissingTests
    Adds all missing tests based on the data set and the regular expresssions
    stored in the test procedure. The default is not to add.

-runAll
    Runs all the tests in the test procedure

-killErrorReports
    Kills all processes with the process name "dwwin.exe" or "SendDump.exe" 
    which are the process that pops up the error reporting dialog in Windows XP
    and 3DS Max 7, respectively. This will be done just before exiting.

-showBlessed
    Shows a preview of the blessed image next to each image output in the 
    html file (only has effect if either -html or -diffHtml are listed).

-showPrevious
    Shows a preview of the previous image next to each image output in the
    html file (only has effect if either -html or -diffHtml are listed).

-previewWidth [width]
    The width of the previews of each image output in the html file (only has
    effect if either -html or -diffHtml are listed). Default is 100.

-previewHeight [height]
    The height of the previews of each image output in the html file (only 
    has effect if either -html or -diffHtml are listed). Default is 100.

-statistics [Output]
    Creates a file with simple statistics. 

-csv [Output]
    Exports the test procedure to a csv file specified. It should be either an
    absolute path, or a relative path from the working directory (i.e. Core).

-html [Output]
    Exports the test procedure to a html file specified. It should be either an
    absolute path, or a relative path from the working directory (i.e. Core).
    This tag is processed last or just prior to -diffHtml.

-diffHtml [Output]
    Exports all tests in the test procedure that are not the same as previous
    to the html file specified. It should be either an absolute path, or a 
    relative path from the working directory (i.e. Core). This tag is processed
    last.

"""
