


from abc import ABC, abstractmethod
from utils import Validator


# Абстрактный родительский класс для всех пользователей
class User(ABC):

    # Инициализация общих данных пользователя
    def __init__(self, user_id, name, phone):
        self.user_id = Validator.identifier(user_id)
        self.name = Validator.text(name, "Имя")
        self.phone = Validator.phone(phone)

    # Изменяем данные только после проверки
    def update_name(self, new_name):
        self.name = Validator.text(new_name, "Имя")

    def update_phone(self, new_phone):
        self.phone = Validator.phone(new_phone)

    def to_dict(self):
        return {"user_id": self.user_id, "name": self.name, "phone": self.phone}

    @classmethod
    def from_dict(cls, data):
        return cls(data["user_id"], data["name"], data["phone"])

    # Обязательный метод получения информации
    @abstractmethod
    def get_info(self):
        pass


# Класс пассажира, наследуется от User
class Passenger(User):

    # Получаем общие атрибуты через super()
    def __init__(self, user_id, name, phone):
        super().__init__(user_id, name, phone)

    # Возвращаем информацию о пассажире
    def get_info(self):
        return f"Passenger ID:{self.user_id}, Name:{self.name}, Phone:{self.phone}"


# Класс водителя, наследуется от User
class Driver(User):

    # Инициализация водителя, автомобиля и статуса
    def __init__(self, user_id, name, phone, car):
        super().__init__(user_id, name, phone)
        self.car = car
        self._is_available = True

    # Возвращаем информацию о водителе
    def get_info(self):
        return (f"Driver ID:{self.user_id}, Name:{self.name}, Phone:{self.phone}, "
                f"Car:{self.car.get_info()}, Available:{self.is_available}")

    def to_dict(self):
        data = super().to_dict()
        data.update(car=self.car.to_dict(), is_available=self.is_available)
        return data

    @classmethod
    def from_dict(cls, data):
        driver = cls(data["user_id"], data["name"], data["phone"], Car.from_dict(data["car"]))
        if type(data["is_available"]) is not bool:
            raise ValueError("Некорректный статус водителя")
        driver._is_available = data["is_available"]
        return driver

    # Получаем статус водителя через property
    @property
    def is_available(self):
        return self._is_available

    # Делаем свободного водителя занятым
    def mark_busy(self):
        if self.is_available:
            self._is_available = False
            return True
        return False

    # Освобождаем водителя после поездки
    def mark_available(self):
        if not self.is_available:
            self._is_available = True
            return True
        return False


# Класс автомобиля водителя
class Car:

    # Инициализация характеристик автомобиля
    def __init__(self, brand, model, plate_number, category):
        self.brand = Validator.text(brand, "Марка")
        self.model = Validator.text(model, "Модель")
        self.plate_number = Validator.text(plate_number, "Номер машины").upper()
        self.category = Validator.text(category, "Категория").lower()
        if self.category not in ("standard", "comfort"):
            raise ValueError("Категория должна быть standard или comfort")

    def to_dict(self):
        return {"brand": self.brand, "model": self.model,
                "plate_number": self.plate_number, "category": self.category}

    @classmethod
    def from_dict(cls, data):
        return cls(data["brand"], data["model"], data["plate_number"], data["category"])

    # Возвращаем информацию об автомобиле
    def get_info(self):
        return f"{self.brand}, {self.model}, Plate:{self.plate_number}, Category:{self.category}"


# Класс заказа такси
class Order:

    # Создаём заказ с начальным статусом new
    def __init__(self, order_id, passenger_id, distance, tariff_name, price):
        self.order_id = Validator.identifier(order_id)
        self.passenger_id = Validator.identifier(passenger_id)
        self.distance = Validator.number(distance, "Расстояние")
        if tariff_name not in ("standard", "comfort"):
            raise ValueError("Неизвестный тариф")
        self.tariff_name = tariff_name
        self.price = Validator.number(price, "Цена", allow_zero=True)
        self.driver_id = None
        self.status = "new"

    def to_dict(self):
        return dict(vars(self))

    @classmethod
    def from_dict(cls, data):
        order = cls(data["order_id"], data["passenger_id"], data["distance"],
                    data["tariff_name"], data["price"])
        status = data["status"]
        if status not in ("new", "accepted", "in_progress", "completed", "cancelled"):
            raise ValueError("Неизвестный статус заказа")
        driver_id = data["driver_id"]
        if driver_id is not None:
            Validator.identifier(driver_id)
        if status == "new" and driver_id is not None:
            raise ValueError("У нового заказа не должно быть водителя")
        if status in ("accepted", "in_progress", "completed") and driver_id is None:
            raise ValueError("У заказа отсутствует водитель")
        order.driver_id = driver_id
        order.status = status
        return order

    # Возвращаем полную информацию о заказе
    def get_info(self):
        return (f'Order ID: {self.order_id},'
                f'Driver ID: {self.driver_id},'
                f'Passenger ID: {self.passenger_id},'
                f'Distance: {self.distance},'
                f'Tariff Name: {self.tariff_name},'
                f'Price: {self.price},'
                f'Status: {self.status}')

    # Назначаем водителя на новый заказ
    def accept(self, driver_id):
        Validator.identifier(driver_id)
        if self.status == "new":
            self.driver_id = driver_id
            self.status = "accepted"
            return True
        return False

    # Начинаем поездку после принятия заказа
    def start_trip(self):
        if self.status == "accepted":
            self.status = "in_progress"
            return True
        return False

    # Завершаем начатую поездку
    def complete_trip(self):
        if self.status == "in_progress":
            self.status = "completed"
            return True
        return False

    # Отменяем новый или принятый заказ
    def cancel(self):
        if self.status == 'new' or self.status == 'accepted':
            self.status = "cancelled"
            return True
        return False


