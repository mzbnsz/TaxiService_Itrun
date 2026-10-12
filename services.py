# В файле services.py я создал класс TaxiService,
# который отвечает за бизнес-логику службы такси.
# В конструкторе хранятся списки пассажиров, водителей и заказов.
# Я реализовал регистрацию пассажиров и водителей с проверкой
# уникальности, поиск пользователей по ID и получение списка
# свободных водителей. Для этого использовал ООП, циклы,
# условия, методы и работу со списками объектов.
# Главный класс управления службой такси
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

