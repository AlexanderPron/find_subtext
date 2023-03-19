import io
from utils.exceptions import (
    Info_exception,
)


def file_validate(file_path: str, file_types=[]) -> str or bool:
    if file_types:
        ftype = file_path.split('.')[-1]
        if ftype and (ftype not in file_types):
            raise Info_exception(f'{ftype}-файлы пока не поддерживаются')
        else:
            try:
                f = io.open(file_path)
                f.close
                return ftype
            except (FileExistsError, FileNotFoundError):
                raise Info_exception('Не верный путь к файлу или имя файла')
    else:
        try:
            f = io.open(file_path)
            f.close
            return True
        except (FileExistsError, FileNotFoundError):
            raise Info_exception('Не верный путь к файлу или имя файла')


def number_validate(val: any) -> int:
    try:
        if int(val) > 1:
            return int(val)
        else:
            raise ValueError
    except ValueError:
        raise Info_exception(f'{val} не допустимое число. Введите целое число большее 1')
