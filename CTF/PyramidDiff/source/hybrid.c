/*------------------------------------------------------------------------
 *
 * Pyramid Difference Computation Tool
 * -----------------------------------
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
 *//**
 * \file
 * \brief   Computes the pyramid difference between two files.
 *//*-------------------------------------------------------------------*/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

#include "main.h"
#include "hybrid.h"
#include "libpng/png.h"

#define TARGA_HEADER_SIZE   18

#define REINTERPRET_CAST(X,Y) (X)(Y)


/*----------------------------------------------------------------------*
 * Endianess enumeration
 *----------------------------------------------------------------------*/
typedef enum
{
    ENDIAN_LITTLE = 0,      /* Little endian (e.g. Intel x86)   */
    ENDIAN_BIG    = 1       /* Big endian                       */
} Endianess;


/*-------------------------------------------------------------------------
 * Different TGA formats
 *-----------------------------------------------------------------------*/
enum TgaFormats
{
    TGA_NOIMAGE                 = 0,
    TGA_UNCOMPRESSEDCOLORMAP    = 1,
    TGA_UNCOMPRESSEDRGB         = 2,
    TGA_UNCOMPRESSEDBW          = 3,
    TGA_RLECOLORMAP             = 9,
    TGA_RLERGB                  = 10,
    TGA_COMPRESSEDBW            = 11,
    TGA_COMPRESSEDCOLORMAP      = 32,
    TGA_COMPRESSEDCOLORMAP2     = 33
};

/*-------------------------------------------------------------------------
 * Color format enumeration
 *-----------------------------------------------------------------------*/
typedef enum
{
    COLORFORMAT_NONE = 0,

    COLORFORMAT_INT_RGBA,
    COLORFORMAT_INT_BGRA,
    COLORFORMAT_INT_ARGB,
    COLORFORMAT_INT_ABGR,

    COLORFORMAT_BYTE_RGBA,
    COLORFORMAT_BYTE_BGRA,
    COLORFORMAT_BYTE_ARGB,
    COLORFORMAT_BYTE_ABGR,
    COLORFORMAT_BYTE_RGB,
    COLORFORMAT_BYTE_BGR,

    COLORFORMAT_SHORT_ARGB_4444,
    COLORFORMAT_SHORT_RGB_565,

    COLORFORMAT_MAX

} ColorFormat;


/*-------------------------------------------------------------------------
 * Image Data structure, stores all necessary data from the image file
 *-----------------------------------------------------------------------*/
typedef struct ImageData_s
{
    int             width;
    int             height;
    int             format; /* ColorFormat */
    int             stride;
    unsigned char*  data;   /* Points to the pixel at (0, 0). This might not be the start of the memory block. */
} ImageData;

/*-------------------------------------------------------------------*//*!
 * \brief   
 * \param   format  Color format descriptor
 * \return  
 *//*-------------------------------------------------------------------*/

static int getColorFormatPixelBytes(ColorFormat format)
{
    static const unsigned int s_bpp[COLORFORMAT_MAX] = {
        0,              /* COLORFORMAT_NONE */
        4, 4, 4, 4,     /* COLORFORMAT_INT_RGBA */
        4, 4, 4, 4,     /* COLORFORMAT_BYTE_RGBA */
        3, 3,           /* COLORFORMAT_BYTE_RGB */
        2, 2            /* COLORFORMAT_SHORT_ARGB_4444 */
    };

    return s_bpp[format];
}

/*-------------------------------------------------------------------*//*!
 * \brief   Creates a blank image of the given dimensions
 * \param   width   Image dimension
 * \param   height  Image dimension
 * \param   format  Image format
 * \return  
 *//*-------------------------------------------------------------------*/

static ImageData* createBlankImage (int width, int height, ColorFormat format)
{
    int         rowSize     = getColorFormatPixelBytes(format) * width;
    int         dataSize    = rowSize * height;
    ImageData*  image       = malloc(sizeof(ImageData) + dataSize);

    if (!image)
        return NULL;

    image->width    = width;
    image->height   = height;
    image->format   = format;
    image->stride   = rowSize;
    image->data     = (unsigned char*)(image + 1);
    memset(image + 1, 0, dataSize);
    return image;
}
/*-------------------------------------------------------------------*//*!
 * \brief   Destroys a given image
 * \param   image	The given image
 * \return  
 *//*-------------------------------------------------------------------*/

static void destroyImage(ImageData* image)
{
	if (image)
		free(image);
}

/*-------------------------------------------------------------------*//*!
 * \brief   Pack the given color information into one unsigned int
 * 
 * This function is only meant to be used with pyramid diff since
 * it uses bit replication
 *
 * \param   a   Alpha
 * \param   r   Red
 * \param   g   Green
 * \param   b   Blue
 * \return  One uint with the given color information in ARGB
 *//*-------------------------------------------------------------------*/

static unsigned int packForPyramid(
	unsigned int a,
	unsigned int r,
	unsigned int g,
	unsigned int b,
	unsigned int imageDepths)
{
	if (imageDepths)
    {
        a >>= (8 - (imageDepths >> 24) & 0xFF);
        r >>= (8 - (imageDepths >> 16) & 0xFF);
        g >>= (8 - (imageDepths >> 8)  & 0xFF);
        b >>= (8 - imageDepths         & 0xFF);
    }
    else if (channelInfo.rDepth + channelInfo.gDepth + channelInfo.bDepth + channelInfo.aDepth == 16)
	{
		/* Bit replicate when 16 bit config */
        r = r | (r >> channelInfo.rDepth);
		g = g | (g >> channelInfo.gDepth);
		b = b | (b >> channelInfo.bDepth);
		a = a | (a >> channelInfo.aDepth);
    }
	else
    {
        a >>= (8 - channelInfo.aDepth);
        r >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.rDepth));
        g >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.gDepth));
        b >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.bDepth));
    }
    return (a << 24) | (r << 16) | (g << 8) | b;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Pack the given color information into one unsigned int
 * 
 * This function is only meant to be used with pyramid diff since
 * it uses bit replication
 *
 * \param   a   Alpha
 * \param   r   Red
 * \param   g   Green
 * \param   b   Blue
 * \return  One uint with the given color information in ARGB
 *//*-------------------------------------------------------------------*/

static unsigned int pack(
	unsigned int a,
	unsigned int r,
	unsigned int g,
	unsigned int b,
	unsigned int imageDepths)
{
	if (imageDepths)
    {
        a >>= (8 - (imageDepths >> 24) & 0xFF);
        r >>= (8 - (imageDepths >> 16) & 0xFF);
        g >>= (8 - (imageDepths >> 8)  & 0xFF);
        b >>= (8 - imageDepths         & 0xFF);
    }
	else
    {
        a >>= (8 - channelInfo.aDepth);
        r >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.rDepth));
        g >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.gDepth));
        b >>= (8 - ((channelInfo.lDepth) ? channelInfo.lDepth : channelInfo.bDepth));
    }
    return (a << 24) | (r << 16) | (g << 8) | b;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Determines CPU endianess at run-time
 * \return  ENDIAN_LITTLE if CPU is little-endian, ENDIAN_BIG
 *          if big-endian. Weirdo endianesses are not supported.
 * \note    Proper optimizing compilers will make this function a no-op 
 *          (i.e. just a constant value).
 *//*-------------------------------------------------------------------*/

static Endianess getEndianess (void)
{
    static const unsigned int v = 0x12345678u;
    const unsigned char* p      = REINTERPRET_CAST(const unsigned char*,&v);
    return (Endianess)((*p == (unsigned char)(0x12)) ? ENDIAN_BIG : ENDIAN_LITTLE);
}

/*-------------------------------------------------------------------*//*!
 * \brief   Flip the color format if the CPU is little endian
 * \param   format  The color format used
 * \return  The proper color format
 *//*-------------------------------------------------------------------*/

static ColorFormat canonizeColorFormat (ColorFormat format)
{
    switch (format)
    {
    case COLORFORMAT_INT_RGBA:
        return (getEndianess() == ENDIAN_BIG) ? COLORFORMAT_BYTE_RGBA : COLORFORMAT_BYTE_ABGR;

    case COLORFORMAT_INT_BGRA:
        return (getEndianess() == ENDIAN_BIG) ? COLORFORMAT_BYTE_BGRA : COLORFORMAT_BYTE_ARGB;

    case COLORFORMAT_INT_ARGB:
        return (getEndianess() == ENDIAN_BIG) ? COLORFORMAT_BYTE_ARGB : COLORFORMAT_BYTE_BGRA;

    case COLORFORMAT_INT_ABGR:
        return (getEndianess() == ENDIAN_BIG) ? COLORFORMAT_BYTE_ABGR : COLORFORMAT_BYTE_RGBA;

    default:
        return format;
    }
}

/*-------------------------------------------------------------------*//*!
 * \brief   Gets the pixel with mirroring.
 *//*-------------------------------------------------------------------*/

static unsigned char* getPixelPtr(const ImageData* image, int x, int y)
{ 
    return image->data + x * getColorFormatPixelBytes((ColorFormat)image->format) + y * image->stride; 
}

/*-------------------------------------------------------------------*//*!
 * \brief   Get the value of a certain pixel on the image
 * \param   img     Pointer to the image data
 * \param   x       x-coordinate
 * \param   y       y-coordinate
 * \return  Value of a pixel in the given image.
 *//*-------------------------------------------------------------------*/

static unsigned int getPixel(ImageData* img, int x, int y)
{
    if (x < 0)
        x = 0 - (x+1);
    if (y < 0)
        y = 0 - (y+1);
    if (x >= img->width)
        x = 2*img->width - (x + 1);
    if (y >= img->height)
        y = 2*img->height - (y + 1);

    return *((unsigned int*)getPixelPtr(img, x, y));
}

/*-------------------------------------------------------------------*//*!
 * \brief   Moves the given color data into an array
 * \param   format  The desired color format
 * \param   p       The array in which the result is stored into
 * \param   argb    The given color
 *//*-------------------------------------------------------------------*/

static void setColorARGB (ColorFormat format, unsigned char* p, unsigned int argb)
{
    switch (canonizeColorFormat(format))
    {
    case COLORFORMAT_BYTE_RGBA:
        p[0] = (unsigned char)(argb >> 16);
        p[1] = (unsigned char)(argb >> 8);
        p[2] = (unsigned char)(argb >> 0);
        p[3] = (unsigned char)(argb >> 24);
        break;

    case COLORFORMAT_BYTE_BGRA:
        p[0] = (unsigned char)(argb >> 0);
        p[1] = (unsigned char)(argb >> 8);
        p[2] = (unsigned char)(argb >> 16);
        p[3] = (unsigned char)(argb >> 24);
        break;

    case COLORFORMAT_BYTE_ARGB:
        p[0] = (unsigned char)(argb >> 24);
        p[1] = (unsigned char)(argb >> 16);
        p[2] = (unsigned char)(argb >> 8);
        p[3] = (unsigned char)(argb >> 0);
        break;

    case COLORFORMAT_BYTE_ABGR:
        p[0] = (unsigned char)(argb >> 24);
        p[1] = (unsigned char)(argb >> 0);
        p[2] = (unsigned char)(argb >> 8);
        p[3] = (unsigned char)(argb >> 16);
        break;

    case COLORFORMAT_BYTE_RGB:
        p[0] = (unsigned char)(argb >> 16);
        p[1] = (unsigned char)(argb >> 8);
        p[2] = (unsigned char)(argb >> 0);
        break;

    case COLORFORMAT_BYTE_BGR:
        p[0] = (unsigned char)(argb >> 0);
        p[1] = (unsigned char)(argb >> 8);
        p[2] = (unsigned char)(argb >> 16);
        break;

    case COLORFORMAT_SHORT_ARGB_4444:
        *(unsigned short*)p = (unsigned short)(
            ((argb >> 16) & 0xf000) |
            ((argb >> 12) & 0x0f00) |
            ((argb >> 8) & 0x00f0) |
            ((argb >> 4) & 0x000f));
        break;

    case COLORFORMAT_SHORT_RGB_565:
        *(unsigned short*)p = (unsigned short)(
            ((argb >> 8) & 0xf800) |
            ((argb >> 5) & 0x07e0) |
            ((argb >> 3) & 0x001f));
        break;

    default:
        break;
    }
}


/*-------------------------------------------------------------------*//*!
 * \brief   
 * \param   image   
 * \param   x       
 * \param   y       
 * \param   argb    
 *//*-------------------------------------------------------------------*/

static void setPixelARGB(ImageData* image, int x, int y, unsigned int argb)
{ 
    setColorARGB((ColorFormat)image->format, getPixelPtr(image, x, y), argb);
}

/*-------------------------------------------------------------------*//*!
 * \brief   Returns larger of two signed values
 * \param   a   First 32-bit integer value
 * \param   b   Second 32-bit integer value
 * \return  Larger of the two values
 *//*-------------------------------------------------------------------*/

static int maxInt(int a, int b)
{
    if (b > a)
        a = b;
    return a;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Returns smaller of two signed values
 * \param   a   First 32-bit integer value
 * \param   b   Second 32-bit integer value
 * \return  Smaller of the two values
 *//*-------------------------------------------------------------------*/

static int minInt(int a, int b)
{

    if (b < a)
        a = b;

    return a;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Returns absolute value of an integer
 * \param   a   32-bit input value
 * \return  abs(a)
 *//*-------------------------------------------------------------------*/

static int absInt(int a)
{
    return (a >= 0) ? a : -a;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Clamps value to be in range [mn,mx]
 * \param   v   Input value
 * \param   mn  Interval minimum (inclusive)
 * \param   mx  Interval maximum (inclusive)
 * \return  Clamped value
 * \note    mn *must* be <= mx
 *//*-------------------------------------------------------------------*/

static int clamp(int v, int mn, int mx)
{
    if (v < mn) 
        v = mn;

    if (v > mx) 
        v = mx;
    
    return v;
}

/*-------------------------------------------------------------------*//*!
 * \brief   Gets the difference of the min and the max in the
 *          9-neighbourhood of the pixel.
 * \param   img     The images from which the pixels are extracted from
 * \param   x       The x-coordinate
 * \param   y       The y-coordinate
 * \return  Difference
 *//*-------------------------------------------------------------------*/

static unsigned int minMaxDiffPixel(ImageData* img, int x, int y)
{
    int j;
    int mins[4] = {0xFF, 0xFF, 0xFF, 0xFF};
    int maxs[4] = {0x0, 0x0, 0x0, 0x0};
    unsigned int result=0;

    for (j = 0; j < 3; j++)
    {
        int i;
        for (i = 0; i < 3; i++)
        {
            int k;
            int data = getPixel(img, x+i-1, y+j-1);
            for (k = 0; k < 4; k++)
            {
                maxs[k] = maxInt(maxs[k], ((data>>(8*k)) & 0xFF));
                mins[k] = minInt(mins[k], ((data>>(8*k)) & 0xFF));
            }
        }
    }   
    for (j = 0; j < 4; j++)
    {
        result |= ((maxs[j] - mins[j]) & 0xFF) << (j*8);
    }
    return result;
}

/*-------------------------------------------------------------------*//*!
 * \brief   
 * \param   img 
 * \param   x   
 * \param   y   
 * \return  
 *//*-------------------------------------------------------------------*/

static unsigned int convolve(ImageData* img, int x, int y)
{
    float kernel[9] = {.75f, .9f, .75f, .9f, 1.f, .9f, .75f, .9f, .75f};
    float factor = 7.6f;
    int j;
    float sum[4] = {0.f, 0.f, 0.f, 0.f};
    unsigned int result=0;

    for (j = 0; j < 3; j++)
    {
        int i;
        for (i = 0; i < 3; i++)
        {
            int k;
            int data = getPixel(img, x+i-1, y+j-1);
            for (k = 0; k < 4; k++)
            {
                sum[k] += kernel[3*j+i] * (float)((data>>(8*k)) & 0xFF);
            }
        }
    }   
    for (j = 0; j < 4; j++)
    {
        result |= ((unsigned int)(sum[j]/factor) & 0xFF) << (j*8);
    }
    return result;
}

/*-------------------------------------------------------------------*//*!

 * \brief   
 * \param   img 
 * \param   x   
 * \param   y   
 * \return  
 *//*-------------------------------------------------------------------*/

static unsigned int bilinear(ImageData* img, int x, int y)
{
    unsigned int data[4];
    unsigned int result = 0;
    {
        int k;
        for (k = 0; k < 4; k++)
            data[k] = getPixel(img, 2*x+(k%2), 2*y+(k/2));
    }
    {
        int k;
        int l;
        for (k = 0; k < 4; k++)
        {
            int channelRes = 0;
            int shift = 8*k;
            for (l = 0; l < 4; l++)
                channelRes += (data[l]>>shift)&0xFF;
            result |= ((channelRes/4)&0xFF) << shift;
        }
    }
    return result;
}


static int fixLSBError(ImageData* img, ImageData* ref)
{
	/* For each channel num of -1, 1, other differences. */
	int numDiffPixels[16] = {0, 0, 0,
							 0, 0, 0,
							 0, 0, 0,
							 0, 0, 0};
	int channelModifiers[4] = {0, 0, 0, 0};
	int y, k;
	int channelShifts[4];

	channelShifts[0] = 8 - channelInfo.bDepth;
	channelShifts[1] = 8 - channelInfo.gDepth;
	channelShifts[2] = 8 - channelInfo.rDepth;
	channelShifts[3] = 8 - channelInfo.aDepth;

	if (!img || !ref || img->width != ref->width || img->height != img->height || img == ref)
		return 0;

	for (y = 0; y < img->height; y++)
	{
		int x;
		for (x = 0; x < img->width; x++)
		{
			unsigned int refPxl = getPixel(ref, x, y);
			unsigned int imgPxl = getPixel(img, x, y);
			int k;
			for (k = 0; k < 4; k++)
			{
				int refValue = (refPxl >> (k*8)) & 0xFF;
				int imgValue = (imgPxl >> (k*8)) & 0xFF;
				int diff = imgValue - refValue;
				if (diff < 0 && diff >= - (1 << channelShifts[k]) - 1)
					numDiffPixels[k*3]++;
				else if (diff > 0 && diff <= (1 << channelShifts[k]) + 1)
					numDiffPixels[k*3+1]++;				  
				else 
					numDiffPixels[k*3+2]++;				  
			}
		}
	}

	for (k = 0; k < 4; k++)
	{
		channelModifiers[k] = 0;
		if (numDiffPixels[k*3] > numDiffPixels[k*3+1])
			channelModifiers[k] = (1 << channelShifts[k]);
		else if (numDiffPixels[k*3] < numDiffPixels[k*3+1])
			channelModifiers[k] = -(1 << channelShifts[k]);
	}

	for (y = 0; y < img->height; y++)
	{
		int x;
		for (x = 0; x < img->width; x++)
		{
			unsigned int refPxl = getPixel(ref, x, y);
			unsigned int imgPxl = getPixel(img, x, y);
			unsigned int newVal = 0;
			int k;
			for (k = 0; k < 4; k++)
			{
				int refValue = (refPxl >> (k*8)) & 0xFF;
				int imgValue = (imgPxl >> (k*8)) & 0xFF;
				if ((imgValue - refValue) *  channelModifiers[k] < 0)
                {
                    int temp = imgValue+channelModifiers[k];
    				if (temp < 0) temp = 0;
                    if (temp > 0xFF) temp = 0xFF;
                    newVal |= temp << (k*8);
                }
                else
                {
                    newVal |= imgValue << (k*8);
                }
			}
			*((unsigned int*)getPixelPtr(img,x,y)) = newVal;
		}
	}
	
	return 1;
}


/*-------------------------------------------------------------------*//*!

 * \brief   Creates a mask image from the given image data
 * \param   src     The image data from which the mask is created
 * \return  The resulting mask
 *//*-------------------------------------------------------------------*/

static ImageData* createMaskImage(ImageData* src)
{
    ImageData* res = 0;

	/* If source data is available */
	if (src)
	{
	    int y;
		res = createBlankImage(src->width, src->height, src->format);
	    for (y = 0; y < src->height; y++)
	    {
	        int x;
	        for (x = 0; x < src->width; x++)
	            *((unsigned int*)getPixelPtr(res, x, y)) = minMaxDiffPixel(src, x, y);
	   }
	}

    return res;
}

/*-------------------------------------------------------------------*//*!

 * \brief   Compute the gaussian pyramid levels.
 * \param   dst     Destination data
 * \param   src     Source data
 *//*-------------------------------------------------------------------*/

static void computePyramid(ImageData** dst, ImageData* src, int numLevels)
{
    int level = 0;
    int y;

    for (level = 0; level < numLevels; level++)
    {
        ImageData* tempRes = createBlankImage(src->width, src->height, COLORFORMAT_INT_RGBA);
        ImageData* res = createBlankImage(src->width/2, src->height/2, COLORFORMAT_INT_RGBA);

        /* Filter */
        for (y = 0; y < tempRes->height; y++)
        {
            int x;
            for (x = 0; x < tempRes->width; x++)
                *((unsigned int*)getPixelPtr(tempRes, x, y)) = convolve(src, x, y);
        }

        /* Scale down */
        for (y = 0; y < res->height; y++)
        {
            int x;
            for (x = 0; x < res->width; x++)
                *((unsigned int*)getPixelPtr(res, x, y)) = bilinear(tempRes, x, y);
        }

        destroyImage(tempRes);
        dst[level] = res;
        src = res;      
    }   
}

/*-------------------------------------------------------------------*//*!
 * \brief   Compare images,
 * \param   img         
 * \param   ref         
 * \param   mask        
 * \param   maskFactor  
 * \return  Maximum masked difference.
 *//*-------------------------------------------------------------------*/

static float compareImages(ImageData* img, ImageData* ref, ImageData* mask, float maskFactor)
{
    int result = 0;
    int y;

    for (y = 0; y < img->height; y++)
    {
        int x;
        for (x = 0; x < img->width; x++)
        {
            int k;
            unsigned int maskData = getPixel(mask, x, y);
            unsigned int imgData = getPixel(img, x, y);
            unsigned int refData = getPixel(ref, x, y);
            for (k = 0; k < 4; k++)
            {
                int channel = 8*k;
                int temp = 0;
                temp = (int)((imgData >> channel) & 0xFF) - (int)((refData >> channel) & 0xFF);
                temp = absInt(temp);
                temp = (temp * (0xFF - clamp((int)(maskFactor*(float)((maskData >> channel) & 0xFF)), 0, 0xFF))) / 0xFF;
                if (temp > 0xFF) temp = 0xFF;
                result = maxInt(result, temp);
            }
        }
    }
    
    return (float)result;
}


/*-------------------------------------------------------------------*//*!
 * \brief   Imports .png files
 * \param   filename    The filename of the imported image
 * \param	isPyramid	Is function used by pyramidDiff? PyramidDiff
 *						packing does certain operations for input data
 * \return  return a struct containing all necessary information for the
 *          pyramid diff function.
 *//*-------------------------------------------------------------------*/

static ImageData* createImageFromPNG(FILE* f, int isPyramid)
{
	png_structp png_ptr;
	png_infop info_ptr;
	png_uint_32 width;
	png_uint_32 height;
	png_byte signature[8];

	int bit_depth;
	int color_type;
	int interlace_type;
	int compression_type;
	int filter_type;
	double  gamma;

	ImageData*  result = NULL;

	if (f == NULL) return result;

	// let libpng check the file to make sure it is a PNG file
	fread(signature, 1, 8, f);
	if (png_sig_cmp(signature, 0, 8) != 0) return result; // not a png

	// let libpng read in the PNG file
	png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, png_voidp_NULL,
			png_error_ptr_NULL, png_error_ptr_NULL);
	if (png_ptr == NULL) return result; // out of memory

	info_ptr = png_create_info_struct(png_ptr);
	if (info_ptr == NULL) 
	{
		png_destroy_read_struct(&png_ptr, png_voidp_NULL, png_voidp_NULL);
		return result; // out of memory
	}

	// libpng's error handling code
	if (setjmp(png_ptr->jmpbuf)) {
		png_destroy_read_struct(&png_ptr, &info_ptr, png_voidp_NULL);
		return NULL;
	}

	png_init_io(png_ptr, f);
	png_set_read_status_fn(png_ptr, png_read_status_ptr_NULL);
	png_set_sig_bytes(png_ptr, 8);
	png_read_info(png_ptr, info_ptr);

	png_get_IHDR(png_ptr, info_ptr, &width, &height, &bit_depth, 
			&color_type, &interlace_type, &compression_type, &filter_type);

	// expand to RGBA of 8 bit channels
	if (color_type == PNG_COLOR_TYPE_PALETTE)
	{
		png_set_palette_to_rgb(png_ptr);
	} else if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
	{
		png_set_expand_gray_1_2_4_to_8(png_ptr);
	}
	if (png_get_valid(png_ptr, info_ptr, PNG_INFO_tRNS))
	{
		png_set_tRNS_to_alpha(png_ptr);
	}
	if (bit_depth == 16)
	{
		png_set_strip_16(png_ptr);
	}
	if (color_type == PNG_COLOR_TYPE_GRAY || 
			color_type == PNG_COLOR_TYPE_GRAY_ALPHA)
	{
		png_set_gray_to_rgb(png_ptr);
	}

#ifdef WIN32
	if (png_get_gAMA(png_ptr, info_ptr, &gamma))
	{
		png_set_gamma(png_ptr, 2.2, gamma); // 2.2 is exponent for windows
	}
#endif

	// update info
	png_read_update_info(png_ptr, info_ptr);
	png_get_IHDR(png_ptr, info_ptr, &width, &height, &bit_depth, 
			&color_type, &interlace_type, &compression_type, &filter_type);

	// parse the libpng structure into the ImageData structure.
	result = createBlankImage(width, height, COLORFORMAT_BYTE_RGBA);
	if (result == NULL) 
	{
		png_destroy_read_struct(&png_ptr, &info_ptr, png_voidp_NULL);
		return result;
	}
	{
		png_uint_32 i;
		png_uint_32 j;
		png_uint_32 rowbytes;
		png_bytep image;
		png_bytepp row_pointers;
		
		rowbytes = png_get_rowbytes(png_ptr, info_ptr);
		image = png_malloc(png_ptr, rowbytes*height);
		row_pointers = png_malloc(png_ptr, height*sizeof(png_bytep));

		for (i = 0; i < height; i++)
		{
			row_pointers[i] = image + i * rowbytes;
		}

		png_read_image(png_ptr, row_pointers);
		png_read_end(png_ptr, png_voidp_NULL);
		
		if (isPyramid)
		{
			for (i = 0; i < height; i++)
			{
				for (j = 0; j < width; j++)
				{
					setPixelARGB(result, j, i, packForPyramid(
							row_pointers[i][j+3], row_pointers[i][j+2], 
							row_pointers[i][j+1], row_pointers[i][j], 0));
				}
			}
		}
		else
		{
			for (i = 0; i < height; i++)
			{
				for (j = 0; j < width; j++)
				{
					setPixelARGB(result, j, i, pack(row_pointers[i][j+3], 
							row_pointers[i][j+2], row_pointers[i][j+1], 
							row_pointers[i][j], 0));
				}
			}
		}

		png_free(png_ptr, row_pointers);
		png_free(png_ptr, image);
	}
	
	png_destroy_read_struct(&png_ptr, &info_ptr, png_voidp_NULL);
	return result;
}


/*-------------------------------------------------------------------*//*!
 * \brief   Imports .tga files
 * \param   filename    The filename of the imported image
 * \param	isPyramid	Is function used by pyramidDiff? PyramidDiff
 *						packing does certain operations for input data
 * \return  return a struct containing all necessary information for the
 *          pyramid diff function.
 *//*-------------------------------------------------------------------*/

static ImageData* createImageFromTGA(FILE* f, int isPyramid)
{
    unsigned char* buf;
    unsigned char* input;
    int id_lgt, cmap_esize, pix_size, flip, cmap_lgt, datatype;
    int depth, w, h, c;
    unsigned char r, e;
    int i,j;
    ImageData*  result = NULL;
    unsigned int orgImageDepths = 0x0;

    buf = (unsigned char*)malloc(TARGA_HEADER_SIZE);

    if (!buf)
        return NULL;

    /* Load targa header */
    if (fread((void*)buf, TARGA_HEADER_SIZE, 1, f) != 1)
    {   
        free(buf);
        return NULL;
    }

    input = buf;
    r = *input++;
    id_lgt = r;                 /*identification field length (1)*/

    input++;                    /*color map type (1)*/

    r = *input++;
    datatype = r;               /*image type code (1)*/

    if (datatype != TGA_UNCOMPRESSEDRGB && datatype != TGA_RLERGB)
    {   
        free(buf);
        return NULL;            /*unsupported format*/
    }

    /*cmap specification (5 bytes)*/
    input       += 2;           /*index of first cmap entry (2)*/
    r           = *input++;
    e           = *input++;
    cmap_lgt    = e * 256 + r;  /*number of cmap entries (2)*/
    r           = *input++;
    cmap_esize  = r;            /*cmap entry size in bits (1)*/

    /*image specification (10 bytes)*/
    input       += 2;           /*lower left x (2)*/
    input       += 2;           /*lower left y (2)*/

    r           = *input++;
    e           = *input++;
    w           = e*256+r;      /*width of the picture (2)*/

    r           = *input++;
    e           = *input++;
    h           = e*256+r;      /*height of the picture (2)*/

    r           = *input++;
    pix_size    = r;            /*size of a pixel in bits (1)*/
    depth       = r / 8;

    if (depth < 3 || depth > 4)
    {   
        free(buf);
        return NULL;            /*unsupported color depth*/
    }

    r       = *input++;
    flip    = (r & 32) ? 0 : 1; /*image descriptor: bit 5 = flip y (1)*/

    free(buf);

    /*image identification field (id_lgt bytes)*/
    if (id_lgt == sizeof(unsigned int))
    {
        if (fread(&orgImageDepths, sizeof(unsigned int), 1, f) != 1)
            return NULL;
    }
    else if (fseek(f, id_lgt, SEEK_CUR))
    {
        return NULL;
    }

    /*color map data (entries * entrybits / 8)*/
    if (fseek(f, cmap_lgt*cmap_esize/8, SEEK_CUR))
        return NULL;

    /* Create Image */
    result = createBlankImage(w, h, COLORFORMAT_BYTE_RGBA);

    if (!result)
        return NULL;

    switch (datatype)
    {
    case TGA_NOIMAGE:
        break;

    case TGA_UNCOMPRESSEDRGB:

        for (i=0; i<h; i++)
        {
            int y = flip ? h - 1 - i : i;

            for (j=0; j<w; j++)
            {
                unsigned char color[4];

                if (fread((void*)color, depth, 1, f) != 1)
                {   
                    destroyImage(result);
                    fclose(f);
                    return NULL;
                }

                if (depth == 3)
				{
					if (isPyramid)
						setPixelARGB(result,j,y, packForPyramid(255, color[2], color[1], color[0], orgImageDepths));
					else
						setPixelARGB(result,j,y, pack(255, color[2], color[1], color[0], orgImageDepths));
				}
                else
				{
					if (isPyramid)
						setPixelARGB(result,j,y, packForPyramid(color[3], color[2], color[1], color[0], orgImageDepths));
					else
						setPixelARGB(result,j,y, pack(color[3], color[2], color[1], color[0], orgImageDepths));
				}
            }
        }
        break;

    case TGA_RLERGB:

        for (c=0; c < w * h; )
        {
            unsigned char packet;
            int repeat;

            if (fread((void*)&packet, 1 , 1 , f) != 1)
            {   
                destroyImage(result);
                fclose(f);
                return NULL;
            }

            repeat = (packet & 0x7f) + 1;

            if(packet & 0x80)
            {   
                /* RLE packet */
                unsigned char color[4];
                unsigned int argb;

                if (fread((void*)color, depth , 1 , f) != 1)
                {   
                    free(result);
                    fclose(f);
                    return NULL;
                }

                if(depth == 3)
					if (isPyramid)
						argb = packForPyramid(255, color[2], color[1], color[0], orgImageDepths);
					else
						argb = pack(255, color[2], color[1], color[0], orgImageDepths);
                else
					if (isPyramid)
						argb = packForPyramid(color[3], color[2], color[1], color[0], orgImageDepths);
					else
						argb = pack(color[3], color[2], color[1], color[0], orgImageDepths);

                for(i=0; i < repeat; i++ , c++)
                {
                    int x = c % w;
                    int y = c / w;

                    if(flip)
                        y = h-1-y;

                    setPixelARGB(result, x, y, argb);
                }
            }
            else
            {   /* raw packet */

                for(i=0; i < repeat; i++ , c++)
                {
                    unsigned char color[4];
                    unsigned int argb;
                    int x = c % w;
                    int y = c / w;

                    if(flip)
                        y = h - 1 - y;

                    if (fread((void*)color, depth, 1, f) != 1)
                    {   
                        destroyImage(result);
                        fclose(f);
                        return NULL;
                    }

                    if(depth == 3)
						if (isPyramid)
							argb = packForPyramid(255, color[2], color[1], color[0], orgImageDepths);
						else
							argb = pack(255, color[2], color[1], color[0], orgImageDepths);
                    else
						if (isPyramid)
							argb = packForPyramid(color[3], color[2], color[1], color[0], orgImageDepths);
						else
							argb = pack(color[3], color[2], color[1], color[0], orgImageDepths);
                    /* else TODO handle depth == 2 */
                    setPixelARGB(result, x, y, argb);
	            }
            }
        }
        break;
    }

    return result;
}


/*-------------------------------------------------------------------*//*!
 * \brief   Main function.
 *//*-------------------------------------------------------------------*/

static float pyramidDiff(FILE* srcFile, FILE* refFile, int fixLSB, ImageType imageType, const int pyramidDepth)
{
    ImageData**  pyramid;
    ImageData**  maskPyramid;
    ImageData**  refPyramid;

    /*---------------------------------------------------------------------
     * Import data from the image that is in the given format
     *-------------------------------------------------------------------*/

	ImageData* src;
	ImageData* ref;
	ImageData* mask;

	switch (imageType)
	{
	case TGA:
		{
			src = createImageFromTGA(srcFile, ((fixLSB)?1:0));
			ref = createImageFromTGA(refFile, ((fixLSB)?1:0));
		}
	case PNG:
		{
			src = createImageFromPNG(srcFile, ((fixLSB)?1:0));
			ref = createImageFromPNG(refFile, ((fixLSB)?1:0));
		}
	}
    mask = createMaskImage(ref);

    if (!src || !ref || !mask)
    {
		if (src)
			destroyImage(src);
		if (ref)
			destroyImage(ref);
		if (mask)
			destroyImage(mask);
        return CT_INVALID_SCORE;
    }

	
	if (fixLSB)
	{
		if (!fixLSBError(src, ref))
		{
		    destroyImage(src);
		    destroyImage(ref);
		    destroyImage(mask);
			return CT_INVALID_SCORE;
		}
	}

	pyramid = malloc(pyramidDepth*sizeof(ImageData*));
    maskPyramid = malloc(pyramidDepth*sizeof(ImageData*));
    refPyramid = malloc(pyramidDepth*sizeof(ImageData*));
	memset(pyramid, 0, pyramidDepth*sizeof(ImageData*));
	memset(maskPyramid, 0, pyramidDepth*sizeof(ImageData*));
	memset(refPyramid, 0, pyramidDepth*sizeof(ImageData*));

    computePyramid(pyramid, src, pyramidDepth);    
    computePyramid(maskPyramid, mask, pyramidDepth);
    computePyramid(refPyramid, ref, pyramidDepth);

	destroyImage(src);
	destroyImage(ref);
	destroyImage(mask);

	{
		float result = compareImages(
				pyramid[pyramidDepth-1], refPyramid[pyramidDepth-1], 
				maskPyramid[pyramidDepth-1], 1.5f);
		int i;

		for (i=0; i<pyramidDepth && pyramid[i]; i++)
			destroyImage(pyramid[i]);

		for (i=0; i<pyramidDepth && maskPyramid[i]; i++)
			destroyImage(maskPyramid[i]);

		for (i=0; i<pyramidDepth && refPyramid[i]; i++)
			destroyImage(refPyramid[i]);

		free(pyramid);
		free(maskPyramid);
		free(refPyramid);
		return result;
	}
}

float PyramidDiff_by_HYBRID(FILE* srcFile, FILE* refFile, ImageType imageType, 
							int pyramidDepth)
{
	return pyramidDiff(srcFile, refFile, 1, imageType, pyramidDepth);
}

float PyramidDiff_NOLSBFIX_by_HYBRID(FILE* srcFile, FILE* refFile, 
									 ImageType imageType, int pyramidDepth)
{
	return pyramidDiff(srcFile, refFile, 0, imageType, pyramidDepth);
}

/*-------------------------------------------------------------------*//*!
 * \brief   This function computes the sum of pixels contained in regions
            of one image that are not also found in another image.  A pixel
            is considered to be in the region of one image but not the other
            if the pixel and all of its neighboring pixels have difference
            values which exceed some maximum allowable difference.

            X denotes a pixel whose diff value exceeds max diff
            O denotes a pixel whose diff value does not exceed max diff

            XXX
            XXX  -- Center pixel is in a difference region
            XXX

            XXX
            XOX  -- Center pixel is NOT in a difference region
            XXX

            XXO
            XXX  -- Center pixel is NOT in a difference region
            XXX

            Using this definition, the function computes the total number of
            pixels which are considered to be in a difference region.

            This is computed as follows:
            1. The function calculates the diff image between two images
               (reference data and answer data) and stores the result in the
               diffVal array.  Each element of the array stores the color
               difference between pixels where the difference is calculated
               as the maximum difference of all channels.
            2. After computing this difference image array, this function
               determines pixels that are in regions of a shape present in
	       one image but not present in the other.  This is determined
	       by looping over each pixel in the difference image.  If the
	       pixel under consideration and all of its neighbors have
	       difference values which exceed the maximum difference value
	       per pixel, the pixel is considered to be in a difference
	       region and a counter is incremented.

 * \param   img             Image being verifired
 * \param   ref             Reference image
 * \param   maxAllowDiff    Maximum allowed color difference
 * \return  Number of pixels with different color.
 *//*-------------------------------------------------------------------*/

static int compareImageRegions(ImageData* img, ImageData* ref, int maxAllowDiff)
{
    int result = 0;
    int x, y, x1, y1;
    int *diffVal = (int*) malloc(sizeof(int) * img->width * img->height);
    char diffPixel;

    if (!diffVal) {
        return -1;
    }

    /* Initialize diff table */
    for (y = img->width * img->height - 1; y >= 0; y--) 
        diffVal[y] = 0;

    /* Calculate diff value for each pixel */
    for (y = 0; y < img->height; y++)
    {
        for (x = 0; x < img->width; x++)
        {
            int k;
            unsigned int imgData = getPixel(img, x, y);
            unsigned int refData = getPixel(ref, x, y);
            for (k = 0; k < 4; k++)
            {
                int channel = 8*k;
                int temp = 0;
                temp = (int)((imgData >> channel) & 0xFF) - (int)((refData >> channel) & 0xFF);
                diffVal[x * img->height + y] = maxInt(diffVal[x * img->height + y], absInt(temp));
            }
        }
    }

    /* Calculate the number of pixels that differ and have neighbors that all differ */
    for (y = 0; y < img->height; y++)
    {
        for (x = 0; x < img->width; x++)
        {
            /* diffPixel == 1 iff the pixel and all of its neighbors has the diff 
               greater than maxAllowDiff 
            */
            diffPixel = 1;
            for(x1 = maxInt(0, x - 1); x1 <= minInt(img->width - 1, x + 1); x1++) {
                for(y1 = maxInt(0, y - 1); y1 <= minInt(img->height - 1, y + 1); y1++) {
                    if (diffVal[x1 * img->height + y1] <= maxAllowDiff) {
                        diffPixel = 0;
                    }
                }
            }
            if (diffPixel) {
                /* fprintf(stderr, "%c%c%c%c", (unsigned char) 255, (unsigned char) 255, (unsigned char) 255, (unsigned char) 255); */
                result++;
            } else {
                /* fprintf(stderr, "%c%c%c%c", (unsigned char) 0, (unsigned char) 0, (unsigned char) 0, (unsigned char) 0); */
            }
        }
    }
    free(diffVal);
    return result;
}

int RegionComparison_by_NVIDIA(FILE* srcFile, FILE* refFile)
{
    ImageData*  src         = NULL;
    ImageData*  ref         = NULL;

    /*---------------------------------------------------------------------
     * Import data from the image that is in the given format
     *-------------------------------------------------------------------*/
    
	src = createImageFromTGA(srcFile, 0);
    ref = createImageFromTGA(refFile, 0);
    
    if (src == 0 || ref == 0)
    {
        if ( src )
            destroyImage(src);
        if ( ref )
            destroyImage(ref);
        return CT_INVALID_SCORE;
    }

	{
		int result = compareImageRegions(src, ref, 5);

		destroyImage(src);
		destroyImage(ref);
	    
		return result;
	}
}

float CompareTGAInfo_by_HUONE(FILE *AnsTGA, FILE *RefTGA)
{
    int i;
    float  errorSum = 0.0f;

    ImageData* ans = createImageFromTGA(AnsTGA, 0);
    ImageData* ref = createImageFromTGA(RefTGA, 0);

    if (ans == 0 || ref == 0) {
        if ( ans )
            destroyImage(ans);
        if ( ref )
            destroyImage(ref);
        return CT_INVALID_SCORE;
    }
    
    if (ans->width != ref->width || ans->height != ref->height || ans->stride != ref->stride || ans->format != ref->format ) {
        destroyImage(ans);
        destroyImage(ref);
        return CT_INVALID_SCORE;
    }
    else {
        for ( i = 0; i < ref->width * ref->height; i++ ) {
            if ( ans->data[i*4  ] != ref->data[i*4  ] ||
                 ans->data[i*4+1] != ref->data[i*4+1] ||
                 ans->data[i*4+2] != ref->data[i*4+2] || 
                 ans->data[i*4+3] != ref->data[i*4+3] ) {  
                errorSum++;
            }
        }
    }

	destroyImage(ans);
	destroyImage(ref);

    return errorSum;
}

float CompareTGAInfo_with_epsilon_by_HUONE(FILE *AnsTGA, FILE *RefTGA, const float e)
{
    int i;
    float  errorSum = 0.0f;
    ImageData* ans = createImageFromTGA(AnsTGA, 0);
    ImageData* ref = createImageFromTGA(RefTGA, 0);

    if (ans == 0 || ref == 0) {
        if ( ans )
            destroyImage(ans);
        if ( ref )
            destroyImage(ref);
        return CT_INVALID_SCORE;
    }
    
    if (ans->width != ref->width || ans->height != ref->height || ans->stride != ref->stride || ans->format != ref->format ) {
        destroyImage(ans);
        destroyImage(ref);
        return CT_INVALID_SCORE;
    }        
    else {
        for ( i = 0; i < ref->width * ref->height; i++ ) {
            if ( (float)fabs(ans->data[i*4  ] - ref->data[i*4  ]) > e ||
                 (float)fabs(ans->data[i*4+1] - ref->data[i*4+1]) > e ||
                 (float)fabs(ans->data[i*4+2] - ref->data[i*4+2]) > e ||
                 (float)fabs(ans->data[i*4+3] - ref->data[i*4+3]) > e ) {
                errorSum++;
            }
        }
    }
	destroyImage(ans);
	destroyImage(ref);
    return errorSum;
}

int ImageOverlapOrNoCover(FILE *AnsTGA)
{
    ImageData* ans = NULL;
    int i;
    int overlapError = 0;
    int noCoverError = 0;
    ans = createImageFromTGA(AnsTGA, 0);
    if (ans == 0) 
    { 
        return CT_INVALID_SCORE; 
    }
    if (channelInfo.lDepth == 1)
    {
        /* we cannot test BW_1 dst surface for noCoverError */
        destroyImage(ans);
        return 0;
    }
    for (i = 0; i < ans->height * ans->width; i++)
    {
        if (channelInfo.aDepth > 1)
        {
            /* we test the alpha channel if it supports more than 2 values */
            if (ans->data[i*4+3] == 0xFF)
            {
                overlapError ++;
            }
            else if (ans->data[i*4+3] == 0)
            {
                noCoverError ++;
            }
        }
        else if (channelInfo.lDepth > 1)
        {
            if (ans->data[i*4+1] == 0xFF)
            {
                overlapError ++;
            }
            else if (ans->data[i*4+1] == 0)
            {
                noCoverError ++;
            }
        }
        /* if dst surface does not support aDepth > 1 or lDepth, we look for purple colour */
        else if (ans->data[i*4] && ans->data[i*4+2])
        {        
            overlapError ++;
        }
        else if (!(ans->data[i*4] || ans->data[i*4+2]))
        {
            noCoverError ++;
        }
    }

	destroyImage(ans);

    return overlapError + noCoverError;
}

/*-------------------------------------------------------------------*//*! 
* \brief   This function is designed to work with two-color images. 
           For a given image and specified row it calculates the location 
           where the color changes from one into the other (col1Pos and 
           col2Pos). This function also calculates the colors found in a 
           specified row (col1 and col2). It returns the number of different 
           colors found in that row. If there are more than 2 colors, the 
           function returns value 3 and exits (without calculating right 
           values for col1, col2, col1Pos and col2Pos. 
           It is used by compareTwoColorGradient comparison method. 

 * \param   img             Image being verified 
 * \param   row             Row for which calculations are applied 
 * \return  col1            First color occurring in the row 
 * \return  col1Pos         Position of the boundary pixel with color col1 
 * \return  col2            Second color occurring in the row 
 * \return  col2Pos         Position of the boundary pixel with color col2 
 * \return  the number of colors found in a row - 1, 2 or 3 (more than 2) 
 *//*-------------------------------------------------------------------*/ 
static int findTwoColorBoundaries(ImageData *img, int row, 
                                   unsigned int *col1, int *col1Pos, 
                                   unsigned int *col2, int *col2Pos) 
{ 
    int x, it; 
    unsigned int color[2] = {0, 0}; 
    int colorFound[2] = {0, 0}; 
    int colorPos[2] = {0, 0}; 
    for (x = 0; x < img->width; x++) { 
        unsigned int clr = getPixel(img, x, row); 
        for ( it = 0; it < 3; it++) { 
            if (it == 2) { 
                /* There are more then two colors */
                return 3; 
            } 
            if (!colorFound[it]) { 
                colorFound[it] = 1; 
                color[it] = clr; 
                colorPos[it] = x; 
                break; 
            } else if (color[it] == clr) { 
                if (it == 0) { 
                    colorPos[it] = x; 
                } 
                break; 
            } 
        } 
    } 
    if (color[0] > color[1]) { 
        *col1 = color[1]; 
        *col2 = color[0]; 
        *col1Pos = colorPos[1]; 
        *col2Pos = colorPos[0]; 
    } else { 
        *col1 = color[0]; 
        *col2 = color[1]; 
        *col1Pos = colorPos[0]; 
        *col2Pos = colorPos[1]; 
    } 
    return colorFound[1] ? 2 : 1; 
} 

/*-------------------------------------------------------------------*//*! 
* \brief   This function is designed for comparing images with two-color 
           gradients. It was originally created for the test H10317. 
           For each row of the image this method validates the following: 
           - There are not more than two colors (say X and Y) 
             used (exactly the same colors as in reference image). 
           - Lets assume that the leftmost pixel has color X. 
             Function calculates value iX -> location of the rightmost 
             pixel with color X and iY -> location of the leftmost 
             pixel with color Y. Value abs(iX - iY) can be treated 
             as the length of the area, along which the color changes 
             from X to Y in the given row of the image. 
             Test checks if this value is smaller than a given maximum. 
           - Lets rX and rY be the corresponding values calculated for 
             the reference image. (iX + iY)/2 and (rX + rY)/2 are treated 
             as the mid-points of color-change areas. 
             The tests makes sure that abs((iX + iY)/2 - (rX + rY)/2) is 
             smaller than a given maximal allowed difference. This value 
             is treated as the distance between color change location for 
             tested and reference image. 
           If any of above tests fail for any row, the test returns score 1. 
           Otherwise the score is 0. 

 * \param   img             Image being verified 
 * \param   ref             Reference image 
 * \param   maxAllowDiff    Maximum allowed color difference 
 * \return  Number of pixels with different color. 
 *//*-------------------------------------------------------------------*/ 

static int compareTwoColorGradient(ImageData* img, ImageData* ref, int maxAllowDiff) 
{ 
    int y; 
    int img1Pos, img2Pos; 
    unsigned int img1, img2; 
    int colors1; 

    int ref1Pos, ref2Pos; 
    unsigned int ref1, ref2; 
    int colors2; 

    /* For each row of the image... */
    for (y = 0; y < img->height; y++) { 
        /* For the tested image calculate the colors in the row */
        /* and the place where color changes */
        if ((colors1 = findTwoColorBoundaries(img, y, &img1, &img1Pos, &img2, &img2Pos)) == 3) { 
            /* Image has more than 2 colors */
            return 1; 
        } 

        /* For the reference image calculate the colors in the row */
        /* and the place where color changes */
        if ((colors2 = findTwoColorBoundaries(ref, y, &ref1, &ref1Pos, &ref2, &ref2Pos)) == 3) { 
            /* This should never happen - the reference image can not have more than 2 colors */
            return -1; 
        } 
        if (colors1 != colors2) { 
            /* images have different number of colors */
            return 1; 
        } 
        if (ref1 != img1 || ref2 != img2) { 
            /* The colors differ */
            return 1; 
        } 
        if (colors1 == 2 && 
            abs(img1Pos - img2Pos) > maxAllowDiff) { 
            /* The area where the color changes is too big */
            return 1; 
        } 
        if (colors1 == 2 && 
            abs(img1Pos + img2Pos - ref1Pos - ref2Pos) > 2*maxAllowDiff) { 
            /* Location where the color changes in the image is too far from the point in reference image */
            return 1; 
        } 
    } 
    return 0; 
} 

int H10317Comparison_by_NVIDIA(FILE* srcFile, FILE* refFile) 
{ 
    ImageData*  src         = NULL; 
    ImageData*  ref         = NULL; 

    /*--------------------------------------------------------------------- 
     * Import data from the image that is in the given format 
     *-------------------------------------------------------------------*/ 
    src = createImageFromTGA(srcFile, 0); 
    ref = createImageFromTGA(refFile, 0); 
    
    if (src == 0 || ref == 0) 
    { 
        if ( src )
            destroyImage(src);
        if ( ref )
            destroyImage(ref);            
        return CT_INVALID_SCORE; 
    }
	{
		int result = compareTwoColorGradient(src, ref, 10);

		destroyImage(src);
		destroyImage(ref);
	    
		return result;
	}
} 

int BoundaryTest_by_ATI (FILE *AnsTGA, float radius, float limit)
{
    unsigned int curColor;
    int i, j;
    int internalErrorCount = 0;
    int externalErrorCount = 0;
    float d2Origin;
    float radius2externalLimit = (radius + limit) * (radius + limit);
    float radius2internalLimit = (radius - limit) * (radius - limit);
    const unsigned int fullColor = pack(0xFF, 0xFF, 0xFF, 0xFF, 0x0);

    ImageData* img = createImageFromTGA(AnsTGA, 0);
    if ( !img )
      return CT_INVALID_SCORE;

    for (j = 0; j < img->height; j ++)
    {
        for (i = 0; i < img->width; i ++)
        {
            curColor = getPixel(img,i,img->height-j-1);
            d2Origin = ((float)i + 0.5f)*((float)i + 0.5f) + ((float)j + 0.5f)*((float)j + 0.5f);
            if (d2Origin > radius2externalLimit && (curColor & 0xFFFFFF) != 0x0)
                externalErrorCount ++;
            else if (d2Origin < radius2internalLimit && curColor != fullColor)
                internalErrorCount ++;
        }
    }
    return externalErrorCount + internalErrorCount;
}


