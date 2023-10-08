'''
롬 폴더의 서브폴더에서 비어있는 폴더를 삭제한다.
'''

import os
from os import path

import config

basePath = config.ROM_PATH
os.chdir(basePath)
subDirs = [f for f in os.listdir('.') if os.path.isdir(f)]

for dir in subDirs:
    
    # remove txt files first
    files = [f for f in os.listdir(dir) if f.endswith('.txt')]
    for file in files:
        os.remove(path.join(dir, file))
        print(file + " is removed.")

    if not os.listdir(dir):
        os.rmdir(dir)
        print(dir + " is removed.")
