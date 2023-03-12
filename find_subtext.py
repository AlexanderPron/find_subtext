import io
import os
import threading

from utils.validators import (
    file_validate,
    number_validate,
)
from utils.constants import (
    russianAlphabet,
    englishAlphbet,
    digits,
)
from utils.compare_docx import compare_docx
from utils.compare_txt import compare_txt

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


eng_rus_alphabet = set.union(russianAlphabet, englishAlphbet, digits)


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


def clear_field(field: tk.Text):
    field.delete(1.0, END)


def progress_start(pb: ttk.Progressbar):
    pb.grid()
    pb.start(25)


def progress_stop(pb: ttk.Progressbar):
    pb.stop()
    pb.grid_forget()


def find_subtext(
    path_file1: str,
    path_file2: str,
    min_words: str,
    field: tk.Text,
    info_label: tk.Label,
    pb: ttk.Progressbar,
):
    info_label.config(text='')
    if not (path_file1 and path_file2):
        info_label.config(text='Выберите файл')
        return
    path_file1 = os.path.abspath(path_file1)
    path_file2 = os.path.abspath(path_file2)
    try:
        f1_extension = file_validate(path_file1, ['txt', 'pdf', 'docx'])
    except TypeError as e:
        info_label.config(text=f'{e}')
        return
    except FileExistsError as e:
        info_label.config(text=f'{e}')
        return
    try:
        f2_extension = file_validate(path_file2, ['txt', 'pdf', 'docx'])
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
    threading.Thread(target=lambda: progress_start(pb)).start()
    if f1_extension == f2_extension == 'docx':
        try:
            compare_docx(path_file1, path_file2, min_words)
            sub = compare_txt(path_file1, path_file2, min_words)
        except ValueError as e:
            info_label.config(text=f'{e}')
            return
    else:
        try:
            sub = compare_txt(path_file1, path_file2, min_words)
        except ValueError as e:
            info_label.config(text=f'{e}')
            return

    field.delete(1.0, END)
    field.insert(INSERT, sub)
    progress_stop(pb)


def main():
    app_version = 'v.1.2'
    main_window = tk.Tk()
    main_window.title(f"Поиск совпадающих подтекстов в двух текстах {app_version}")
    main_window.geometry("1050x500")
    frame1 = tk.LabelFrame(main_window, text='Входные данные')
    frame1.grid(column=0, row=0, padx=5, pady=5, sticky=NSEW)
    frame2 = tk.LabelFrame(main_window, text='Выходные данные')
    frame2.grid(column=1, row=0, padx=5, pady=5, sticky=NSEW)
    frame3 = tk.Frame(main_window)
    frame3.grid(column=0, row=1, padx=5, pady=5, sticky=NSEW)
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
    min_words_field.insert(0, '5')
    min_words_field.grid(column=0, row=5, padx=5, pady=5, sticky=W)

    info_label = Label(frame1, text='', anchor=W, fg='red', wraplength=200)
    info_label.grid(column=0, row=6, padx=5, pady=5, sticky=EW)

    SVBar = tk.Scrollbar(frame2)
    SVBar.pack(side=tk.RIGHT, fill="y")
    SHBar = tk.Scrollbar(frame2, orient=tk.HORIZONTAL)
    SHBar.pack(side=tk.BOTTOM, fill="x")
    TBox = tk.Text(
        frame2,
        yscrollcommand=SVBar.set,
        xscrollcommand=SHBar.set,
        # wrap="none"
    )
    TBox.pack(expand=0, fill=tk.BOTH)
    SHBar.config(command=TBox.xview)
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
    pb = ttk.Progressbar(
        frame4,
        orient='horizontal',
        mode='indeterminate',
        length=200,
    )
    pb.grid(column=4, row=0, padx=5, pady=5)
    pb.grid_remove()

    main_window.mainloop()


if __name__ == '__main__':
    main()
