// Copyright (c) 2012 The Khronos Group Inc.
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
// the following conditions: 
// The above copyright notice and this permission notice shall be included 
// in all copies or substantial portions of the Materials. 
// THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

#include "HierarchyPreservationChecking.h"

// #define TESTING
// for node_translate_x_cube*.dae, result should be "different".
// for multiModel_01_stressTest_00*.dae, result should be "same".

int main(int argc, char* argv[])
{
	if (argc < NUM_COMMAND_LINE_PARAMETERS)
	{
		printf("Usage : HierarchyPreservationChecking.exe file1.dae file2.dae\n");
		exit(0);
	}

	DAE *dae;
	dae = new DAE;

	daeDocument *pDocuments[NUM_COMMAND_LINE_PARAMETERS - 1];
	domCOLLADA *root[NUM_COMMAND_LINE_PARAMETERS - 1];
	domCOLLADA::domScene *scene[NUM_COMMAND_LINE_PARAMETERS - 1];
	domVisual_scene *visualScene[NUM_COMMAND_LINE_PARAMETERS - 1];
	

	// loading files to DAE containers
	for (int i = 0;i < NUM_COMMAND_LINE_PARAMETERS - 1;i++)
	{
		root[i] = dae->open(argv[i + PARAMETER_OFFSET]);
		
		if (root[i] == NULL)
		{
			printf("DOM Load error at = %d\n", i);
			printf("Filename = %s\n", argv[i]);

			// clear memory if needed:
			delete dae;
	
			// report error code:
			return -1;
		}

		// visual scene library for each 
		scene[i] = root[i]->getScene();

		// Get visual scene
		visualScene[i] = daeSafeCast <domVisual_scene> ( scene[i]->getInstance_visual_scene()->getUrl().getElement() );

		// Check visual scene
		if (visualScene[i] == NULL)
		{
			printf("Error: Visual Scene loading error at = %d\n", i);
			printf("Filename = %s\n", argv[i]);
			
			// clear memory if needed:
			delete dae;
	
			// report error code:
			return -1;
		}

		// check documents
		pDocuments[i] = dae->getDoc(argv[i + PARAMETER_OFFSET]);

		if (pDocuments[i] == NULL)
		{
			printf("Documents Load error at = %d\n", i);
			printf("Filename = %s\n", argv[i]);

			// clear memory if needed:
			delete dae;
	
			// report error code:
			return -1;
		}
	}

	NodeHPChecker * pNChecker = new NodeHPChecker(pDocuments[0], pDocuments[1], visualScene[0], visualScene[1]);
	
	if (pNChecker->IsPreserved())
	{
#ifdef TESTING
		printf("They are the same.\n");
#endif
		return 1;
	}
	else
	{
#ifdef TESTING
		printf("They are not the same.\n");
#endif

		return 0;
	}
}