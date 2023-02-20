from utils.OrderedSet import OrderedSet
import io
from utils.validators import (
    file_validate,
    number_validate
)

from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd

import textractplus as tp
import fitz


def select_file(path_file: Entry):
    filepath = fd.askopenfilename(
        filetypes=[
            ("All supported", ".txt .doc .docx .rtf .pdf"),
            ("Text files", ".txt"),
            ("Word files", ".doc .docx .rtf"),
            ("PDF files", ".pdf"),
        ]
    )
    if filepath != "":
        path_file.delete(0, END)
        path_file.insert(0, filepath)


def save_to_file(field: tk.Text):
    filepath = fd.asksaveasfilename(defaultextension='.txt', filetypes=[("Text files", ".txt")])
    if filepath != "":
        with io.open(filepath, mode='w+', encoding='utf-8') as f:
            f.write(f'{field.get(1.0, END)}')


def clear_field(field: tk.Text):
    field.delete(1.0, END)


def doc_to_txt(file_pathname):
    text = tp.process(file_pathname, encoding='utf-8')
    text = text.decode('utf-8')
    return text


def pdf_to_txt(file_pathname):
    doc = fitz.open(file_pathname)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def get_text_from_file(file_pathname: str):
    type_file = file_pathname.split('.')[-1].lower()
    if type_file in ['doc', 'docx', 'rtf']:
        return doc_to_txt(file_pathname)
    elif type_file == 'pdf':
        return pdf_to_txt(file_pathname)
    else:
        with io.open(file_pathname) as f:
            txt = f.read()
        return txt


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


def process(path_file1: str, path_file2: str, min_words: str, field: tk.Text, info_label: tk.Label):
    info_label.config(text='')
    try:
        file_validate(path_file1, ['txt', 'pdf', 'docx'])
    except TypeError as e:
        info_label.config(text=f'{e}')
        return
    except FileExistsError as e:
        info_label.config(text=f'{e}')
        return
    try:
        file_validate(path_file2, ['txt', 'pdf', 'docx'])
    except TypeError as e:
        info_label.config(text=f'{e}')
        return
    except FileExistsError as e:
        info_label.config(text=f'{e}')
        return
    try:
        number_validate(min_words)
        min_words = int(min_words)
    except ValueError as e:
        info_label.config(text=f'{e}')
        return
    txt1 = get_text_from_file(path_file1)
    txt2 = get_text_from_file(path_file2)
    words1 = extractWords(txt1, alphabet=russianAlphabet)
    words2 = extractWords(txt2, alphabet=russianAlphabet)
    if len(words1) <= len(words2):
        subtext_bigrams = compareTwoTexts(txt1, txt2)
        words = words1
    else:
        subtext_bigrams = compareTwoTexts(txt2, txt1)
        words = words2

    parts = bigramlist_to_wordslist(words, subtext_bigrams)
    summary = ''
    uniq_parts = []
    for i in parts:
        if i not in uniq_parts:
            uniq_parts.append(i)
    for i in uniq_parts:
        if len(i) >= min_words:
            summary += f'{" ".join(i)}\n'
    field.delete(1.0, END)
    field.insert(INSERT, summary)


def main():
    app_version = 'v.1.0'
    main_window = tk.Tk()
    main_window.title(f"Поиск совпадающих подтекстов в двух текстах {app_version}")
    main_window.geometry("1050x500")
    frame1 = tk.LabelFrame(main_window, text='Входные данные')
    frame1.grid(column=0, row=0, padx=5, pady=5, sticky=NSEW)
    frame2 = tk.LabelFrame(main_window, text='Выходные данные')
    frame2.grid(column=1, row=0, padx=5, pady=5, sticky=NSEW)
    frame3 = tk.Frame(main_window)
    frame3.grid(column=0, row=1, padx=5, pady=5, sticky=NSEW)

    label_f1 = Label(frame1, text='Выберите файл 1', anchor=W)
    label_f1.grid(column=0, row=0, padx=5, pady=5, sticky=EW)
    path_file1 = Entry(frame1)
    path_file1.grid(column=0, row=1, padx=5, pady=5, sticky=EW)
    choose_file1 = Button(frame1, text='Выбрать...', command=lambda: select_file(path_file1))
    choose_file1.grid(column=1, row=1, padx=5, pady=5)

    label_f2 = Label(frame1, text='Выберите файл 2', anchor=W)
    label_f2.grid(column=0, row=2, padx=5, pady=5, sticky=EW)
    path_file2 = Entry(frame1)
    path_file2.grid(column=0, row=3, padx=5, pady=5, sticky=EW)
    choose_file2 = Button(frame1, text='Выбрать...', command=lambda: select_file(path_file2))
    choose_file2.grid(column=1, row=3, padx=5, pady=5)

    label_f2 = Label(frame1, text='Минимальное количество слов совпадений', anchor=W)
    label_f2.grid(column=0, row=4, padx=5, pady=5, sticky=EW)
    min_words_field = Entry(frame1, width=5)
    min_words_field.insert(0, '5')
    min_words_field.grid(column=0, row=5, padx=5, pady=5, sticky=W)

    info_label = Label(frame1, text='', anchor=W, fg='red')
    info_label.grid(column=0, row=6, padx=5, pady=5, sticky=EW)

    SVBar = tk.Scrollbar(frame2)
    SVBar.pack(side=tk.RIGHT, fill="y")
    SHBar = tk.Scrollbar(frame2, orient=tk.HORIZONTAL)
    SHBar.pack(side=tk.BOTTOM, fill="x")
    TBox = tk.Text(
        frame2,
        yscrollcommand=SVBar.set,
        xscrollcommand=SHBar.set,
        wrap="none"
    )
    TBox.pack(expand=0, fill=tk.BOTH)
    SHBar.config(command=TBox.xview)
    SVBar.config(command=TBox.yview)

    start_btn = Button(
        frame3,
        text='Старт',
        command=lambda: process(path_file1.get(), path_file2.get(), min_words_field.get(), TBox, info_label)
    )
    save_to_file_btn = Button(
        frame3,
        text='Сохранить',
        command=lambda: save_to_file(TBox)
    )
    clear_btn = Button(
        frame3,
        text='Очистить',
        command=lambda: clear_field(TBox)
    )
    quit_app_btn = Button(
        frame3,
        text='Выход',
        command=main_window.destroy
    )
    start_btn.grid(column=0, row=0, padx=5, pady=5)
    save_to_file_btn.grid(column=1, row=0, padx=5, pady=5)
    clear_btn.grid(column=2, row=0, padx=5, pady=5)
    quit_app_btn.grid(column=3, row=0, padx=5, pady=5)

    main_window.mainloop()


if __name__ == '__main__':
    main()
