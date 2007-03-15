#include "main.h"
#include "hybrid.h"

int main(int argc, const char* argv[])
{
	const char* srcName;
	const char* dstName;
	size_t srcLength;
	size_t dstLength;
	FILE* src;
	FILE* dst;

	if (argc < 3) return CT_INVALID_SCORE;

	channelInfo.rDepth = 8;
	channelInfo.gDepth = 8;
	channelInfo.bDepth = 8;
	channelInfo.aDepth = 8;
	channelInfo.lDepth = 0; // don't care... force to use RGBA

	srcName = argv[1];
	dstName = argv[2];

	// if both filenames end with .tga, feed in as tga
	srcLength = strlen(srcName);
	dstLength = strlen(dstName);
	if ((srcLength > 4) && (dstLength > 4) &&
			((srcName[srcLength-1] == 'a') || (srcName[srcLength-1] == 'A')) &&
			((srcName[srcLength-2] == 'g') || (srcName[srcLength-2] == 'g')) &&
			((srcName[srcLength-3] == 't') || (srcName[srcLength-3] == 't')) &&
			(srcName[srcLength-4] == '.') && (dstName[dstLength-4] == '.') &&
			((dstName[dstLength-1] == 'a') || (dstName[dstLength-1] == 'A')) &&
			((dstName[dstLength-2] == 'g') || (dstName[dstLength-2] == 'g')) &&
			((dstName[dstLength-3] == 't') || (dstName[dstLength-3] == 't')))
	{
		fopen_s(&src, srcName, "rt");
		fopen_s(&dst, dstName, "rt");
		if ((src == NULL) || (dst == NULL)) return CT_INVALID_SCORE;
		
		return (int)PyramidDiff_NOLSBFIX_by_HYBRID(src, dst, TGA);
	}

	// not both files end with .tga, so feed it as png
	fopen_s(&src, srcName, "rb");
	fopen_s(&dst, dstName, "rb");
	if ((src == NULL) || (dst == NULL)) return CT_INVALID_SCORE;

	return (int)PyramidDiff_NOLSBFIX_by_HYBRID(src, dst, PNG);
}
