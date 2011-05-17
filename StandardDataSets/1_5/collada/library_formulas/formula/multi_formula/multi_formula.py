# Copyright (C) 2011 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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

tagLstRoot             = ['library_formulas', 'formula']
rootAttrName           = 'id'
tagLstNewparam         = ['library_formulas', 'formula', 'newparam']
newparamAtttName       = 'sid'
tagLstTarget           = ['library_formulas', 'formula', 'target', 'param']
tagLstTechnique        = ['library_formulas', 'formula', 'technique_common']
tagLstNewParamDataType = [['newparam', 'float'], ['newparam', 'int']]

# formula 1
rootAttrVal1           = 'pythagorean'
newparamAttrVal1       = ['hypotenuse', 'side1', 'side2']
tagLstCsymbol1         = ['library_formulas', 'formula', 'technique_common', 'math', 'apply', 'apply', 'apply', 'csymbol']
newparamCount1         = [1, 2]

# formula 2
rootAttrVal2           = 'pitch'
newparamAttrVal2       = ['target1', 'value', 'pitch']
tagLstCsymbol2         = [['library_formulas', 'formula', 'technique_common', 'math', 'apply', 'apply', 'csymbol'], 
		          ['library_formulas', 'formula', 'technique_common', 'math', 'apply', 'csymbol']]
newparamCount2         = [3, 0]

class SimpleJudgingObject:
    def __init__(self, _tagLstRoot, _rootAttrName, _tagLstNewparam, _newparamAtttName, _tagLstTarget, _tagLstTechnique, _tagLstNewParamDataType,
                 _rootAttrVal1, _newparamAttrVal1, _tagLstCsymbol1, _newparamCount1,
                 _rootAttrVal2, _newparamAttrVal2, _tagLstCsymbol2, _newparamCount2):
                 
        self.tagListRoot = _tagLstRoot
        self.rootAttrName = _rootAttrName
        self.tagListNewparam = _tagLstNewparam
        self.newparamAtttName = _newparamAtttName
        self.tagListTarget = _tagLstTarget
        self.tagListTechnique = _tagLstTechnique
        self.tagListNewparamDataType = _tagLstNewParamDataType
        
        self.rootAttrVal1 = _rootAttrVal1
        self.newparamAttrVal1 = _newparamAttrVal1
        self.tagListCsymbol1 = _tagLstCsymbol1
        self.newparamCount1 = _newparamCount1
        
        self.rootAttrVal2 = _rootAttrVal2
        self.newparamAttrVal2 = _newparamAttrVal2
        self.tagListCsymbol2 = _tagLstCsymbol2
        self.newparamCount2 = _newparamCount2
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()

    # Add the name space to the tags
    def AddNSToTagList(self, context):
        nameSpace = self.__assistant.GetNameSpace(context, self.tagListTechnique)
        
       	if (nameSpace != None):
       	    for i in range(3, len(self.tagListCsymbol1)):
       	        self.tagListCsymbol1[i] = nameSpace + ":" + self.tagListCsymbol1[i]
       	    
       	    for i in range(3, len(self.tagListCsymbol2[0])):
       	        self.tagListCsymbol2[0][i] = nameSpace + ":" + self.tagListCsymbol2[0][i]
       	    
       	    for i in range(3, len(self.tagListCsymbol2[1])):
       	        self.tagListCsymbol2[1][i] = nameSpace + ":" + self.tagListCsymbol2[1][i]
       	        
    def CheckFormula1(self, context):

        # check that the newparam attributes are preserved
        if ( (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal1[0])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal1[1])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal1[2])) ):
            return False
        
        # check that the target data is preserved
        if ( not self.__assistant.ElementDataCheck(context, self.tagListTarget, self.newparamAttrVal1[0], "string") ):
            return False
        
        # check that the newparam data types are preserved
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal1, self.tagListNewparamDataType[0]) != self.newparamCount1[0]) ):
            context.Log("FAILED: newparam <float> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <float> type is preserved")
        
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal1, self.tagListNewparamDataType[1]) != self.newparamCount1[1]) ):
            context.Log("FAILED: newparam <int> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <int> type is preserved")
        
        # check that the csymbol data is preserved
        if ( (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol1, self.newparamAttrVal1[1], "string")) or
             (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol1, self.newparamAttrVal1[2], "string")) ):
            return False
        
        return True

    def CheckFormula2(self, context):

        # check that the newparam attributes are preserved
        if ( (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal2[0])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal2[1])) or
             (not self.__assistant.AttributeCheck(context, self.tagListNewparam, self.newparamAtttName, self.newparamAttrVal2[2])) ):
            return False
        
        # check that the target data is preserved
        if ( not self.__assistant.ElementDataCheck(context, self.tagListTarget, self.newparamAttrVal2[0], "string") ):
            return False
        
        # check that the newparam data types are preserved
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal2, self.tagListNewparamDataType[0]) != self.newparamCount2[0]) ):
            context.Log("FAILED: newparam <float> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <float> type is preserved")
        
        if ( (self.__assistant.GetElementCount(self.tagListRoot, self.rootAttrName, self.rootAttrVal2, self.tagListNewparamDataType[1]) != self.newparamCount2[1]) ):
            context.Log("FAILED: newparam <int> type not preserved")
            return False
        else:
            context.Log("PASSED: newparam <int> type is preserved")
        
        # check that the csymbol data is preserved
        if ( (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol2[0], self.newparamAttrVal2[1], "string")) or
             (not self.__assistant.ElementDataCheck(context, self.tagListCsymbol2[1], self.newparamAttrVal2[2], "string")) ):
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
        
        self.AddNSToTagList(context)
        
        if (self.CheckFormula1(context) == False):
	    self.status_exemplary = False
            return self.status_exemplary 
        
        self.status_exemplary = self.CheckFormula2(context)
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLstRoot, rootAttrName, tagLstNewparam, newparamAtttName, tagLstTarget, tagLstTechnique, tagLstNewParamDataType,
                                    rootAttrVal1, newparamAttrVal1, tagLstCsymbol1, newparamCount1,
                                    rootAttrVal2, newparamAttrVal2, tagLstCsymbol2, newparamCount2);
