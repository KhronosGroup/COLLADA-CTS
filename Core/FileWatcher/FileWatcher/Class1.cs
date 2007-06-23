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
