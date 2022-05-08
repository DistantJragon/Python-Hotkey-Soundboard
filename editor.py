import json
print('Enter "c" to go back or cancel')
while True:
    print('Choose what you want to edit\n1. Sound Entries\n2. Options')
    userWish = input()
    if userWish == 'c':
        break
    elif userWish == '1':
        while True:
            break
    elif userWish == '2':
        print()
        jsonFile = open('optionsList.json')
        jsonData = json.load(jsonFile)
        options = jsonData['options']
        optionKeys = options.keys()
        i = 1
        for option in options:
            currentOption = options[option]
            print('{}. {}: {}\n     {}\n'.format(i, option, currentOption['state'], currentOption['description']))
            i += 1
        while True:
            userWish = input()
            if userWish == 'c':
                break
            else:
                try:
                    userWish = int(userWish)
                except ValueError:
                    print('Invalid choice\n')
            
    else:
        print('Invalid choice\n')