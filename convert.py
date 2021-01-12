from os import listdir
from os.path import isfile, join

from json_excel_converter import Converter
from json_excel_converter.xlsx import Writer

import json

if __name__ == '__main__':
    onlyfiles = [f for f in listdir('json') if isfile(join('json', f))]
    data = []
    for file in onlyfiles:
        with open('json/' + file, 'r') as f:
            data += json.load(f)

    conv = Converter()
    conv.convert(data, Writer(file='output.xlsx'))
    print('Convert to Xlsx success!')
