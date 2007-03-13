#ifndef __HYBRID_H__
#define __HYBRID_H__
/*------------------------------------------------------------------------
 *
 * Hybrid utilities
 * -----------------
 *
 * (C) 2006 Hybrid Graphics, Ltd.
 * All Rights Reserved.
 *
 * This file consists of unpublished, proprietary source code of
 * Hybrid Graphics, and is considered Confidential Information for
 * purposes of non-disclosure agreement. This file is released to
 * Khronos Group as supporting material for the development of OpenVG
 * conformance tests. Permission is granted for Khronos Group and
 * OpenVG contributors to use, compile, run and modify this file for
 * the sole purpose of finalizing the OpenVG conformance tests. Any
 * other use, including inclusion of this material in the final OpenVG
 * conformance tests, will require a separate licensing agreement
 * between Hybrid Graphics and Khronos Group. Distribution or use for
 * other purposes is expressly forbidden. Please contact
 * licensing@hybrid.fi for further information.
 *
 *
 *//*-------------------------------------------------------------------*/

/*-------------------------------------------------------------------------
 * File type enumeration.
 * If you want to add your own file types, add an enumeration value and
 * a internal function to extract the info from the desired file type.
 *-----------------------------------------------------------------------*/

#include <stdio.h>

extern float	PyramidDiff_by_HYBRID(FILE* srcFile, FILE* refFile);
extern float	PyramidDiff_NOLSBFIX_by_HYBRID(FILE* srcFile, FILE* refFile);
extern int		RegionComparison_by_NVIDIA(FILE* srcFile, FILE* refFile);
extern int		H10317Comparison_by_NVIDIA(FILE* srcFile, FILE* refFile);
extern int      BoundaryTest_by_ATI(FILE *AnsTGA, float radius, float limit);

extern float	CompareTGAInfo_by_HUONE(FILE *AnsTGA, FILE *RefTGA);
extern float	CompareTGAInfo_with_epsilon_by_HUONE(FILE *AnsTGA, FILE *RefTGA, const float e);
extern int		ImageOverlapOrNoCover(FILE *AnsTGA);

#endif /* __HYBRID_H__ */
