from abc import ABC, abstractmethod
from utils import Validator


# Абстрактный родитель для тарифов: задаёт обязательный метод расчёта.
# Создать Tariff() напрямую нельзя — нужны дочерние классы.
class Tariff(ABC):

    # Каждый дочерний тариф обязан реализовать этот метод
    @abstractmethod
    def calculate_price(self, distance):
        pass


# Тариф «Стандарт»: наследует общий интерфейс Tariff
class StandardTariff(Tariff):

    # Атрибут класса: название тарифа для хранения в заказе
    name = "standard"

    # Проверяем расстояние и считаем цену: подача 10 + 3 за километр.
    # При неверном расстоянии Validator вызовет ValueError.
    def calculate_price(self, distance):
        Validator.number(distance, "Расстояние")
        return 10 + 3 * distance


# Тариф «Комфорт»: тот же интерфейс, но другая стоимость
class ComfortTariff(Tariff):

    # Через объект тарифа название доступно как tariff.name
    name = "comfort"

    # Проверяем расстояние и считаем цену: подача 20 + 5 за километр
    def calculate_price(self, distance):
        Validator.number(distance, "Расстояние")
        return 20 + 5 * distance