# read png files in a folder and rename them
import os
import re

#read args from coomand line
import sys
if len(sys.argv) != 2:
    print("Usage: python imgEdit.py <subDir>")
    sys.exit(1)

from os import path

subdir = path.join('images/', sys.argv[1])
os.chdir(subdir)

#read png files in current directory
files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.png')]
for f in files:
    # from file get the name without extension
    name = os.path.splitext(f)[0]
    
    sname = re.sub(r'\([^)]*\)', '', name)
    sname = re.sub(r'\[[^)]*\]', '', sname)


    sname = sname.strip()
    # remove dot if it is last char
    while sname[-1] == '.': sname = sname[:-1]
    sname = sname.strip()
    # print name and sname
    if (name == sname): continue
    if (os.path.exists(sname + '.png')):
        print("File exists: ", sname + '.png')
        continue    
    print("[{}] --> [{}]".format(name, sname))
    os.rename(f, sname + '.png')

    

    
