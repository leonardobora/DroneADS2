import unittest
from src.weather import Weather

class TestWeather(unittest.TestCase):
    def setUp(self):
        self.weather = Weather()

    def test_get_forecast(self):
        forecast = self.weather.get_wind_for_time("06h")
        self.assertIsNotNone(forecast)
        self.assertEqual(forecast["speed_kmh"], 17)

if __name__ == '__main__':
    unittest.main()
