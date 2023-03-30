from control import StateSpace as SS
import numpy as np

from utils.typing import FloatArray

class Governor(object):
    
    def __init__(self):
        self.P: float = 0
        
        # ここではgovernorのダイナミクスを考慮しない
        A: FloatArray = np.zeros((0, 0))
        B: FloatArray = np.zeros((0, 1))
        C: FloatArray = np.zeros((1, 0))
        D: FloatArray = np.identity(2)
        sys = SS(A, B, C, D)
        SS.set_inputs(sys, ['omega_governor', 'u_governor'])
        SS.set_outputs(sys, ['omega_governor', 'Pmech'])

        self.sys: SS = sys

    def initialize(self, P: float) -> FloatArray:
        self.P = P
        # governorに状態はない
        x: FloatArray = np.zeros((0, 1))
        return x

    def get_nx(self) -> int:
        return 0

    def get_P(self, u: FloatArray):
        P: FloatArray = self.P + u
        dx: FloatArray = np.array([])
        return (dx, P)

    def get_sys(self) -> SS:
        return self.sys
    
    def get_state_name(self):
        nx = self.get_nx()
        name_tag = []
        if nx != 0:
            name_tag = ['state_governor' + str(i+1) for i in range(nx)]
        return name_tag
