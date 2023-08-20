from numpy.linalg import norm
from cmath import phase

import guilda.backend as G

from guilda.bus.bus import Bus


class BusSlack(Bus):
    def __init__(self, Vabs: float, Vangle: float, shunt: complex):
        super().__init__(shunt)
        self.Vabs: float = Vabs
        self.Vangle: float = Vangle

    def get_constraint(self, Vr: float, Vi: float, P: float, Q: float):
        Vabs = float(norm([Vr, Vi]))
        Vangle = phase(complex(Vr, Vi))
        return G.array([
            [Vabs-self.Vabs], 
            [Vangle-self.Vangle]
        ])
