# test read and write json file

import json

# write json file
data = {'name': 'Honux', 'shares': 100, 'price': 542.23}

import os

# set current directory
data["path"] = os.getcwd()

with open('test.json', 'w') as f:
    json.dump(data, f)
   


# read json file
with open('test.json', 'r') as f:
    jsonData = json.load(f)

print("원본 데이터: ", data)
print("json 데이터: ", jsonData)
print("동일성 검사: ", data == jsonData)
