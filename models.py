from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone

    @abstractmethod
    def get_info(self):
        pass


class Passenger(User):
    def __init__(self, user_id, name, phone):
        super().__init__(user_id, name, phone)

    def get_info(self):
        return f"Passenger ID:{self.user_id}, Name:{self.name}, Phone:{self.phone}"

class Driver(User):
    def __init__(self, user_id, name, phone, car):
        super().__init__(user_id, name, phone)
        self.car = car
        self._is_available = True

    def get_info(self):
        return (f"Driver ID:{self.user_id}, Name:{self.name}, Phone:{self.phone}, "
                f"Car:{self.car}, Available:{self.is_available}")

    @property
    def is_available(self):
        return self._is_available

    def mark_busy(self):
        if self.is_available:
            self._is_available = False
            return True
        return False

    def mark_available(self):
        if not self.is_available:
            self._is_available = True
            return True
        return False


class Car:
    def __init__(self, brand, model, plate_number, category):
        self.brand = brand
        self.model = model
        self.plate_number = plate_number
        self.category = category

    def get_info(self):
        return f"{self.brand}, {self.model}, Plate:{self.plate_number}, Category:{self.category}"


class Order:
    def __init__(self, order_id, passenger_id, distance, tariff_name, price):
        self.order_id = order_id
        self.passenger_id = passenger_id
        self.distance = distance
        self.tariff_name = tariff_name
        self.price = price
        self.driver_id = None
        self.status = "new"

    def get_info(self):
        return (f'Order ID: {self.order_id},'
                f'Driver ID: {self.driver_id},'
                f'Passenger ID: {self.passenger_id},'
                f'Distance: {self.distance},'
                f'Tariff Name: {self.tariff_name},'
                f'Price: {self.price},'
                f'Status: {self.status}')