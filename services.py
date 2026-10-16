from pathlib import Path
from models import Order, Passenger, Driver, Car
from tariffs import StandardTariff, ComfortTariff
from utils import Validator, read_json, write_json
from decorators import log_action


class TaxiService:

    # Создаём списки пассажиров, водителей и заказов
    def __init__(self, data_path=None, log_path=None):
        self.passengers = []
        self.drivers = []
        self.orders = []
        self.data_path = Path(data_path) if data_path is not None else None
        self.log_path = Path(log_path) if log_path is not None else None
        self.next_order_id = 1
        self._loaded = self.data_path is None
        if self.data_path is not None:
            self.load_data()

    # Регистрация пассажира с проверкой уникальности ID
    def add_passenger(self, passenger):
        for existing_passenger in self.passengers:
            if existing_passenger.user_id == passenger.user_id:
                return False

        self.passengers.append(passenger)
        self.save_data()
        return True

    # Регистрация водителя с проверкой ID и номера машины
    def add_driver(self, driver):
        for existing_driver in self.drivers:
            if (
                existing_driver.user_id == driver.user_id
                or existing_driver.car.plate_number == driver.car.plate_number
            ):
                return False

        self.drivers.append(driver)
        self.save_data()
        return True

    # Поиск пассажира по его ID
    def find_passenger(self, user_id):
        for existing_passenger in self.passengers:
            if existing_passenger.user_id == user_id:
                return existing_passenger
        return None

    # Поиск водителя по его ID
    def find_driver(self, user_id):
        for existing_driver in self.drivers:
            if existing_driver.user_id == user_id:
                return existing_driver
        return None

    # Получение списка всех свободных водителей
    def get_available_drivers(self):
        available_drivers = []
        for driver in self.drivers:
            if driver.is_available:
                available_drivers.append(driver)
        return available_drivers

    # Проверяем наличие пассажира и допустимость расстояния
    @log_action
    def create_order(self, order_id=None, passenger_id=None, distance=None, tariff=None):
        if order_id is None:
            order_id = self.next_order_id
        Validator.identifier(order_id)
        Validator.number(distance, "Расстояние")
        if type(tariff) not in (StandardTariff, ComfortTariff):
            raise ValueError("Неизвестный тариф")
        passenger = self.find_passenger(passenger_id)
        if self.find_order(order_id) is not None:
            raise ValueError("Заказ с таким ID уже существует")
        if passenger is None:
            raise ValueError("Пассажир не найден")
        price = tariff.calculate_price(distance)

        # Создаём заказ с рассчитанной стоимостью
        order = Order(
            order_id,
            passenger_id,
            distance,
            tariff.name,
            price
        )
        # Сохраняем новый заказ в списке сервиса
        self.orders.append(order)
        self.next_order_id = max(self.next_order_id, order_id + 1)
        self.save_data()
        return order

    # Поиск заказа по его ID
    def find_order(self, order_id):
        for existing_order in self.orders:
            if existing_order.order_id == order_id:
                return existing_order
        return None

    # Назначаем свободного водителя на заказ
    @log_action
    def assign_driver(self, order_id, driver_id):
        order = self.find_order(order_id)
        if order is None:
            raise ValueError("Заказ не найден")
        driver = self.find_driver(driver_id)
        if driver is None:
            raise ValueError("Водитель не найден")
        # Проверяем доступность водителя
        if not driver.is_available:
            raise ValueError("Водитель занят")
        if driver.car.category != order.tariff_name:
            raise ValueError("Категория автомобиля не соответствует тарифу")
        # Назначаем водителя на заказ и делаем его занятым
        if not order.accept(driver_id):
            raise ValueError("Заказ нельзя принять")
        driver.mark_busy()
        self.save_data()
        return order

    # Начинаем поездку только для принятого заказа
    @log_action
    def start_trip(self, order_id):
        order = self.find_order(order_id)
        if order is None:
            raise ValueError("Заказ не найден")

        if not order.start_trip():
            raise ValueError("Поездку нельзя начать")

        self.save_data()
        return order

    # Завершаем поездку и освобождаем водителя
    @log_action
    def complete_trip(self, order_id):
        order = self.find_order(order_id)
        if order is None:
            raise ValueError("Заказ не найден")

        # Проверяем наличие назначенного водителя
        driver = self.find_driver(order.driver_id)
        if driver is None:
            raise ValueError("Водитель не найден")

        # Освобождаем водителя только после завершения поездки
        if not order.complete_trip():
            raise ValueError("Поездку нельзя завершить")

        driver.mark_available()
        self.save_data()
        return order

    # Отмена нового или принятого заказа с освобождением водителя
    @log_action
    def cancel_order(self, order_id):
        order = self._require(self.find_order(order_id), "Заказ")
        driver = None
        if order.driver_id is not None:
            driver = self._require(self.find_driver(order.driver_id), "Водитель")
        if not order.cancel():
            raise ValueError("Заказ нельзя отменить")
        if driver is not None:
            driver.mark_available()
        self.save_data()
        return order

    @staticmethod
    def _require(value, label):
        if value is None:
            raise ValueError(f"{label} не найден")
        return value

    # Перед изменением проверяем все новые значения
    def update_passenger(self, user_id, name=None, phone=None):
        passenger = self._require(self.find_passenger(user_id), "Пассажир")
        validated = Passenger(user_id, passenger.name if name is None else name,
                              passenger.phone if phone is None else phone)
        passenger.update_name(validated.name)
        passenger.update_phone(validated.phone)
        self.save_data()
        return passenger

    def update_driver(self, user_id, name=None, phone=None, car=None):
        driver = self._require(self.find_driver(user_id), "Водитель")
        validated = Passenger(user_id, driver.name if name is None else name,
                              driver.phone if phone is None else phone)
        if car is not None:
            if not isinstance(car, Car):
                raise ValueError("Необходим объект автомобиля")
            if any(o.driver_id == user_id and o.status in ("accepted", "in_progress")
                   for o in self.orders):
                raise ValueError("Нельзя изменять автомобиль во время активного заказа")
            if any(d.user_id != user_id and d.car.plate_number == car.plate_number
                   for d in self.drivers):
                raise ValueError("Номер автомобиля уже зарегистрирован")
        driver.update_name(validated.name)
        driver.update_phone(validated.phone)
        if car is not None:
            driver.car = car
        self.save_data()
        return driver

    def delete_passenger(self, user_id):
        passenger = self._require(self.find_passenger(user_id), "Пассажир")
        if any(o.passenger_id == user_id for o in self.orders):
            raise ValueError("Нельзя удалить пассажира со связанными заказами")
        self.passengers.remove(passenger)
        self.save_data()
        return True

    def delete_driver(self, user_id):
        driver = self._require(self.find_driver(user_id), "Водитель")
        if any(o.driver_id == user_id for o in self.orders):
            raise ValueError("Нельзя удалить водителя со связанными заказами")
        self.drivers.remove(driver)
        self.save_data()
        return True

    # История и статистика вычисляются из общего списка заказов
    def get_orders(self, passenger_id=None, driver_id=None, status=None):
        return [o for o in self.orders
                if (passenger_id is None or o.passenger_id == passenger_id)
                and (driver_id is None or o.driver_id == driver_id)
                and (status is None or o.status == status)]

    def calculate_total_revenue(self):
        return sum(o.price for o in self.orders if o.status == "completed")

    def get_statistics(self):
        return {"Пассажиры": len(self.passengers), "Водители": len(self.drivers),
                "Заказы": len(self.orders),
                "Завершённые поездки": len(self.get_orders(status="completed")),
                "Отменённые заказы": len(self.get_orders(status="cancelled")),
                "Выручка, сомони": self.calculate_total_revenue()}

    # Сохранение вызывается после успешных изменений сервиса
    def save_data(self):
        if self.data_path is None:
            return
        if not self._loaded:
            raise ValueError("Данные не загружены: перезапись запрещена")
        write_json(self.data_path, {
            "next_order_id": self.next_order_id,
            "passengers": [p.to_dict() for p in self.passengers],
            "drivers": [d.to_dict() for d in self.drivers],
            "orders": [o.to_dict() for o in self.orders],
        })

    # Сначала восстанавливаем и проверяем всё состояние, затем применяем
    def load_data(self):
        if self.data_path is None:
            return
        self._loaded = False
        data = read_json(self.data_path)
        if data is None:
            self.passengers, self.drivers, self.orders = [], [], []
            self.next_order_id = 1
            self._loaded = True
            self.save_data()
            return
        try:
            passengers = [Passenger.from_dict(p) for p in data["passengers"]]
            drivers = [Driver.from_dict(d) for d in data["drivers"]]
            orders = [Order.from_dict(o) for o in data["orders"]]
            for values in ([p.user_id for p in passengers],
                           [d.user_id for d in drivers],
                           [d.car.plate_number for d in drivers],
                           [o.order_id for o in orders]):
                if len(values) != len(set(values)):
                    raise ValueError("Повторяющиеся ID или номера автомобилей")
            passenger_ids = {p.user_id for p in passengers}
            driver_map = {d.user_id: d for d in drivers}
            busy_ids = set()
            for order in orders:
                if order.passenger_id not in passenger_ids:
                    raise ValueError("Не найден пассажир заказа")
                if order.driver_id is not None:
                    driver = driver_map.get(order.driver_id)
                    if driver is None:
                        raise ValueError("Не найден водитель заказа")
                    # Для активных заказов категория должна совпадать сейчас
                    if order.status in ("accepted", "in_progress"):
                        if driver.car.category != order.tariff_name:
                            raise ValueError("Неподходящая категория автомобиля")
                        if order.driver_id in busy_ids:
                            raise ValueError("У водителя несколько активных заказов")
                        busy_ids.add(order.driver_id)
            for driver in drivers:
                if driver.is_available != (driver.user_id not in busy_ids):
                    raise ValueError("Занятость водителя не соответствует заказам")
            next_id = data["next_order_id"]
            Validator.identifier(next_id)
            if next_id <= max((o.order_id for o in orders), default=0):
                raise ValueError("Некорректный следующий ID заказа")
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ValueError(f"Некорректные данные JSON; файл не изменён: {exc}") from exc
        self.passengers, self.drivers, self.orders = passengers, drivers, orders
        self.next_order_id = next_id
        self._loaded = True

    # Названия из исходного ТЗ используют ту же реализацию
    accept_order = assign_driver
    complete_order = complete_trip
