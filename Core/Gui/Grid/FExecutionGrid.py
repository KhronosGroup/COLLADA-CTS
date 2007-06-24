# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os.path
import cPickle
import Core.Common.FGlobals as FGlobals

from Core.Gui.Dialog.FPreferenceDialog import *
from Core.Gui.Grid.FCommentsEditor import *
from Core.Gui.Grid.FCommentsRenderer import *
from Core.Gui.Grid.FEditableCommentsRenderer import *
from Core.Gui.Grid.FEnvironmentRenderer import *
from Core.Gui.Grid.FGrid import *
from Core.Gui.Grid.FImageData import *
from Core.Gui.Grid.FImageRenderer import *
from Core.Gui.Grid.FLogRenderer import *
from Core.Gui.Grid.FResultRenderer import *
from Core.Gui.Grid.FJudgementRenderer import *
from Core.Gui.Grid.FTimeRenderer import *
from Core.Gui.Grid.FValidationRenderer import *
from Core.Logic.FJudgementCompiler import *

class FExecutionGrid(FGrid):
    __FILENAME = 1
    __ANNOTATIONS = 2
    __BLESSED = 3
    __INPUT = 4
    __RESULT = 5
    __DIFFERENT = 6
    __LOGS = 7
    __TIME = 8
    __ENVIRONMENT = 11
    __TEST_ID = 13
    __NEXT_KEY = 14 # WARNING: this is an increasing key: [15-199] is reserved for steps.
    __BADGE_START = 200 # WARNING: this is an increasing key: [200-299] is reserved for badge levels.
    __COLLADA_ASSET_KEYWORD = 300
    __COLLADA_ASSET_SUBJECT = 301
    __COLLADA_ASSET_ID = 302
    
    __COLUMNS = { __FILENAME : ("Test Filename", 100),
                __ANNOTATIONS : ("Comments", 100),
                __BLESSED : ("Blessed", 100),
                __INPUT : ("Test Scene", 100),
                __RESULT : ("Result", 240),
                __DIFFERENT : ("Different from Previous", 100),
                __LOGS : ("Logs", 100),
                __TIME : ("Time", 100),
                __ENVIRONMENT : ("Environment", 100),
                __COLLADA_ASSET_KEYWORD : ("Categories", 100),
                __COLLADA_ASSET_SUBJECT : ("Description", 100),
                __COLLADA_ASSET_ID : ("Test Id", 50),
                __TEST_ID : ("#", 30)}
    
    def __init__(self, parent, testProcedure, simplified, feelingViewerPath,
            pythonPath):
        FGrid.__init__(self, parent)
        
        self.__simplified = simplified
        self.__testProcedure = testProcedure
        self.__feelingViewerPath = feelingViewerPath
        self.__pythonPath = pythonPath
        self.__allColumns = []
        self.__outputKeys = []
        self.__executions = [] # [(id, test, execution),]
        self.__executionsKeyMap = {} # {id:position,}
        
        self.__executionPassed = 0
        self.__executionFailed = 0
        self.__executionTotal = 0
        self.__judgementCompiler = None
        
        self.__prefBlessed = None
        self.__prefPrevious = None
        self.__prefHeight = None
        self.__prefWidth = None
        self.__prefDiff = None
        self.__prefColumns = None
        
        # renderers and editors
        self.__blessedRenderer = None
        self.__inputRenderer = None
        self.__outputsImageRenderers = []
        self.__outputsValidationRenderers = []
        self.__resultRenderer = None
        self.__judgementRenderer = None
        self.__logRenderer = None
        self.__environmentRenderer = None
        self.__commentsRenderer = None
        self.__commentsEditor = None
        self.__wrappedTextRenderer = None
        self.__timeRenderer = None
        
        self.__Initialize()
        
        dialog = FPreferenceDialog(self, [], [])
        width, height = dialog.GetThumbnailSize()
        showBlessed = dialog.GetShowBlessed()
        showPrevious = dialog.GetShowPrevious()
        diffPath = dialog.GetDiffPath()
        shownColumns = self.__allColumns
        save = True
        
        if (not (simplified)):
            guiPrefFilename = os.path.join(RUNS_FOLDER, 
                    testProcedure.GetName(), TEST_GUI_PREFERENCES)
            if (os.path.isfile(guiPrefFilename)):
                f = open(guiPrefFilename, "r")
                tempDict = cPickle.load(f)
                f.close()
                
                if (tempDict.has_key("width")):
                    width = tempDict["width"]
                if (tempDict.has_key("height")):
                    height = tempDict["height"]
                if (tempDict.has_key("showBlessed")):
                    showBlessed = tempDict["showBlessed"]
                if (tempDict.has_key("showPrevious")):
                    showPrevious = tempDict["showPrevious"]
                if (tempDict.has_key("diffPath")):
                    diffPath = tempDict["diffPath"]
                if (tempDict.has_key("shownColumns")):
                    shownColumns = tempDict["shownColumns"]
                
                save = False
        
        self.SetPreferences(width, height, showBlessed, showPrevious, 
                            diffPath, shownColumns, save)
    
    def AppendExecutionContext(self):
        FGrid.AppendContext(self, None, None)
        FGrid.AppendContext(self, "Bless Execution", 
                            self.__OnContextBlessExecution)
        FGrid.AppendContext(self, "Update Execution Result", 
                            self.__OnContextUpdateResult)
    
    def __OnContextBlessExecution(self, e):
        keys = self.GetSelectedKeys()
        if (len(keys) == 0): return
        
        busyInfo = wx.BusyInfo("Blessing execution. Please wait...")
        changed = False
        for key in keys:
            position = self.__executionsKeyMap[key]
            id, test, execution = self.__executions[position]
            
            if (execution == None): continue
            
            self.PartialRefreshRemove(test)
            test.BlessExecution(self.__testProcedure, execution)
            test.UpdateResult(self.__testProcedure, execution)
            self.PartialRefreshAdd(test)
            
        self.PartialRefreshDone()
    
    def __OnContextUpdateResult(self, e):
        keys = self.GetSelectedKeys()
        if (len(keys) == 0): return
        
        busyInfo = wx.BusyInfo("Updating execution result. Please wait...")
        for key in keys:
            position = self.__executionsKeyMap[key]
            id, test, execution = self.__executions[position]
            self.PartialRefreshRemove(test)
            test.UpdateResult(self.__testProcedure, execution)
            self.PartialRefreshAdd(test)
        self.PartialRefreshDone()
    
    def SetAnimateAll(self, value):
        self.__inputRenderer.SetAnimateAll(value)
        self.__blessedRenderer.SetAnimateAll(value)
        for outputRenderer in self.__outputsImageRenderers:
            outputRenderer.SetAnimateAll(value)
        self.ForceRefresh()
    
    def GetAllColumns(self):
        return self.__allColumns
    
    def GetShownColumns(self):
        return self.__prefColumns
    
    def GetShowBlessed(self):
        return self.__prefBlessed
    
    def GetShowPrevious(self):
        return self.__prefPrevious
    
    def GetThumbnailWidth(self):
        return self.__prefWidth
    
    def GetThumbnailHeight(self):
        return self.__prefHeight
    
    def GetDiff(self):
        return self.__prefDiff
        
    def SetPreferences(self, newWidth, newHeight, newBlessed, newPrevious, 
                       newDiff, newColumns, save = True):
        if ((newWidth == self.__prefWidth) and 
                (newHeight == self.__prefHeight) and 
                (newBlessed == self.__prefBlessed) and
                (newPrevious == self.__prefPrevious) and
                (newDiff == self.__prefDiff) and
                (newColumns == self.__prefColumns)):
            return
        
        self.__prefWidth = newWidth
        self.__prefHeight = newHeight
        self.__prefBlessed = newBlessed
        self.__prefPrevious = newPrevious
        self.__prefDiff = newDiff
        self.__prefColumns = newColumns
        
        if (save):
            self.__SavePreferences()
        
        self.__blessedRenderer.SetThumbnailSize(newWidth, newHeight)
        self.__inputRenderer.SetThumbnailSize(newWidth, newHeight)
        self.__logRenderer.SetDiffCommand(newDiff)
        for renderer in self.__outputsImageRenderers:
            renderer.SetDiffCommand(newDiff)
            renderer.SetThumbnailSize(newWidth, newHeight)
            renderer.SetShowBlessed(newBlessed)
            renderer.SetShowPrevious(newPrevious)
        
        shownColumns = []
        for columnPair in self.__prefColumns:
            shownColumns.append(columnPair[0])
        self.SetColumnOrder(shownColumns)
        
        # this should be enough width the spacing and font size
        self.SetDefaultRowSize(self.__prefHeight + 35, True)
        
        numImages = 1
        if (self.__prefBlessed):
            numImages = numImages + 1
        if (self.__prefPrevious):
            numImages = numImages + 1
        
        self.SetColSize(FExecutionGrid.__BLESSED, max(self.__prefWidth + 10, 100))
        self.SetColSize(FExecutionGrid.__INPUT, max(self.__prefWidth + 10, 100))
        for key in self.__outputKeys:
            self.SetColSize(key, max(numImages * (self.__prefWidth + 10), 100))
        
        self.FullRefresh()
    
    def AddExecution(self, id, test, execution):
        if (self.__executionsKeyMap.has_key(id)):
            raise KeyError, "Key already exists: " + str(id)
        
        self.__executionsKeyMap[id] = len(self.__executions)
        self.__executions.append((id, test, execution))
        self.AppendRow(id)
    
    def ReplaceExecution(self, id, test, execution):
        if (not self.__executionsKeyMap.has_key(id)):
            raise KeyError, "Key does not exist: " + str(id)
        
        position = self.__executionsKeyMap[id]
        self.__executions[position] = (id, test, execution)
    
    def DeleteExecution(self, id):
        if (not self.__executionsKeyMap.has_key(id)):
            raise KeyError, "Key does not exist: " + str(id)
        
        position = self.__executionsKeyMap[id]
        self.DeleteRow(id)
        self.__executions.pop(position)
        self.__executionsKeyMap.pop(id)
        for key in self.__executionsKeyMap.keys():
            pos = self.__executionsKeyMap[key]
            if (pos > position):
                self.__executionsKeyMap[key] = pos - 1
    
    def __Initialize(self):
        self.__blessedRenderer = FImageRenderer(self.__feelingViewerPath, 
                self.__pythonPath, self.__prefWidth, 
                self.__prefHeight, self.__testProcedure, self.__prefBlessed, 
                self.__prefPrevious, False)
        self.__inputRenderer = FImageRenderer(self.__feelingViewerPath, 
                self.__pythonPath, self.__prefWidth, 
                self.__prefHeight, self.__testProcedure, self.__prefBlessed, 
                self.__prefPrevious, False)
        self.__outputsImageRenderers = []
        self.__outputsValidationRenderers = []
        self.__resultRenderer = FResultRenderer()
        self.__judgementRenderer = FJudgementRenderer()
        self.__logRenderer = FLogRenderer()
        self.__environmentRenderer = FEnvironmentRenderer()
        self.__commentsRenderer = FEditableCommentsRenderer()
        self.__commentsEditor = FCommentsEditor()
        self.__wrappedTextRenderer = FCommentsRenderer()
        self.__timeRenderer = FTimeRenderer()
        
        self.__AddColumn(FExecutionGrid.__TEST_ID,
                FExecutionGrid.__COLUMNS[FExecutionGrid.__TEST_ID])
        self.__AddColumn(FExecutionGrid.__COLLADA_ASSET_ID,
                FExecutionGrid.__COLUMNS[FExecutionGrid.__COLLADA_ASSET_ID],
                self.__wrappedTextRenderer)
        self.__AddColumn(FExecutionGrid.__COLLADA_ASSET_KEYWORD,
                FExecutionGrid.__COLUMNS[FExecutionGrid.__COLLADA_ASSET_KEYWORD],
                self.__wrappedTextRenderer)
        self.__AddColumn(FExecutionGrid.__COLLADA_ASSET_SUBJECT,
                FExecutionGrid.__COLUMNS[FExecutionGrid.__COLLADA_ASSET_SUBJECT],
                self.__wrappedTextRenderer)
        self.__AddColumn(FExecutionGrid.__FILENAME, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__FILENAME],
                self.__wrappedTextRenderer)
        self.__AddColumn(FExecutionGrid.__BLESSED, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__BLESSED], 
                self.__blessedRenderer)
        self.__AddColumn(FExecutionGrid.__INPUT, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__INPUT], 
                self.__inputRenderer)
        
        for step, app, op, setting in self.__testProcedure.GetStepGenerator():
            if (op == VALIDATE):
                title = "<" + str(step) + "> " + op
                if (app != None) and (op in OPS_NEEDING_APP):
                    title = title + " (" + app + ")"
                outputRenderer = FValidationRenderer()
                self.__outputsValidationRenderers.append(outputRenderer)
            else:
                title = "<" + str(step) + "> " + op + " (" + app + ")"
                outputRenderer = FImageRenderer(self.__feelingViewerPath, 
                        self.__pythonPath, 100, 100, self.__testProcedure, 
                        self.__prefBlessed, self.__prefPrevious, True)
                self.__outputsImageRenderers.append(outputRenderer)
                self.__outputKeys.append(FExecutionGrid.__NEXT_KEY + step)
            self.__AddColumn(FExecutionGrid.__NEXT_KEY + step, (title, 150), 
                    outputRenderer)
            
        self.__AddColumn(FExecutionGrid.__RESULT, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__RESULT], 
                self.__resultRenderer)

        for i in range(len(FGlobals.badgeLevels)):
            self.__AddColumn(FExecutionGrid.__BADGE_START + i,
                (FGlobals.badgeLevels[i] + " badge", 20),
                self.__judgementRenderer)

        self.__AddColumn(FExecutionGrid.__DIFFERENT, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__DIFFERENT])
        self.__AddColumn(FExecutionGrid.__LOGS, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__LOGS], 
                self.__logRenderer)
        self.__AddColumn(FExecutionGrid.__ANNOTATIONS, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__ANNOTATIONS], 
                self.__commentsRenderer, self.__commentsEditor)
        self.__AddColumn(FExecutionGrid.__TIME, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__TIME],
                self.__timeRenderer)
        self.__AddColumn(FExecutionGrid.__ENVIRONMENT, 
                FExecutionGrid.__COLUMNS[FExecutionGrid.__ENVIRONMENT], 
                self.__environmentRenderer)
    
    def __AddColumn(self, key, columnInfo, renderer = None, editor = None):
        self.AppendColumn(key, columnInfo[0], columnInfo[1], renderer, editor)
        self.__allColumns.append((key, columnInfo[0]))
    
    def __SavePreferences(self):
        tempDict = {"width" : self.__prefWidth,
                    "height" : self.__prefHeight,
                    "showBlessed" : self.__prefBlessed,
                    "showPrevious" : self.__prefPrevious,
                    "diffPath" : self.__prefDiff,
                    "shownColumns" : self.__prefColumns}
        
        guiPrefFilename = os.path.join(RUNS_FOLDER, 
                self.__testProcedure.GetName(), TEST_GUI_PREFERENCES)
        f = open(guiPrefFilename, "w")
        cPickle.dump(tempDict, f)
        f.close()
    
    # clears the table and repopulates
    def FullRefresh(self):
        self.ClearGrid()
        
        # Restart the counters.
        self.__executionTotal = 0
        self.__executionPassed = 0
        self.__executionFailed = 0
        self.__judgementCompiler = FJudgementCompiler()
        
        # Iterate over the tests, filling in the table
        # and processing the results.
        for id, test, execution in self.__executions:
            self.PartialRefreshAdd(test)
        self.PartialRefreshDone()
    
    def PartialRefreshRemove(self, test):
        self.__executionTotal = self.__executionTotal - 1

        # Retrieve the execution that is currently displayed.
        id = test.GetTestId()
        row = self.__executionsKeyMap[id]
        (id, test, execution) = self.__executions[row]
        
        # Remove the passed/failed status.
        if execution != None:
            result = execution.GetResult()
            if result != None:
                if result.GetResult():
                    self.__executionPassed = self.__executionPassed - 1
                else:
                    self.__executionFailed = self.__executionFailed - 1

            # Remove the judgements.
            for i in range(len(FGlobals.badgeLevels)):
                badgeName = FGlobals.badgeLevels[i]
                badgeResult = execution.GetJudgementResult(badgeName)
                self.__judgementCompiler.RemoveJudgement(i, badgeResult)

    def PartialRefreshAdd(self, test):        
        self.__executionTotal = self.__executionTotal + 1
        
        id = test.GetTestId()
            
        execution = test.GetCurrentExecution()
        if (execution == None):
            comments = test.GetCurrentComments()
            executionDir = None
        else:
            comments = execution.GetComments()
            executionDir = execution.GetExecutionDir()
                
        if (execution != None): 
            logs = [] # probably want to put this in a class
            for step, app, op, setting in (self.__testProcedure.GetStepGenerator()):
                if (op == VALIDATE):
                    self.InsertData(id, FExecutionGrid.__NEXT_KEY + step, 
                            [execution.GetErrorCount(step), 
                             execution.GetWarningCount(step),
                             execution.GetOutputLocation(step)])
                else:
                    outputFilenameList = execution.GetOutputLocation(step)
                    
                    logs.append((execution.GetLog(step),
                                 os.path.basename(execution.GetExecutionDir()),
                                 os.path.basename(test.GetTestDir()),
                                 self.__testProcedure.GetName()))
                    
                    # application specific python script no operation
                    if (outputFilenameList == None): continue 
                    
                    if (self.__simplified):
                        previousList = None
                    else:
                        previousList = test.GetPreviousOutputLocation(step)
                    
                    self.InsertData(id, FExecutionGrid.__NEXT_KEY + step, 
                            FImageData(outputFilenameList, 
                                       test.GetBlessed(),
                                       previousList,
                                       execution.GetErrorCount(step),
                                       execution.GetWarningCount(step),
                                       execution.GetLog(step),
                                       test,
                                       execution.GetExecutionDir()))
                                       
            # Judgement for badge levels
            for i in range(len(FGlobals.badgeLevels)):
                badgeName = FGlobals.badgeLevels[i]
                badgeResult = execution.GetJudgementResult(badgeName)
                badgeExecutionLog = execution.GetJudgementLog(badgeName)
                
                # Process and render the judgement information
                self.InsertData(id, FExecutionGrid.__BADGE_START + i, FJudgement(badgeResult, badgeExecutionLog))
                self.__judgementCompiler.ProcessJudgement(i, badgeResult)
            
            # Display the environment columns
            self.InsertData(id, FExecutionGrid.__DIFFERENT, execution.GetDiffFromPrevious())
            self.InsertData(id, FExecutionGrid.__RESULT, (execution.GetResult(), execution, test))
            self.InsertData(id, FExecutionGrid.__LOGS, logs)
            self.InsertData(id, FExecutionGrid.__TIME, execution.GetTimeRan())
            self.InsertData(id, FExecutionGrid.__ENVIRONMENT, execution.GetEnvironment())
            
            result = execution.GetResult()
            if result != None:
                if result.GetResult():
                    self.__executionPassed = self.__executionPassed + 1
                else:
                    self.__executionFailed = self.__executionFailed + 1
        else:
            self.ClearRow(id)

        # Insert this data afterwards so that ClearRow can do its work.
        self.InsertData(id, FExecutionGrid.__TEST_ID, test.GetTestId())
        self.InsertData(id, FExecutionGrid.__FILENAME, (test.GetSeparatedFilename(),))
        self.InsertData(id, FExecutionGrid.__COLLADA_ASSET_ID, (test.GetCOLLADAId(),))
        self.InsertData(id, FExecutionGrid.__COLLADA_ASSET_KEYWORD, (test.GetCOLLADAKeyword(),))
        self.InsertData(id, FExecutionGrid.__COLLADA_ASSET_SUBJECT, (test.GetCOLLADASubject(),))
        self.InsertData(id, FExecutionGrid.__ANNOTATIONS, (comments, test, execution))
        self.InsertData(id, FExecutionGrid.__INPUT, FImageData([test.GetAbsFilename(),], test = test, executionDir = executionDir))
        
        blessed = test.GetBlessed()
        if ((blessed != None) and (len(blessed) != 0)):
            self.InsertData(id, FExecutionGrid.__BLESSED,  FImageData(blessed, test = test, executionDir = executionDir))

    def PartialRefreshDone(self):
        if not self.__simplified:
            self.GetParent().SetStatistics(self.__executionTotal, self.__executionPassed, self.__executionFailed)
            self.GetParent().SetBadgesEarned(self.__judgementCompiler.GenerateStatement())
        self.Refresh()

