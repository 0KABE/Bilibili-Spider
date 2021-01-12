from os import listdir
from os.path import isfile, join

import json

if __name__ == '__main__':
    onlyfiles = [f for f in listdir('json') if isfile(join('json', f))]
    data = []
    for file in onlyfiles:
        with open('json/' + file, 'r') as f:
            data += json.load(f)

    with open('output.json', 'w') as f:
        json.dump(data, f)
    print(onlyfiles)
