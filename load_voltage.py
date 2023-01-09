from component import Component

import numpy as np

class LoadVoltage(Component):
# モデル ：定電圧負荷モデル
#       ・状態：なし
#       ・入力：２ポート「電圧フェーザの実部の倍率,電圧フェーザの虚部の倍率」
#               *入力αのとき値は設定値の(1+α)倍となる．
#親クラス：componentクラス
#実行方法：obj = load_voltage()
#　引数　：なし
#　出力　：componentクラスのインスタンス
    def __init__(self):
        self.x_equilibrium = np.zeros([0, 1])
        self.S = np.array([]).reshape(1, -1)
        self.R = np.array([]).reshape(1, -1)

        self.V_equilibrium = None
        self.I_equilibrium = None
        self.Y = None

    def set_equilibrium(self, Veq, Ieq):
        self.V_equilibrium = Veq
        self.I_equilibrium = Ieq

    def get_dx_constraint(self, V, u, t=None, x=None, I=None):
        dx = np.zeros([0, 1])
        constraint = np.array([[V.real], [V.imag]]) - np.array([[self.V_equilibrium.real*(1+u[0, 0])], [[self.V_equilibrium.imag*(1+u[1, 0])]]])
        return [dx, constraint]

    def get_dx_constraint_linear(self, V, I, u, t=None, x=None):
        [A, B, C, D, BV, DV, BI, DI, _, _] = self.get_linear_matrix_(x, V)
        dx = np.zeros([0, 1])
        diff_I = np.array([[I.real], [I.imag]]) - np.array([[self.I_equilibrium.real], [self.I_equilibrium.imag]])
        diff_V = np.array([[V.real], [V.imag]]) - np.array([[self.V_equilibrium.real], [self.V_equilibrium.imag]])
        constraint = D@u + DI@diff_I + DV@diff_V
        return [dx, constraint]

    def get_nu(self):
        return 2

    def get_linear_matrix_(self, *args):
        A = np.array([]).reshape(1, -1)
        B = np.zeros([0, 2])
        C = np.zeros([2, 0])
        D = np.identity(2) @ np.array([[self.I_equilibrium.real], [self.I_equilibrium.imag]])
        BV = np.zeros([0, 2])
        BI = np.zeros([0, 2])
        DV = np.zeros([2, 2])
        DI = -np.identity(2)
        R = self.R
        S = self.S
        return [A, B, C, D, BV, DV, BI, DI, R, S]