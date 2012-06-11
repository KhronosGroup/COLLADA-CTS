
# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

# This sample judging object does the following:
#
# JudgeBaseline: just verifies that the standard steps did not crash.
# JudgeSuperior: also verifies that the validation steps are not in error.
# JudgeExemplary: same as intermediate badge.

# We import an assistant script that includes the common verifications
# methods. The assistant buffers its checks, so that running them again
# does not incurs an unnecessary performance hint.
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLstNewparam         = ['library_formulas', 'formula', 'newparam']
newparamAtttName       = 'sid'
newparamAttrVal        = ['hypotenuse', 'side1', 'side2']
tagLstTarget           = ['library_formulas', 'formula', 'target', 'param']
tagLstTechnique        = ['library_formulas', 'formula', 'technique_common']
tagLstCsymbol          = ['library_formulas', 'formula', 'technique_common', 'math', 'apply', 'apply', 'apply', 'csymbol']

tagLstRoot             = ['library_formulas', 'formula']
rootAttrName           = 'id'
rootAttrVal            = 'pythagorean'
tagLstNewParamDataType = [['newparam', 'float'], ['newparam', 'int']]
newparamCount          = [1, 2]

class SimpleJudgingObject:
    def __init__(self, _tagLstNewparam, _newparamAtttName, _newparamAttrVal, _tagLstTarget, _tagLstTechnique, _tagLstCsymbol,
                 _tagLstRoot, _rootAttrName, _rootAttrVal, _tagLstNewParamDataType, _newparamCount):
                 
        self.tagListNewparam = _tagLstNewparam
        self.newparamAtttName = _newparamAtttName
        self.newparamAttrVal = _newparamAttrVal
        self.tagListTarget = _tagLstTarget
        self.tagListTechnique = _tagLstTechnique
        self.tagListCsymbol = _tagLstCsymbol
        
        self.tagListRoot = _tagLstRoot
        self.rootAttrName = _rootAttrName
        self.rootAttrVal = _rootAttrVal
        self.tagListNewparamDataType = _tagLstNewParamDataType
        self.newparamCount = _newparamCount
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()

    # Add the name space to the tags
    def AddNSToTagList(self, context):
        nameSpace = self.__assistant.GetNameSpace(context, self.tagListTechnique)
        
       	if (nameSpace != None):
       	    for i in range(3, len(self.tagListCsymbol)):
       	        self.tagListCsymbol[i] = nameSpace + ":" + self.tagListCsymbol[i]

    def CheckFormula(self, context):
        self.AddNSToTagList(context)
    
        # check that the newparam attributes are preserved
        if ( (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal[0])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal[1])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal[2])) ):
            return False
        
        # check that the target data is preserved
        if ( not self.__assistant.ElementDataCheck(context, self.tagListTarget, self.newparamAttrVal[0], "string") ):
            return False
        
        # check that the newparam data types are preserved
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal, self.tagListNewparamDataType[0]) != self.newparamCount[0]) ):
            context.Log("FAILED: newparam <float> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <float> type is preserved")
        
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal, self.tagListNewparamDataType[1]) != self.newparamCount[1]) ):
            context.Log("FAILED: newparam <int> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <int> type is preserved")
        
        # check that the csymbol data is preserved
        if ( (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol, self.newparamAttrVal[1], "string")) or
             (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol, self.newparamAttrVal[2], "string")) ):
            return False
        
        return True
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], [])
        
        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
	# if superior fails, no point in further checking
        if (self.status_superior == False):
            self.status_exemplary = self.status_superior
            return self.status_exemplary
        
        self.status_exemplary = self.CheckFormula(context)
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLstNewparam, newparamAtttName, newparamAttrVal, tagLstTarget, tagLstTechnique, tagLstCsymbol,
                                    tagLstRoot, rootAttrName, rootAttrVal, tagLstNewParamDataType, newparamCount);