


from abc import ABC, abstractmethod


# Абстрактный родительский класс для всех пользователей
class User(ABC):

    # Инициализация общих данных пользователя
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone

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
                f"Car:{self.car}, Available:{self.is_available}")

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
        self.brand = brand
        self.model = model
        self.plate_number = plate_number
        self.category = category

    # Возвращаем информацию об автомобиле
    def get_info(self):
        return f"{self.brand}, {self.model}, Plate:{self.plate_number}, Category:{self.category}"


# Класс заказа такси
class Order:

    # Создаём заказ с начальным статусом new
    def __init__(self, order_id, passenger_id, distance, tariff_name, price):
        self.order_id = order_id
        self.passenger_id = passenger_id
        self.distance = distance
        self.tariff_name = tariff_name
        self.price = price
        self.driver_id = None
        self.status = "new"

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


# Проверяем работу методов управления заказом
order = Order(1, 2, 5, "standard", 25)

order.accept(7)
order.start_trip()

print(order.complete_trip())  # True
print(order.status)           # completed
print(order.complete_trip())  # False