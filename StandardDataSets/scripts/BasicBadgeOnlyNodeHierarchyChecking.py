
# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
# [WARNING] this structure is subject to changes.
#

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeExemplary: also verifies that the validation steps are not in error.
# JudgeSuperior: same as intermediate badge.

# this will check the node hiearchy as well
import os
import subprocess

class SimpleJudgingObject:
    def __init__(self):
        pass
    
    def CheckEnvirmoment(self):
        if (os.environ.has_key('COLLADA_CTF_EXTERNAL_TOOL')):
            print "There is checker defined as below:"
            print os.environ['COLLADA_CTF_EXTERNAL_TOOL']
            return True
        else:
            print "Missing envirmental variable: COLLADA_CTF_EXTERNAL_TOOL"  
            return False 
    
    def CheckHierarchy(self, context):
        absInputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())
        #print absInputFileName
        outFileNames = context.GetStepOutputFilenames("Export")
        if len(outFileNames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False 
        #print outFileNames[0]
        
        if self.CheckEnvirmoment():
            # We have the tool installed correctly.
            command = os.environ['COLLADA_CTF_EXTERNAL_TOOL'] + "\HierarchyPreservationChecking.exe " + absInputFileName + " " + outFileNames[0]
            #print command
            p = subprocess.Popen(command)
            result = p.wait()
            #print result
            if (result == 1):
               return True
            elif (result == 0):
               context.Log("FAILED: two tree for node are not same based on schema. Error may come from child parent relation changed or id attribute problem.")
               return False
            else:
               context.Log("FAILED: Hierarchy program can not load DOM correctly.")
               return False
        else:
            context.Log("FAILED: There is no tool for hierarchy checking")
            return False
        
    def JudgeBaseline(self, context):
        
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...                  
        if not self.CheckHierarchy(context):
            context.Log("Error in node hierarchy checking...")
            return False
        
        if (context.HasStepCrashed()):
            context.Log("FAILED: Crashes during required steps.")
            return False
        else:
            context.Log("PASSED: No crashes.")

        # Check the required steps for positive results and that a rendering was done.
        if not context.HaveStepsPassed([ "Import", "Export", "Validate" ]):
            context.Log("FAILED: Import, export and validate steps must be present and successful.")
            return False
        if not context.DoesStepsExists([ "Render" ]):
            context.Log("FAILED: A render step is required.")
            return False
        context.Log("PASSED: Required steps executed and passed.")
        return True
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    # QUESTION: Is there a way to fetch the result of JudgeBaseline so we don't have to run it again?
    def JudgeExemplary(self, context):
        context.Log("N/A")
        return False
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeSuperior(self, context):
        context.Log("N/A")
        return False

    # To pass FX you need to pass basic?
    # This object could also include additional
    # tests that were specific to the FX badges
    def JudgeFx(self, context):
        context.Log("N/A")
        return False

    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgePhysics(self, context):
        context.Log("N/A")
        return False
    
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject();
judgingObject.CheckEnvirmoment();