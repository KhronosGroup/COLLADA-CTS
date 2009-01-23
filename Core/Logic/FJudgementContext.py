# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import Core.Common.FGlobals as FGlobals

from Core.Logic.FResult import *

class FJudgementContext:
    """ This context interfaces the test procedure and the verification
        modules with the judging/post-processing scripts.

        Its purpose is to give the judging scripts the necessary
        information and functions to do custom verification.
    """

    def __init__(self, testProcedure, testId):
        self.__testProcedure = testProcedure
        self.__testId = testId
        self.__log = ""
        
        # Pre-cache some common references.
        self.__currentTest = testProcedure.GetTest(self.__testId)
        self.__currentExecution = self.__currentTest.GetCurrentExecution()
        
        # Create the tokens for some run-time caches
        self.__renderSteps = None
        
    def GetCurrentTestId(self):
        """ Retrieves the identifier of the test case that is currently
            being judged.
            @return The identifier of the current test case. """
        return self.__testId
        
    def GetInputFilename(self, testId=None):
        """ Retrieves the filename of the input COLLADA document
            for a test case.
            @param testId Optional parameter used to identify which
                test input filename to retrieve. If this parameter is not
                provided, the input filename for the current test case
                is returned.
            @return The input filename for the test case document. """
        
        test = self.__GetTest(testId)
        if test == None: return ""
        else: return test.GetFilename()
    
    def GetAbsInputFilename(self, testId=None):
        test = self.__GetTest(testId)
        if test == None: return ""
        else: return test.GetAbsFilename()
    
    def FindTestId(self, substring0, substring1=None, substring2=None):
        """ Retrieves the identifier for the first test case that contains
            the given substrings in its separated filename.
            This operation is COSTLY. CACHE THE RESULT if you need it
            in more than one badge level.
            If more than one test cases contains the given substrings, only
            the first one in no determinate order, is returned.            
            @param substring0 A first substring to match. This parameter
                is necesssary.
            @param substring1 An optional second substring to match.
            @param substring2 An optional third substring to match.
            @return The test identifier for a test case matching the given
                substrings. """
        
        # Look against the whole test procedure for the first substring.
        step1 = []
        for test in self.__testProcedure.GetTestGenerator():
            if (test.GetFilename().find(substring0) != -1):
                step1.append(test)
                
        # Check for the second substring.
        if (substring1 != None):
            step2 = []
            for test in step1:
                if (test.GetFilename().find(substring1) != -1):
                    step2.append(test)
        else: step2 = tests

        # Check for the third substring.
        if (substring2 != None):
            step3 = []
            for test in step2:
                if (test.GetFilename().find(substring2) != -1):
                    step3.append(test)
        else: step3 = step2
                    
        # Return any left-over test's identifier.
        if (len(step3) > 0): return step3[0].GetTestId()
        else: return None
        
        
    def Log(self, message):
        """ Appends a new line to the log.
            This log will be displayed to the user within the UI.
            @param message The message to display to the user. """
        self.__log += message + "\n"

    def CompareImages(self, filename1, filename2):
        """ Compares the two images referenced by their filenames.
            This function uses the default comparator.
            @param filename1 The filename of the first image.
            @param filename2 The filename of the second image.
            @return An integer indicating how close the two images are. """
        compareResult = FGlobals.imageComparator.CompareImages(filename1, filename2)
        return compareResult.GetExtra()
        
    def GetStepResults(self, filterType=None, testId=None):
        """ This function retrieves the standard steps results.
            @param filterType A string used to filter the steps to retrieve.
                Example: "Render", "Validation", "Import" or "Export"
            @param testId Optional parameter used to retrieve the standard
                steps results for another test case. If this parameter
                is not provided, the list of filenames for the current
                test case is returned.
            @return An indexed list of booleans containing the
                standard steps results. """
        out = []
        execution = self.__GetExecution(testId)
        if (execution == None): return out
        result = execution.GetResult()
        if (filterType == None):
            for index, output in result.GetOutputGenerator():
                if (output >= FResult.PASSED_IMAGE and output <= FResult.PASSED_VALIDATION):
                    out.append(True)
                elif (output >= FResult.IGNORED_TYPE and output <= FResult.IGNORED_NONE):
                    out.append(True)
                else: out.append(False)
        else:
            for index, application, type, settings in self.__testProcedure.GetStepGenerator():
                if (type == filterType):
                    output = result.GetOutput(index)
                    if (output >= FResult.PASSED_IMAGE and output <= FResult.PASSED_VALIDATION):
                        out.append(True)
                    elif (output >= FResult.IGNORED_TYPE and output <= FResult.IGNORED_NONE):
                        out.append(True)
                    else: out.append(False)
        return out
    
    def GetStepImageFilenames(self, testId=None):
        """ This function retrieves the list of filename for the images
            generated by the standard steps of a given test case.
            @param testId Optional parameter used to retrieve the list of
                image filenames for another test case. If this parameter
                is not provided, the list of filenames for the current
                test case is returned.
            @return An indexed list containing the image filenames. """
            
        execution = self.__GetExecution(testId)
        if (execution == None): return []

        # Do not use the "Render" filter for the standard steps
        # mainly because the Feeling Viewer does its work during "Import".
        if (self.__renderSteps == None):
            self.__renderSteps = []
            result = execution.GetResult()
            for index, output in result.GetOutputGenerator():
                if (output == FResult.PASSED_IMAGE or
                        output == FResult.PASSED_ANIMATION or
                        output == FResult.FAILED_IMAGE or
                        output == FResult.FAILED_ANIMATION or
                        output == FResult.IGNORED_NO_BLESS_IMAGE or
                        output == FResult.IGNORED_NO_BLESS_ANIMATION):
                    self.__renderSteps.append(index)
        
        out = []
        for index in self.__renderSteps:
            location = execution.GetOutputLocation(index)
            out.append(location[0])
        return out
    
    def GetStepOutputFilenames(self, filterType=None, testId=None):
        """ This function retrieves the list of output filenames.
            This list can be filtered by one of the step types: "Export",
            "Import", "Render" or "Validate". Note that if you are interested
            in all the image files, you should use GetStepImageFilenames.
            
            @param filterType A string used to filter the steps to retrieve.
                Example: "Render", "Validation", "Import" or "Export"
            @param testId Optional parameter used to retrieve the list of
                output filenames for another test case. If this parameter
                is not provided, the list of output filenames for the current
                test case is returned.
            @return An indexed list containing the output filenames. """
            
        out = []
        
        execution = self.__GetExecution(testId)
        if (execution != None):
            for index, application, type, settings in self.__testProcedure.GetStepGenerator():
                if (filterType == None or type == filterType):
                    location = execution.GetOutputLocation(index)
                    out.append(location[0])
        return out
        
    def HasStepCrashed(self, testId=None):
        """ This function retrieves whether any of the standard steps
            of the given test case resulted in a crash.
            All judging scripts should include this function call for the
            current test case.
            @param testId Optional parameter used to retrieve the standard
                steps results. If this parameter is not provided, the
                standard steps results for the current test case are
                verified for crashes.
            @return A boolean indicating whether a crash has occured. """
        execution = self.__GetExecution(testId)
        if (execution == None): return False # Should this be changed to True? To force a failure?
        result = execution.GetResult()
        for index, output in result.GetOutputGenerator():
            if output == FResult.CRASH: return True
        return False
        
    def DoesStepsExists(self, stepTypes):
        """ This function verifies that at least one step exists for
            each given step type. This function checks on a global level
            and does not verify any execution results.
            @param stepTypes A list of step types.
                Examples: [ "Import", "Render" ].
            @return A boolean indicating whether all the requested step types
                exists in the test procedure. """

        if (len(stepTypes) == 0): return False
            
        # This list is used to keep track of whether steps exist for the wanted types.
        existence = []
        for type in stepTypes:
            existence.append(False)
        
        # Compare the test procedure against the requested step type list.
        for index, application, type, settings in self.__testProcedure.GetStepGenerator():
            for i in range(len(stepTypes)):
                if (not existence[i]) and (type == stepTypes[i]):
                    existence[i] = True
        
        # Compile the results
        exists = True
        for e in existence: exists = exists and e
        return exists
        
    def HaveStepsPassed(self, stepTypes, testId=None):
        """ This function verifies that all at least one step exists for
            each given step type and that for a given execution, the result
            for all the steps of a given list of types are positive.
            @param stepTypes A list of step types.
                Examples: [ "Import", "Render" ].
            @param testId Optional parameters used to retrieve the given step
                results. If no test id is provided, the current execution results
                are used.
            @return A boolean indicating whether all the requested step types
                exists and have positive results. """

        if (len(stepTypes) == 0): return False
        
        # Retrieve the wanted execution and its results.
        execution = self.__GetExecution(testId)
        if (execution == None): return False
        result = execution.GetResult()

        # This list is used to keep track of whether steps exist for the wanted types.
        existence = []
        for type in stepTypes: existence.append(False)
        
        # Compare the test procedure against the requested step type list.
        # We keep track of the passed results by implication:
        #   if one fails, the function returns False right away.
        for index, application, type, settings in self.__testProcedure.GetStepGenerator():
            for i in range(len(stepTypes)):
                if type == stepTypes[i]:
                    existence[i] = True                    

                    # Check the execution results for this step.
                    output = result.GetOutput(index)
                    if (output >= FResult.PASSED_IMAGE and output <= FResult.PASSED_VALIDATION):
                        pass # Cummulative True.
                    elif (output >= FResult.IGNORED_TYPE and output <= FResult.IGNORED_NONE):
                        pass # Cummulative True.
                    else: return False
        
        # Compile the existence results.
        exists = True
        for e in existence: exists = exists and e
        return exists

    def GetLog(self):
        """ This function is considered INTERNAL.
            It is called by the execution to retrieve the judging log after the
            judging function has been called. """
        return self.__log
            
    def ResetLog(self):
        """ This function is considered INTERNAL.
            It is called by the execution to erase the log after retrieving it.
            This is useful to avoid re-creating the context between judgements. """
        self.__log = ""
        
    def __GetTest(self, testId):
        """ This function is considered PRIVATE.
            Use this function to correctly support null test identifiers. """
        if (testId == None):
            return self.__currentTest
        else:
            return self.__testProcedure.GetTest(testId)

    def __GetExecution(self, testId):
        """ This function is considered PRIVATE.
            Use this function to correctly support null test identifiers. """
        if (testId == None):
            return self.__currentExecution
        else:
            test = self.__testProcedure.GetTest(testId)
            if not test.HasCurrentExecution():
                return None
            return test.GetCurrentExecution()
