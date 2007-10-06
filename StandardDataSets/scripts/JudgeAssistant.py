# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.

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
        @param defaultLogText Whether the default log strings should be output.
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
        equivalent to the images generated for another test case.
        @param context The judgement context.
        @param substring0 A first substring to match. This parameter is necesssary.
        @param substring1 An optional second substring to match.
        @param substring2 An optional third substring to match.
        @param maxDifference The maximum difference allowed between the images of the two tests.
        @param defaultLogText Whether the default log strings should be output.
        @return Whether the images generated of this test case are
            equivalent to the images of the other test case. """
    def CompareImagesAgainst(self, context, testCaseId0, testCaseId1=None, testCaseId2=None, maxDifference = 5, defaultLogText = True):
        
        # Look for a buffered result set.
        result = None
        tokenList = [testCaseId0, testCaseId1, testCaseId2]
        tokenListString = self.TokenListString(tokenList)
        for resultSet in self.__compareImagesResults:
            if resultSet[0] == tokenList:
                result = resultSet
                break

        if result == None:
            result = [tokenList]

            # Look for the other test case.
            otherTestId = context.FindTestId(testCaseId0, testCaseId1, testCaseId2)
            result.append(otherTestId != None)

            # Retrieve the image filenames for this test case.
            imageFilenames = context.GetStepImageFilenames()
            imageFilenameCount = len(imageFilenames)
            result.append(imageFilenameCount > 0)

            if result[1] and result[2]:
                # Retrieve the image filenames for the other test case.
                otherFilenames = context.GetStepImageFilenames(otherTestId)
                otherFilenameCount = len(otherFilenames)
                result.append(otherFilenameCount > 0)
                
                if result[3]:
                    # Compare the images by index.
                    count = min(imageFilenameCount, otherFilenameCount)
                    for i in range(count):
                        result.append(context.CompareImages(imageFilenames[i], otherFilenames[i]))

            # Cache these results.
            self.__compareImagesResults.append(result)
                
        # Log the results.
        if defaultLogText:
            if not result[1]:
                context.Log("FAILED: You must also run the '" + tokenListString + "' test case.")
            if not result[2]:
                context.Log("FAILED: This test must include a 'Render' step.")
            if len(result) > 4 and not result[3]:
                context.Log("FAILED: The '" + tokenListString + "' must include a 'Render' step.")
            for i in range(len(result) - 4):
                if (len(result) == 5): identifier = "Output"
                else: identifier = "Output #%i" % i + 1
                if result[4+i] > maxDifference:
                    context.Log("FAILED: " + identifier + " doesn't match the '" + tokenListString + "' test. Result: %i" % result[4+i])
                else:
                    context.Log("PASSED: " + identifier + " matches the '" + tokenListString + "' test. Result: %i" % result[4+i])

        # Compile the results.
        localResult = True
        if not result[1] or not result[2]: localResult = False
        elif not result[3]: localResult = False
        else:
            for i in range(len(result) - 4):
                if result[4+i] > maxDifference: localResult = False
        if not localResult: self.__result = False
        return localResult
            
    """ [INTERNAL] Generates a nice string with the given list tokens.
        @param tokens A list of tokens.
        @return A string containing the list of tokens in a nice form. """
    def TokenListString(self, tokens):
        
        # Remove all bad tokens first.
        badTokens = []
        for i in range(len(tokens)):
            if tokens[i] == None or tokens[i] == "": badTokens.append(i)
        if len(badTokens) > 0:
            tokens = tokens[0:-1]
            badTokens.reverse()
            for i in badTokens:
                del tokens[i:i]

        # Generate the nice string.
        output = ""
        count = len(tokens)
        for i in range(count):
            token = tokens[i]
            if i == 0: output += token.title()
            elif i < count - 1: output += ", " + token.lower()
            else: output += " and " + token.lower()
        return output
