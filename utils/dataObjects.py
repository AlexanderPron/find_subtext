from dataclasses import dataclass


@dataclass
class WordData:
    """Тип данных для объекта слова"""
    word: str = None  # Слово
    first_symbol_pos: int = None  # Номер позиции первого символа слова в файле
    line_num: int = None  # Номер строки, в которой находится слово
    wnumber: int = None  # Порядковый номер слова в тексте


@dataclass
class DocxWordData:
    """Тип данных для объекта слова"""
    word: str = None  # Слово
    paragraph_num: int = None  # Номер параграфа, в котором находится слово
    first_symbol_pos: int = None  # Номер позиции первого символа слова в параграфе
    wnumber: int = None  # Порядковый номер слова в тексте


@dataclass
class Subtext:
    """Тип данных для объекта подтекста"""
    quote: str = None  # цитата
    linenum_file_1: int = None  # Номер строки первого файла, в которой содержится первое слово цитаты
    linenum_file_2: int = None  # Номер строки второго файла, в которой содержится первое слово цитаты

