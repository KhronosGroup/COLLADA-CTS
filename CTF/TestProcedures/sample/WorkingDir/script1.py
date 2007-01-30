import win32api
import subprocess
import time
import os
import sys

def GetDirectoryStatistics(path):
    fileCount = 0
    dirCount = 0
    size = 0
    for root, dirs, files in os.walk(path):
        fileCount = fileCount + len(files)
        dirCount = dirCount + len(dirs)
        for file in files:
            size = size + os.path.getsize(os.path.join(root, file))
    return (size, fileCount, dirCount)

logFilename = "C:\\work\\package\\CTF_1.3\\TestProcedures\\sample\\Test50\\Execution_2006_07_28_(0)\\step1\\step1.log"
if (logFilename == None):
    log = None
else:
    log = open(logFilename, "a")
p = subprocess.Popen('"C:\\work\\package\\CTF_1.3\\Feeling_Viewer_1.1.1\\FViewerCLIR.exe" -backColor 0x00000000 -cam testCamera -width 300 -height 300 -startFrame 0.0 -endFrame 0.0 -numFrame 1 "C:\\work\\package\\CTF_1.3\\StandardDataSets\\Collada\\09_FXComposer\\Demon\\Demon.dae" "C:\\work\\package\\CTF_1.3\\TestProcedures\\sample\\Test50\\Execution_2006_07_28_(0)\\step1\\Demon.png"', stdout = log, stderr = subprocess.STDOUT)
watcher = subprocess.Popen('"C:\\work\\package\\CTF_1.3\\Core\\FileWatcher.exe" "C:\\work\\package\\CTF_1.3\\TestProcedures\\sample" 60000')
while ((p.poll() == None) and (watcher.poll() == None)):
    time.sleep(1)
if (watcher.poll() == None):
    handle = win32api.OpenProcess(1, 0, watcher.pid)
    win32api.TerminateProcess(handle, 0)
    win32api.CloseHandle(handle)
if (p.poll() == None):
    handle = win32api.OpenProcess(1, 0, p.pid)
    win32api.TerminateProcess(handle, 0)
    win32api.CloseHandle(handle)
    if (log != None):
        log.close()
    sys.exit(1)
if (log != None):
    log.close()

