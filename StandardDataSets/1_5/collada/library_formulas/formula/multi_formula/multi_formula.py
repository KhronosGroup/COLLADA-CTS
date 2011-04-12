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

tagLstNewparam   = ['library_formulas', 'formula', 'newparam']
newparamAtttName = 'sid'
tagLstTarget = ['library_formulas', 'formula', 'target', 'param']

# formula 1
newparamAttrVal1  = ['target1', 'value', 'pitch']
tagLstCsymbol1 = [['library_formulas', 'formula', 'technique_common', 'math:math', 'math:apply', 'math:apply', 'math:csymbol'], 
		  ['library_formulas', 'formula', 'technique_common', 'math:math', 'math:apply', 'math:csymbol']]

# formula 2
newparamAttrVal2  = ['hypotenuse', 'side1', 'side2']
tagLstCsymbol2 = ['library_formulas', 'formula', 'technique_common', 'math:math', 'math:apply', 'math:apply', 'math:csymbol']

class SimpleJudgingObject:
    def __init__(self, _tagLstNewparam, _newparamAtttName, _tagLstTarget, _newparamAttrVal1, _tagLstCsymbol1, _newparamAttrVal2, _tagLstCsymbol2):
        self.tagLstNewparam = _tagLstNewparam
        self.newparamAtttName = _newparamAtttName
        self.tagLstTarget = _tagLstTarget
        
        self.newparamAttrVal1 = _newparamAttrVal1
        self.tagLstCsymbol1 = _tagLstCsymbol1
        
        self.newparamAttrVal2 = _newparamAttrVal2
        self.tagLstCsymbol2 = _tagLstCsymbol2
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        
        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline

    def CheckFormula1(self):
        # check that the newparam attributes are preserved
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal1[0])
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal1[1])
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal1[2])
        
        # check that the target data is preserved
        self.__assistant.ElementDataCheck(context, self.tagLstTarget, self.newparamAttrVal1[0], "string")
        
        # check that the csymbol data is preserved
        self.__assistant.ElementDataCheck(context, self.tagLstCsymbol1[0], self.newparamAttrVal1[1], "string")
        self.__assistant.ElementDataCheck(context, self.tagLstCsymbol1[1], self.newparamAttrVal1[2], "string")
        
    def CheckFormula2(self):
        # check that the newparam attributes are preserved
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal2[0])
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal2[1])
        self.__assistant.AttributeCheck(context, self.tagLstNewparam, self.newparamAtttName, self.newparamAttrVal2[2])
        
        # check that the target data is preserved
        self.__assistant.ElementDataCheck(context, self.tagLstTarget, self.newparamAttrVal2[0], "string")
        
        # check that the csymbol data is preserved
        self.__assistant.ElementDataCheck(context, self.tagLstCsymbol2, self.newparamAttrVal2[1], "string")
        self.__assistant.ElementDataCheck(context, self.tagLstCsymbol2, self.newparamAttrVal2[2], "string")

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
        
        self.CheckFormula1()
        
        if (self.__assistant.GetResults() == False):
	    self.status_exemplary = False
            return self.status_exemplary 
        
        self.CheckFormula2()
        
        self.status_exemplary = self.__assistant.DeferJudgement(context)
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLstNewparam, newparamAtttName, tagLstTarget, newparamAttrVal1, tagLstCsymbol1, newparamAttrVal2, tagLstCsymbol2);
