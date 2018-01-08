from px2path import Px2path


options = {
    'filepath': 'pxpath5x9/',
    'characters': 'ABCDEFGHIJ',
    'grid': [5,9]
}

font = Px2path(**options)
print(font.characters)
