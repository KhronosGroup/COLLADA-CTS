# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

from Core.Common.DOMParser import *
from Core.Common.CheckingModule import *

""" A judge assistant. The purpose of this structure is to abstract
    out the parts that are very common amongst the different per-test
    case judging scripts. This should writing and maintaining per-test
    case judging scripts easier and cheaper.
    
    NOTE: The judge assistant does keep track of all the results it has
    provided so far. It is usally good practice to do all the checks
    for a badge level without checking the individual results. You can
    use the GetResults() function at the end of your badge level judging
    script in order to retrieve the assistant's judgement. Alternatively,
    if your per-test case script only uses the asistant's judgement, use
    the DeferJudgement() function to log an appropriate message. """ 
class JudgeAssistant:
    def __init__(self):
        self.__checkCrashesResult = None
        self.__checkStepsResult = []
        self.__compareImagesResults = []
        self.__compareRendersResults = None
        self.__preservationResults = None
        self.__inputFileName = ""
        self.__outputFileNameList = []
        
        # This is the persistant result value.
        self.__result = True

    
    """ Retrieves the overall result of the assistant's checks.
        @return The overall result. """
    def GetResults(self):
        return self.__result
        
    """ Retrieves the overall result of the assistant's checks
        and defers the judgment to it.
        @param context The judgement context.
        @return The overall result. """
    def DeferJudgement(self, context):
        if self.__result:
            context.Log("PASSED: Assistant judgement is positive.")
        else:
            context.Log("FAILED: Assistant judgement is negative.")
        return self.__result
        
    """ Resets the overall judgement result.
        Keeps the cached values intact. """
    def ResetJudgement(self):
        self.__result = True
        
    """ Checks whether any of the steps have crashed.
        The result of this function is cached so that running
        it multiple times never impacts performance.
        @param context The judgement context.
        @param != Whether the default log strings should be output.
        @return Whether any of the steps have crashed. """
    def CheckCrashes(self, context, defaultLogText = True):

        # The results of this check are cached
        if self.__checkCrashesResult == None:
            self.__checkCrashesResult = not context.HasStepCrashed()
 
        if defaultLogText:
            # Default result logging
            if self.__checkCrashesResult:
                context.Log("PASSED: No crashes.")
            else:
                context.Log("FAILED: Crashes during required steps.")

        # Keep track of the results.
        if not self.__checkCrashesResult: self.__result = False
        return self.__checkCrashesResult
        return True

    """ Checks whether the expected steps were run and passed.
        @param context The judgement context.
        @param stepsPassedList The list of steps that were expected to run and pass.
            Example: ["Import", "Export", "Validate"]
        @param stepsExistsList The list of steps that were expected to run.
            Example: ["Render"]
        @param defaultLogText Whether the default log strings should be output.
        @return Whether any of the steps have crashed. """                
    def CheckSteps(self, context, stepsPassedList, stepsExistsList, defaultLogText = True):

        # The result for one set of inputs is cached.
        if len(self.__checkStepsResult) != 4:
            self.__checkStepsResult = [None,None,None,None]
        if (self.__checkStepsResult[0] != stepsPassedList and self.__checkStepsResult[1] != stepsExistsList):
            self.__checkStepsResult[0] = stepsPassedList
            self.__checkStepsResult[1] = stepsExistsList
            if stepsPassedList != None and len(stepsPassedList) > 0:
                self.__checkStepsResult[2] = context.HaveStepsPassed(stepsPassedList)
            else: self.__checkStepsResult[2] = True
            if stepsExistsList != None and len(stepsExistsList) > 0:
                self.__checkStepsResult[3] = context.DoesStepsExists(stepsExistsList)
            else: self.__checkStepsResult[3] = True
        
        # Output the result for the user.
        if defaultLogText:
            if not self.__checkStepsResult[2]:
                context.Log("FAILED: " + self.TokenListString(stepsPassedList) + " step(s) must be present and successful.")
            if not self.__checkStepsResult[3]:
                context.Log("FAILED: " + self.TokenListString(stepsExistsList) + " step(s) required.")
            if self.__checkStepsResult[2] and self.__checkStepsResult[3]:
                context.Log("PASSED: Required steps executed and passed.")

        # Compile the results
        if not self.__checkStepsResult[2] or not self.__checkStepsResult[3]: self.__result = False
        return self.__checkStepsResult[2] and self.__checkStepsResult[3]

    """ Checks whether the images generated for this test case are
        equivalent to the images generated for another test case. Only does 
        comparison on the first Render step of each test case.
        @param context The judgement context.
        @param substring0 A first substring to match. This parameter is necesssary.
        @param substring1 An optional second substring to match.
        @param substring2 An optional third substring to match.
        @param maxDifference The maximum difference allowed between the images of the two tests.
        @param defaultLogText Whether the default log strings should be output.
        @return Whether the images generated of this test case are
            equivalent to the images of the other test case. """
    def CompareImagesAgainst(self, context, testCaseId0, testCaseId1=None, testCaseId2=None, maxDifference = 5, defaultLogText = True, compareEqual = True):
        # Look for a buffered result set.
        result = None
        tokenList = [testCaseId0, testCaseId1, testCaseId2]
        tokenListString = self.TokenListString(tokenList)
#        for resultSet in self.__compareImagesResults:
#            if resultSet[0] == tokenList:
#                result = resultSet
#                break

        if result == None:
            result = [tokenList]

            # Look for the other test case.
            otherTestId = context.FindTestId(testCaseId0, testCaseId1, testCaseId2)
            result.append(otherTestId != None)

            # Retrieve the image filenames for this test case.
            # renderSteps[0] is the first render step
            renderSteps = context.GetStepImageFilenames()
            if (len(renderSteps) > 0):
                imageFilenames = renderSteps[0]
                imageFilenameCount = len(imageFilenames)
            else:
                imageFilenameCount = 0
                
            result.append(imageFilenameCount > 0)
            
            if result[1] and result[2]:
                # Retrieve the image filenames for the other test case.
                otherRenderSteps = context.GetStepImageFilenames(otherTestId)
                if (len(otherRenderSteps) > 0):
                    otherFilenames = otherRenderSteps[0]
                    otherFilenameCount = len(otherFilenames)
                else:
                    otherFilenameCount = 0
                
                result.append(otherFilenameCount > 0)
                
                if result[3]:
                    # Compare the images by index.
                    count = min(imageFilenameCount, otherFilenameCount)
                    for i in range(count):
#                        print "image1: " + imageFilenames[i]
#                        print "image2: " + otherFilenames[i]
                        result.append(context.CompareImages(imageFilenames[i], otherFilenames[i]))

            # Cache these results.
            self.__compareImagesResults.append(result)
                
        # Log the results.
        if defaultLogText:
            if not result[1] or not result[3]:
                context.Log("FAILED: You must also run the '" + tokenListString + "' test case.")
            if not result[2]:
                context.Log("FAILED: This test must include a 'Render' step.")
            if len(result) > 4 and not result[3]:
                context.Log("FAILED: The '" + tokenListString + "' must include a 'Render' step.")
            for i in range(len(result) - 4):
                if (len(result) == 5): 
                    identifier = "Output"
                else: identifier = "Output #%s" % str(i + 1)

                if (compareEqual):
                    if result[4+i] > maxDifference:
                        context.Log("FAILED: " + identifier + " doesn't match the '" + tokenListString + "' test. Result: %s" % str(result[4+i]))
                    else:
                        context.Log("PASSED: " + identifier + " matches the '" + tokenListString + "' test. Result: %s" % str(result[4+i]))
                else:
                    if result[4+i] > maxDifference:
                        context.Log("PASSED: " + identifier + " doesn't match the '" + tokenListString + "' test. Result: %s" % str(result[4+i]))
                    else:
                        context.Log("FAILED: " + identifier + " matches the '" + tokenListString + "' test. Result: %s" % str(result[4+i]))

        # Compile the results.
        localResult = True
        if not result[1] or not result[2]: localResult = False
        elif not result[3]: localResult = False
        else:
            for i in range(len(result) - 4):
                if (compareEqual):
                    if result[4+i] > maxDifference: localResult = False
                else:
                    if result[4+i] <= maxDifference: localResult = False
        if not localResult: self.__result = False
        return localResult
            
    """ [INTERNAL] Generates a nice string with the given list tokens.
        @param tokens A list of tokens.
        @return A string containing the list of tokens in a nice form. """
    def TokenListString(self, tokens):
        newTokens = []
        for i in range(len(tokens)):
            if tokens[i] != None and tokens[i] != "":
                newTokens.append(tokens[i])
   
        output = ""
        count = len(newTokens)
        for i in range(count):
            token = newTokens[i]
            if i == 0: output += token.title()
            elif i < count - 1: output += ", " + token.lower()
            else: output += " and " + token.lower()
        
        return output

############################################################

    # Sets the input file and output file list
    def SetInputOutputFiles(self, context):
        outputFileList = []
    
        # Get the input file
        self.__inputFileName = context.GetAbsInputFilename(context.GetCurrentTestId())

        # Get the output file
        outputFileList = context.GetStepOutputFilenames("Export")
        
        if len(outputFileList) == 0:
            context.Log("FAILED: There are no export steps.")
            return False
        else:
            del self.__outputFileNameList[:]
            self.__outputFileNameList.extend( outputFileList )
            return True
        

    # Compare images between the input render and the first output render
    def CompareRenderedImages(self, context):
        self.__compareRendersResults = True
        msg = "PASSED: Output images match input images."
    
        # Retrieve the image files for this test case.
        imageFilenames = context.GetStepImageFilenames()
        if (len(imageFilenames) == 0):
            self.__compareRendersResults = False
            msg = "FAILED: Unable to retrieve image locations."
        else:
            inputImages = imageFilenames[0]
            outputImages = imageFilenames[1]
            if (len(inputImages) != len(outputImages)):
                self.__compareRendersResults = False
                msg = "FAILED: Number of input images do not match output images."
            else:
                # Compare each image in the render steps
                for i in range(len(inputImages)):
                    print ""
                    print inputImages[i]
                    print outputImages[i]
                    print ""
                    result = context.CompareImages(inputImages[i], outputImages[i])
                    if result > 5:
                        self.__compareRendersResults = False
                        msg = "FAILED: Output images do not match input images."

        if (not self.__compareRendersResults):
            self.__result = False
            
        context.Log(msg)
        return self.__compareRendersResults        
    
    # Checks whether images in the import render step show animation
    def HasAnimatedImages(self, context):
        self.__compareRendersResults = False
        msg = "FAILED: Images do not show animation."
    
        # Retrieve the image files for this test case.
        imageFilenames = context.GetStepImageFilenames()
        if (len(imageFilenames) == 0):
            self.__compareRendersResults = False
            msg = "FAILED: Unable to retrieve image locations."
        else:
            inputImages = imageFilenames[0]
            if (len(inputImages) < 3):
                self.__compareRendersResults = False
                msg = "FAILED: Number of animation images are too few."
            else:
                # Compare each image in the list with its previous image
                for i in range(1, len(inputImages)):
                    result = context.CompareImages(inputImages[i], inputImages[i-1])
                    if result > 5:
                        self.__compareRendersResults = True
                        msg = "PASSED: Images show animation."
                        break
#                        print "failed on image: " + inputImages[i]

        if (not self.__compareRendersResults):
            self.__result = False
            
        context.Log(msg)
        return self.__compareRendersResults 

    # Checks for the existence of an element in an output file specified by the tagList path
    def ElementPreserved(self, context, tagList, defaultLogText = True):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        # get required elements from the path def'ed by the tagLst
        elementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)

        if (len(elementList) > 0):
            logMsg = "PASSED: <"+ tagList[len(tagList)-1] +"> is preserved."
            self.__preservationResults = True
        else:
            logMsg = "FAILED: <"+ tagList[len(tagList)-1] +"> is not preserved."
            self.__preservationResults = False
            self.__result = False

        if (defaultLogText):
            context.Log(logMsg)

        testIO.Delink()
        return self.__preservationResults
        
        
    # Checks for the existence of an element in an output file specified by a list of paths in tagListArray
    # The first tagList should contain the original tag, while the ones after
    # contain the possible tags the original can be transformed into
    def ElementTransformed(self, context, tagListArray):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        # Get the original input tag to check for
        inputTagList = tagListArray[0]

        # get required elements from the path def'ed by the tagLst
        for eachtagList in tagListArray:
            elementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), eachtagList)
            if (len(elementList) > 0):
                testIO.Delink()
                context.Log("PASSED: <"+ inputTagList[len(inputTagList)-1] +"> is preserved as <"+ eachtagList[len(eachtagList)-1] +">")
                self.__preservationResults = True
                return self.__preservationResults
                
        testIO.Delink()
        context.Log("FAILED: <"+ inputTagList[len(inputTagList)-1] +"> is not preserved.")
        self.__preservationResults = False
        self.__result = False
        return self.__preservationResults
        
    # Checks for the existence of a specific element type with a specific id in the output file
    # The tagListArray contains the possible path(s) that the node can be found in 
    def ElementPreservedById(self, context, tagListArray, id):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        # get required elements from the path def'ed by the tagLst
        for eachtagList in tagListArray:
            elementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), eachtagList)
            if (len(elementList) > 0):
                for eachElement in elementList:
                    if (GetAttriByEle(eachElement, "id") == id):
                        testIO.Delink()
                        context.Log("PASSED: <"+ eachElement.nodeName +" id =\'"+ id + "\'> is preserved.")
                        self.__preservationResults = True
                        return self.__preservationResults

        testIO.Delink()
        context.Log("FAILED: <"+ tagListArray[0][len(tagListArray[0])-1] +" id =\'"+ id + "\'> is not preserved.")
        self.__preservationResults = False
        self.__result = False
        return self.__preservationResults
        
    # Checks an element's attribute value in the output file against a known attributeName and attributeValue
    def AttributeCheck(self, context, tagList, attributeName, attributeValue):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        # check for tag found in output file
        elementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)

        for eachElement in elementList:
            if (GetAttriByEle(eachElement, attributeName) == attributeValue):
                context.Log("PASSED: " + attributeName + "=\'" + attributeValue + "\' of <"+ tagList[len(tagList)-1] +"> is preserved.")
                self.__preservationResults = True
                break

        if (self.__preservationResults != True):
            context.Log("FAILED: " + attributeName + "=\'" + attributeValue + "\' of <"+ tagList[len(tagList)-1] +"> is not preserved.")
            self.__preservationResults = False
            self.__result = False
        
        testIO.Delink()
        return self.__preservationResults


    # Compares an element's attribute value between the input and output file with a known attributeName
    def AttributePreserved(self, context, tagList, attributeName):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
                
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0]) )

        # get input and output tags
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), tagList)
        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)

        if ( len(inputElementList) > 0 and len(outputElementList) > 0 ):
            resetElements = testPChecker.ResetElements(inputElementList, outputElementList)

            # check whether the attribute is retrieved and are equal
            if resetElements[0] == True:            
                resChkVale = testPChecker.checkAttri(attributeName)
                if resChkVale[0] == True:
                    context.Log("PASSED: " + attributeName + " of <"+ tagList[len(tagList)-1] +"> is preserved.")
                    self.__preservationResults = True
                else:
                    context.Log("FAILED: " + attributeName + " of <"+ tagList[len(tagList)-1] +"> is not preserved.")
                    self.__preservationResults = False
                    self.__result = False
            else:
                context.Log("FAILED: " + attributeName + " of <"+ tagList[len(tagList)-1] +"> is not found.")
                self.__preservationResults = False
                self.__result = False
        else:
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> is not found.")
            self.__preservationResults = False
            self.__result = False

        testIO.Delink()
        return self.__preservationResults
    
    
    # Compares an element's data against known data of type "float" or "string"
    def ElementDataCheck(self, context, tagList, knownData, dataType="float"):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
    
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        # get required elements from the path def'ed by the tagLst
        elementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)
        
        # separate each data value for comparison
        dataToCheckList = knownData.split()
        
        foundMatch = False
        for index in range( len(elementList) ):
            outputDataList = elementList[index].childNodes[0].nodeValue.split()
            
            if ( len(outputDataList) > 0 and len(outputDataList) == len(dataToCheckList) ):
                foundMatch = True
                for i in range( len(outputDataList) ):
                    if (dataType == "float"):
                        if ( not IsValueEqual(float(outputDataList[i]), float(dataToCheckList[i]), 'float') ):
                            foundMatch = False
                            break
                    else:
                        if ( not IsValueEqual(outputDataList[i], dataToCheckList[i], 'string') ):
                            foundMatch = False
                            break
            else:
                foundMatch = False
            
            if (foundMatch):
                break
                
        if (foundMatch):
            context.Log("PASSED: <"+ tagList[len(tagList)-1] +"> data is preserved.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> data is not preserved.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults
        
    # Compares an element's data between the input and output file of type "float" or "string"
    def ElementDataPreserved(self, context, tagList, dataType="float"):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0]) )

        # get input and output tags
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), tagList)
        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)
        
        dataToCheckList = inputElementList[0].childNodes[0].nodeValue.split()

        foundMatch = False
        for index in range( len(outputElementList) ):
            outputDataList = outputElementList[index].childNodes[0].nodeValue.split()
            
            if ( len(outputDataList) > 0 and len(outputDataList) == len(dataToCheckList) ):
                foundMatch = True
                for i in range( len(outputDataList) ):
                    if (dataType == "float"):
                        if ( not IsValueEqual(float(outputDataList[i]), float(dataToCheckList[i]), 'float') ):
                            foundMatch = False
                            break
                    else:
                        if ( not IsValueEqual(outputDataList[i], dataToCheckList[i], 'string') ):
                            foundMatch = False
                            break
            else:
                foundMatch = False
            
            if (foundMatch):
                break

        if (foundMatch):
            context.Log("PASSED: <"+ tagList[len(tagList)-1] +"> data is preserved.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> data is not preserved.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults

    # Checks for the existence of any data in all elements found in the tagList path
    def ElementDataExists(self, context, tagList):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)
        dataExists = True

        if (len(outputElementList) > 0):
            for index in range( len(outputElementList) ):
                if ( outputElementList[index].hasChildNodes() ):
                    
                    # If the element has more than a single child, then it contains child elements and not data
                    if ( len(outputElementList[index].childNodes) > 1):
                        dataExists = False
                        break

                    childNode = outputElementList[index].childNodes[0]
                    
                    # TEXT_NODE indicates that child node is data
                    if (childNode.nodeType == childNode.TEXT_NODE):
                        if (childNode == None or len(childNode.nodeValue.split()) == 0):
                            dataExists = False
                            break
                    else:
                        dataExists = False
                        break
                else:
                    dataExists = False
                    break
        else:
            dataExists = False

        if (dataExists):
            context.Log("PASSED: <"+ tagList[len(tagList)-1] +"> data exists.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> data does not exist.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults
        
    # Compares the number of data in an element between the input and output as specified by the tag list
    def ElementDataCountPreserved(self, context, tagList):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        # get input and output tags
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), tagList)
        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)
        
        if ( len(inputElementList) == 0 or len(outputElementList) == 0 ):
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> in input or output is not found.")
            self.__preservationResults = False
            self.__result = False
            testIO.Delink()
            return self.__preservationResults
        
        inputDataCount = len(inputElementList[0].childNodes[0].nodeValue.split())
        outputDataCount = len(outputElementList[0].childNodes[0].nodeValue.split())
        
        if (inputDataCount == outputDataCount):
            context.Log("PASSED: <"+ tagList[len(tagList)-1] +"> data count is preserved.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: <"+ tagList[len(tagList)-1] +"> data count is not preserved.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults
        
    # Check for the preservation of element data in the tagListArray[] paths
    # The first tagListArray[0] should contain the original tag, while the ones after
    # contain the possible tag locations the dat can be in
    def ElementDataPreservedIn(self, context, tagListArray, dataType="float"):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0]) )

        # get input tags
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), tagListArray[0])
        
        dataToCheckList = inputElementList[0].childNodes[0].nodeValue.split()
        
        # Get the original input tag to check for
        inputTagList = tagListArray[0]

        # get required elements from the path def'ed by the tagLst
        for eachtagList in tagListArray:
            outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), eachtagList)

            foundMatch = False
            for index in range( len(outputElementList) ):
                outputDataList = outputElementList[index].childNodes[0].nodeValue.split()
                if ( len(outputDataList) > 0 and len(outputDataList) == len(dataToCheckList) ):
                    foundMatch = True
                    for i in range( len(outputDataList) ):
                        if (dataType == "float"):
                            if ( not IsValueEqual( float(outputDataList[i]), float(dataToCheckList[i]), 'float') ):
                                foundMatch = False
                                break
                        else:
                            if ( not IsValueEqual( outputDataList[i], dataToCheckList[i], 'string') ):
                                foundMatch = False
                                break
                else:
                    foundMatch = False
            
                if (foundMatch):
                    break
            if (foundMatch):
                break

        # Get the original input tag to check for
        inputTagList = tagListArray[0]
        
        if (foundMatch):
            context.Log("PASSED: <"+ inputTagList[len(inputTagList)-1] +"> data is preserved.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: <"+ inputTagList[len(inputTagList)-1] +"> data is not preserved.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults
        
    
    # Checks the preservation of the attributes in attrLst for each node with the IDs in nodeIdLst
    # nodeIdLst: list of node IDs
    # attrLst: list of attributes names to check for preservation
    def CheckAttrByID(self, context, nodeIdLst, attrLst):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0])  )
           
        # use id for the element
        for eachNodeId in nodeIdLst:
            resSetEle = testPChecker.ResetElementById(eachNodeId)
               
            # check whether there is id retrived correctly
            if resSetEle[0] == True:
                for eachAttr in attrLst:
                    resChkAttri = testPChecker.checkAttri(eachAttr)
                  
                    if resChkAttri[0] == True:
                        context.Log("PASSED: In " + eachNodeId + ", required attribute " + eachAttr + " is preserved.")                        
                    else:
                        testIO.Delink()
                        context.Log("FAILED: In " + eachNodeId + ", required attribute " + eachAttr + " is not preserved.")
                        self.__preservationResults = False
                        self.__result = False
                        return self.__preservationResults
            else:
                testIO.Delink()
                context.Log("FAILED: " + eachNodeId + " doesn't exist.")
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
            
        # flag for all test: only pass all, then we can give a bdage
        context.Log("PASSED: All attributes are preserved.")
        testIO.Delink()
        self.__preservationResults = True
        return self.__preservationResults
            
    # Compares the attributes in attrLst 
    def CheckAttrWithoutID(self, context, parentId, tagName, attrLst):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0]) )
        resGetByTag = testPChecker.ResetElementsByTag(parentId,  tagName)
            
        if resGetByTag[0] == False:
            context.Log("Failed: Attributes are not preserved.")
            context.Log("Message: " + resGetByTag[1])
            self.__preservationResults = False
            self.__result = False
            return self.__preservationResults
        
        for eachAttr in attrLst:
            # Get all tags and then compare the attributes:
            resEleTags = testPChecker.checkElesAttribute(eachAttr)
            
            if resEleTags[0] == False:
                testIO.Delink()
                context.Log("FAILED: Attribute " + eachAttr + " is not preserved.")
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
            else:
                context.Log("PASSED: Attribute " + eachAttr + " is preserved.")
            
        # flag for all test: only pass all, then we can give a bdage
        context.Log("PASSED: All attributes are preserved.")
        testIO.Delink()
        self.__preservationResults = True
        return self.__preservationResults

    # Checks for attribute preservation of an element given its child element
    # tagList: root location to start searching for the child element
    # childTagName: name of the child element
    # attrName: name of the attribute to check
    def CheckAttrByChild(self, context, tagList, childTagName, attrName):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        inputRoot = testIO.GetRoot(self.__inputFileName)
        outputRoot = testIO.GetRoot(self.__outputFileNameList[0])
        
        inputTagLst = GetElementsByTags(inputRoot, tagList)
        inputElementList = inputTagLst[0].getElementsByTagName(childTagName)
        inputCount = len(inputElementList)
        
        outputTagLst = GetElementsByTags(outputRoot, tagList)
        outputElementList = outputTagLst[0].getElementsByTagName(childTagName)
        outputCount = len(outputElementList)
        
        if (inputCount == 0 or outputCount == 0):
            context.Log("FAILED: <"+ childTagName +"> in input or output not found.")
            self.__preservationResults = False
            self.__result = False
        else:
            # Get parent node and attribute
            inputParent = inputElementList[0].parentNode
            inputAttrValue = GetAttriByEle(inputParent, attrName)
            
            outputParent = outputElementList[0].parentNode
            outputAttrValue = GetAttriByEle(outputParent, attrName)
            
            if (inputAttrValue == outputAttrValue):
                context.Log("PASSED: " + attrName + " attribute for parent node of <"+ childTagName +"> is preserved.")
                self.__preservationResults = True
            else:
                context.Log("FAILED: " + attrName + " attribute for parent node of <"+ childTagName +"> is not preserved.")
                self.__preservationResults = False
                self.__result = False
            
        testIO.Delink()
        return self.__preservationResults
        
################## newParam checking #######################

    # Checks for the preservation or transformation of newparam/param
    # If we start with newparam/param in the input file, the newparam can be baked into the referencing element
    #   or preserved in <effect><newparam> and <effect><profile_COMMON><newparam>
    # Only works for newparam/param pair of type float, float2, float3, float4
    # Will also work for inverse baking (moving baked value into newparam/param)
    def NewparamCheck(self, context, originalLocation, bakedLocation, newparamLocations):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        testPChecker = PresChecker(testIO.GetRoot(self.__inputFileName), testIO.GetRoot(self.__outputFileNameList[0]) )

        # get input tags
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), originalLocation)
        
        # check the original input file for the existence of the element first
        if (len(inputElementList) == 0):
            context.Log("FAILED: Element is not found in the input file.")
            self.__preservationResults = False
            self.__result = False
            testIO.Delink()
            return self.__preservationResults
        
        dataToCheckList = inputElementList[0].childNodes[0].nodeValue.split()
        
        # check the baked location for existence of data
        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), bakedLocation)
        baked = False
        for index in range( len(outputElementList) ):
            outputDataList = outputElementList[index].childNodes[0].nodeValue.split()
            if ( len(outputDataList) > 0 and len(outputDataList) == len(dataToCheckList) ):
                baked = True
                for i in range( len(outputDataList) ):
                    if ( not IsValueEqual( float(outputDataList[i]), float(dataToCheckList[i]), 'float') ):
                        baked = False
                        break
            else:
                baked = False
            
            if (baked):
                break

        # if value is not baked, check for the existence of the value in a newparam
        if (not baked):
            foundInNewparam = False
            newparamSID = None
            for eachLocation in newparamLocations:
                outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), eachLocation)

                foundInNewparam = False
                for index in range( len(outputElementList) ):
                    outputDataList = outputElementList[index].childNodes[0].nodeValue.split()
                    if ( len(outputDataList) > 0 and len(outputDataList) == len(dataToCheckList) ):
                        foundInNewparam = True
                        for i in range( len(outputDataList) ):
                            if ( not IsValueEqual( float(outputDataList[i]), float(dataToCheckList[i]), 'float') ):
                                foundInNewparam = False
                                break
                    else:
                        foundInNewparam = False
                    
                    # newparam was found, so now get its sid
                    if (foundInNewparam):
                        newparam = outputElementList[index].parentNode
                        newparamSID = GetAttriByEle(newparam, 'sid')
#                        print "newparam sid: " + newparamSID
                        break

                if (foundInNewparam):
                    break
        
            # match was found in newparam, so now check that the correct param references it
            foundParam = False
            if (foundInNewparam and newparamSID != None):
                paramLocation = bakedLocation
                paramLocation[len(paramLocation)-1] = 'param'
            
                outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), paramLocation)
                for eachParam in outputElementList:
                    paramRef = GetAttriByEle(eachParam, 'ref')
                    if (paramRef == newparamSID):
                         foundParam = True
                         break
        
        if (baked):
            context.Log("PASSED: "+ originalLocation[len(originalLocation)-1] +" data is baked into the referencing element.")
            self.__preservationResults = True
        elif (foundInNewparam and foundParam):
            context.Log("PASSED: "+ originalLocation[len(originalLocation)-1] +" data is found in newparam/param.")
            self.__preservationResults = True
        else:
            context.Log("FAILED: "+ originalLocation[len(originalLocation)-1] +" data is not baked or found in newparam/param.")
            self.__preservationResults = False
            self.__result = False
                
        testIO.Delink()
        return self.__preservationResults
        
################## Preservation checking (elements order not required to be equal) ##################

    # Helper function to compare the attributes between two elements.
    # inputElement: the first element
    # outputElement: second element to compare with inputElement
    def CompareAttributes(self, inputElement, outputElement):
        inputAttributes = inputElement.attributes
        outputAttributes = outputElement.attributes
        
        if (inputAttributes.length != outputAttributes.length):
            return False
         
        for attrName in inputAttributes.keys():
            if (inputElement.getAttribute(attrName) != outputElement.getAttribute(attrName)):
                return False
            
        return True
        
    # Helper function to compare the data between two elements.
    # inputElement: the first element
    # outputElement: second element to compare with inputElement
    def CompareData(self, inputElement, outputElement):
        inputData = inputElement.childNodes[0].nodeValue
        outputData = outputElement.childNodes[0].nodeValue
        
        if (inputData != outputData):
            return False
            
        return True

    # Helper function that recursively checks the preservation of elements, attributes, and data.
    # inputElement: the current element to check in the input file.
    # outputElement: the current element to check in the output file.
    def CheckPreservation(self, context, inputElement, outputElement, ordered):
    
        # Compare attributes
        if (self.CompareAttributes(inputElement, outputElement) == False):
            context.Log("FAILED: attributes do not match for <" + inputElement.nodeName + ">.")
            return False
        else:
            print "attributes match"
    
        # If there is 1 child and it is of type TEXT_NODE, then the element contains data only
        if ( len(inputElement.childNodes) == 1 and inputElement.childNodes[0].nodeType == inputElement.TEXT_NODE):
            if ( len(outputElement.childNodes) == 1 and outputElement.childNodes[0].nodeType == outputElement.TEXT_NODE):
                if (not self.CompareData(inputElement, outputElement)):
                    context.Log("FAILED: Data do not match for <" + inputElement.nodeName + ">.")
                    return False
                else:
                    print "data of " + inputElement.nodeName + " match."
            else:
                context.Log("FAILED: Data do not match for <" + inputElement.nodeName + ">.")
                return False
               
        if ( len(inputElement.childNodes) != len(outputElement.childNodes) ):
            context.Log("FAILED: Number of child elements not equal for <" + inputElement.nodeName + ">.")
            return False
        
        for inputChild in inputElement.childNodes:
            if (inputChild.nodeType == inputChild.ELEMENT_NODE):
                print "node type is element, named: " + inputChild.nodeName
                
                found = False
                for outputChild in outputElement.childNodes:
                    if (outputChild.nodeName == inputChild.nodeName):
                        print "found child: " + outputChild.nodeName
                        found = True
                        if (self.CheckPreservation(context, inputChild, outputChild, ordered) == False):
                            return False
                        else:
                            break
                
                if (not found):
                    context.Log("FAILED: <" + inputChild.nodeName + "> not found.")
                    return False
                    
        return True
            
    # Checks that all elements, attributes, and data are preserved between input and
    # files. Used for extra preservation.
    # taglist: the path to the beginning of the preservation check.
    # identifier: attribute that identifies the element to check in case there are multiple
    #    elements in the same tagList path.
    def FullPreservation(self, context, tagList, identifier, ordered="False"):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
                
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        preserved = True
        
        inputElementList = FindElement(testIO.GetRoot(self.__inputFileName), tagList)
        outputElementList = FindElement(testIO.GetRoot(self.__outputFileNameList[0]), tagList)
        if ( len(inputElementList) == 0 ):
            context.Log("FAILED: Unable to find <"+ tagList[len(tagList)-1] +"> in input.")
            preserved = False
        elif ( len(outputElementList) == 0 ):
            context.Log("FAILED: Unable to find <"+ tagList[len(tagList)-1] +"> in output.")
            preserved = False
              
        if (preserved == True):
            for eachInputElement in inputElementList:
                profileName = eachInputElement.getAttribute(identifier)
                found = False
                for eachOutputElement in outputElementList:
                    if (eachOutputElement.getAttribute(identifier) == profileName):
                        found = True
                        if (self.CheckPreservation(context, eachInputElement, eachOutputElement, ordered) == False):
                            preserved = False
                        
                        break
            
                if (not found):
                    context.Log("FAILED: <" + eachInputElement.nodeName + "> with " + identifier + "=\"" + profileName + "\" not found.")
                    preserved = False
                    
                if (not preserved):
                    break
        
        if (preserved):
            context.Log("PASSED: Extra information is preserved.")
            self.__preservationResults = True
        else:
            self.__preservationResults = False
            self.__result = False
            
        testIO.Delink()
        return self.__preservationResults

################## Transform stack preservation ##################

    # Checks for complete preservation of the transform stack.
    # nodeIdLst: list of nodes to check
    def TransformStackPreserved(self, context, nodeIdLst):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
        
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()

        # Find matrix stack from the node list, the id should be preserved
        for eachNode in nodeIdLst:
            rootOut = testIO.GetRoot( self.__outputFileNameList[0] )
            rootIn = testIO.GetRoot( self.__inputFileName )
            
            # input nodes with transformation for testing
            nodeOutContTrs = GetElementByID(rootOut, eachNode)
            nodeInContTrs = GetElementByID(rootIn, eachNode)
            
            if (nodeOutContTrs == None or nodeInContTrs == None):
                testIO.Delink()
                context.Log("FAILED: Node '" + eachNode + "' in input or output does not exist.")
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
            
            # get transformation from it
            trsOutList = GetTransformationsOfNode(nodeOutContTrs)
            trsInList = GetTransformationsOfNode(nodeInContTrs)
            
            # compare transform stack count
            if len( trsOutList ) != len( trsInList ):
                testIO.Delink()
                context.Log("FAILED: Number of transforms in node '" + eachNode + "' are not equal.")
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
            
            for index in range(0, len(trsOutList)):
                # Compare transform element name
                if (trsInList[index].nodeName != trsOutList[index].nodeName):
                    context.Log("FAILED: " + trsInList[index].nodeName + " not equal to " + trsOutList[index].nodeName + ".")
                    return False            
            
                # Check for attribute preservation
                if (self.CompareAttributes(trsInList[index], trsOutList[index]) == False):
                    context.Log("FAILED: attributes do not match for <" + trsInList[index].nodeName + ">.")
                    return False

                outputDataList = trsOutList[index].childNodes[0].nodeValue.split()
                inputDataList = trsInList[index].childNodes[0].nodeValue.split()
                
                if ( len(outputDataList) != len(inputDataList) ):
                    testIO.Delink()
                    context.Log("FAILED: Transform stacks of node '" + eachNode + "' are not equal.")
                    self.__preservationResults = False
                    self.__result = False
                    return self.__preservationResults
                    
                for i in range(0, len(outputDataList) ):
                    if ( not IsValueEqual(float(outputDataList[i]), float(inputDataList[i]), 'float') ):
                        testIO.Delink()
                        context.Log("FAILED: Transform stacks of node '" + eachNode + "' are not equal.")
                        self.__preservationResults = False
                        self.__result = False
                        return self.__preservationResults

            context.Log("PASSED: Transform stacks of node '" + eachNode + "' are preserved.")

        testIO.Delink()
        self.__preservationResults = True
        return self.__preservationResults

################## Complete element preservation (including ordering and exact data) ##################


    # Get number of element child nodes filtering an ignore list
    # element: the element to check for child nodes
    # ignoreList: list of node names to ignore
    def GetElementChildNodes(self, element, ignoreList):
        childElementList = []
        for eachChild in element.childNodes:
            if (eachChild.nodeName not in ignoreList):
                if (eachChild.nodeType == eachChild.ELEMENT_NODE):
                    childElementList.append(eachChild)
        
        return childElementList

    # Helper function that recursively checks the preservation of elements, attributes, and data.
    # inputElement: the current element to check in the input file.
    # outputElement: the current element to check in the output file.
    def CheckPreservationHelper(self, context, inputElement, outputElement, ignoreList):
    
        print inputElement.nodeName + " : " + outputElement.nodeName
        
        # Compare attributes
        if (self.CompareAttributes(inputElement, outputElement) == False):
            context.Log("FAILED: attributes do not match for <" + inputElement.nodeName + ">.")
            return False
        else:
            print "attributes match"
        
        # If there is 1 child and it is of type TEXT_NODE, then the element contains data only
        if ( len(inputElement.childNodes) == 1 and inputElement.childNodes[0].nodeType == inputElement.TEXT_NODE):
            if ( len(outputElement.childNodes) == 1 and outputElement.childNodes[0].nodeType == outputElement.TEXT_NODE):
                if (not self.CompareData(inputElement, outputElement)):
                    context.Log("FAILED: Data do not match for <" + inputElement.nodeName + ">.")
                    return False
                else:
                    print "data of " + inputElement.nodeName + " match."
            else:
                context.Log("FAILED: Data do not match for <" + inputElement.nodeName + ">.")
                return False

        inputChildElementList = self.GetElementChildNodes(inputElement, ignoreList)
        outputChildElementList = self.GetElementChildNodes(outputElement, ignoreList)

        inputNumbOfChildElements = len(inputChildElementList)
        outputNumbOfChildElements = len(outputChildElementList)
        
        if (inputNumbOfChildElements != outputNumbOfChildElements):
            context.Log("FAILED: Number of child elements not equal for " + inputElement.nodeName + ".")
            return False
        
        for index in range(0, inputNumbOfChildElements):
            inputChild = inputChildElementList[index]
            outputChild = outputChildElementList[index]
        
            if (inputChild.nodeType == inputChild.ELEMENT_NODE and outputChild.nodeType == outputChild.ELEMENT_NODE ):
                if (inputChild.nodeName == outputChild.nodeName):
                    print "node type is element, named: " + inputChild.nodeName
                    if ( self.CheckPreservationHelper(context, inputChild, outputChild, ignoreList) == False ):
                        return False
                else:
                    print "failed. " + inputChild.nodeName + " : " + outputChild.nodeName
                    return False
        
        return True

    # Checks that all elements, attributes, and data are preserved between input and
    # files. Used for extra preservation.
    # taglist: the path to the beginning of the preservation check.
    # identifier: attribute that identifies the element to check in case there are multiple
    #    elements in the same tagList path.
    def CompletePreservation(self, context, nodeType, nodeId, ignoreList):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults
                
        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
        
        preserved = True
        
        inputElement = GetElementByID(testIO.GetRoot(self.__inputFileName), nodeId)
        outputElement = GetElementByID(testIO.GetRoot(self.__outputFileNameList[0]), nodeId)
        
        if ( inputElement == None ):
            context.Log("FAILED: Unable to find " + nodeType + " with id '" + nodeId + "' in input.")
            preserved = False
        elif ( outputElement == None ):
            context.Log("FAILED: Unable to find " + nodeType + " with id '" + nodeId + "' in output.")
            preserved = False
        elif ( inputElement.nodeName != outputElement.nodeName ):
            context.Log("FAILED: Node type with id " + nodeId + " do not match.")
            preserved = False
        
        if (preserved == True):
            preserved = self.CheckPreservationHelper(context, inputElement, outputElement, ignoreList)
        
        if (preserved):
            context.Log("PASSED: " + nodeType + " with id '" + nodeId + "' is completely preserved.")
            self.__preservationResults = True
        else:
            self.__preservationResults = False
            self.__result = False
            
        testIO.Delink()
        return self.__preservationResults
        
################## instance element checking ##################

    def _GetInstanceCount(self, daeElement, tagName, attrName=None, attrVal=None):

        # get the count in visual scene of input file
        elementList = daeElement.getElementsByTagName(tagName)
        count = len(elementList)

        if (attrName != None and attrVal != None):
            count = 0
            for eachNode in elementList:
                attributeVal = GetAttriByEle( eachNode, attrName)
                if (attrName == "url" or attrName == "source" or attrName == "target"):
                    attributeVal = attributeVal[1:len( attributeVal )]

	        if (attributeVal == attrVal):
	            count = count + 1	    

	print "count of " + tagName + ": " + str(count)
	return count
    
    # Compares the count of an element in the path specified by a tag list path. If both 
    # attrName and attrVal are not None, the count will only include those elements with
    # that attribute and value.
    # tagList: the path to the element
    # tagName: the element name
    # attrName: the attribute name
    # attrVal: the attribute value
    def CompareElementCount(self, context, tagList, tagName, attrName=None, attrVal=None):
        if ( len(self.__inputFileName) == 0 or len(self.__outputFileNameList) == 0 ):
            if (self.SetInputOutputFiles(context) == False):
                self.__preservationResults = False
                self.__result = False
                return self.__preservationResults

        testIO = DOMParserIO( self.__inputFileName, self.__outputFileNameList )
        # load files and generate root
        testIO.Init()
      
        inputRoot = testIO.GetRoot(self.__inputFileName)
        outputRoot = testIO.GetRoot(self.__outputFileNameList[0])

        # get the count of the element in the input file
        inputElementList = GetElementsByTags(inputRoot, tagList)
        if ( len(inputElementList) > 0 ):
            inputCount = self._GetInstanceCount(inputElementList[0], tagName, attrName, attrVal)
        else:
            inputCount = 0
        
        # get the count of the element in the output file
        outputElementList = GetElementsByTags(outputRoot, tagList)
        if ( len(outputElementList) > 0 ):
            outputCount = self._GetInstanceCount(outputElementList[0], tagName, attrName, attrVal)
        else:
            outputCount = 0
        
        print "input count: " + str(inputCount)
        print "output count of " + tagName + ": " + str(outputCount)
               
        if (outputCount == inputCount):
            if (attrName == None):
                context.Log("PASSED: Number of " + tagName + " are preserved.")
            else:
                context.Log("PASSED: Number of " + tagName + " with " + attrName + "=" + attrVal + " are preserved.")
            
            self.__preservationResults = True
        else:
            if (attrName == None):
                context.Log("FAILED: Number of " + tagName + " are not preserved.")
            else:
                context.Log("FAILED: Number of " + tagName + " with " + attrName + "=" + attrVal + " are not preserved.")

            self.__preservationResults = False
            self.__result = False
            
        testIO.Delink()
        return self.__preservationResults