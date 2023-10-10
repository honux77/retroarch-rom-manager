import json
import os
from os import path

configJson = json.load(open('config.json', 'r'))

ROM_PATH = configJson['basePath']
TARGET_PATH = configJson['targetPath']
LAST_ROM = configJson['lastRom']

EXT = configJson['ext']
XML_LIST = configJson['xmlList']
BASE_IMAGE = configJson['baseImage']
ICON = configJson['icon']
