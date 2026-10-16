"""Консольный интерфейс. Запуск: python3 main.py."""

# Path помогает работать с путями к папкам и файлам
from pathlib import Path

# Импортируем модели, сервис и доступные тарифы
from models import Passenger, Driver, Car
from services import TaxiService
from tariffs import StandardTariff, ComfortTariff


# Определяем папку, в которой находится main.py.
# __file__ — путь текущего файла.
# resolve() — полный путь, parent — родительская папка.
ROOT = Path(__file__).resolve().parent


# Показываем приглашение, получаем строку и преобразуем её в int.
# Например: ввод "5" → число 5.
# Если пользователь введёт "abc", возникнет ValueError.
def integer(prompt):
    return int(input(prompt))


# Выводим информацию о каждом объекте в переданном списке.
# У пассажира, водителя и заказа есть свой метод get_info().
def show(items):
    if not items:
        print("Список пуст")

    for item in items:
        print(item.get_info())


# Запрашиваем характеристики и создаём объект автомобиля.
# Возвращаем готовый Car, чтобы затем передать его водителю.
def read_car():
    return Car(
        input("Марка: "),
        input("Модель: "),
        input("Номер: "),
        input("Категория (standard/comfort): ")
    )


# По выбору пользователя возвращаем объект нужного тарифа.
# Возвращается StandardTariff() или ComfortTariff(), а не строка.
def choose_tariff():
    choice = input("Тариф: 1 — Стандарт, 2 — Комфорт: ")

    if choice == "1":
        return StandardTariff()

    if choice == "2":
        return ComfortTariff()

    raise ValueError("Неизвестный тариф")


# Обрабатываем одно действие из меню пассажиров.
# service — объект TaxiService, choice — выбранный пункт строкой.
def passengers_menu(service, choice):

    # Создаём пассажира и передаём его сервису для регистрации.
    # add_passenger() возвращает False, если ID уже используется.
    if choice == "1":
        passenger = Passenger(
            integer("ID: "),
            input("Имя: "),
            input("Телефон: ")
        )

        if not service.add_passenger(passenger):
            raise ValueError("ID пассажира уже занят")

    # Передаём список всех пассажиров функции вывода
    elif choice == "2":
        show(service.passengers)

    # Находим пассажира по ID.
    # _require() возвращает найденный объект или вызывает ошибку.
    # Квадратные скобки создают список из одного объекта для show().
    elif choice == "3":
        show([
            service._require(
                service.find_passenger(integer("ID: ")),
                "Пассажир"
            )
        ])

    # Пустой ввод заменяем на None: это сигнал «оставить старое значение».
    # update_passenger() возвращает изменённый объект для вывода.
    elif choice == "4":
        user_id = integer("ID: ")

        show([
            service.update_passenger(
                user_id,
                input("Имя (Enter — оставить): ") or None,
                input("Телефон (Enter — оставить): ") or None
            )
        ])

    # Сервис проверит, можно ли удалить выбранного пассажира
    elif choice == "5":
        service.delete_passenger(integer("ID: "))

    else:
        raise ValueError("Неизвестный пункт меню")


# Обрабатываем одно действие из меню водителей
def drivers_menu(service, choice):

    # Собираем данные водителя и создаём ему автомобиль.
    # read_car() возвращает объект Car прямо в конструктор Driver.
    if choice == "1":
        user_id = integer("ID: ")

        # Два результата input() записываем в две переменные
        name, phone = input("Имя: "), input("Телефон: ")

        if not service.add_driver(
            Driver(user_id, name, phone, read_car())
        ):
            raise ValueError("ID или номер автомобиля уже занят")

    elif choice == "2":
        show(service.drivers)

    elif choice == "3":
        show([
            service._require(
                service.find_driver(integer("ID: ")),
                "Водитель"
            )
        ])

    # Получаем новые данные; пустые поля оставляем без изменений
    elif choice == "4":
        user_id = integer("ID: ")
        name = input("Имя (Enter — оставить): ") or None
        phone = input("Телефон (Enter — оставить): ") or None

        # Условное выражение: если ввели "1", вызываем read_car().
        # При любом другом ответе записываем в car значение None.
        car = (
            read_car()
            if input("Изменить автомобиль? (1 — да): ") == "1"
            else None
        )

        show([service.update_driver(user_id, name, phone, car)])

    # Получаем от сервиса только свободных водителей
    elif choice == "5":
        show(service.get_available_drivers())

    elif choice == "6":
        service.delete_driver(integer("ID: "))

    else:
        raise ValueError("Неизвестный пункт меню")


# Обрабатываем создание, поиск и управление заказами
def orders_menu(service, choice):

    # Сначала показываем стоимость, затем запрашиваем подтверждение
    if choice == "1":
        passenger_id = integer("ID пассажира: ")
        tariff = choose_tariff()

        # Заменяем запятую точкой: можно ввести и "5,5", и "5.5".
        # float() преобразует строку в дробное число.
        distance = float(
            input("Расстояние, км: ").replace(",", ".")
        )

        print(f"Стоимость: {tariff.calculate_price(distance)} сомони")

        # Создаём заказ только после подтверждения.
        # Именованные аргументы явно показывают, что передаём методу.
        if input("Создать заказ? (1 — да): ") == "1":
            show([
                service.create_order(
                    passenger_id=passenger_id,
                    distance=distance,
                    tariff=tariff
                )
            ])

    elif choice == "2":
        show(service.get_orders())

    elif choice == "3":
        show([
            service._require(
                service.find_order(integer("ID заказа: ")),
                "Заказ"
            )
        ])

    # Фильтр status="new" оставляет только новые заказы
    elif choice == "4":
        show(service.get_orders(status="new"))

    # Передаём сервису ID заказа и ID выбранного водителя
    elif choice == "5":
        show([
            service.assign_driver(
                integer("ID заказа: "),
                integer("ID водителя: ")
            )
        ])

    # Для трёх похожих действий выбираем метод через словарь.
    # Здесь методы записаны без (): они ещё не вызываются.
    elif choice in ("6", "7", "8"):
        action = {
            "6": service.start_trip,
            "7": service.complete_trip,
            "8": service.cancel_order
        }[choice]

        # Теперь вызываем выбранный метод и показываем результат.
        # Например, при choice="6" выполнится service.start_trip(ID).
        show([action(integer("ID заказа: "))])

    # Получаем историю заказов выбранного пассажира
    elif choice == "9":
        show(
            service.get_orders(
                passenger_id=integer("ID пассажира: ")
            )
        )

    # Получаем все заказы, закреплённые за выбранным водителем
    elif choice == "10":
        show(
            service.get_orders(
                driver_id=integer("ID водителя: ")
            )
        )

    else:
        raise ValueError("Неизвестный пункт меню")


# Выводим один показатель статистики по номеру пункта
def statistics_menu(service, choice):

    # items() даёт пары «название — значение».
    # list() позволяет выбирать эти пары по индексу.
    values = list(service.get_statistics().items())

    # Получаем допустимые пункты: ("1", "2", "3", "4", "5", "6").
    # range(1, 7) перебирает числа от 1 до 6 включительно.
    if choice not in tuple(str(i) for i in range(1, 7)):
        raise ValueError("Неизвестный пункт меню")

    # Индексы списка начинаются с 0, поэтому вычитаем 1.
    # Пару распаковываем в название показателя и его значение.
    label, value = values[int(choice) - 1]

    print(f"{label}: {value}")


# Связываем пункт главного меню с текстом подменю и его функцией.
# Каждое значение — кортеж: (текст, функция).
# \n переносит вывод на новую строку.
MENUS = {
    "1": (
        "Пассажиры\n"
        "1. Добавить\n"
        "2. Показать всех\n"
        "3. Найти по ID\n"
        "4. Изменить\n"
        "5. Удалить",
        passengers_menu
    ),
    "2": (
        "Водители\n"
        "1. Добавить\n"
        "2. Показать всех\n"
        "3. Найти по ID\n"
        "4. Изменить\n"
        "5. Свободные\n"
        "6. Удалить",
        drivers_menu
    ),
    "3": (
        "Заказы\n"
        "1. Создать\n"
        "2. Все заказы\n"
        "3. Найти по ID\n"
        "4. Новые\n"
        "5. Принять\n"
        "6. Начать поездку\n"
        "7. Завершить\n"
        "8. Отменить\n"
        "9. История пассажира\n"
        "10. История водителя",
        orders_menu
    ),
    "4": (
        "Статистика\n"
        "1. Пассажиры\n"
        "2. Водители\n"
        "3. Заказы\n"
        "4. Завершённые\n"
        "5. Отменённые\n"
        "6. Выручка",
        statistics_menu
    ),
}


# Главная функция создаёт сервис и запускает меню.
# Пути можно передать отдельно — это удобно для тестов.
def main(data_path=None, log_path=None):

    # Если путь не передан, используем папку data рядом с main.py.
    # Оператор / у Path соединяет части пути.
    # При создании TaxiService загружает сохранённые данные.
    try:
        service = TaxiService(
            data_path
            if data_path is not None
            else ROOT / "data/taxi_data.json",

            log_path
            if log_path is not None
            else ROOT / "data/actions.log"
        )

    # При ошибке загрузки прекращаем запуск.
    # return 1 сообщает о неудачном завершении.
    except (ValueError, OSError) as exc:
        print(f"Не удалось загрузить данные: {exc}")
        return 1

    # Внешний try обрабатывает выход и ошибки записи файлов
    try:

        # Главное меню повторяется, пока не выполнится break
        while True:
            print(
                "\nTaxiService\n"
                "1. Пассажиры\n"
                "2. Водители\n"
                "3. Заказы\n"
                "4. Статистика\n"
                "5. Сохранить\n"
                "0. Выход"
            )

            choice = input("> ")

            # break завершает ближайший цикл — здесь главное меню
            if choice == "0":
                break

            # Сохраняем вручную и переходим к началу главного цикла.
            # continue пропускает оставшуюся часть текущей итерации.
            if choice == "5":
                service.save_data()
                print("Данные сохранены")
                continue

            # Проверяем, есть ли такой ключ в словаре MENUS
            if choice not in MENUS:
                print("Неизвестный пункт меню")
                continue

            # Получаем текст выбранного подменю и его функцию
            title, action = MENUS[choice]

            # Внутренний цикл повторяет выбранное подменю
            while True:
                print(f"\n{title}\n0. Назад")
                subchoice = input("> ")

                # Выходим только из подменю обратно в главное
                if subchoice == "0":
                    break

                # Вызываем функцию выбранного раздела.
                # Например: passengers_menu(service, subchoice).
                try:
                    action(service, subchoice)

                # Ошибку показываем пользователю, затем повторяем подменю.
                # exc — объект пойманной ошибки.
                except (ValueError, TypeError, OSError) as exc:
                    print(f"Ошибка: {exc}")

                # else у try выполняется, если внутри try не было ошибки
                else:
                    print("Готово")

    # Ctrl+C или конец ввода завершают работу без длинного traceback
    except (EOFError, KeyboardInterrupt):
        print("\nВыход")

    # Обрабатываем ошибку файловой операции вне подменю
    except OSError as exc:
        print(f"Ошибка сохранения: {exc}")
        return 1

    # finally выполняется при обычном выходе и при исключении.
    # Перед завершением пробуем сохранить актуальное состояние.
    finally:
        try:
            service.save_data()
        except (ValueError, OSError) as exc:
            print(f"Не удалось сохранить данные: {exc}")

    # Код 0 означает успешное завершение главной функции
    return 0


# Запускаем меню только при непосредственном запуске этого файла.
# При import main этот блок не выполняется.
# SystemExit передаёт операционной системе код завершения main().
if __name__ == "__main__":
    raise SystemExit(main())