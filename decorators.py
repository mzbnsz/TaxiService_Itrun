"""Журнал успешных действий с заказами."""
from datetime import datetime
from functools import wraps
from pathlib import Path
import logging


# Декоратор получает метод и добавляет запись его действий в журнал
def log_action(function):

    # Сохраняем имя и описание исходного метода.
    # Без wraps имя декорированного метода стало бы wrapper.
    @wraps(function)
    def wrapper(self, *args, **kwargs):

        # Вызываем исходный метод и сохраняем возвращённый заказ.
        # self — объект TaxiService.
        # args — позиционные аргументы, kwargs — именованные.
        # Если метод вызовет ошибку, запись в журнал не выполнится.
        result = function(self, *args, **kwargs)

        # Записываем действие, только если указан путь к журналу
        if self.log_path is not None:
            try:

                # Получаем путь и создаём недостающие родительские папки.
                # exist_ok=True разрешает использовать существующую папку.
                path = Path(self.log_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                # Режим "a" добавляет записи в конец, сохраняя предыдущие.
                # with автоматически закроет файл после работы.
                with path.open("a", encoding="utf-8") as stream:

                    # Записываем дату и время, название метода и ID заказа.
                    # \n переносит следующую запись на новую строку.
                    stream.write(
                        f"{datetime.now().isoformat(timespec='seconds')} | "
                        f"{function.__name__} | order_id={result.order_id}\n"
                    )

            # Ошибка записи журнала не отменяет выполненное действие.
            # %s заменяется текстом ошибки из переменной exc.
            except OSError as exc:
                logging.warning(
                    "Действие выполнено, но журнал не записан: %s",
                    exc
                )

        # Возвращаем заказ тому, кто вызвал метод сервиса
        return result

    # Возвращаем функцию-обёртку, не вызывая её
    return wrapper