from control import StateSpace as SS
import numpy as np

from guilda.utils.typing import FloatArray

class Avr():
    
    def __init__(self):
        self.Vfd_st: complex = 0
        self.V_abs_st: float = 0

        A, B, C, D = self.get_linear_matrix()
        sys = SS(A, B, C, D)
        sys.set_inputs(['V_abs', 'Efd', 'u_avr'])
        sys.set_outputs(['Vfd'])
        self.sys = sys

    @property
    def nx(self) -> int:
        # このavrには状態がない
        return 0

    def initialize(self, Vfd: complex, V_abs: float):
        self.Vfd_st = Vfd
        self.V_abs_st = V_abs
        # 状態がない
        x = np.zeros((0, 1))
        return x

    def get_Vfd(self, u: FloatArray, x_avr: FloatArray, V_abs: float, Efd: complex):
        Vfd = self.Vfd_st + u[0, 0]
        dx = np.zeros((0, 1))
        return dx, Vfd

    def get_sys(self):
        return self.sys
    
    def get_linear_matrix(self):
        # ここではavrのダイナミクスを考慮しない
        A = np.zeros((0, 0))
        B = np.zeros((0, 3))
        C = np.zeros((1, 0))
        D = np.array([[0, 0, 1]])
        return A, B, C, D

    def get_state_name(self):
        nx = self.nx
        name_tag = []
        if nx != 0:
            name_tag = ['state_avr' + str(i+1) for i in range(nx)]
        return name_tag
