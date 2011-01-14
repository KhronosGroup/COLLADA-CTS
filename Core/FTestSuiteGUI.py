# Copyright (C) 2006-2010 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import wx.wizard
import shutil
import threading
import zipfile
import glob, os
import shutil

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Core.Gui.Dialog.FAppSettingsDialog import *
from Core.Gui.Dialog.FBlessedViewerDialog import *
from Core.Gui.Dialog.FCompareSetupDialog import *
from Core.Gui.Dialog.FExecutionDialog import *
from Core.Gui.Dialog.FOpenDialog import *
from Core.Gui.Dialog.FPreferenceDialog import *
from Core.Gui.Dialog.FProgressDialog import *
from Core.Gui.Dialog.FRegExDialog import *
from Core.Gui.Dialog.FRunConfigDialog import *
from Core.Gui.Dialog.FSelectDataSetDialog import *
from Core.Gui.Dialog.FSettingDialog import *
from Core.Gui.Grid.FExecutionGrid import *
from Core.Gui.FMenuBar import *
from Core.Gui.FImageType import *
from Core.FTestSuite import *
from Core.FHtmlExporter import *
from Core.FCsvExporter import *

def makeArchive(fileList, archive):
     """
     'fileList' is a list of file names - full path each name
     'archive' is the file name for the archive with a full path
     """
     try:
     	 typeList = [".png", ".dae", ".html", ".csv", ".sha", ".log", ".py", ".txt"]
         a = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
         for f in fileList:
             found = False
             for t in typeList:             
                 pos = f.find(t)
		 if (pos > -1):
		     # Insure its the last thing
		     flen = len(f)
		     tlen = len(t)
#		     print "flen: %s  tlen: %s  pos: %s" % (flen, tlen, pos)
		     if (pos == (flen - tlen)):
		         pos = f.find("blessed")
		         if (pos < 0):
		             found = True
             if (found):
#  	         print "archiving file %s" % (f)
	         a.write(f)
	     else:
	     	 print "shipping file %s" % (f)

         a.close()
         return True
     except: return False

def dirEntries(dir_name, subdir, *args):
     '''Return a list of file names found in directory 'dir_name'
     If 'subdir' is True, recursively access subdirectories under 'dir_name'.
     Additional arguments, if any, are file extensions to match filenames. Matched
         file names are added to the list.
     If there are no additional arguments, all files found in the directory are
         added to the list.
     Example usage: fileList = dirEntries(r'H:\TEMP', False, 'txt', 'py')
         Only files with 'txt' and 'py' extensions will be added to the list.
     Example usage: fileList = dirEntries(r'H:\TEMP', True)
         All files and all the files in subdirectories under H:\TEMP will be added
         to the list.
     '''
     fileList = []
     for file in os.listdir(dir_name):
         dirfile = os.path.join(dir_name, file)
         if os.path.isfile(dirfile):
             if not args:
                 fileList.append(dirfile)
             else:
                 if os.path.splitext(dirfile)[1][1:] in args:
                     fileList.append(dirfile)
         # recursively access file names in subdirectories
         elif os.path.isdir(dirfile) and subdir:
             print "Accessing directory:", dirfile
             fileList.extend(dirEntries(dirfile, subdir, *args))
     return fileList
     
class FSFrame(FTestSuite):
    def __init__(self, MDIparent, createToolbar):
        FTestSuite.__init__(self)
        self.__MDIparent = MDIparent
        
        self.menu = FMenuBar(self, createToolbar)
        self.SetMenuBar(self.menu)
        self.menu.Bind(FMenuBar.ID_NEW, self.__OnNew)
        self.menu.Bind(FMenuBar.ID_EXIT, self.__OnExit)
        self.menu.Bind(FMenuBar.ID_HELP, self.__OnHelp)
        self.menu.Bind(FMenuBar.ID_ABOUT, self.__OnAbout)
        self.menu.Bind(FMenuBar.ID_OPEN, self.__OnOpen)
    
    def __OnNew(self, e):
        dialog = FRunConfigDialog(self, self.applicationMap)
        if (dialog.ShowModal() == wx.ID_OK):
            testProcedure = self.SaveProcedure(dialog.title, 
                    dialog.selectedRun, dialog.GetComments())
            if (testProcedure != None):
                child = RunTable(self.__MDIparent, wx.ID_ANY, testProcedure)
                child.Maximize(True)
                child.Show(True)
        dialog.Destroy()
    
    def __OnOpen(self, e):
        fileChooser = FOpenDialog(self)
        if (fileChooser.ShowModal() == wx.ID_OK):
            self.OpenTestProcedure(fileChooser.GetPath())
    
    def __BusyInfoOpenTestProcedure(self, filename):
        busyInfo = wx.BusyInfo("Opening test procedure: loading. Please " +
                               "wait...")
        return self.Load(filename)
    
    def __BusyInfoCheckForNewTests(self, testProcedure, regExId):
        busyInfo = wx.BusyInfo("Opening test procedure: checking regular " +
                               "expression. Please wait...")
        return testProcedure.CheckForNewTests(regExId)
    
    def OpenTestProcedure(self, filename):
        testProcedure = self.__BusyInfoOpenTestProcedure(filename)
        recovered = testProcedure.GetRecoveredTestIds()
        if (recovered != ""):
            FUtils.ShowWarning(self, "Encountered unfinished test " +
                    "executions. Recovering to previous finished execution " +
                    "for these tests:\n\n" + recovered)
        
        for regExId in testProcedure.GetRegExIdGenerator():
            dataSets = self.__BusyInfoCheckForNewTests(testProcedure, regExId)
            if (len(dataSets) == 0): continue
            
            displayDataSets = ""
            for dataSet in dataSets:
                displayDataSets = (displayDataSets +
                        FUtils.GetRelativePath(dataSet, MAIN_FOLDER) + "\n")
            
            if (FUtils.ShowConfirmation(self, 
                    "Found these missing data sets for " +
                    "Regular Expression " + str(regExId) + ": \n" +
                    testProcedure.GetRegExString(regExId) + "\n\n\n" + 
                    displayDataSets + "\n\n" +
                    "Do you want to add them to the test procedure? " +
                    "Selecting \"No\" will also ignore them from future " +
                    "confirmations.", False)):
                settings = testProcedure.GetRegExSettings(regExId)
                for dataSet in dataSets:
                    testProcedure.AddTest(dataSet, settings)
            else:
                ignored = testProcedure.GetIgnoredRegExList(regExId)
                if (len(ignored) == 0):
                    ignored.append("") # len(dataSet) != 0
                for dataSet in dataSets:
                    displayedFilename = FUtils.GetRelativePath(dataSet, 
                                                               MAIN_FOLDER)
                    regExPath = FUtils.NormalizeRegEx(displayedFilename)
                    newIgnored = ignored[-1]
                    if (newIgnored != ""):
                        newIgnored = newIgnored + "|" 
                    newIgnored = newIgnored + regExPath
                    if (len(newIgnored) < 30000):
                        ignored[-1] = newIgnored
                    else:
                        ignored.append(regExPath)
                testProcedure.SetRegEx(regExId, 
                        testProcedure.GetRegExList(regExId), ignored)
        
        busyInfo = wx.BusyInfo("Opening test procedure: Creating grid. " +
                               "Please wait...")
        
        child = RunTable(self.__MDIparent, wx.ID_ANY, testProcedure)
        child.Maximize(True)
        child.Show(True)
    
    def __OnExit(self, e):
        self.__MDIparent.Destroy()
        
    def __OnHelp(self, e):
        # XXX: this is windows only
        os.startfile(DOCUMENTATION)
    
    def __OnAbout(self, e):
        message = ("COLLADA Conformance Test Suite v" + str(VERSION) +"\n\n" +
                   "Copyright (C) 2006-2010 Khronos Group\n" +
                   "Available only to Khronos members.\n")
        wx.MessageDialog(self, message, "About COLLADA Conformance Test Suite", 
                         style = wx.OK).ShowModal()

class RunTable(FSFrame, wx.MDIChildFrame):
    def __init__(self, parent, id, testProcedure):
        wx.MDIChildFrame.__init__(self, parent, id, testProcedure.GetName(), 
                size = (400, 320),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        FSFrame.__init__(self, self.GetParent(), True)
        self.menu.Bind(FMenuBar.ID_SAVEAS, self.__OnSaveAs)
        self.menu.Bind(FMenuBar.ID_EXPORT_ALL_CSV, self.__OnExportAllCsv)
        self.menu.Bind(FMenuBar.ID_EXPORT_ALL, self.__OnExportAll)
        self.menu.Bind(FMenuBar.ID_EXPORT_SELECTED, self.__OnExportSelected)
        self.menu.Bind(FMenuBar.ID_CLOSE, self.__OnClose)
        self.menu.Bind(FMenuBar.ID_PACKAGE_RESULTS, self.__OnPackageResults)
        self.Bind(wx.EVT_CLOSE, self.__OnClose)
        self.menu.Bind(FMenuBar.ID_RELOAD, self.__OnReload)
        self.menu.Bind(FMenuBar.ID_PREFERENCES, self.__OnPreference)
        self.menu.Bind(FMenuBar.ID_ADD_TEST, self.__OnAddTest)
        self.menu.Bind(FMenuBar.ID_RUN_SELECTED, self.__OnRunSelected)
        self.menu.Bind(FMenuBar.ID_RUN_ALL, self.__OnRunAll)
        self.menu.Bind(FMenuBar.ID_RUN_UNRAN, self.__OnRunUnran)
        self.menu.Bind(FMenuBar.ID_SELECT_ALL, self.__OnSelectAll)
        self.menu.Bind(FMenuBar.ID_REFRESH, self.__OnRefreshTable)
        self.menu.Bind(FMenuBar.ID_REFRESH_SELECTED, self.__OnRefreshSelected)
        self.menu.Bind(FMenuBar.ID_ANIMATE, self.__OnAnimate)
        self.menu.Bind(FMenuBar.ID_REGEX, self.__OnRegEx)
        self.CreateStatusBar()
        self.__mdiId = self.GetParent().AddTestProcedure(testProcedure)
        
        self.__testProcedure = testProcedure
        
        self.__csvExporter = FCsvExporter()
        self.__htmlExporter = FHtmlExporter()
        
        self.__animateAll = False
        
        self.__grid = self.__CreateGrid()
        self.__grid.SortColumn(0, True)
        for test in self.__testProcedure.GetTestGenerator():
            id = test.GetTestId()
            self.__grid.AddExecution(id, test, test.GetCurrentExecution())
            self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def SetStatistics(self, total, passed, failed):
        self.menu.SetTotal(total)
        self.menu.SetPassed(passed)
        self.menu.SetFailed(failed)
        
    def SetBadgesEarned(self, badgesEarned):
        self.menu.SetBadgesEarned(badgesEarned)
    
    def __OnAnimate(self, e):
        e.Skip()
        newValue = not e.IsChecked()
        if (self.__animateAll != newValue):
            self.__animateAll = newValue
            self.__grid.SetAnimateAll(newValue)
    
    def __OnSelectAll(self, e):
        e.Skip()
        self.__grid.SelectAll()
    
    def __CreateGrid(self):
        grid = FExecutionGrid(self, self.__testProcedure, False, 
                self.configDict["feelingViewerGUI"], 
                self.configDict["pythonExecutable"])
        grid.AppendContext("Run Selected", self.__OnContextRun)
        grid.AppendContext(None, None)
        grid.AppendContext("Show Previous", self.__OnContextShowPrevious)
        grid.AppendContext("Compare Execution With", self.__OnCompare)
        grid.AppendContext(None, None)
        grid.AppendContext("View Settings", self.__OnViewSettings)
        grid.AppendContext("Change Settings", self.__OnChangeSettings)
        grid.AppendContext(None, None)
        grid.AppendContext("Delete Execution", self.__OnContextDeleteExecution)
        grid.AppendContext("Delete Test", self.__OnContextDeleteTest)
        grid.AppendContext(None, None)
        grid.AppendContext("View Blessed", self.__OnContextViewBlessed)
        grid.AppendExecutionContext()
        return grid
    
    def __OnRegEx(self, e):
        dialog = FRegExDialog(self, self.__testProcedure, self.applicationMap)
        dialog.ShowModal()
    
    def __OnContextViewBlessed(self, e):
        if (len(self.__grid.GetSelectedKeys()) == 0): return
        if (len(self.__grid.GetSelectedKeys()) > 1):
            FUtils.ShowWarning(self, "Select only one test to view settings.")
            return
        
        key = self.__grid.GetSelectedKeys()[0]        
        test = self.__testProcedure.GetTest(key)
        
        # FBlessedViewerDialog may unbless.
        self.__grid.PartialRefreshRemove(test)
        FBlessedViewerDialog(self, test.GetDataSetPath()).ShowModal()
        self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def __OnViewSettings(self, e):
        if (len(self.__grid.GetSelectedKeys()) == 0): return
        if (len(self.__grid.GetSelectedKeys()) > 1):
            FUtils.ShowWarning(self, "Select only one test to view settings.")
            return
        
        key = self.__grid.GetSelectedKeys()[0]
        setting = self.__testProcedure.GetTest(key).GetSettings()
        
        FSettingDialog(self, self.__testProcedure, self.applicationMap, False, 
                       setting).ShowModal()
    
    def __OnChangeSettings(self, e):
        if (len(self.__grid.GetSelectedKeys()) == 0): return
        
        settings = []
        for step, app, op, setting in self.__testProcedure.GetStepGenerator():
            settings.append(None)
            for key in self.__grid.GetSelectedKeys():
                test = self.__testProcedure.GetTest(key)
                if (settings[-1] == None):
                    settings[-1] = test.GetSettings()[step]
                else:
                    if (settings[-1] != test.GetSettings()[step]):
                        settings[-1] = None
                        break
        
        dialog = FSettingDialog(self, self.__testProcedure, 
                                self.applicationMap, True, settings)
        if (dialog.ShowModal() == wx.ID_OK):
            newSettings = dialog.GetSettings()
            
            addedTestDesc = []
            removedTestKeys = []
            for key in self.__grid.GetSelectedKeys():
                test = self.__testProcedure.GetTest(key)
                settings = test.GetSettings()
                
                changed = False
                # should be same length or else something is seriously wrong
                for i in range(len(newSettings)):
                    if (newSettings[i] != settings[i]):
                        changed = True
                        break
                
                if (changed):
                    addedTestDesc.append((key, test.GetDataSetPath(), newSettings))
                    removedTestKeys.append(key)
            if (len(addedTestDesc) > 0):
                message = ("Permanently delete the following tests and " +
                           "replace then with empty ones with the new " +
                           "settings?\n")
                if (self.__DisplayDeleteTestMessage(removedTestKeys, message)):
                    for desc in addedTestDesc:
                        test = self.__testProcedure.GetTest(desc[0])
                        self.__grid.PartialRefreshRemove(desc[0])
                        self.__testProcedure.RemoveTest(desc[0])
                        testId = self.__testProcedure.AddTest(desc[1], desc[2])
                        test = self.__testProcedure.GetTest(testId)
                        if (testId == desc[0]):
                            self.__grid.ReplaceExecution(desc[0], test, test.GetCurrentExecution())
                        else:
                            print ("<FTestSuiteGUI> inconsistency - should " +
                                   "not happen... recovering")
                            self.__grid.DeleteExecution(desc[0])
                            self.__grid.AddExecution(testId, test, test.GetCurrentExecution())
                        self.__grid.PartialRefreshAdd(test)
                    self.__grid.PartialRefreshDone()
    
    def __OnContextRun(self, e):
        self.__OnRunSelected(e)
    
    def __OnContextShowPrevious(self, e):
        keys = self.__grid.GetSelectedKeys()
        if (len(keys) != 1):
            FUtils.ShowWarning(self, "Select only 1 execution.")
            return
        
        test = self.__testProcedure.GetTest(keys[0])
        self.__grid.PartialRefreshRemove(test)
        executions = test.GetHistory()
        tuples = []
        for execution in executions:
            tuples.append((test, execution))
        
        self.__WarnIfOpened(self.__testProcedure.GetName())
        
        frame = FExecutionDialog(self, "Previous Execution", 
                self.__testProcedure, tuples, self.__animateAll, 
                self.configDict["feelingViewerGUI"],
                self.configDict["pythonExecutable"], self.__GetPreferences())
        frame.ShowModal()
        frame.Destroy()
        self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def __WarnIfOpened(self, name):
        loadedTestProcedures = self.GetParent().GetLoadedTestProcedure(name)
        
        for mdiId, testProcedure in loadedTestProcedures:
            if ((mdiId != self.__mdiId) and (testProcedure != None)):
                FUtils.ShowWarning(self, "Another window is using " +
                        "the selected test procedure. If you make " +
                        "changes in the comparison, you will need " +
                        "to reload to synchronize the displayed " +
                        "values.")
                break
    
    def __OnCompare(self, e):
        keys = self.__grid.GetSelectedKeys()
        if (len(keys) != 1): 
            FUtils.ShowWarning(self, "Select only 1 execution.")
            return
        
        test = self.__testProcedure.GetTest(keys[0])
        
        if (test.GetCurrentExecution() == None):
            FUtils.ShowWarning(self, "Test not ran.")
            return
        
        compareDialog = FCompareSetupDialog(self, 
                FImageType.EXECUTION, self.__testProcedure.GetName(),
                os.path.basename(test.GetTestDir()), 
                os.path.basename(test.GetCurrentExecutionDir()))
        
        if (compareDialog.ShowModal() == wx.ID_OK):
            path = compareDialog.GetPath()
            if (path != None):
                blessed = compareDialog.GetShowBlessed()
                dialogTestProcedure = compareDialog.GetTestProcedure()
                
                self.__WarnIfOpened(dialogTestProcedure)
                
                testFilename = os.path.join(RUNS_FOLDER, dialogTestProcedure, compareDialog.GetTest(), TEST_FILENAME)
                
                tuples = []
                if (blessed):
                    blessedExecution = test.GetBlessedExecution(self.__testProcedure)
                    if (blessedExecution != None):
                        tuples.append((test, blessedExecution))
                
                tuples.append((self.Load(testFilename), self.Load(path)))
                tuples.append((test, test.GetCurrentExecution()))
                
                self.__grid.PartialRefreshRemove(test)
                dialog = FExecutionDialog(self, "Execution Comparison",
                        self.__testProcedure, tuples, self.__animateAll, 
                        self.configDict["feelingViewerGUI"],
                        self.configDict["pythonExecutable"], 
                        self.__GetPreferences())
                dialog.ShowModal()
                self.__grid.PartialRefreshAdd(test)
                self.__grid.PartialRefreshDone()
    
    def __OnContextDeleteTest(self, e):
        keys = self.__grid.GetSelectedKeys()
        if (len(keys) == 0): return
        
        message = "Permanently delete the following tests?\n"
        if (self.__DisplayDeleteTestMessage(keys, message)):
            busyInfo = wx.BusyInfo("Deleting tests. Please wait...")
            for key in keys:
                test = self.__testProcedure.GetTest(key)
                self.__grid.PartialRefreshRemove(test)
                self.__testProcedure.RemoveTest(key)
                self.__grid.DeleteExecution(key)
                # Intentionally: there is no partial refresh add.
            
            self.__grid.PartialRefreshDone()

    def __DisplayDeleteTestMessage(self, keys, message):
        for key in keys:
            test = self.__testProcedure.GetTest(key)
            message = (message + "    " + test.GetSeparatedFilename() + "\n")
        return FUtils.ShowConfirmation(self, message, True)
    
    def __OnReload(self, e):
        path = os.path.normpath(
                os.path.join(RUNS_FOLDER, self.__testProcedure.GetName()))
        self.OpenTestProcedure(os.path.join(path, TEST_PROCEDURE_FILENAME))
        self.Close()
        self.Destroy()
    
    def __OnContextDeleteExecution(self, e):
        keys = self.__grid.GetSelectedKeys()
        if (len(keys) == 0): return
        
        message = ("Permanently delete the latest execution from the " +
                   "following tests?\n")
        for key in keys:
            test = self.__testProcedure.GetTest(key)
            message = (message + "    " + test.GetSeparatedFilename() + "\n")
        if (FUtils.ShowConfirmation(self, message, True)):
            changed = False
            for key in keys:
                test = self.__testProcedure.GetTest(key)
                if (test.HasCurrentExecution()):
                    self.__grid.PartialRefreshRemove(test)
                    test.DeleteCurrentExecution()
                    self.__grid.ReplaceExecution(key, test, test.GetCurrentExecution())
                    self.__grid.PartialRefreshAdd(test)
            self.__grid.PartialRefreshDone()
    
    def __OnRefreshTable(self, e):
        busyInfo = wx.BusyInfo("Refreshing execution table. Please wait...")
        for test in self.__testProcedure.GetTestGenerator():
            result = test.GetCurrentResult()
            test.RefreshCOLLADA()
            if (result != None) and (not result.IsOverriden()):
                test.UpdateResult(self.__testProcedure, test.GetCurrentExecution())

        # Intentionally refresh the full table.
        # This is very costly and should only be called when the user pressed the "Refresh" button.
        self.__grid.FullRefresh()
        
    def __OnRefreshSelected(self, e):
        keys = self.__grid.GetSelectedKeys()
        if (len(keys) == 0): return
        
        busyInfo = wx.BusyInfo("Refreshing selected rows. Please wait...")
        for key in keys:
            test = self.__testProcedure.GetTest(key)
            self.__grid.PartialRefreshRemove(test)
            test.RefreshCOLLADA()
            result = test.GetCurrentResult()
            if (result != None) and (not result.IsOverriden()):
                test.UpdateResult(self.__testProcedure, test.GetCurrentExecution())
            self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def __OnSaveAs(self, e):
        # contains some of the same code as in FRunConfigDialog
        if (not os.path.isdir(RUNS_FOLDER)):
            print ("<FTestSuiteGUI> No test procedures directory... " +
                   "this is weird... returning")
            return
        
        dialog = wx.TextEntryDialog(self, "Name to save test procedure.", 
                "Save Test Procedure As", "", wx.OK | wx.CANCEL | wx.CENTER)
        
        while (True):
            if (dialog.ShowModal() == wx.ID_OK):
                value = dialog.GetValue()
                if (value == ""):
                    FUtils.ShowWarning(self, "Enter a non empty name.")
                    continue
                
                if (value == self.__testProcedure.GetName()):
                    FUtils.ShowWarning(self, 
                            "Entered name is same as current name.")
                    continue
                
                if (not FUtils.IsValidFilename(value)):
                    FUtils.ShowWarning(self, "Not valid title for test " +
                            "procedure; cannot contain the following " +
                            "characters: \n" + FUtils.GetInvalidString())
                    continue
                
                if (os.path.isdir(os.path.join(RUNS_FOLDER, value))):
                    message = ("A test procedure with name \"" + value + 
                            "\" already exists. Overwrite?")
                    if (not FUtils.ShowConfirmation(self, message, False)):
                        continue
                
                break
            else:
                return
        
        busyInfo = wx.BusyInfo("Saving test procedure. Please wait...")
        
        src = os.path.normpath(
                os.path.join(RUNS_FOLDER, self.__testProcedure.GetName()))
        dest = os.path.normpath(os.path.join(RUNS_FOLDER, value))
        
        if (os.path.isdir(dest)):
            try:
                print "removing " + dest
                shutil.rmtree(dest)
            except OSError, e:
                text = (str(dest) + " is in use. Select another name for " +
                        "the run or close any application using that " +
                        "directory.")
                self.__ShowWarning(text)
                return
        
        print "copying from " + src + " to " + dest
        shutil.copytree(src, dest)
        self.OpenTestProcedure(
                os.path.abspath(os.path.join(dest, TEST_PROCEDURE_FILENAME)))
        self.Close()
        self.Destroy()

    def __OnPackageResults(self, e):
        fileChooser = wx.FileDialog(self, "Package Results to ...", 
                MAIN_FOLDER, "",  
                "ZIP file (*.zip)|*.zip", 
                wx.SAVE)
	dir = os.path.normpath(PACKAGE_RESULTS_DIR)
	basename=dir + '\\results'
	d = os.path.dirname(basename)
	if not os.path.exists(d):
		os.makedirs(d)

	rdirname = dir + '\\results_Files';
	print "removing dir: %s" % (rdirname)
	shutil.rmtree(rdirname, True)
			
	print "basename: %s" % (basename)

	self.__csvExporter.ToCsv(basename+".csv", 
	    self.__testProcedure, self.__grid.GetShowBlessed(),
	    self.__grid.GetShowPrevious(), 
	    self.__grid.GetThumbnailWidth(),
	    self.__grid.GetThumbnailHeight())
	self.__htmlExporter.ToHtml(basename+".html", 
	    self.__testProcedure, self.__grid.GetShowBlessed(),
	    self.__grid.GetShowPrevious(), 
	    self.__grid.GetThumbnailWidth(),
	    self.__grid.GetThumbnailHeight())

	makeArchive(dirEntries(dir, True) + dirEntries(os.path.normpath(SCRIPTS_DIR), True) + [os.path.normpath(CONFIGURATION_FILE)], basename + ".zip")
	    
    def __OnExportAllCsv(self, e):
        fileChooser = wx.FileDialog(self, "Export Test Procedure As ...", 
                MAIN_FOLDER, "",  
                "CSV file (*.csv)|*.csv", 
                wx.SAVE)
        dir = fileChooser.GetPath()
        if (fileChooser.ShowModal() == wx.ID_OK):
            print "writing to cvs: %s" % (fileChooser.GetPath())
            busyInfo = wx.BusyInfo("Exporting to CSV. Please wait...")
            self.__csvExporter.ToCsv(fileChooser.GetPath(), 
                    self.__testProcedure, self.__grid.GetShowBlessed(),
                    self.__grid.GetShowPrevious(), 
                    self.__grid.GetThumbnailWidth(),
                    self.__grid.GetThumbnailHeight())
    
    def __OnExportAll(self, e):
        fileChooser = wx.FileDialog(self, "Export Test Procedure As ...", 
                MAIN_FOLDER, "",  
                "HTML file (*.html)|*.html", 
                wx.SAVE)
        if (fileChooser.ShowModal() == wx.ID_OK):
            busyInfo = wx.BusyInfo("Exporting to HTML. Please wait...")
            self.__htmlExporter.ToHtml(fileChooser.GetPath(), 
                    self.__testProcedure, self.__grid.GetShowBlessed(),
                    self.__grid.GetShowPrevious(), 
                    self.__grid.GetThumbnailWidth(),
                    self.__grid.GetThumbnailHeight())
    
    def __OnExportSelected(self, e):
        fileChooser = wx.FileDialog(self, "Export Test Procedure As ...", 
                MAIN_FOLDER, "",  
                "HTML file (*.html)|*.html", 
                wx.SAVE)
        if (fileChooser.ShowModal() == wx.ID_OK):
            busyInfo = wx.BusyInfo("Exporting to HTML. Please wait...")
            self.__htmlExporter.ToHtml(fileChooser.GetPath(),
                    self.__testProcedure, self.__grid.GetShowBlessed(), 
                    self.__grid.GetShowPrevious(),                     
                    self.__grid.GetThumbnailWidth(),
                    self.__grid.GetThumbnailHeight(), 
                    self.__grid.GetSelectedKeys())
    
    def __OnPreference(self, e):
        (oldWidth, oldHeight, oldBlessed, oldPrevious, oldDiff, 
                oldColumns) = self.__GetPreferences()
        dialog = FPreferenceDialog(self, self.__grid.GetAllColumns(), 
                oldColumns, oldBlessed, oldPrevious, oldWidth, oldHeight, 
                oldDiff) 
        
        if (dialog.ShowModal() == wx.ID_OK): 
            busyInfo = wx.BusyInfo("Updating grid with new preferences. " +
                                   "Please wait...")
            newWidth, newHeight = dialog.GetThumbnailSize()
            self.__grid.SetPreferences(newWidth, newHeight, 
                    dialog.GetShowBlessed(), dialog.GetShowPrevious(), 
                    dialog.GetDiffPath(), dialog.GetColumns())
        
        dialog.Destroy()
    
    def __GetPreferences(self):
        return (self.__grid.GetThumbnailWidth(), 
                self.__grid.GetThumbnailHeight(),
                self.__grid.GetShowBlessed(), self.__grid.GetShowPrevious(),
                self.__grid.GetDiff(), self.__grid.GetShownColumns())
    
    def __OnClose(self, e):
        self.GetParent().RemoveTestProcedure(self.__mdiId)
        self.Destroy()
    
    def __BusyInfoAddTest(self):
        busyInfo = wx.BusyInfo("Searching Data Sets. Please wait...")
        wizard = wx.wizard.Wizard(self, -1, "Add Tests")
        page1 = FAppSettingsDialog(wizard, self.__testProcedure, 
                                   self.applicationMap)
        page2 = FSelectDataSetDialog(wizard, self.__testProcedure, page1)
        
        wizard.FitToPage(page1)
        wizard.FitToPage(page2)
        
        wx.wizard.WizardPageSimple_Chain(page1, page2)
        return (page1, page2, wizard)
    
    def __OnAddTest(self, e):
        page1, page2, wizard = self.__BusyInfoAddTest()
        
        if wizard.RunWizard(page1):
            self.__CollectData(page1, page2)
    
    def __CollectData(self, optionsPage, dataSetPage):
        busyInfo = wx.BusyInfo("Adding tests. Please wait...")
        for testName in dataSetPage.GetChecked():
            test = self.__AddTest(testName, optionsPage.GetSettings())
            self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def __AddTest(self, dataSetName, settings):
        testId = self.__testProcedure.AddTest(dataSetName, settings)
        test = self.__testProcedure.GetTest(testId)
        self.__grid.AddExecution(testId, test, test.GetCurrentExecution())
        return test

    def __OnRunSelected(self, e):
        if (len(self.__grid.GetSelectedKeys()) == 0): return
        
        self.__Run(self.__grid.GetSelectedKeys())
    
    def __OnRunAll(self, e):
        testsToRun = []
        for test in self.__testProcedure.GetTestGenerator():
            testsToRun.append(test.GetTestId())
        if (len(testsToRun) == 0): return
        
        self.__Run(testsToRun)
    
    def __OnRunUnran(self, e):
        testsToRun = []
        for test in self.__testProcedure.GetTestGenerator():
            if (not test.HasCurrentExecution()):
                testsToRun.append(test.GetTestId())
        if (len(testsToRun) == 0): return
        
        self.__Run(testsToRun)
    
    def __Run(self, keys):
        dialog = FProgressDialog(self, 1, "Running Tests. Please wait.")
        dialog.SetCancelFunc(self.__OnCancelRun)
        myThread = Runner(dialog, self.__testProcedure.RunTests, keys, 
                self.applicationMap, self.__StandardCallback(dialog), self.__MarkerCallback(dialog))
        myThread.start()
        dialog.ShowModal()
        myThread.join()
        
        dialog.Destroy()
        busyInfo = wx.BusyInfo("Updating after running. Please wait...")
        
        for testId in keys:
            test = self.__testProcedure.GetTest(testId)
            self.__grid.PartialRefreshRemove(test)
            self.__grid.ReplaceExecution(testId, test, test.GetCurrentExecution())
            self.__grid.PartialRefreshAdd(test)
        self.__grid.PartialRefreshDone()
    
    def __StandardCallback(self, dialog):
        def __callBack(current, max, message):
            if (max != None):
                dialog.SetGaugeMax(max)
            if (current != None):
                wx.PostEvent(dialog,
                         FProgressGaugeEvent(dialog.GetId(), current))
            wx.PostEvent(dialog, 
                         FProgressMessageEvent(dialog.GetId(), message))
        
        return __callBack
        
    def __MarkerCallback(self, dialog):
        def __callBack(doClear, filename):
            if doClear:
                wx.PostEvent(dialog, FProgressMarkerClearEvent(dialog.GetId()))
            else:
                wx.PostEvent(dialog, FProgressMarkerAddEvent(dialog.GetId(), filename))
                
        return __callBack

    def __OnCancelRun(self, dialog):
        self.__testProcedure.CancelRun(self.__StandardCallback(dialog))

class Runner(threading.Thread):
    def __init__(self, dialog, func, *args):
        threading.Thread.__init__(self)
        self.__func = func
        self.__args = args
        self.__dialog = dialog
        self.__dialogId = dialog.GetId()
        self.__cancelled = False
    
    def run(self):
        self.__func(*self.__args)
        wx.PostEvent(self.__dialog, FProgressDoneEvent(self.__dialogId))

class MainFrame(FSFrame, wx.MDIParentFrame):
    def __init__(self, parent, id, title):
        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        FSFrame.__init__(self, self, False)
        self.__testProcedures = {}
        self.__currentId = -1
    
    def GetLoadedTestProcedure(self, name):
        results = []
        for id in self.__testProcedures.keys():
            if (self.__testProcedures[id].GetName() == name):
                results.append((id, self.__testProcedures[id]))
        return results
    
    def AddTestProcedure(self, testProcedure):
        self.__currentId = self.__currentId + 1
        self.__testProcedures[self.__currentId] = testProcedure
        return self.__currentId
    
    def RemoveTestProcedure(self, id):
        self.__testProcedures.pop(id)
    
