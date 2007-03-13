#include "hybrid.h"

int main(int argc, const char* argv[])
{
	const char* srcName;
	const char* dstName;
	FILE* src;
	FILE* dst;

	if (argc < 3) return 0;

	srcName = argv[1];
	dstName = argv[2];
	fopen_s(&src, srcName, "rt");
	fopen_s(&dst, dstName, "rt");

	return (int)PyramidDiff_NOLSBFIX_by_HYBRID(src, dst);
}
