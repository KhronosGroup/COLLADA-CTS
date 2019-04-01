# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os.path

CURDIR = os.path.dirname(os.path.abspath(__file__))
CTS_ROOT = os.path.normpath(os.path.join(CURDIR, '..', '..'))

IMPORT = "Import"
EXPORT = "Export"
RENDER = "Render"
VALIDATE = "Validate"
OPERATIONS = [IMPORT, EXPORT, RENDER, VALIDATE]
OPS_NEEDING_APP = [IMPORT, VALIDATE]
SCHEMA_LOCATION = "COLLADASchema.xsd"
SCHEMA_NAMESPACE = "http://www.collada.org/2005/11/COLLADASchema"
ABSTRACT_APPLICATION = "FApplication.py"
SCRIPTS_DIR = "../Scripts"
IMAGE_COMPARATORS_DIR = "../ImageComparators" # directory where image comparators are stored
IMAGE_COMPARATORS_LABEL = "imageComparator" # tag in the config file for selected comparator
ROOT_DIR = "../StandardDataSets" # backward compatibility
DATA_SET_DIRS = ["../StandardDataSets",] # rel. path
SETTINGS_DIR = "../ApplicationSettings"
SETTING_EXT = "txt"
LOG_EXT = "log"
RUNS_FOLDER = "../TestProcedures"
MAIN_FOLDER = ".."
CSV_POSTFIX = "_Files"
HTML_POSTFIX = "_Files"
IMAGES_DIR = "images"
BLESSED_DIR = "Blessed"
BLESSED_EXECUTIONS = "executions"
BLESSED_ANIMATIONS = "animations"
BLESSED_EXECUTIONS_HASH = "executionsManager"
BLESSED_DEFAULT_FILE = "default.txt"
TEST_PROCEDURE_FILENAME = "serializedTestProcedure.obj"
TEST_PROCEDURE_COMMENTS = "comments.txt"
TEST_GUI_PREFERENCES = "prefs.obj"
ASSET_FILENAME = "../temp.txt"
TEST_FILENAME = "serializedTest.obj"
EXECUTION_FILENAME = "serializedExecution.obj"
EXECUTION_PREFIX = "Execution_"
STEP_PREFIX = "step"
TEST_PREFIX = "Test"
DCC_WORK1 = "WorkingDir"
DCC_WORK2 = "Execution"
DCC_WORK3 = "Step"
PASS = 1
FAIL = 0
CONFIGURATION_FILE = "../config.txt"
DOCUMENTATION = os.path.join(CTS_ROOT, "Documentation", "README.doc")
FILEWATCHER = "FileWatcher.exe"
KILLER = "ProcessKiller.exe"
VERSION = 1.0
PACKAGE_RESULTS_DIR = "../PackagedResults"
