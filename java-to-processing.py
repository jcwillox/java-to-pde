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
    print("    -v  --verbose      enable verbose logging")
    quit()

if (len(sys.argv) < 3):
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
            if (name=="data"):
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
def findEndBracket(lines, start, list):
    openBrackets = 0
    for x in range(start, len(lines)):
        line = lines[x].replace(" ", "")

        if (line.find("{", len(line)-2) > -1):
            openBrackets += 1
        elif (line.find("}", 0, 1) > -1):
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

def parseMain():
    pass
    ### SPECIAL CASE FOR MAIN METHOD ###
        
    ### CHECK IF DIRECTORY IS NAMED CORRECTLY
    # fileName = os.path.splitext(name)[0]
    # if (os.path.split(destFolder)[-1]!=fileName):
    #     destFolder += "/" + fileName


    ### REMOVE MAIN CLASS HEADER/FOOTER, ATTEMPT FORMATTING ###
    # for x in range(len(lines)):
    #     if (x >= len(lines)): break

    #     line = lines[x]

    #     if (formatCode):
    #         if (line.find("    ", 0, 4) > -1):
    #             if (not line=="\n"):
    #                 lines[x] = line[4:-1] # Remove 4 spaces from the beginning of line, to account for removal of main class
    #                 lines[x] += "\n"
                    
        

    #     line = line.replace(" ", "")
    #     if (line.find("extendsPApplet{", len(line)-16) > -1):
    #         ### FIND CLOSING BRACKET OF MAIN CLASS ###
    #         y = findEndBracket(x, lines)
    #         # print("x: %s, y: %s" % (x,y))
    #         # print(lines[x])
    #         # print(lines[y])
    #         del lines[y] # remove closing bracket header line    
    #         del lines[x] # remove beginning header line

    # ### REMOVE JAVA MAIN FUNCTION ###
    # for x in range(len(lines)):
    #     if (x >= len(lines)): break

    #     line = lines[x].replace(" ", "")
    #     if (line.find("publicstaticvoidmain(String", 0, 28) > -1):
    #         #del lines[x] # remove beginning header line
            
    #         ### FIND CLOSING BRACKET OF MAIN CLASS ###
    #         y = findEndBracket(x, lines)
    #         #print("x: %s, y: %s" % (x,y+1))
    #         #print(lines[x:y+1])
    #         del lines[x:y+1]

        
def main():
    ### Script Vars ###
    overwrite = False
    formatCode = True
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
        elif opt in ("--version"):
            print("[Version] 1.0.0")
            sys.exit()
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
    if (not os.path.exists(dataFolder)): 
        os.makedirs(destFolder)

    for file, name in javaFiles:
        file = open(file, "r")
        lines = file.readlines()

        # if (isMainMethod(lines)): 
        #     print("[Main Method] %s" % name)
        
        lines = parseGeneric(lines)

        for line in lines:
            #print(line, end='')
            pass

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
        
        
        




   
