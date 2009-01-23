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

# Do not need in the FApplications
unitTestPath = os.path.abspath('.')
unitTestPath = unitTestPath.replace('\\', '\\\\')
print unitTestPath
mbPath = unitTestPath + '\\step0\\multi_visualscene.mb'
rdPath = unitTestPath + '\\step1'
logFilename = rdPath + "\\step1.log"
# 

# Need in the FApplications
numFrames = 15

if (logFilename == None):
    log = None
else:
    log = open(logFilename, "a")

watcher = subprocess.Popen('"C:\\Projects\\COLLADA_CTF\\trunk\\conform\\ctf\\Core\\FileWatcher.exe" "' + unitTestPath + '" 30000000')

for index in range(numFrames):
    print index
    
    p = subprocess.Popen('Render -rd "' + rdPath + '" -cam "|testCamera' + str(index) + '" -r ctfHw -x 300 -y 300 -ard 1.0 -s 1 -e 1 -b 1 -of png  -im "multi_visualscene' + str(index) + '"' + ' ' + '"' + mbPath + '"', stdout = log, stderr = subprocess.STDOUT)
    
    while ((p.poll() == None) and (watcher.poll() == None)):
        time.sleep(1)
    
    print 'One of subprocess is finished.'
    
    if (watcher.poll() == None):
        if index == numFrames - 1:
            handle = win32api.OpenProcess(1, 0, watcher.pid)
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)        
        else:
            continue
    
    if (p.poll() == None):
        print 'exit from child process'
        print p.pid
        handle = win32api.OpenProcess(1, 0, p.pid)
        win32api.TerminateProcess(handle, 0)
        win32api.CloseHandle(handle)
        if (log != None):
            log.close()
        sys.exit(1)

for index in range(numFrames):
    oldFilename = rdPath + "\\multi_visualscene"+str(index)+".png.1"
    try:
        os.rename(oldFilename, rdPath + "\\multi_visualscene"+str(index*3+1)+".png")
        print index
    except Exception, e:
        print 'Can not export'
        log = open(logFilename, "a")
        log.write("\nError: unable to rename: " + oldFilename + "\n")
        log.write(str(e) + "\n")
        log.close()