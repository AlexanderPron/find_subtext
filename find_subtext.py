import io
import os
import threading
from datetime import datetime as dt
from pathlib import Path
import logging

from utils.validators import (
    file_validate,
    number_validate,
)
from utils.constants import (
    russianAlphabet,
    englishAlphbet,
    digits,
    log_file,
    result_folder,
)
from utils.exceptions import (
    Info_exception,
)
from utils.compare_docx import compare_docx
from utils.compare_txt import compare_txt
from utils.dataObjects import Subtext
from utils.docx_elements import iter_block_items

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from babel.dates import format_datetime

# imorts for test()
from docx import Document
from docx.text.run import Run
# ================


eng_rus_alphabet = set.union(russianAlphabet, englishAlphbet, digits)

os.makedirs(result_folder, exist_ok=True)

logging.basicConfig(filename=log_file, format='%(asctime)s :: %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def select_file(path_file: Entry):
    filepath = fd.askopenfilename(
        filetypes=[
            ("All supported", ".txt .docx .pdf"),
            ("Text files", ".txt"),
            ("Word files", ".docx"),
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


def clear_field(field: tk.Text, label_result: tk.Label, open_folder_btn: tk.Button):
    field.delete(1.0, END)
    label_result.grid_remove()
    open_folder_btn.grid_remove()


def progress_start(pb: ttk.Progressbar, label_result: tk.Label, open_folder_btn: tk.Button):
    label_result.grid_remove()
    open_folder_btn.grid_remove()
    pb.grid()
    pb.start(25)


def progress_stop(pb: ttk.Progressbar):
    pb.stop()
    pb.grid_remove()


def open_folder(label_result: tk.Label):
    path_folder = Path(label_result.cget('text').split('\n')[1]).resolve().parent
    os.system(f'explorer {path_folder}')


def make_output(path_file1: str, path_file2: str, subs: list[Subtext]) -> str:
    file_name1 = path_file1.split('\\')[-1]
    file_name2 = path_file2.split('\\')[-1]
    output = f'Сравнение содержимого файлов на цитирование.\n\
{format_datetime(dt.now(), format="<dd MMMM yyyy> <HH:mm:ss>", locale="ru")}\n\
Файл 1: <{file_name1}>\n\
Файл 2: <{file_name2}>\n\
Предоставление найденных  совпадений:\n'
    for sub in subs:
        output += f'[{sub.linenum_file_1}|{sub.linenum_file_2}]\n{sub.quote}\n\
*******************************************************************************\n'
    return output


def find_subtext(
    path_file1: str,
    path_file2: str,
    min_words: str,
    field: tk.Text,
    info_label: tk.Label,
    pb: ttk.Progressbar,
    label_result: tk.Label,
    open_folder_btn: tk.Button,
):
    info_label.config(text='')
    if not (path_file1 and path_file2):
        info_label.config(text='Выберите файл')
        return
    path_file1 = os.path.abspath(path_file1)
    path_file2 = os.path.abspath(path_file2)
    try:
        f1_extension = file_validate(path_file1, ['txt', 'pdf', 'docx'])
        f2_extension = file_validate(path_file2, ['txt', 'pdf', 'docx'])
        min_words = number_validate(min_words)
    except Info_exception as e:
        info_label.config(text=f'{e}')
        return
    pb.grid()
    threading.Thread(target=lambda: progress_start(pb, label_result, open_folder_btn)).start()
    created_files = ()
    if f1_extension == f2_extension == 'docx':
        try:
            created_files = compare_docx(path_file1, path_file2, min_words)
            subs = compare_txt(path_file1, path_file2, min_words)
        except Info_exception as e:
            pb.grid_remove()
            progress_stop(pb)
            info_label.config(text=f'{e}')
            return
    else:
        try:
            subs = compare_txt(path_file1, path_file2, min_words)
        except Info_exception as e:
            pb.grid_remove()
            progress_stop(pb)
            info_label.config(text=f'{e}')
            return
    output = make_output(path_file1, path_file2, subs)
    field.delete(1.0, END)
    field.insert(INSERT, output)
    progress_stop(pb)
    if created_files:
        label_result.config(
            text=f'Результаты сохранены в файлах:\n\
{created_files[0]}\n{created_files[1]}'
        )
        label_result.grid()
        open_folder_btn.grid()


def main():
    app_version = 'v.1.3 Release'
    main_window = tk.Tk()
    main_window.title(f"Поиск совпадающих подтекстов в двух текстах {app_version}")
    main_window.geometry('1150x460')
    main_window.minsize(width=500, height=460)
    main_window.columnconfigure(0, weight=0)
    main_window.columnconfigure(1, weight=2)
    main_window.rowconfigure(0, weight=1)
    main_window.rowconfigure(1, weight=0)
    frame1 = tk.LabelFrame(main_window, text='Входные данные', width=400)
    frame1.grid(column=0, row=0, padx=5, pady=5, sticky=NSEW)
    frame2 = tk.LabelFrame(main_window, text='Выходные данные')
    frame2.grid(column=1, row=0, padx=5, pady=5, sticky=NSEW)
    frame3 = tk.Frame(main_window)
    frame3.grid(column=0, row=1, padx=5, pady=5, sticky=NSEW, )
    frame4 = tk.Frame(main_window)
    frame4.grid(column=1, row=1, padx=5, pady=5, sticky=NSEW)

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
    min_words_field.insert(0, '10')
    min_words_field.grid(column=0, row=5, padx=5, pady=5, sticky=W)

    info_label = Label(frame1, text='', anchor=W, fg='red', wraplength=200)
    info_label.grid(column=0, row=6, padx=5, pady=5, sticky=EW)

    pb = ttk.Progressbar(
        frame4,
        orient='horizontal',
        mode='indeterminate',
        length=200,
    )
    pb.grid(column=0, row=0, padx=5, pady=5, sticky=W)
    pb.grid_remove()

    label_result = Label(frame4, text='', anchor=E, justify=LEFT)
    label_result.grid(column=0, row=0, padx=5, pady=5, sticky=NSEW)
    label_result.grid_remove()

    open_folder_btn = Button(frame4, text='Открыть папку...', command=lambda: open_folder(label_result))
    open_folder_btn.grid(column=0, row=1, padx=5, pady=5, sticky=W)
    open_folder_btn.grid_remove()

    SVBar = tk.Scrollbar(frame2)
    SVBar.pack(side=tk.RIGHT, fill="y")
    TBox = tk.Text(
        frame2,
        yscrollcommand=SVBar.set,
        wrap="word",
    )
    TBox.pack(expand=1, fill=tk.BOTH)
    SVBar.config(command=TBox.yview)
    start_btn = Button(
        frame3,
        text='Старт',
        command=lambda: threading.Thread(
            target=lambda: find_subtext(
                path_file1.get(),
                path_file2.get(),
                min_words_field.get(),
                TBox,
                info_label,
                pb,
                label_result,
                open_folder_btn,
            )
        ).start()
    )
    save_to_file_btn = Button(
        frame3,
        text='Сохранить',
        command=lambda: save_to_file(TBox)
    )
    clear_btn = Button(
        frame3,
        text='Очистить',
        command=lambda: clear_field(TBox, label_result, open_folder_btn)
    )
    quit_app_btn = Button(
        frame3,
        text='Выход',
        command=main_window.destroy
    )
    empty_label = Label(frame3, text='\n\n')
    empty_label.grid(column=0, row=1, padx=5, pady=5, sticky=NSEW)
    start_btn.grid(column=0, row=2, padx=5, pady=5)
    save_to_file_btn.grid(column=1, row=2, padx=5, pady=5)
    clear_btn.grid(column=2, row=2, padx=5, pady=5)
    quit_app_btn.grid(column=3, row=2, padx=5, pady=5)

    main_window.mainloop()


def test():
    path_file1 = 'D:\develop\ОТЧЕТ_ЭНЕРДЖИНЕТ_ФИНАЛ_в_отправку_13_12_2022.docx'
    f = open(path_file1, 'rb')
    document1 = Document(f)
    f.close()
    elements = iter_block_items(document1)
    i = 0
    while True:
        try:
            print(i)
            print(next(elements))
            i += 1
        except StopIteration:
            break


if __name__ == '__main__':
    try:
        # main()
        test()
    except Exception as e:
        logger.exception(msg=e, exc_info=True)
