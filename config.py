import json
import os
from os import path

configJson = json.load(open('config.json', 'r'))

ROM_PATH = configJson['basePath']
EXT = configJson['ext']
XML_LIST = configJson['xmlList']
