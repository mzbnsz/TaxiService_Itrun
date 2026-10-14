# В файле services.py я создал класс TaxiService,
# который отвечает за бизнес-логику службы такси.
# В конструкторе хранятся списки пассажиров, водителей и заказов.
# Я реализовал регистрацию пассажиров и водителей с проверкой
# уникальности, поиск пользователей по ID и получение списка
# свободных водителей. Для этого использовал ООП, циклы,
# условия, методы и работу со списками объектов.
# Главный класс управления службой такси

from models import Order

class TaxiService:

    # Создаём списки пассажиров, водителей и заказов
    def __init__(self):
        self.passengers = []
        self.drivers = []
        self.orders = []

    # Регистрация пассажира с проверкой уникальности ID
    def add_passenger(self, passenger):
        for existing_passenger in self.passengers:
            if existing_passenger.user_id == passenger.user_id:
                return False

        self.passengers.append(passenger)
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
    def create_order(self, order_id, passenger_id, distance, tariff):
        passenger = self.find_passenger(passenger_id)
        if self.find_order(order_id) is not None:
            raise ValueError("Заказ с таким ID уже существует")
        if passenger is None:
            raise ValueError("Пассажир не найден")
        if distance <= 0:
            raise ValueError("Расстояние должно быть больше нуля")
        price = tariff.calculate_price(distance)

        # Создаём заказ с рассчитанной стоимостью
        order = Order(
            order_id,
            passenger_id,
            distance,
            tariff.__class__.__name__,
            price
        )
        # Сохраняем новый заказ в списке сервиса
        self.orders.append(order)
        return order

    # Поиск заказа по его ID
    def find_order(self, order_id):
        for existing_order in self.orders:
            if existing_order.order_id == order_id:
                return existing_order
        return None

    # Назначаем свободного водителя на заказ
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
        # Назначаем водителя на заказ и делаем его занятым
        if not order.accept(driver_id):
            raise ValueError("Заказ нельзя принять")
        driver.mark_busy()
        return order
    # Начинаем поездку только для принятого заказа
    def start_trip(self, order_id):
        order = self.find_order(order_id)
        if order is None:
            raise ValueError("Заказ не найден")

        if not order.start_trip():
            raise ValueError("Поездку нельзя начать")

        return order

    # Завершаем поездку и освобождаем водителя
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
        return order
