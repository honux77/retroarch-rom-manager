# read png files in a folder and rename them
import os
import re

#read args from coomand line
import sys
if len(sys.argv) != 3:
    print("Usage: python imgEdit.py <subDir> <ext>")
    sys.exit(1)

from os import path

subdir = path.join('roms/', sys.argv[1])
os.chdir(subdir)

extName = sys.argv[2]

#read png files in current directory
files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(extName)]
for f in files:
    # from file get the name without extension
    name = os.path.splitext(f)[0]
    # remove string /(.)/ from name
    sname = re.sub(r'[\[\(][^\]\)]*[\]\)]', '', name)
    sname = sname.strip()
    # remove dot if it is last char
    while sname[-1] == '.': sname = sname[:-1]
    sname = sname.strip()
    # print name and sname
    if (name == sname): continue
    print("[{}] --> [{}]".format(name, sname))
    os.rename(f, sname + "." + extName)

    

    
