# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os
import os.path

import Core.Common.FUtils as FUtils
import Core.Common.FGlobals as FGlobals
from Core.Common.FConstants import *
from Core.Common.FSerializer import *
from Core.Logic.FTestProcedure import *

class FTestSuite(FSerializer):
    def __init__(self):
        FSerializer.__init__(self)
        
        configDict = {}
        if (os.path.isfile(CONFIGURATION_FILE)):
            f = open(CONFIGURATION_FILE)
            line = f.readline()
            while (line):
                while (line.count("\t\t") > 0):
                    line = line.replace("\t\t", "\t")
                key, value = line.split("\t",1)
                if (configDict.has_key(key)):
                    print ("Warning: Ignoring redefinition of configuration " +
                           "key: " + key + ".")
                    continue
                configDict[key] = value[:-1] # remove \n
                line = f.readline()
            f.close
        
        # import the application specific scripts
        self.applicationMap = {}
        if (os.path.isdir(SCRIPTS_DIR)):
            for entry in os.listdir(SCRIPTS_DIR):
                filename = os.path.normpath(os.path.join(SCRIPTS_DIR, entry))
                if ((not os.path.isfile(filename)) or
                        (FUtils.GetExtension(filename) != "py") or
                        (entry == "__init__.py") or
                        (entry == ABSTRACT_APPLICATION)): continue
                
                properName = FUtils.GetProperFilename(entry)
                exec("from Scripts." + properName + " import *")
                exec("application = " + properName + "(configDict)")
                prettyName = application.GetPrettyName()
                
                if (self.applicationMap.has_key(prettyName)):
                    print ("Warning: Ignoring redefinition of application \"" +
                            prettyName + "\" from \"" + entry + "\"")
                    continue
                
                self.applicationMap[prettyName] = application
        
        # import the image comparator
        comparatorName = configDict[IMAGE_COMPARATORS_LABEL]
        exec("from ImageComparators." + comparatorName + " import *")
        exec("FGlobals.imageComparator = " + comparatorName + "(configDict)")
        
        self.configDict = configDict
    
    def SaveProcedure(self, procedureName, procedureTree, comments = ""):
        testProcedureDir = os.path.abspath(
                os.path.normpath(os.path.join(RUNS_FOLDER, procedureName)))
        try:
            os.mkdir(testProcedureDir)
        except OSError, e:
            print "<FTestSuite> could not make the test procedure directory"
            print e
            return None
        testProcedure = FTestProcedure(procedureTree)
        self.Save(testProcedure, 
                  os.path.join(testProcedureDir, TEST_PROCEDURE_FILENAME))
        testProcedure.SetProcedureDirectory(testProcedureDir)
        f = open(os.path.join(testProcedureDir, TEST_PROCEDURE_COMMENTS), "w")
        f.write(comments)
        f.close()
        return testProcedure
    