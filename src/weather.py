import random

class Weather:
    def __init__(self):
        self.wind_data = [
            {"hour": "06h", "speed_kmh": 17, "gust_kmh": 31, "direction": "ENE"},
            {"hour": "09h", "speed_kmh": 18, "gust_kmh": 33, "direction": "E"},
            {"hour": "12h", "speed_kmh": 19, "gust_kmh": 35, "direction": "E"},
            {"hour": "15h", "speed_kmh": 19, "gust_kmh": 35, "direction": "E"},
            {"hour": "18h", "speed_kmh": 20, "gust_kmh": 37, "direction": "E"},
            {"hour": "21h", "speed_kmh": 20, "gust_kmh": 37, "direction": "E"},
            # Dia 2
            {"hour": "06h", "speed_kmh": 20, "gust_kmh": 37, "direction": "E"},
            {"hour": "09h", "speed_kmh": 18, "gust_kmh": 35, "direction": "E"},
            {"hour": "12h", "speed_kmh": 16, "gust_kmh": 19, "direction": "E"},
            {"hour": "15h", "speed_kmh": 19, "gust_kmh": 19, "direction": "E"},
            {"hour": "18h", "speed_kmh": 21, "gust_kmh": 21, "direction": "E"},
            {"hour": "21h", "speed_kmh": 21, "gust_kmh": 21, "direction": "E"},
            # Dia 3
            {"hour": "06h", "speed_kmh": 15, "gust_kmh": 28, "direction": "ENE"},
            {"hour": "09h", "speed_kmh": 17, "gust_kmh": 15, "direction": "E"},
            {"hour": "12h", "speed_kmh": 8, "gust_kmh": 8, "direction": "NE"},
            {"hour": "15h", "speed_kmh": 20, "gust_kmh": 20, "direction": "E"},
            {"hour": "18h", "speed_kmh": 16, "gust_kmh": 17, "direction": "E"},
            {"hour": "21h", "speed_kmh": 15, "gust_kmh": 15, "direction": "ENE"},
            # Dia 4
            {"hour": "06h", "speed_kmh": 4, "gust_kmh": 6, "direction": "WSW"},
            {"hour": "09h", "speed_kmh": 5, "gust_kmh": 6, "direction": "WSW"},
            {"hour": "12h", "speed_kmh": 7, "gust_kmh": 13, "direction": "WSW"},
            {"hour": "15h", "speed_kmh": 8, "gust_kmh": 19, "direction": "SSW"},
            {"hour": "18h", "speed_kmh": 9, "gust_kmh": 13, "direction": "E"},
            {"hour": "21h", "speed_kmh": 11, "gust_kmh": 20, "direction": "ENE"},
            # Dia 5
            {"hour": "06h", "speed_kmh": 4, "gust_kmh": 7, "direction": "NE"},
            {"hour": "09h", "speed_kmh": 5, "gust_kmh": 8, "direction": "ENE"},
            {"hour": "12h", "speed_kmh": 7, "gust_kmh": 9, "direction": "E"},
            {"hour": "15h", "speed_kmh": 11, "gust_kmh": 15, "direction": "E"},
            {"hour": "18h", "speed_kmh": 15, "gust_kmh": 28, "direction": "E"},
            {"hour": "21h", "speed_kmh": 15, "gust_kmh": 28, "direction": "E"},
        ]

    def get_wind_for_time(self, hour, day=0):
        """
        Retorna condições de vento para hora específica e dia.
        :param hour: Hora no formato "HHh"
        :param day: Dia (0-4)
        """
        hour_map = {
            "06h": 0, "09h": 1, "12h": 2,
            "15h": 3, "18h": 4, "21h": 5
        }
        
        if hour in hour_map:
            index = (day * 6) + hour_map[hour]
            if index < len(self.wind_data):
                return self.wind_data[index]
        
        return self.wind_data[0]

    def __str__(self):
        """
        Representação textual das condições climáticas atuais.
        """
        wind = self.get_wind_for_time(None)  # Para demonstração
        return f"Weather(wind_speed={wind['speed']:.2f} km/h, wind_direction={wind['direction']})"
