import unittest
from src.navigation import Navigation

class TestNavigation(unittest.TestCase):
    def setUp(self):
        self.navigation = Navigation()

    def test_calculate_distance(self):
        # Teste usando coordenadas reais de Curitiba (do arquivo CSV)
        coord1 = (-49.2160678044742, -25.4233146347775)  # CEP: 82821020
        coord2 = (-49.3400481020638, -25.4936598469491)  # CEP: 81350686
        
        distance = self.navigation.calculate_distance(coord1, coord2)
        
        # A distância aproximada entre estes pontos é ~14.7 km (valor calculado mais preciso)
        self.assertAlmostEqual(distance, 14.7, places=1)
        
        # Teste com outro par de coordenadas
        coord3 = (-49.2336060009616, -25.4300625729625)  # CEP: 82530380
        coord4 = (-49.2047594214569, -25.4608672106041)  # CEP: 82930390
        
        distance2 = self.navigation.calculate_distance(coord3, coord4)
        
        # Verifica se a distância é positiva e razoável
        self.assertGreater(distance2, 0)
        self.assertLess(distance2, 50)  # Não deve ser maior que 50km dentro de Curitiba

    def test_same_point(self):
        # Teste com o mesmo ponto (distância deve ser zero)
        coord = (-49.2160678044742, -25.4233146347775)
        distance = self.navigation.calculate_distance(coord, coord)
        self.assertAlmostEqual(distance, 0, places=3)

if __name__ == '__main__':
    unittest.main()
