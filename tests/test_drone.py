# tests/test_drone.py

import unittest
from src.drone import Drone
from src.battery import Battery
from src.weather import Weather
from src.navigation import Navigation
from src.cep_mapper import CEPMapper
import math

class TestDrone(unittest.TestCase):
    def setUp(self):
        self.battery = Battery(capacity=100)
        # Usando uma coordenada real de Curitiba como ponto inicial
        self.initial_position = (-49.2160678044742, -25.4233146347775)  # CEP: 82821020
        self.cep_mapper = CEPMapper('data/coordenadas.csv')
        self.drone = Drone(
            initial_position=self.initial_position,
            battery=self.battery,
            weather=Weather(),
            navigation=Navigation(),
            cep_mapper=self.cep_mapper
        )
        self.drone.remaining_autonomy = 3600  # 1 hora de autonomia inicial

    def test_initial_battery(self):
        self.assertEqual(self.drone.battery.current_charge, 100)

    def test_flight_time(self):
        # Teste com uma distância real (~2km)
        distance = 2.0  # 2 km
        time = self.drone.calculate_flight_time(distance)
        
        # Com velocidade base de 30 km/h, 2 km devem levar ~240 segundos
        expected_time = math.ceil((distance / self.drone.BASE_SPEED) * 3600)
        self.assertEqual(time, expected_time)
        
        # Teste considerando tempo de decolagem/pouso
        total_time = time + 60  # Adiciona 60s para procedimentos
        self.assertEqual(total_time, expected_time + 60)

    def test_move_with_wind(self):
        # Usando coordenadas reais próximas (~1.5km de distância)
        target_position = (-49.2047594214569, -25.4608672106041)  # CEP: 82930390
        
        autonomia_inicial = self.drone.remaining_autonomy
        
        # Tenta mover o drone
        success = self.drone.move_to(target_position)
        
        print(f"\nResultados do teste de movimento:")
        print(f"Posição inicial (long, lat): {self.initial_position}")
        print(f"Posição alvo (long, lat): {target_position}")
        print(f"Posição final (long, lat): {self.drone.position}")
        print(f"Autonomia inicial: {autonomia_inicial}s")
        print(f"Autonomia final: {self.drone.remaining_autonomy}s")
        print(f"Movimento bem-sucedido: {success}")
        
        # Verificações
        self.assertTrue(success, "O movimento do drone falhou")
        self.assertNotEqual(self.drone.position, self.initial_position)
        self.assertEqual(self.drone.position, target_position)
        
        # Verifica consumo de autonomia
        autonomia_consumida = autonomia_inicial - self.drone.remaining_autonomy
        self.assertGreater(autonomia_consumida, 0)
        self.assertLess(autonomia_consumida, 1800)  # Não deve consumir mais que 30 minutos em um voo curto

    def test_move_different_distances(self):
        self.drone.remaining_autonomy = 28800  # 8 horas de autonomia
        
        # Coordenadas mais próximas e em horários com vento mais favorável
        positions = [
            # Pontos para testar com ventos do dia 4 (ventos mais fracos/favoráveis)
            (-49.2336060009616, -25.4300625729625),  # Teste com vento WSW de 4-7 km/h
            (-49.2047594214569, -25.4608672106041),  # Teste com vento SSW de 8 km/h
            (-49.3400481020638, -25.4936598469491)   # Teste com vento E de 9-11 km/h
        ]
        
        for target in positions:
            print(f"\nMovendo para: {target}")
            success = self.drone.move_to(target)
            self.assertTrue(success, f"Falha ao mover para {target}")
            self.assertEqual(self.drone.position, target)
        
        self.assertGreater(self.drone.remaining_autonomy, 0)

    def test_insufficient_autonomy(self):
        # Define uma autonomia baixa
        self.drone.remaining_autonomy = 300  # Apenas 5 minutos
        
        # Tenta mover para um ponto distante (~13.7km)
        target_position = (-49.3400481020638, -25.4936598469491)  # CEP: 81350686
        
        # O movimento deve falhar devido à autonomia insuficiente
        success = self.drone.move_to(target_position)
        self.assertFalse(success, "O drone não deveria conseguir fazer este voo")
        self.assertEqual(self.drone.position, self.initial_position)

    def test_can_reach_with_recharge(self):
        # Testa se o drone pode alcançar um ponto e se precisa recarregar
        target_position = (-49.2047594214569, -25.4608672106041)  # CEP: 82930390
        self.drone.remaining_autonomy = 300  # Apenas 5 minutos
        
        # O movimento deve falhar devido à autonomia insuficiente
        success = self.drone.move_to(target_position)
        self.assertFalse(success, "O drone não deveria conseguir fazer este voo")
        
        # Verifica se o drone precisa retornar a um ponto de recarga
        charging_point = self.drone.find_nearest_charging_point(self.drone.position)
        self.assertIsNotNone(charging_point, "Deve encontrar um ponto de recarga próximo")

    def test_move_to_charging_point(self):
        # Testa se o drone se move para um ponto de recarga
        self.drone.remaining_autonomy = 7200  # 2 horas de autonomia
        charging_point = (-49.2733, -25.4284)  # Ponto de recarga
        
        success = self.drone.move_to(charging_point)
        self.assertTrue(success, "O drone deve conseguir mover-se para o ponto de recarga")
        self.assertEqual(self.drone.position, charging_point, "A posição do drone deve ser o ponto de recarga")

if __name__ == '__main__':
    unittest.main()
