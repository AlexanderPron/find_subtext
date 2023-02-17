from utils.OrderedSet import OrderedSet
import io
from difflib import SequenceMatcher


russianAlphabet = {
    'й', 'ф', 'я', 'ц', 'ы', 'ч', 'у', 'в', 'с', 'к', 'а',
    'м', 'е', 'п', 'и', 'н', 'р', 'т', 'г', 'о', 'ь', 'ш',
    'л', 'б', 'щ', 'д', 'ю', 'з', 'ж', 'х', 'э', 'ъ', 'ё'
}


def compareTwoTexts(txt1, txt2, alphabet=russianAlphabet):
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
        raise ValueError('no common ngrams')
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


# def bigram_to_wordslist(words: list, bg: tuple) -> list:
#     """ ВАЖНО: В кортеже биграммы bg первым элементом должен быть порядковый номер слова из текста text"""
#     wlist = [words[bg[0]], words[bg[0] + 1]]
#     return wlist


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


def main():
    with io.open('data/1_smaller.txt', encoding='utf-8') as f:
        txt1 = f.read()
    with io.open('data/1_bigger.txt', encoding='utf-8') as f:
        txt2 = f.read()
    subtext_bigrams = compareTwoTexts(txt1, txt2)

# =========== Вариант 1 ======================================

    words = extractWords(txt1, alphabet=russianAlphabet)
    parts = bigramlist_to_wordslist(words, subtext_bigrams)
    summary = ''
    for i in parts:
        summary += f"{' '.join(i)}\n============================================\n"
    with io.open('rezult.txt', mode='w+', encoding='utf-8') as f:
        f.write(f'{summary}')

# =========== Вариант 2. Будет чуть позже =====================

# =============================================================
    # with io.open('rezult.txt', mode='w+', encoding='utf-8') as f:
    #     f.write(f'{summary}')


if __name__ == '__main__':
    main()
