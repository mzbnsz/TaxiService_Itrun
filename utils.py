"""Проверки данных и безопасная запись JSON."""
import json
import math
import os
import re
import tempfile
from pathlib import Path


# Общие проверки данных перед созданием и изменением объектов
class Validator:

    # Проверяем непустой текст и убираем пробелы по краям
    @staticmethod
    def text(value, label="Значение"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} не может быть пустым")
        return value.strip()

    # Разрешаем только положительный целочисленный ID
    @staticmethod
    def identifier(value):
        if type(value) is not int or value <= 0:
            raise ValueError("ID должен быть положительным целым числом")
        return value

    # Проверяем телефон: 9–15 цифр и необязательный + в начале
    @staticmethod
    def phone(value):
        if not isinstance(value, str) or not re.fullmatch(r"\+?[0-9]{9,15}", value):
            raise ValueError("Телефон: от 9 до 15 цифр, допускается + в начале")
        return value

    # Проверяем конечное положительное число; ноль разрешаем отдельно
    @staticmethod
    def number(value, label="Число", allow_zero=False):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{label} должно быть конечным числом")
        if value < 0 or (value == 0 and not allow_zero):
            raise ValueError(f"{label}: недопустимое значение")
        return value


# Проверяем наличие файла; при первом запуске возвращаем None
def read_json(path):
    path = Path(path)
    if not path.exists():
        return None

    # Читаем JSON; при повреждении вызываем понятную ошибку
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Файл данных повреждён. Исходный файл сохранён; "
            "исправьте его или переименуйте вручную."
        ) from exc


# Сохраняем данные через временный файл, защищая основной от неполной записи
def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None

    # Записываем JSON во временный файл и передаём данные на диск
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())

        # Заменяем основной файл только после успешной записи
        temporary.replace(path)

    # Удаляем оставшийся временный файл, в том числе при ошибке
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()