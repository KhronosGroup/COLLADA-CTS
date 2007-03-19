PyramidDiff Command Line Interface:

PyramidDiff is dependent on several open source projects: libpng and zlib. The 
source code for libpng and zlib are not allowed to be included in this svn 
repository. You can download them at http://www.libpng.org/pub/png/libpng.html 
and http://www.zlib.net/ respectively. Unzip libpng to 
CTF/PyramidDiff/source/libpng so that CTF/PyramidDiff/source/libpng/png.h now
exists. Also unzip zlib to CTF/PyramidDiff/source/zlib so that
CTF/PyramidDiff/source/zlib/zlib.h exists. 

At the time of writing, the latest versions of these projects are libpng 1.2.16
and zlib 1.2.3.

Now it should be possible to compile PyramidDiff using the standard method in
Visual Studio 2005 using CTF/PyramidDiff/make/PyramidDiff.sln. Note that the 
Visual Studio Conversion Wizard may show up if the libpng and zlib projects
are for previous versions of Visual Studio.
