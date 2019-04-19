import sys
import os
import shutil
import distutils.core

overwrite = False
formatCode = True

for arg in sys.argv:
    if (arg=="-h" or arg=="--help" or len(sys.argv) < 2):
        print("usage: python java-to-processing.py <source dir> <dest dir> {[option]}")
        print("options: ")
        print("    -o  --overwrite    Overwrite files in destination folder")
        print("    -nf --noformat     Do not attempt some basic formatting,\n" + 
              "                       use if it produces weirdly formatted code")
        print("    -h  --help         this cruft")
        print("    -v  --version      displays the version of this script")
        sys.exit()
    elif (arg=="-v" or arg=="--version"):
        print("[Version] 1.0.0")
        sys.exit()
    elif (arg=="-o" or arg=="--overwrite"):
        overwrite = True
    elif (arg=="-nf" or arg=="--noformat"):
        formatCode = False

sourceFolder = sys.argv[1]
destFolder = sys.argv[2]

print("[source] %s" % sourceFolder)
print("[dest] %s" % destFolder)
print("[overwrite] %s" % overwrite)
print("[formatCode] %s" % formatCode)

javaFiles = []

dataFolder = None

print("[Java Files]")

for (root, dirs, files) in os.walk(sourceFolder):
    ### LOCATE .JAVA FILES ###
    for name in files:
        if (name.__contains__(".java") and not root.__contains__("java\\com\\processing\\sketch") and not root.__contains__("java/com/processing/sketch")):
            print("     %s" % os.path.join(root, name))
            javaFiles.append((os.path.join(root, name), name))

    ### LOCATE DATA DIRECTORY ###
    for name in dirs:
        if (name=="data"):
            dataFolder = os.path.join(root, name)

print("[Data Folder] %s\n" % dataFolder)

answer = input("Is this information correct. Continue and Convert? [y/n]: ")
if (answer.lower()!="y"): exit()

### IF DATA FOLDER PRESENT WRITE TO DEST ###
if (dataFolder is not None):
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


### BEGIN PARSING ###

def findEndBracket(start, list):
    openBrackets = 0
    for x in range(start, len(lines)):
        line = lines[x].replace(" ", "")

        if (line.find("{", len(line)-2) > -1):
            openBrackets += 1
        elif (line.find("}", 0, 1) > -1):
            openBrackets -= 1
            if (openBrackets==0):
                return x


for file, name in javaFiles:

    def isImport(line): 
        line = line.replace(" ", "")
        if (line.find("import", 0, 6) > -1):
            return line.__contains__("processing.")
        return False

    def isPackage(line): return line.find("package", 0, 7) > -1

    def isMainMethod(lines):
        if (str(lines).__contains__("public static void main(")): return True
        return False

    file = open(file, "r")
    lines = file.readlines()

    if (isMainMethod(lines)): 
        print("[Main Method] %s" % name)

        ### SPECIAL CASE FOR MAIN METHOD ###
        
        ### CHECK IF DIRECTORY IS NAMED CORRECTLY
        # fileName = os.path.splitext(name)[0]
        # if (os.path.split(destFolder)[-1]!=fileName):
        #     destFolder += "/" + fileName


        ### REMOVE MAIN CLASS HEADER/FOOTER, ATTEMPT FORMATTING ###
        for x in range(len(lines)):
            if (x >= len(lines)): break

            line = lines[x]

            if (formatCode):
                if (line.find("    ", 0, 4) > -1):
                    if (not line=="\n"):
                        lines[x] = line[4:-1] # Remove 4 spaces from the beginning of line, to account for removal of main class
                        lines[x] += "\n"
                        
            

            line = line.replace(" ", "")
            if (line.find("extendsPApplet{", len(line)-16) > -1):
                ### FIND CLOSING BRACKET OF MAIN CLASS ###
                y = findEndBracket(x, lines)
                # print("x: %s, y: %s" % (x,y))
                # print(lines[x])
                # print(lines[y])
                del lines[y] # remove closing bracket header line    
                del lines[x] # remove beginning header line

        ### REMOVE JAVA MAIN FUNCTION ###
        for x in range(len(lines)):
            if (x >= len(lines)): break

            line = lines[x].replace(" ", "")
            if (line.find("publicstaticvoidmain(String", 0, 28) > -1):
                #del lines[x] # remove beginning header line
                
                ### FIND CLOSING BRACKET OF MAIN CLASS ###
                y = findEndBracket(x, lines)
                #print("x: %s, y: %s" % (x,y+1))
                #print(lines[x:y+1])
                del lines[x:y+1]

    ### CONVERT JAVA CLASS TO PROCESSING PDE ###
    for x in range(len(lines)):
        if (x >= len(lines)): break

        if (isPackage(lines[x])):
            del lines[x]
        elif (isImport(lines[x])):
            lines[x] = ""

    # for x in range(10):
    #     try:
    #         lines.remove(None)
    #     except:
    #         pass
        

    for line in lines:
        #print(line)
        pass

    destPath = "%s/%s.pde" % (destFolder, os.path.splitext(name)[0])
    if (overwrite==False and os.path.isfile(destPath)): print("File already exists, to overwrite use --overwrite")
    else:
        file = open(destPath, "w")
        for line in lines:
            file.write(line)
        file.close()

print("Conversion Complete!")
        
        
        
        




   
