# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
        
        # Read in and parse the configuration file.
        configDict = {}
        if (os.path.isfile(CONFIGURATION_FILE)):
            with open(CONFIGURATION_FILE) as f:
                for line_num, line in enumerate(f):
                    tokens = line.strip().split("\t")
                    tokens = [t.strip() for t in tokens if len(t.strip()) > 0]
                    if len(tokens) != 2:
                        print 'Warning: ignoring configuration line %d: "%s"' % (line_num, line.strip())
                        continue
                    if tokens[0] in configDict:
                        print 'Warning: ignoring redefinition of configuration key "%s" on line %d' % (tokens[0], line_num)
                        continue
                    configDict[tokens[0]] = tokens[1]
            
        # Further parse the badge levels configuration.
        FGlobals.badgeLevels = []
        if configDict.has_key("badgeLevels"):
            wantedBadgeList = configDict["badgeLevels"].split(",")
            for badge in wantedBadgeList:
                # Strip extra whitespaces and enforce title-case.
                level = badge.strip().title()
                if (len(level) > 0):
                    FGlobals.badgeLevels.append(level)

        # Further parse the adopter package status
        FGlobals.adoptersPackage = False
        if configDict.has_key("adoptersPackage"):
            FGlobals.adoptersPackage = configDict["adoptersPackage"]
        
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
        comparatorFile = os.path.abspath(os.path.normpath(
                os.path.join(IMAGE_COMPARATORS_DIR, 
                        configDict[IMAGE_COMPARATORS_LABEL] + ".py")))
        if (os.path.isfile(comparatorFile)):
            comparatorName = configDict[IMAGE_COMPARATORS_LABEL]
        else:
            print comparatorFile + " not found. Defaulting to byte comparator."
            comparatorName = "FByteComparator" # default comparator
        
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
    