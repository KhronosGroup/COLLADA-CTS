// Copyright (c) 2012 The Khronos Group Inc.// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to // the following conditions: // The above copyright notice and this permission notice shall be included // in all copies or substantial portions of the Materials. // THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

using System;
using System.IO;
using System.Diagnostics;

namespace FileWatcher
{
	/// <summary>
	/// Summary description for Class1.
	/// </summary>
	class Class1
	{
		/// <summary>
		/// The main entry point for the application.
		/// </summary>
		[STAThread]
		static void Main(string[] args)
		{
            if (args.Length != 2) 
            {
                PrintUsage();
                return;
            }

            string filepath = args[0];
            int waitTime = Convert.ToInt32(args[1]);

            FileSystemWatcher watcher = new FileSystemWatcher();
            watcher.Path = filepath;
            watcher.Filter = "";
            watcher.IncludeSubdirectories = true;

            WaitForChangedResult result;
            do
            {
                result = watcher.WaitForChanged(WatcherChangeTypes.All, 
                                                waitTime);
            } while (!result.TimedOut);

            Console.WriteLine("timedout!");
		}

        static void PrintUsage()
        {
            Console.WriteLine(
"Usage: FileWatcher <directory> <time>\n" +
"where:\n" +
"    directory    The directory to watch. Must be absolute path.\n" +
"    time         The amount of time with no disk activity to wait before \n" +
"                 returning in milliseconds.\n");
        }
	}
}
