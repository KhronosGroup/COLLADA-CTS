
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
tagLstRoot             = [['library_kinematics_models', 'kinematics_model', 'technique_common', 'formula'], ['library_formulas', 'formula']]
rootAttrName           = 'id'
tagLstNewparam         = ['newparam']
newparamAtttName       = 'sid'
tagLstTarget           = ['target', 'param']
tagLstTechnique        = ['technique_common']
tagLstNewParamDataType = [['newparam', 'float'], ['newparam', 'int']]

rootAttrVal           = 'pitch'
newparamAttrVal       = ['target1', 'value', 'pitch']
tagLstCsymbol         = [['technique_common', 'math', 'apply', 'apply', 'csymbol'], ['technique_common', 'math', 'apply', 'csymbol']]
newparamCount         = [3, 0]

class SimpleJudgingObject:
    def __init__(self, _tagLstNewparam, _newparamAtttName, _newparamAttrVal, _tagLstTarget, _tagLstTechnique, _tagLstCsymbol,
                 _tagLstRoot, _rootAttrName, _rootAttrVal, _tagLstNewParamDataType, _newparamCount):

    def __init__(self, _tagLstRoot, _rootAttrName, _tagLstNewparam, _newparamAtttName, _tagLstTarget, _tagLstTechnique, _tagLstNewParamDataType,
                 _rootAttrVal, _newparamAttrVal, _tagLstCsymbol, _newparamCount):

        self.tagListRoot = _tagLstRoot
        self.rootAttrName = _rootAttrName
        self.tagListNewparam = _tagLstNewparam
        self.newparamAtttName = _newparamAtttName
        self.tagListTarget = _tagLstTarget
        self.tagListTechnique = _tagLstTechnique
        self.tagListNewparamDataType = _tagLstNewParamDataType
        
        self.rootAttrVal = _rootAttrVal
        self.newparamAttrVal = _newparamAttrVal
        self.tagListCsymbol = _tagLstCsymbol
        self.newparamCount = _newparamCount
        
        # Variable to hold the original location of the formula
        self.tagListInKinematics = self.tagListRoot[0]
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()

    def SetTagLists(self, context):
        if (self.__assistant.AttributeCheck(context, self.tagListRoot[0], self.rootAttrName, self.rootAttrVal, False)):
            self.tagListRoot = self.tagListRoot[0]
        elif (self.__assistant.AttributeCheck(context, self.tagListRoot[1], self.rootAttrName, self.rootAttrVal, False)):
            self.tagListRoot = self.tagListRoot[1]
        else:
            context.Log("FAILED: unable to find formula")
            return False
        
        tempTagList = self.tagListRoot
        tempTagList.append(self.tagListNewparam)
	self.tagListNewparam = tempTagList
        
        tempTagList = self.tagListRoot
        tempTagList.append(self.tagListTarget)
	self.tagListTarget = tempTagList
	
        tempTagList = self.tagListRoot
        tempTagList.append(self.tagListTechnique)
	self.tagListTechnique = tempTagList
	
	self.AddNSToTagList(context)
	
        tempTagList = self.tagListRoot
        tempTagList.append(self.tagListCsymbol)
	self.tagListCsymbol = tempTagList
	
	return True
	
    # Add the name space to the tags
    def AddNSToTagList(self, context):
        nameSpace = self.__assistant.GetNameSpace(context, self.tagListTechnique)
        
       	if (nameSpace != None):
       	    for i in range(len(self.tagListCsymbol)):
       	        self.tagListCsymbol[i] = nameSpace + ":" + self.tagListCsymbol[i]

    def CheckFormula(self, context):
        if (not self.SetTagLists()):
            return False

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
        if ( (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol[0], self.newparamAttrVal[1], "string")) or
             (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol[1], self.newparamAttrVal[2], "string")) ):
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
	# if baseline fails, no point in further checking
        if (self.status_baseline == False):
            self.status_superior = self.status_baseline
            return self.status_superior
        
        self.status_exemplary = self.CheckFormula(context)
        return self.status_exemplary 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
	# if superior fails, no point in further checking
        if (self.status_superior == False):
            self.status_exemplary = self.status_superior
            return self.status_exemplary
        
        self.__assistant.AttributeCheck(context, tagListInKinematics, self.rootAttrName, self.rootAttrVal)
        
        self.status_exemplary = self.__assistant.DeferJudgement(context)
        return self.status_exemplary
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLstNewparam, newparamAtttName, newparamAttrVal, tagLstTarget, tagLstTechnique, tagLstCsymbol,
                                    tagLstRoot, rootAttrName, rootAttrVal, tagLstNewParamDataType, newparamCount);

judgingObject = SimpleJudgingObject(tagLstRoot, rootAttrName, tagLstNewparam, newparamAtttName, tagLstTarget, tagLstTechnique, tagLstNewParamDataType,
                                    rootAttrVal, newparamAttrVal, tagLstCsymbol, newparamCount);
