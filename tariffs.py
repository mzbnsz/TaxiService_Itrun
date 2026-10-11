from abc import ABC, abstractmethod

class Tariff(ABC):
    @abstractmethod
    def calculate_price(self, distance):
        pass


class StandardTariff(Tariff):
    def calculate_price(self, distance):
        return 10 + 3 * distance

class ComfortTariff(Tariff):
    def calculate_price(self, distance):
        return 20 + 5 * distance


tarriffs = [
    StandardTariff(),
    ComfortTariff()
]

for tarriff in tarriffs:
    print(tarriff.calculate_price(5))