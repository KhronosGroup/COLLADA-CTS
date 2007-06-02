# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# The judging 'context' currently includes:
# [WARNING] this structure is subject to changes.
#
# - 'log': string used by this script to give output information to users.
# - 'testId': the unique identifier for this test in the 'testProcedure'.
# - 'testProcedure': the global test procedure object.
#                    See FTestProcedure for more information.

class LocalJudgingObject:
    def __init__(self):
        # Might be we pass in the "context" straight here as well and cache
        # the test passing.
        self.__temp = False
        
    def JudgeBasic(self, context):
        # This is where you can test XML or force the comparison of image files
        # or any custom verification you want to do...
        context['log'] += "Judging as basic.."
        return True
    
    # Since this is a basic badge test, the intermediate and advanced
    # badges should be enabled, but simply execute the basic test function.
    def JudgeIntermediate(self, context):
        context['log'] += "Judging as intermediate.."
        return False # self.JudgeBasic(self, context)

    def JudgeAdvanced(self, context):
        context['log'] += "Judging as advanced.."
        return self.JudgeIntermediate(context)
       
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = LocalJudgingObject();
