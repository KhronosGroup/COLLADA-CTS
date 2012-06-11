
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

from Core.Common.DOMParser import *
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = [['library_controllers', 'controller', 'skin', 'vertex_weights', 'input']]
attrName = ''
attrVal = ''
dataToCheck = ''

class SimpleJudgingObject:
    def __init__(self, _tagLst, _attrName, _attrVal, _data):
        self.tagList = _tagLst
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.dataToCheck = _data
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__inputFileName = ''
        self.__outputFileNameList = []
        self.__assistant = JudgeAssistant.JudgeAssistant()

    # Compares source data between input and output files
    def SourcePreserved(self, context, matchSemantic):
        # Get the input file
        self.__inputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())
        
        # Get the output file
        outputFilenames = context.GetStepOutputFilenames("Export")
        if len(outputFilenames) == 0:
            context.Log("FAILED: There are no export steps.")
            return False
        else:
            del self.__outputFileNameList[:]
            self.__outputFileNameList.extend( outputFilenames )
    
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        # get input list
        inputInputLst = FindElement(testIO.GetRoot(self.__inputFileName), self.tagList[0])
        if len( inputInputLst ) == 0:
            context.Log('FAILED: ' + matchSemantic + ' semantic of input is not found')
            return False
        
        inputOutputLst = []
        for eachTagList in self.tagList:
            inputOutputLst = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), eachTagList)
            if (len(inputOutputLst) > 0):
                break
                
        if len( inputOutputLst ) == 0:
            context.Log('FAILED: ' + matchSemantic + ' semantic of output is not found')
            return False
            
        for eachInput in inputInputLst:
            inputSemantic = GetAttriByEle(eachInput, 'semantic')
            if (inputSemantic == matchSemantic):
                dataType = 'Name_array'
                inputDataElement = GetDataFromInput( testIO.GetRoot(self.__inputFileName), eachInput, dataType)

                if inputDataElement == None:
                    dataType = 'IDREF_array'
                    inputDataElement = GetDataFromInput( testIO.GetRoot(self.__inputFileName), eachInput, dataType)
                    if inputDataElement == None:
                        context.Log('FAILED: ' + matchSemantic + ' source data in input is not found')
                        return False
                    else:
                        break
                else:
                    break
                    
        for eachOuput in inputOutputLst:
            if (GetAttriByEle(eachOuput, 'semantic') == inputSemantic):
                outputDataElement = GetDataFromInput( testIO.GetRoot(self.__outputFileNameList[0]), eachOuput, dataType)

                if outputDataElement == None:
                    context.Log('FAILED: ' + dataType + ' ' + matchSemantic + ' source in output is not found')
                    return False
                else:
                    break
        
        if (inputDataElement != None and outputDataElement != None):
            inputDataList = inputDataElement.childNodes[0].nodeValue.split()
            outputDataList = outputDataElement.childNodes[0].nodeValue.split()
        
            if (len(inputDataList) != len(outputDataList)):
                context.Log('FAILED: ' + matchSemantic + ' source data is not preserved')
                return False
                                
            for i in range( len(inputDataList) ):
                if (dataType == "float_array"):
                    if ( not IsValueEqual( float(outputDataList[i]), float(inputDataList[i]), 'float') ):
                        context.Log('FAILED: ' + matchSemantic + ' source data is not preserved')
                        return False
                else:
                    if ( not IsValueEqual(outputDataList[i], inputDataList[i], 'string') ):
                        context.Log('FAILED: ' + matchSemantic + ' source data is not preserved')
                        return False
        else:
            context.Log('FAILED: ' + matchSemantic + ' source data is not preserved')
            return False

        context.Log('PASSED: ' + matchSemantic + ' source data is preserved')
        return True
        
    def JudgeBaseline(self, context):
        # No step should crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])
        
        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline
    
    # To pass superior you need to pass baseline, this object could also include additional 
    # tests that were specific to the superior badge.
    def JudgeSuperior(self, context):
        # if baseline fails, no point in further checking
        if (self.status_baseline == False):
            self.status_superior = self.status_baseline
            return self.status_superior
        
        # Compare the rendered images between import and export, and if passed, 
        # compare images against reference test
        if ( self.__assistant.CompareRenderedImages(context) ):
            self.status_superior = self.SourcePreserved(context, 'JOINT')
            return self.status_superior
        
        self.__assistant.DeferJudgement(context)
        return self.status_superior
            
    # To pass exemplary you need to pass superior, this object could also include additional
    # tests that were specific to the exemplary badge
    def JudgeExemplary(self, context):
        self.status_exemplary = self.status_superior
        return self.status_exemplary 
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);
