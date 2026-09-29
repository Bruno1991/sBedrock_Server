"""
Testes unitarios para a Mansao Estatua Gigante de Creeper.
Valida o dimensionamento geometrico 3:1, zonas de andares e seguranca de espaco.
"""

import unittest

class TestCreeperMansionSpecs(unittest.TestCase):
    def setUp(self):
        # Parametros da Mansao Creeper
        self.scale = 3
        self.origin_x = -12
        self.end_x = 11
        self.width = (self.end_x - self.origin_x) + 1 # 24 blocos

        self.origin_z = -74
        self.end_z = -51
        self.depth = (self.end_z - self.origin_z) + 1 # 24 blocos

        self.base_y = 77
        self.top_y = 154
        self.height = (self.top_y - self.base_y) + 1 # 78 blocos

    def test_proportional_dimensions(self):
        """Garante que a estatua obedece exatamente a proporcao 3:1 do modelo oficial do Creeper."""
        # Cabeca oficial: 8x8x8 pixels -> 24x24x24 blocos
        head_height = 154 - 131 + 1
        self.assertEqual(head_height, 24)
        self.assertEqual(self.width, 24)
        self.assertEqual(self.depth, 24)

        # Tronco oficial: 8x4x12 pixels -> 24x12x36 blocos
        body_width = 24
        body_depth = (-57 - (-68)) + 1
        body_height = (130 - 95) + 1
        self.assertEqual(body_width, 24)
        self.assertEqual(body_depth, 12)
        self.assertEqual(body_height, 36)

        # Patas oficiais: 4 patas de 4x4x6 pixels -> 12x12x18 blocos cada
        leg_height = (94 - 77) + 1
        self.assertEqual(leg_height, 18)

    def test_vertical_floors_integrity(self):
        """Valida que todos os 7 andares possuem pe-direito habitavel (>= 4 blocos)."""
        floors = [
            ("Andar 1 - Hall & Patas", 77, 94),
            ("Andar 2 - Jardim Zen", 95, 103),
            ("Andar 3 - Metalurgia & Fornalhas", 104, 112),
            ("Andar 4 - Alquimia & Pocao", 113, 121),
            ("Andar 5 - Biblioteca & Encantamento", 122, 130),
            ("Andar 6 - Grande Armazem", 131, 142),
            ("Andar 7 - Suite Master no Topo", 143, 153),
        ]
        for name, y_start, y_end in floors:
            clearance = (y_end - y_start) + 1
            self.assertGreaterEqual(clearance, 8, f"{name} pe-direito insuficiente: {clearance}")

    def test_tnt_flight_path_isolation(self):
        """Garante que a estatua nao intercepta o corredor de voo da maquina de TNT (Z = 0, Y = 150)."""
        # Maquina voa em Z = 0 e Y = 150
        # Estatua esta localizada entre Z = -74 e Z = -51
        self.assertLess(self.end_z, -50)
        distance_to_tnt_corridor = 0 - self.end_z
        self.assertGreaterEqual(distance_to_tnt_corridor, 50, "Estatua deve estar a pelo menos 50 blocos do corredor de TNT!")

if __name__ == '__main__':
    unittest.main()
