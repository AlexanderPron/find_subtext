import sys
import os
from pathlib import Path


russianAlphabet = {
    'й', 'ф', 'я', 'ц', 'ы', 'ч', 'у', 'в', 'с', 'к', 'а',
    'м', 'е', 'п', 'и', 'н', 'р', 'т', 'г', 'о', 'ь', 'ш',
    'л', 'б', 'щ', 'д', 'ю', 'з', 'ж', 'х', 'э', 'ъ', 'ё'
}

englishAlphbet = {
    'q', 'a', 'z', 'w', 's', 'x', 'e', 'd', 'c', 'r', 'f',
    'v', 't', 'g', 'b', 'y', 'h', 'n', 'u', 'j', 'm', 'i',
    'k', 'o', 'l', 'p'
}

digits = {
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
}

if getattr(sys, "frozen", False):
    (filepath, tempfilename) = os.path.split(sys.argv[0])
    BASE_DIR = Path(filepath).resolve().parent
else:
    BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__))).resolve().parent
