using System;
using System.Diagnostics;

namespace ProcessKiller
{
	class Class1
	{
		[STAThread]
		static void Main(string[] args)
		{
            if (args.Length != 1)
            {
                Console.WriteLine("Usage: ProcessKiller <processName>");
                return;
            }
            string processName = args[0];

            foreach (Process p in Process.GetProcessesByName(processName))
            {
                p.Kill();
            }
		}
	}
}
