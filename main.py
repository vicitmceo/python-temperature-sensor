import json
import random
import urllib.error
import urllib.request
from typing import Protocol, runtime_checkable

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=46.48&longitude=30.73&current=temperature_2m"
)


@runtime_checkable
class TemperatureSensor(Protocol):
    """Контракт датчика температури."""

    def read_temperature(self) -> float:
        """Поточна температура в градусах Цельсія."""
        ...

    def get_sensor_id(self) -> str:
        """Унікальний ідентифікатор датчика."""
        ...


class WeatherAPISensor:
    """Температура в Одесі з відкритого API (open-meteo.com, без ключа)."""

    def read_temperature(self) -> float:
        try:
            with urllib.request.urlopen(OPEN_METEO_URL, timeout=10) as response:
                data = json.load(response)
            return float(data["current"]["temperature_2m"])
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as err:
            raise RuntimeError(f"Не вдалося отримати погоду: {err}") from err

    def get_sensor_id(self) -> str:
        return "WAS26-Odesa"


class SimulatedSensor:
    """Базова температура плюс випадкове відхилення."""

    def __init__(self, base: float, deviation: float) -> None:
        self.base = base
        self.deviation = deviation

    def read_temperature(self) -> float:
        return self.base + random.uniform(-self.deviation, self.deviation)

    def get_sensor_id(self) -> str:
        return f"SIM-{self.base:g}±{self.deviation:g}"


class FakeAlways25:
    def read_temperature(self) -> float:
        return 25.0

    def get_sensor_id(self) -> str:
        return "Fake-25"


class BrokenSensor:
    def read_temperature(self) -> float:
        raise RuntimeError("Датчик зламаний!")

    def get_sensor_id(self) -> str:
        return "BROKEN-999"


class RealDHT22:
    """Приклад «справжнього» датчика, потрібен для перевірки сумісності."""

    def read_temperature(self) -> float:
        return 22.0

    def get_sensor_id(self) -> str:
        return "DHT22-001"


def monitor_room(sensors: list[TemperatureSensor]) -> None:
    for sensor in sensors:
        sensor_id = sensor.get_sensor_id()
        try:
            print(f"[{sensor_id}] Температура: {sensor.read_temperature():.1f} °C")
        except Exception as err:
            print(f"[{sensor_id}] ПОМИЛКА: {err}")


def main() -> None:
    sensors = [
        WeatherAPISensor(),
        SimulatedSensor(base=21.5, deviation=3.0),
        FakeAlways25(),
        BrokenSensor(),
    ]
    monitor_room(sensors)

    print(isinstance(RealDHT22(), TemperatureSensor))   # True
    print(isinstance({"temp": 22}, TemperatureSensor))  # False


if __name__ == "__main__":
    main()
