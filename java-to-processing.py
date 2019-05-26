import sys
import os
import shutil
import distutils.core
import getopt

def usage():
    print("usage: python java-to-processing.py <source dir> <dest dir> [options...]")
    print("options: ")
    print("    -o  --overwrite    Overwrite files in destination folder")
    print("        --noformat     Do not attempt some basic formatting,\n" + 
            "                     use if it produces weirdly formatted code")
    print("    -h  --help         this cruft")
    print("        --version      displays the version of this script")
    #print("    -v  --verbose      enable verbose logging")
    sys.exit()

if (len(sys.argv) < 3):
    if ("--version" in sys.argv):
        print("[Version] 2.5.0")
        sys.exit()
    else:
        usage()

def getJavaFiles(sourceFolder):
    javaFiles = []
    for (root, dirs, files) in os.walk(sourceFolder):
        ### LOCATE .JAVA FILES ###
        for name in files:
            if (os.path.splitext(name)[-1]==".java" and not name.__contains__("Sketch.java")):
                print("     %s" % os.path.join(root, name))
                javaFiles.append((os.path.join(root, name), name))
    return javaFiles

def getDataFolder(sourceFolder):
    for (root, dirs, files) in os.walk(sourceFolder):
        ### LOCATE DATA DIRECTORY ###
        for name in dirs:
            if (name=="data" and "src" in root):
                return os.path.join(root, name)
    return None


### IF DATA FOLDER PRESENT WRITE TO DEST ###
def copyDataFolder(dataFolder, destFolder, overwrite):
    if (overwrite):
        try:
            distutils.dir_util.copy_tree(dataFolder, destFolder + "/data")
        except distutils.core.DistutilsError as e:
            print('Error: %s' % e)
    else:
        try:
            shutil.copytree(dataFolder, destFolder + "/data")
        # Directories are the same
        except shutil.Error as e:
            print('Directory not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Directory not copied. Error: %s' % e)

### PARSING METHODS ###
def findEndBracket(lines, start):
    openBrackets = 0
    for x in range(start, len(lines)):
        line = lines[x].replace(" ", "")

        if (line.find("{", len(line)-2) > -1):
            openBrackets += 1
        if (line.find("}", 0, 1) > -1):
            openBrackets -= 1
            if (openBrackets==0):
                return x

def getMainMethod(javaFiles):
    for file, name in javaFiles:
        file = open(file, "r")
        lines = file.readlines()

        if (isMainMethod(lines)): 
            return name


### Statement Parsers ###
def isImport(line): 
        line = line.replace(" ", "")
        if (line.find("import", 0, 6) > -1):
            return line.__contains__("processing.")
        return False

def isPackage(line): return line.find("package", 0, 7) > -1

def isMainMethod(lines):
    if (str(lines).__contains__("public static void main(")): return True
    return False

### File Parsers ###
def parseGeneric(lines):
    ### CONVERT JAVA CLASS TO PROCESSING PDE ###
    removeIndexes = []
    for idx, line in enumerate(lines):
        if (isPackage(line)):
            removeIndexes.append(idx)
        elif (isImport(line)):
            removeIndexes.append(idx)
    
    _lines = []
    removeIndexes = set(removeIndexes)

    for idx, line in enumerate(lines):
        if (idx not in removeIndexes):
            _lines.append(line)
        
    return _lines

def formatMainMethod(line):
    if (line.find("    ", 0, 4) > -1):
        if (not line=="\n"):
            line = line[4:-1] # Remove 4 spaces from the beginning of line, to account for removal of main class
            line += "\n"
    return line

def isClassHeader(line):
    line = line.replace(" ", "")
    if (line.find("extendsPApplet{", len(line)-16) > -1):
        return True
    return False

def isJavaMainFunction(line):
    line = line.replace(" ", "")
    if (line.find("publicstaticvoidmain(String", 0, 28) > -1):
        return True
    return False

def parseMainMethod(lines):
    removeIndexes = []
    for idx, line in enumerate(lines):
        if (formatCode): 
            lines[idx] = formatMainMethod(line)
        if (isClassHeader(line)):
            removeIndexes.append(idx)
            y = findEndBracket(lines, idx)
            removeIndexes.append(y)
        elif (isJavaMainFunction(line)):
            y = findEndBracket(lines, idx)
            
            #print(list(range(idx,y+1)))
            #print([lines[x] for x in range(idx,y+1)])
            removeIndexes.extend(range(idx,y+1))
            
    
    # Return array minus the remove indexes
    _lines = []
    removeIndexes = set(removeIndexes)

    for idx, line in enumerate(lines):
        if (idx not in removeIndexes):
            _lines.append(line)
        
    return _lines

formatCode = True

def main():
    global formatCode
    ### Script Vars ###
    overwrite = False
    verbose = False

    sourceFolder = sys.argv[1]
    destFolder = sys.argv[2]

    ### Parse Options ###
    try:
        opts, args = getopt.getopt(sys.argv[3:], "hvo", ["help", "version", "verbose", "noformat", "overwrite"])
    except:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-o", "--overwrite"):
            print("-o")
            overwrite = True
        elif opt in ("--noformat"):
            formatCode = False
        elif opt in ("-v", "--verbose"):
            verbose = True

    print("[Java Files]")
    javaFiles = getJavaFiles(sourceFolder)

    mainMethod = getMainMethod(javaFiles)
    destFolder = os.path.join(destFolder, os.path.splitext(mainMethod)[0])

    print("[source] %s" % sourceFolder)
    print("[dest] %s" % destFolder)
    print("[overwrite] %s" % overwrite)
    print("[formatCode] %s" % formatCode)

    dataFolder = getDataFolder(sourceFolder)
    print("[Data Folder] %s" % dataFolder)

    print("[Main Method] %s" % mainMethod)
    print()

    answer = input("Is this information correct. Continue and Convert? [y/n]: ")
    if (answer.lower()!="y"): quit()
    
    if (dataFolder != None): copyDataFolder(dataFolder, destFolder, overwrite)

    # Create folder for main method
    if (not os.path.exists(destFolder)): 
        os.makedirs(destFolder)

    for file, name in javaFiles:
        file = open(file, "r")
        lines = file.readlines()

        if (name == mainMethod):
            print("Parsing Main Method")
            lines = parseMainMethod(lines)
        
        lines = parseGeneric(lines)

        #for line in lines:
            #print(line, end='')
        #    pass

        ### Write Output File ###

        destPath = "%s/%s.pde" % (destFolder, os.path.splitext(name)[0])
        if (overwrite==False and os.path.isfile(destPath)): 
            print("File already exists, to overwrite use --overwrite")
        else:
            file = open(destPath, "w")
            file.writelines(lines)
            file.close()

if __name__ == '__main__':
    main()
        
        
        




   
