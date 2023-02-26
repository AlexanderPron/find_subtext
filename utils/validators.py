import io


def file_validate(file_path: str, file_types=[]) -> bool:
    if file_types:
        ftype = file_path.split('.')[-1]
        if ftype and (ftype not in file_types):
            raise TypeError(f'{ftype}-файлы пока не поддерживаются')
        else:
            try:
                f = io.open(file_path)
                f.close
                return True
            except (FileExistsError, FileNotFoundError):
                raise FileExistsError('Не верный путь к файлу или имя файла')
    else:
        try:
            f = io.open(file_path)
            f.close
            return True
        except (FileExistsError, FileNotFoundError):
            raise FileExistsError('Не верный путь к файлу или имя файла')


def number_validate(val: any) -> bool:
    try:
        if int(val) > 1:
            return True
        else:
            raise ValueError
    except ValueError:
        raise ValueError(f'{val} не допустимое число. Введите целое число большее 1')
