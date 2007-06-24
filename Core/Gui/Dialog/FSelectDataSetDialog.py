# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import wx
import wx.wizard
import os.path
import re
import copy

import Core.Common.FUtils as FUtils
import Core.Common.FCOLLADAParser as FCOLLADAParser
from Core.Common.FConstants import *
from Core.Logic.FDataSetParser import *

class FSelectDataSetDialog(wx.wizard.WizardPageSimple, FDataSetParser):
    """The dialog to select the data set for new tests. 
    
    private members:
        self.__iconChecked -- index for the checked image in the ImageList for
        TreeCtrl.
        self.__iconUnchecked -- index for the unchecked image in the ImageList 
        for TreeCtrl.
        self.__treeCtrl -- the TreeCtrl to display the directory structure.
        
    """
    
    __CHECKED = True
    __UNCHECKED = False
    __FILE = True
    __FOLDER = False
    
    __TREE = 0
    __REGEX = 1
    
    def __init__(self, parent, testProcedure, settingsPage):
        """Creates this dialog.
        
        arguments:
            parent -- the parent frame for this dialog.
        
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)
        FDataSetParser.__init__(self)
        
        self.__allPaths = []
        self.__settingsPage = settingsPage
        self.__testProcedure = testProcedure
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topSizer)
        
        title = wx.StaticText(self, wx.ID_ANY, "Select Data Set")
        
        self.__treeRadio = wx.RadioButton(self, style = wx.RB_GROUP)
        self.__treeRadio.Bind(wx.EVT_RADIOBUTTON, self.__OnTreeButtonClicked)
        self.__commentsCtrl = None
        self.__iconUnchecked = None
        self.__iconChecked = None
        self.__treeCtrl = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, 
                wx.Size(300, 250), wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT)
        self.__treeCtrl.AssignImageList(self.__LoadImages())
        self.__PopulateTree(self.__treeCtrl)
        self.__treeCtrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)
        self.__treeCtrl.Bind(wx.EVT_LEFT_DCLICK, self.__OnLeftDouble)
        
        self.__regButton = wx.RadioButton(self)
        self.__regButton.Bind(wx.EVT_RADIOBUTTON, self.__OnRegExButtonClicked)
        self.__regExpLabel = wx.StaticText(self, -1, "Regular Expression")
        self.__regExpCtrl = wx.TextCtrl(self, -1)
        self.__regExpUpdateButton = wx.Button(self, wx.ID_ANY, "&Update")
        self.__regExpUpdateButton.Bind(wx.EVT_BUTTON, self.__OnUpdate)
        self.__regExpExample1 = wx.StaticText(self, wx.ID_ANY, 
                "eg. For everything with \"animation\" in " +
                "StandardDataSets/Collada section:")
        self.__regExpExample1.SetOwnForegroundColour(wx.BLUE)
        self.__regExpExample2 = wx.StaticText(self, wx.ID_ANY,
                "StandardDataSets\\\\Collada\\\\[\\S]*animation[\\S]*")
        self.__regExpExample2.SetOwnForegroundColour(wx.BLUE)
        
        treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeSizer.Add(self.__treeRadio, 0, wx.ALL, 5)
        treeSizer.Add(self.__treeCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        bottomOuterSizer = wx.BoxSizer(wx.VERTICAL)
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(self.__regButton, 0, wx.ALL, 5)
        bottomSizer.Add(self.__regExpLabel, 1, wx.EXPAND | wx.ALL, 5)
        bottomSizer.Add(self.__regExpCtrl, 2, 
                wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 5)
        bottomSizer.Add(self.__regExpUpdateButton, 0, wx.ALL, 5)
        bottomOuterSizer.Add(bottomSizer)
        bottomOuterSizer.Add(self.__regExpExample1, 0, 
                wx.ALIGN_CENTER | wx.TOP, 2)
        bottomOuterSizer.Add(self.__regExpExample2, 0,
                wx.ALIGN_CENTER | wx.TOP, 2)
        
        topSizer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        topSizer.Add(treeSizer, 1, wx.EXPAND)
        topSizer.Add(self.__GetCommentsSizer(), 0, 
                wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        topSizer.Add(bottomOuterSizer, 0, wx.ALIGN_CENTER)
        
        self.__treeRadio.SetValue(True)
        self.__mode = FSelectDataSetDialog.__TREE
        self.__OnTreeButtonClicked(None)
        
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.__OnFinish)
    
    def __OnFinish(self, e):
        settings = self.__settingsPage.GetSettings()
        regExId = self.__testProcedure.GetRegExId(settings)
        
        if (regExId == -1):
            concatRegEx = []
        else:
            concatRegEx = copy.deepcopy(
                    self.__testProcedure.GetRegExList(regExId))
            if (concatRegEx[-1] != ""):
                concatRegEx[-1] = concatRegEx[-1] + "|"
        
        try:
            paths, regEx = self.__GetDataSets(concatRegEx)
        except re.error, ex:
            FUtils.ShowWarning(self, "Bad regular expression.")
            e.Veto()
            return
        
        if (regEx == []): return
        if (regExId == -1):
            self.__testProcedure.AddRegEx(settings, regEx)
        else:
            if (FUtils.ShowConfirmation(self, "The following regular " +
                    "expression is already assigned to the selected " +
                    "settings:\n\n" +
                    self.__testProcedure.GetRegExString(regExId) + "\n\n" +
                    "Do you want to overwrite? No will append the new " +
                    "regular expression with the one above.", False)):
                self.__testProcedure.SetRegEx(regExId, regEx, 
                        self.__testProcedure.GetIgnoredRegExList(regExId))
            else:
                self.__testProcedure.SetRegEx(regExId, concatRegEx,
                        self.__testProcedure.GetIgnoredRegExList(regExId))
    
    def GetChecked(self):
        paths, regEx = self.__GetDataSets()
        return paths
    
    # concatRegEx is a list of strings. The last element should be empty or 
    # ends with "|" (ready for appending)
    def __GetDataSets(self, concatRegEx = []):
        if (self.__mode == FSelectDataSetDialog.__TREE):
            paths = []
            rootItem =  self.__treeCtrl.GetRootItem()
            if (rootItem.IsOk()):
                for childItem, childDataSetDir in self.__visibleRoot:
                    dir = os.path.dirname(os.path.abspath(childDataSetDir))
                    dir = FUtils.GetRelativePath(dir, os.getcwd())
                    self.__GetCheckedRecursive(paths, childItem, dir, False)
            
            regEx = []
            if (len(paths) != 0):
                regEx.append("")
                if (concatRegEx == []):
                    concatRegEx.append("")
                curIndex = 0
                concatCurIndex = len(concatRegEx) - 1
                for path in paths:
                    relPath = FUtils.NormalizeRegEx(
                            FUtils.GetRelativePath(path, MAIN_FOLDER))
                    newRegEx = regEx[curIndex] + relPath + "|"
                    concatNewRegEx = (concatRegEx[concatCurIndex] + relPath + 
                                      "|")
                    
                    if (len(newRegEx) < 30000):
                        regEx[curIndex] = newRegEx
                    else:
                        regEx[curIndex] = regEx[curIndex][:-1]
                        regEx.append(relPath + "|")
                        curIndex = curIndex + 1
                    if (len(concatNewRegEx) < 30000):
                        concatRegEx[concatCurIndex] = concatNewRegEx
                    else:
                        concatRegEx[concatCurIndex] = concatRegEx[concatCurIndex][:-1]
                        concatRegEx.append(relPath + "|")
                        concatCurIndex = concatCurIndex + 1
                regEx[curIndex] = regEx[curIndex][:-1]
                concatRegEx[concatCurIndex] = concatRegEx[concatCurIndex][:-1]
        else:
            regEx = self.__GetRegEx()
            paths, items = self.__GetPathsAndItems(regEx)
            if (regEx == ""):
                regEx = []
            else:
                if (len(concatRegEx) == 0):
                    concatRegEx.append("")
                    
                concatNewRegEx = concatRegEx[-1] + regEx
                if (len(concatNewRegEx) < 30000):
                    concatRegEx[-1] = concatNewRegEx
                else:
                    # the text control only allows up to 30k characters
                    concatRegEx.append(regEx)
                regEx = [regEx]
        
        return (paths, regEx)
    
    def __GetRegEx(self):
        return self.__regExpCtrl.GetValue()
    
    def __GetPathsAndItems(self, regEx):
        dir = FUtils.NormalizeRegEx(os.path.normpath(MAIN_FOLDER))
        pattern = re.compile(dir + "[/\\\\]" + regEx + "$")
        
        paths = []
        items = []
        for path, item in self.__allPaths:
            match = pattern.match(path)
            if (match != None):
                if (match.group() == path):
                    paths.append(os.path.dirname(path))
                    items.append(item)
        return (paths, items)
    
    def __LoadImages(self):
        """Loads the images used for this dialog.
        
        It assigns values to self.__iconChecked and self.__iconUnchecked.
        
        returns
            an ImageList containing the images.
            
        """
        imageList = wx.ImageList(16, 16)
        
        icon = wx.Bitmap(os.path.join(IMAGES_DIR, "checkbox.bmp"), 
                         wx.BITMAP_TYPE_BMP)
        icon.SetMaskColour(wx.Color(255, 255, 255))
        self.__iconUnchecked = imageList.Add(icon)
        
        icon = wx.Bitmap(os.path.join(IMAGES_DIR, "checkboxFilled.bmp"), 
                         wx.BITMAP_TYPE_BMP)
        icon.SetMaskColour(wx.Color(255, 255, 255))
        self.__iconChecked = imageList.Add(icon)
        
        return imageList
    
    def __PopulateTree(self, tree):
        """Adds entries (with given icon) to the tree.
        
        Searches from the current directory down from the directories in 
        DATA_SET_DIRS. It then adds this directory as the root of the tree 
        along with the icon given to its left. Finally, it calls 
        __PopulateTreeRecurse to fill in the tree with the files 
        and directories in the root directory.
        
        arguments:
            tree -- The TreeCtrl to fill in.
            icon -- The index of the ImageList (associated with this tree) of
            the image to put next to each entry.
        """
        foundDataSetDir = False
        for dataSetDir in DATA_SET_DIRS:
            if (os.path.isdir(dataSetDir)):
                foundDataSetDir = True
                break
        
        if (not foundDataSetDir): return
        
        self.__visibleRoot = []
        treeRoot = tree.AddRoot("") # will not be shown
        for dataSetDir in DATA_SET_DIRS:
            if (not os.path.isdir(dataSetDir)): continue
            
            child = self.__PopulateTreeRecurse(tree, treeRoot, dataSetDir, 
                                               True)
            self.__visibleRoot.append((child, dataSetDir))
            self.__treeCtrl.Expand(child)
        
        self.__treeCtrl.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.__OnCollapse)
    
    def __PopulateTreeRecurse(self, tree, child, path, fullPath):
        """Recursively adds entries to the tree.
        
        It assumes that the tree has a root already. It will add folders
        and files to the tree from path to the child along with the icon next
        to the text. Data sets are defined once there is a file inside a folder
        with the same proper name as the file. The tree marks data sets by
        enclosing them in square brackets.
        
        arguments:
            tree -- The TreeCtrl (or subtree) to fill in.
            child -- The index of the item in the tree to add more items to.
            path -- The path of where to get the items.
        
        """
        file, dirs = self.GetValidFileAndDirs(path)
        
        if (file != None):
            newChild = tree.AppendItem(child, "[" + os.path.basename(file) + 
                                       "]")
            self.__allPaths.append((os.path.normpath(file), newChild))
            tree.SetPyData(newChild, [FSelectDataSetDialog.__FILE, 
                                      FSelectDataSetDialog.__UNCHECKED])
            tree.SetItemImage(newChild, self.__iconUnchecked, 
                              wx.TreeItemIcon_Normal)
            return newChild
        
        if (fullPath):
            newChild = tree.AppendItem(child, 
                    FUtils.GetRelativePath(path, MAIN_FOLDER))
        else:
            newChild = tree.AppendItem(child, os.path.basename(path))
        tree.SetPyData(newChild, [FSelectDataSetDialog.__FOLDER, 
                                  FSelectDataSetDialog.__UNCHECKED])
        tree.SetItemImage(newChild, self.__iconUnchecked, 
                          wx.TreeItemIcon_Normal)
        
        for dir in dirs:
            self.__PopulateTreeRecurse(tree, newChild, dir, False)
        
        return newChild
    
    def __GetCommentsSizer(self):
        """Returns the Sizer used for comments."""
        staticBox = wx.StaticBox(self, wx.ID_ANY, "Description")
        sizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)
        
        self.__commentsCtrl = wx.TextCtrl(self, wx.ID_ANY, "", 
                style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.__commentsCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        sizer.Add(self.__commentsCtrl, 1, wx.EXPAND | wx.ALL, 5)
        
        return sizer
    
    def __UnCheckTree(self):
        rootItem =  self.__treeCtrl.GetRootItem()
        if (rootItem.IsOk()):
            child, cookie = self.__treeCtrl.GetFirstChild(rootItem)
            while (child.IsOk()):
                self.__Check(self.__treeCtrl, child)
                directory, checked = self.__treeCtrl.GetItemPyData(child)
                if (checked == FSelectDataSetDialog.__CHECKED):
                    self.__Check(self.__treeCtrl, child)
                child = self.__treeCtrl.GetNextSibling(child)
    
    def __OnUpdate(self, e):
        try:
            self.__UnCheckTree()
            paths, items = self.__GetPathsAndItems(self.__GetRegEx())
            for item in items:
                self.__Check(self.__treeCtrl, item)
        except re.error, e:
            FUtils.ShowWarning(self, "Bad regular expression.")
    
    def __OnTreeButtonClicked(self, e):
        self.__treeCtrl.SetBackgroundColour(wx.WHITE)
        self.__regExpLabel.Enable(False)
        self.__regExpCtrl.Enable(False)
        self.__regExpExample1.Enable(False)
        self.__regExpExample2.Enable(False)
        self.__regExpUpdateButton.Enable(False)
        self.__mode = FSelectDataSetDialog.__TREE
    
    def __OnRegExButtonClicked(self, e):
        self.__treeCtrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        self.__regExpLabel.Enable(True)
        self.__regExpCtrl.Enable(True)
        self.__regExpExample1.Enable(True)
        self.__regExpExample2.Enable(True)
        self.__regExpUpdateButton.Enable(True)
        self.__mode = FSelectDataSetDialog.__REGEX
    
    def __OnCollapse(self, e):
        item = e.GetItem()
        for visibleItem, visibleDataSetDir in self.__visibleRoot:
            if (item == visibleItem):
                e.Veto()
    
    def __OnLeftDown(self, e):
        """Test to see if clicked on a checkbox.
        
        arguments:
            e -- The Event that was generated from the mouse click.
        
        """
        item, where = e.GetEventObject().HitTest(e.GetPosition())
        
        if (where == wx.TREE_HITTEST_ONITEMICON):
            if (self.__mode == FSelectDataSetDialog.__TREE):
                self.__Check(e.GetEventObject(), item)
        elif (where == wx.TREE_HITTEST_ONITEMLABEL):
            directory, checked = self.__treeCtrl.GetItemPyData(item)
            if (directory != FSelectDataSetDialog.__FILE): return
            
            path = self.__treeCtrl.GetItemText(item)[1:-1]
            dataSetDirectory = FUtils.GetProperFilename(path)
            path = os.path.join(dataSetDirectory, path)
            parent = self.__treeCtrl.GetItemParent(item)
            while (parent != self.__treeCtrl.GetRootItem()):
                path = os.path.join(self.__treeCtrl.GetItemText(parent), path)
                parent = self.__treeCtrl.GetItemParent(parent)
            path = os.path.join(MAIN_FOLDER, path)
            
            comments = ""
            
            if (os.path.isfile(path) and FCOLLADAParser.IsCOLLADADocument(path)):
                (title, subject, keyword) = FCOLLADAParser.GetCOLLADAAssetInformation(path)
                comments = "[%s] Keywords: %s\nDescription: %s" % (title, keyword, subject)
            
            self.__commentsCtrl.SetValue(comments)
        
        e.Skip()
    
    def __OnLeftDouble(self, e):
        """ Do nothing, i.e. don't expand the entry from double clicking.
        
        This is to remove the annoyance that clicking checkboxes fast will 
        expand and collapse the tree.
        
        arguments:
            e -- The Event that was generated from the mouse double-click.
        
        """
        pass
    
    def __Check(self, tree, item):
        """Toggles the checkbox of the item and its children.
        
        arguments:
            tree -- The TreeCtrl that the item is in.
            item -- The index of the item that was clicked on in the tree.
        
        """
        if (tree.GetPyData(item)[1] == FSelectDataSetDialog.__CHECKED):
            item = self.__GetHighestItem(item, FSelectDataSetDialog.__CHECKED)
            self.__SetImage(item, tree, self.__iconUnchecked, 
                            FSelectDataSetDialog.__UNCHECKED)
        else:
            item = self.__GetHighestItem(item, 
                                         FSelectDataSetDialog.__UNCHECKED)
            self.__SetImage(item, tree, self.__iconChecked, 
                            FSelectDataSetDialog.__CHECKED)
    
    def __GetHighestItem(self, item, state):
        rootItem = self.__treeCtrl.GetRootItem()
        parentItem = self.__treeCtrl.GetItemParent(item)
        
        while (parentItem != rootItem):
            child, cookie = self.__treeCtrl.GetFirstChild(parentItem)
            while (child.IsOk()):
                if (child != item):
                    directory, checked = self.__treeCtrl.GetItemPyData(child)
                    if (checked == state):
                        return item
                child = self.__treeCtrl.GetNextSibling(child)
            item = parentItem
            parentItem = self.__treeCtrl.GetItemParent(item)
        return item
    
    def __SetImage(self, item, tree, icon, data):
        """Check item in tree and calls __SetImageRecursive on its children.
        
        It checks an item by changing the image next to the entry to icon and 
        PyData to data.
        
        arguments:
            item -- The index of the item in the tree to update.
            tree -- The TreeCtrl to update.
            icon -- The index of the ImageList (associated with this tree) of
            the image to put next to each entry.
            data -- The data to set the PyData to for this item.
        
        """
        tree.SetItemImage(item, icon, wx.TreeItemIcon_Normal)
        tree.GetPyData(item)[1] = data
        
        if tree.ItemHasChildren(item):
            child, cookie = tree.GetFirstChild(item)
            self.__SetImageRecursive(child, tree, icon, data, True)
    
    def __SetImageRecursive(self, item, tree, icon, data, firstChild):
        """Check item in tree and its children and siblings.
        
        It checks an item by changing the image next to the entry to icon and 
        PyData to data. It calls __SetImage on the item and __SetImageRecursive
        on its siblings.
        
        arguments:
            item -- The index of the item in the tree to update.
            tree -- The TreeCtrl to update.
            icon -- The index of the ImageList (associated with this tree) of
            the image to put next to each entry.
            data -- The data to set the PyData to for this item.
            firstChild -- True if setting image on the first child.
        
        """
        self.__SetImage(item, tree, icon, data)
        
        if (firstChild):
            sibling = tree.GetNextSibling(item)
            while (sibling):
                self.__SetImageRecursive(sibling, tree, icon, data, False)
                sibling = tree.GetNextSibling(sibling)

    def __GetCheckedRecursive(self, paths, item, dir, firstChild):
        """Appends to list the paths of checked files in tree from item down.
        
        arguments:
            paths -- The list to put the check paths in.
            item -- The index of the item in tree to determine if goes in list.
            dir -- The current directory of search.
            firstChild -- True if setting image on the first child.
        
        """
        directory, checked = self.__treeCtrl.GetItemPyData(item)
        if ((directory == FSelectDataSetDialog.__FILE) and 
                (checked == FSelectDataSetDialog.__CHECKED)):
            # remove the [ ] enclosing brackets and extension
            filename = self.__treeCtrl.GetItemText(item)[1:-1]
            filename = FUtils.GetProperFilename(filename)
            paths.append(FUtils.GetCollapsePath(os.path.join(dir, filename)))
        
        if (self.__treeCtrl.ItemHasChildren(item)):
            child, cookie = self.__treeCtrl.GetFirstChild(item)
            self.__GetCheckedRecursive(paths, child, 
                    os.path.join(dir, self.__treeCtrl.GetItemText(item)), True)
        
        if (firstChild):
            sibling = self.__treeCtrl.GetNextSibling(item)
            while (sibling):
                self.__GetCheckedRecursive(paths, sibling, dir, False)
                sibling = self.__treeCtrl.GetNextSibling(sibling)
    
# Used to start up this dialog without the entire application.
##class MainFrame(wx.MDIParentFrame):
##    def __init__(self, parent, id, title):
##        wx.MDIParentFrame.__init__(self, parent, id, title, size = (600, 480),
##                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
##                
##        wiz = wx.wizard.Wizard(self, -1, "Add a Test")
##        page1 = FSelectDataSetDialog(wiz)
##        self.page1 = page1
##        wiz.FitToPage(page1)
##        wiz.RunWizard(page1)
##        
##       # print page1.GetChecked()
##        
##        print page1.GetDataSets()
##    
##app = wx.PySimpleApp()
##frame = MainFrame(None,-1, "Test")
##app.MainLoop()
