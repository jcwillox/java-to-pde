# Java Project to Processing Project Converter
A simple python script that will convert java projects (e.g. created in IntelliJ or Eclipse) using the processing library to projects compatible with the processing IDE (".pde" files). This is still quite experimental so use with care.

## Usage
```
usage: python java-to-processing.py <source dir> <dest dir> [options...]
options:
    -o  --overwrite    Overwrite files in destination folder
        --noformat     Do not attempt some basic formatting,
                     use if it produces weirdly formatted code
    -h  --help         this cruft
        --version      displays the version of this script
    -v  --verbose      enable verbose logging
```
 
## Examples
Using python:

`python java-to-processing.py "C:\java\project" "C:\processing"`

Using the compiled binary:

`java-to-processing.exe "C:\java\project" "C:\processing"`

