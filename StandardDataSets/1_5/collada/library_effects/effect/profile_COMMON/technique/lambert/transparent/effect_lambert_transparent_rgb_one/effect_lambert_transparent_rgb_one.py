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
tagLst = [['library_effects', 'effect', 'profile_COMMON', 'technique', 'lambert', 'transparent', 'color'], ['library_effects', 'effect', 'profile_COMMON', 'newparam', 'float4'], ['library_effects', 'effect', 'newparam', 'float4']]
attrName = 'opaque'

# RGB_ONE
oneAttrVal = 'RGB_ONE'
oneDataToCheck = '0.3 0.3 0.3 0'

# RGB_ZERO
zeroAttrVal = 'RGB_ZERO'
zeroDataToCheck = '0.7 0.7 0.7 0'

class SimpleJudgingObject:
    def __init__(self, _tagLst, _attrName, _oneAttrVal, _oneDataToCheck, _zeroAttrVal, _zeroDataToCheck):
        self.tagList = _tagLst
        self.attrName = _attrName
        
        self.oneAttrVal = _oneAttrVal
        self.oneDataToCheck = _oneDataToCheck
        
        self.zeroAttrVal = _zeroAttrVal
        self.zeroDataToCheck = _zeroDataToCheck
        
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
    
    # Need to allow for legal transformation between RGB_ONE and RGB_ZERO
    def CheckTransparent(self, context):
    
    	transparentTagList = (self.tagList[0])[0:len(self.tagList[0])-1]
    	opaqueAttr = self.GetAttrValue(context, transparentTagList, self.attrName)

	if ( (opaqueAttr == self.oneAttrVal) or (opaqueAttr == None) ):
	    # Check each of the possible locations for the transparent data
    	    if ( self.ElementDataCheck(context, self.tagList[0], self.oneDataToCheck, "float", False) or
    	    	 self.ElementDataCheck(context, self.tagList[1], self.oneDataToCheck, "float", False) or
    	    	 self.ElementDataCheck(context, self.tagList[2], self.oneDataToCheck, "float", False) ):
                context.Log("PASSED: Transparent value is preserved, with opaque attribute " + self.oneAttrVal + ".")
                return True
	
	elif ( (opaqueAttr == self.zeroAttrVal) ):
	    # Check each of the possible locations for the transparent data
    	    if ( self.ElementDataCheck(context, self.tagList[0], self.zeroDataToCheck, "float", False) or
    	    	 self.ElementDataCheck(context, self.tagList[1], self.zeroDataToCheck, "float", False) or
    	    	 self.ElementDataCheck(context, self.tagList[2], self.zeroDataToCheck, "float", False) ):
                context.Log("PASSED: Transparent value is preserved, with opaque attribute " + self.zeroAttrVal + ".")
                return True
    	
        context.Log("FAILED: Transparent value is not preserved.")
        return False
        

    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])

        if (self.__assistant.GetResults() == False): 
            self.status_baseline = False
            return False

        # Compare the rendered images between import and export
        # Then compare images against alpha 1 reference test for equivalence
        # Then compare images against rgb white test for non-equivalence
        # Last, check for preservation of element data
        if ( self.__assistant.CompareRenderedImages(context) ):
            if ( self.__assistant.CompareImagesAgainst(context, "_ref_lamb_transparent_rgbzero_alpha1", None, None, 5, True, True) ):
                if ( self.__assistant.CompareImagesAgainst(context, "_ref_lamb_transparent_rgbzero_white", None, None, 5, True, False) ):
                    self.status_baseline = self.CheckTransparent(context)
                    return self.status_baseline
                    
        self.status_baseline = self.__assistant.DeferJudgement(context)
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
        self.status_exemplary = self.status_superior
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, oneAttrVal, oneDataToCheck, zeroAttrVal, zeroDataToCheck);