import unittest
from src.battery import Battery

class TestBattery(unittest.TestCase):
    def setUp(self):
        self.battery = Battery()

    def test_battery_consumption(self):
        self.battery.consume_charge(10)
        self.assertEqual(self.battery.current_charge, 99.7)

if __name__ == '__main__':
    unittest.main()
