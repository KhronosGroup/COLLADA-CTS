# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FImageType:
    
    # Enumerated type is shared with FImageRenderArea and FCompareSetupDialog.
    #
    IMAGE = 1
    EXECUTION = 2
    LOG = 3
    ANIMATION = 4
    VALIDATION = 5 # You cannot compare that one, but it is necessary for FImageRenderArea.

