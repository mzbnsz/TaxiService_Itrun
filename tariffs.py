from abc import ABC, abstractmethod


# Общий интерфейс расчёта стоимости для всех тарифов
class Tariff(ABC):
    @abstractmethod
    def calculate_price(self, distance):
        pass


# Стандарт: 10 за подачу + 3 за каждый километр
class StandardTariff(Tariff):
    def calculate_price(self, distance):
        return 10 + 3 * distance


# Комфорт: 20 за подачу + 5 за каждый километр
class ComfortTariff(Tariff):
    def calculate_price(self, distance):
        return 20 + 5 * distance


# Проверяем оба тарифа на расстоянии 5 км
tariffs = [
    StandardTariff(),
    ComfortTariff()
]

for tariff in tariffs:
    print(tariff.calculate_price(5))