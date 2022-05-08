import json
jsonFile = open('optionsList.json')
jsonData = json.load(jsonFile)
options = jsonData['options']
optionsStr = json.dumps(jsonData)
print(optionsStr)