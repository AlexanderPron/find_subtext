from utils.OrderedSet import OrderedSet
import docxpy
import fitz
import io

from utils.constants import (
    russianAlphabet,
    englishAlphbet,
    digits,
)
from utils.dataObjects import WordData

eng_rus_alphabet = set.union(russianAlphabet, englishAlphbet, digits)


def docx_to_txt(file_pathname):
    text = docxpy.process(file_pathname)
    return text


def pdf_to_txt(file_pathname):
    doc = fitz.open(file_pathname)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def get_text_from_file(file_pathname: str):
    type_file = file_pathname.split('.')[-1].lower()
    encoding_list = ['utf-8', 'cp1251']
    if type_file == 'docx':
        return docx_to_txt(file_pathname)
    elif type_file == 'pdf':
        return pdf_to_txt(file_pathname)
    else:
        for encode in encoding_list:
            try:
                with io.open(file_pathname, encoding=encode) as f:
                    txt = f.read()
                    return txt
            except UnicodeDecodeError:
                continue
        raise ValueError(f'Не подходящая кодировка файла {file_pathname.split("//")[-1]}\nПопробуйте \
перекодировать его в utf-8 или windows-1251')


def compareTwoTexts(txt1, txt2, alphabet=eng_rus_alphabet):
    # txt1 should be the shorter one
    ngramd1 = extractNGrams(txt1, alphabet)
    ngramd2 = extractNGrams(txt2, alphabet)
    return extractCommonPassages(getCommonNGrams(ngramd1, ngramd2))


def extractNGrams(txt, alphabet):
    ''' На входе текст и алфавит
    На выходе словарь: ключ - биграмма(2 слова через пробел), значение - список номеров первых слов биграммы
    П.С. номер слова - порядковый номер слова в файле txt
    Например: {'пьеса реанимация': [0, 25], ...} - слово "пьеса" биграммы "пьеса реанимация"
    в файле txt по счёту первое и 26-ое '''

    words = extractWords(txt, alphabet)
    ngrams = []
    for i in range(len(words) - 1):
        ngrams.append(
            (words[i] + ' ' + words[i + 1], i)
        )
    ngramDic = {}
    for ngram in ngrams:
        try:
            ngramDic[ngram[0]].append(ngram[1])
        except KeyError:
            ngramDic[ngram[0]] = [ngram[1]]
    return ngramDic


def extractWords(s, alphabet):
    arr = []
    temp = []
    for char in s.lower():
        if char in alphabet or char == '-' and len(temp) > 0:
            temp.append(char)
        else:
            if len(temp) > 0:
                arr.append(''.join(temp))
                temp = []
    if len(temp) > 0:
        arr.append(''.join(temp))
    return arr


def getReverseDic(ngramDic):
    reverseDic = {}
    for key in ngramDic:
        for index in ngramDic[key]:
            reverseDic[index] = key
    return reverseDic


def getCommonNGrams(ngramDic1, ngramDic2):
    # ngramDic1 should be for the shorter text
    allCommonNGrams = []
    for nGram in ngramDic1:
        if nGram in ngramDic2:
            for i in ngramDic1[nGram]:
                for j in ngramDic2[nGram]:
                    allCommonNGrams.append((nGram, i, j))
    allCommonNGrams.sort(key=lambda x: x[1])
    commonNGramSet = OrderedSet((item[1], item[2]) for item in allCommonNGrams)
    return commonNGramSet


def extractCommonPassages(commonNGrams):
    if not commonNGrams:
        raise ValueError('Нет биграмм или неверная кодировка файла')
    commonPassages = []
    temp = []
    while commonNGrams:
        if not temp:
            temp = [commonNGrams.popFirst()]
            if not commonNGrams:
                break
        if (temp[-1][0] + 1, temp[-1][1] + 1) in commonNGrams:
            temp.append((temp[-1][0] + 1, temp[-1][1] + 1))
            commonNGrams.discard((temp[-1][0], temp[-1][1]))
        else:
            commonPassages.append(temp)
            temp = []
    if temp:
        commonPassages.append(temp)
    return commonPassages


def bigramlist_to_wordslist(words: list, bg_list: list) -> list:
    rezlist = []
    temp = -1
    for bg in bg_list:
        wlist = []
        k = 0
        for item in bg:
            if k == 0:
                if temp == item[0]:
                    continue
                wlist.extend([words[item[0]], words[item[0] + 1]])
                k += 1
                temp = item[0]
            else:
                wlist.append(words[item[0] + 1])
                temp = item[0]
        if wlist:
            rezlist.append(wlist)
    return rezlist


def ext_extractWords(s: str, alphabet) -> list[WordData]:
    arr = []
    temp = []
    char_pos = 0
    curr_line = 1
    word_number = 0
    lines = s.split('\n')
    for line in lines:
        temp = []
        for char in line.lower():
            if char in alphabet or char == '-' and len(temp) > 0:
                temp.append(char)
            else:
                if len(temp) > 0:
                    word = WordData(
                        word=''.join(temp),
                        first_symbol_pos=char_pos - len(temp),
                        line_num=curr_line,
                        wnumber=word_number
                    )
                    arr.append(word)
                    word_number += 1
                    temp = []
            char_pos += 1
        if len(temp) > 0:
            word = WordData(
                word=''.join(temp),
                first_symbol_pos=char_pos - len(temp),
                line_num=curr_line,
                wnumber=word_number
            )
            arr.append(word)
        curr_line += 1
        char_pos += 1
    return arr


def compare_txt(path_file1, path_file2, min_words):
    try:
        txt1 = get_text_from_file(path_file1)
        txt2 = get_text_from_file(path_file2)
    except ValueError as e:
        return e

    words1 = extractWords(txt1, alphabet=eng_rus_alphabet)
    words2 = extractWords(txt2, alphabet=eng_rus_alphabet)
    ext_words1 = ext_extractWords(txt1, alphabet=eng_rus_alphabet)
    ext_words2 = ext_extractWords(txt2, alphabet=eng_rus_alphabet)
    sub = ''
    if len(words1) <= len(words2):
        try:
            subtext_bigrams = compareTwoTexts(txt1, txt2)
        except ValueError as e:
            return e
        ext_words = ext_words1
        tmp = ext_words2
        txt = txt1
        file_name1 = path_file1.split('\\')[-1]
        file_name2 = path_file2.split('\\')[-1]
    else:
        subtext_bigrams = compareTwoTexts(txt2, txt1)
        ext_words = ext_words2
        tmp = ext_words1
        txt = txt2
        file_name1 = path_file2.split('\\')[-1]
        file_name2 = path_file1.split('\\')[-1]
    for subtext in subtext_bigrams:
        if len(subtext) >= min_words - 1:
            line_n2 = tmp[subtext[0][1]].line_num
            line_n1 = ext_words[subtext[0][0]].line_num
            start_pos = ext_words[subtext[0][0]].first_symbol_pos
            end_pos = ext_words[subtext[-1][0] + 1].first_symbol_pos + len(ext_words[subtext[-1][0] + 1].word)
            el = txt[start_pos: end_pos]
            sub += f'\n=========================\nВ строке {line_n1} файла {file_name1} и \
в строке {line_n2} файла {file_name2}:\n{el}'
    return sub
    # parts = bigramlist_to_wordslist(words, subtext_bigrams)
    # summary = ''
    # uniq_parts = []
    # for i in parts:
    #     if i not in uniq_parts:
    #         uniq_parts.append(i)
    # for i in uniq_parts:
    #     if len(i) >= min_words:
    #         summary += f'{" ".join(i)}\n\n'
