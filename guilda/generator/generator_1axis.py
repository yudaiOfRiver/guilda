from typing import List, Optional, Tuple, Union
import numpy as np
from math import sin, cos, atan, atan2, sqrt
from cmath import phase
import control as ct
from control import StateSpace as SS

from guilda.base import StateEquationRecord
from guilda.utils import complex_to_col_vec
from guilda.utils.typing import FloatArray

from guilda.generator.generator import Generator


class Generator1Axis(Generator):
    '''
モデル：同期発電機の1軸モデル
        ・状態：３つ「回転子偏角"δ",周波数偏差"Δω",内部電圧"E"」
              *AVRやPSSが付加されるとそれらの状態も追加される
        ・入力：２ポート「界磁入力"Vfield", 機械入力"Pmech"」
              *定常値からの追加分を指定
親クラス：componentクラス
実行方法：obj = generator_1axis(omega, parameter)
    引数：・omega: float値．系統周波数(50or60*2pi)
     ・parameter : pandas.Series型．「'Xd', 'Xd_prime','Xq','T','M','D'」を列名として定義
    出力：componentクラスのインスタンス

    Args:
        Component (_type_): _description_
    '''

    def get_self_x_name(self) -> List[str]:
        return super().get_self_x_name() + ['Eq']

    @property
    def nx_gen(self):
        return 3

    def get_dx_constraint(
        self,
        V: complex = 0,
        I: complex = 0,
        x: Optional[FloatArray] = None,
        u: Optional[FloatArray] = None,
            t: float = 0) -> Tuple[FloatArray, FloatArray]:

        assert x is not None
        assert u is not None

        Xd = self.parameter.Xd
        Xdp = self.parameter.Xd_prime
        Xq = self.parameter.Xq
        Tdo = self.parameter.Tdo
        M = self.parameter.M
        D = self.parameter.D

        V_abs = abs(V)
        V_angle = atan2(V.imag, V.real)

        delta: float = x[0, 0]
        omega: float = x[1, 0]
        E = x[2, 0]

        V_abs_cos = V.real*cos(delta) + V.imag*sin(delta)
        V_abs_sin = V.real*sin(delta) - V.imag*cos(delta)

        Ir = (E-V_abs_cos)*sin(delta)/Xdp + V_abs_sin*cos(delta)/Xq
        Ii = -(E-V_abs_cos)*cos(delta)/Xdp + V_abs_sin*sin(delta)/Xq

        con = np.array([[I.real - Ir], [I.imag - Ii]])

        Efd = Xd*E/Xdp - (Xd/Xdp - 1)*V_abs_cos

        # スカラーを返す
        dx_avr, dx_pss, dx_gov, \
            Vfd, P_mech = self.get_components_dx(x, u, omega, V_abs, Efd)

        dE = (-Efd + Vfd)/Tdo
        dDelta: float = self.omega0*omega
        dOmega: float = (
            P_mech
            - D*omega
            - V_abs*E*sin(delta-V_angle)/Xdp
            + V_abs**2*(1/Xdp-1/Xq)*sin(2*(delta-V_angle))/2
        )/M

        dx_gen = [[dDelta], [dOmega], [dE]]

        dx = np.vstack((dx_gen, dx_avr, dx_pss, dx_gov))

        return dx, con

    def get_linear_matrix(self, V: complex = 0, x: Optional[FloatArray] = None) -> StateEquationRecord:
        if (x is None or not any(x)) and V is None:
            return self.system_matrix.copy()

        if x is None or not any(x):
            x = self.x_equilibrium

        if V is None:
            V = self.V_equilibrium

        omega0 = self.omega0
        Xd = self.parameter.Xd
        Xdp = self.parameter.Xd_prime
        Xq = self.parameter.Xq
        Tdo = self.parameter.Tdo
        M = self.parameter.M
        d = self.parameter.D

        A_swing = np.array([
            [0, omega0, 0],
            [0, -d/M,   0],
            [0, 0,      0]
        ])
        # u1 = Pmech
        # u2 = Vfd
        # u3 = Pout
        # u4 = Efd
        B_swing = np.array([
            [0,   0,     0,    0],
            [1/M, 0,     -1/M, 0],
            [0,   1/Tdo, 0,    -1/Tdo]
        ])

        # y1 = delta
        # y2 = omega
        # y3 = E
        C_swing = np.identity(3)

        D_swing = np.zeros([3, 4])

        sys_swing = SS(A_swing, B_swing, C_swing, D_swing)

        swing_inputs = ['Pmech', 'Vfd', 'Pout', 'Efd_swing']
        swing_outputs = ['delta', 'omega', 'E']
        SS.set_inputs(sys_swing, swing_inputs)
        SS.set_outputs(sys_swing, swing_outputs)

        # 状態の平衡点を取得
        delta = x[0, 0]
        E = x[2, 0]

        # 以下、行ベクトル
        dV_abscos_dV = np.array([cos(delta), sin(delta)]).reshape(1, -1)
        dV_abssin_dV = np.array([sin(delta), -cos(delta)]).reshape(1, -1)
        dIr_dV = -dV_abscos_dV*sin(delta)/Xdp + dV_abssin_dV*cos(delta)/Xq
        dIi_dV = dV_abscos_dV*cos(delta)/Xdp + dV_abssin_dV*sin(delta)/Xq

        # 以下、スカラー
        V_abscos = V.real*cos(delta) + V.imag*sin(delta)
        V_abssin = V.real*sin(delta) - V.imag*cos(delta)
        dV_abscos = -V_abssin
        dV_abssin = V_abscos

        # 以下、行ベクトル
        vec1 = np.concatenate(
            [np.array([[dV_abscos]]), np.array([[0]]), dV_abscos_dV], axis=1)
        vec2 = np.array([0, Xd/Xdp, 0, 0]).reshape(1, -1)
        dEfd = -vec1*(Xd/Xdp-1) + vec2

        # 以下、スカラー
        dIr_dd = (-dV_abscos*sin(delta)+(E-V_abscos)*cos(delta)) / \
            Xdp + (dV_abssin*cos(delta)-V_abssin*sin(delta))/Xq
        dIi_dd = (dV_abscos*cos(delta)+(E-V_abscos)*sin(delta)) / \
            Xdp + (dV_abssin*sin(delta)+V_abssin*cos(delta))/Xq

        Ieq_vec = np.array([[(E-V_abscos)*sin(delta)/Xdp + V_abssin*cos(delta)/Xq],
                            [-(E-V_abscos)*cos(delta)/Xdp + V_abssin*sin(delta)/Xq]])

        # (delta, E, V) => (Ir, Ii)
        KI_vec1 = np.concatenate(
            [np.array([[dIr_dd]]), np.array([[sin(delta)/Xdp]]), dIr_dV], axis=1)
        KI_vec2 = np.concatenate(
            [np.array([[dIi_dd]]), np.array([[-cos(delta)/Xdp]]), dIi_dV], axis=1)
        KI = np.concatenate([KI_vec1, KI_vec2], axis=0)

        vec3 = np.concatenate([np.zeros([2, 2]), np.identity(2)], axis=1)
        dP = np.array([V.real, V.imag]).reshape(1, -1) @ KI + Ieq_vec.T @ vec3

        # sys_fbの直達行列(4×4)
        D_fb = np.concatenate([dP, dEfd, KI], axis=0)
        A_fb = np.zeros((1, 0))
        B_fb = np.zeros((0, 4))
        C_fb = np.zeros((4, 0))
        sys_fb = SS(A_fb, B_fb, C_fb, D_fb)

        fb_inputs = ['delta', 'E', 'Vr', 'Vi']
        fb_outputs = ['P', 'Efd', 'Ir', 'Ii']
        SS.set_inputs(sys_fb, fb_inputs)
        SS.set_outputs(sys_fb, fb_outputs)

        V_abs = abs(V)
        # sys_Vの直達行列(3×2)
        D_V = np.concatenate([np.identity(2), np.array(
            [V.real, V.imag]).reshape(1, -1)/V_abs], axis=0)
        A_V = np.zeros((1, 0))
        B_V = np.zeros((0, 2))
        C_V = np.zeros((3, 0))
        sys_V = SS(A_V, B_V, C_V, D_V)

        V_inputs = ['Vrin', 'Viin']
        V_outputs = ['Vr', 'Vi', 'V_abs']
        SS.set_inputs(sys_V, V_inputs)
        SS.set_outputs(sys_V, V_outputs)

        sys_avr = self.avr.get_sys()
        sys_pss = self.pss.get_sys()
        sys_gov = self.governor.get_sys()

        # interconnectを使うためにはIOSystemでなくてはいけない
        io_swing = ct.ss2io(sys_swing, name='sys_swing')
        io_fb = ct.ss2io(sys_fb, name='sys_fb')
        io_V = ct.ss2io(sys_V, name='sys_V')
        io_avr = ct.ss2io(sys_avr, name='sys_avr')
        io_pss = ct.ss2io(sys_pss, name='sys_pss')
        io_gov = ct.ss2io(sys_gov, name='sys_gov')

        # 内部のつながりと外部の入出力を設定
        io_closed = ct.interconnect(
            [io_swing, io_fb, io_V, io_avr, io_pss, io_gov],
            connections=[
                ['sys_swing.Pout', 'sys_fb.P'],
                ['sys_avr.Efd', 'sys_fb.Efd'],
                ['sys_swing.Efd_swing', 'sys_fb.Efd'],
                ['sys_fb.delta', 'sys_swing.delta'],
                ['sys_fb.E', 'sys_swing.E'],
                ['sys_fb.Vr', 'sys_V.Vr'],
                ['sys_fb.Vi', 'sys_V.Vi'],
                ['sys_avr.V_abs', 'sys_V.V_abs'],
                ['sys_swing.Vfd', 'sys_avr.Vfd'],
                ['sys_avr.u_avr', 'sys_pss.v_pss'],
                ['sys_pss.omega', 'sys_swing.omega'],
                ['sys_gov.omega_governor', 'sys_swing.omega'],
                ['sys_swing.Pmech', 'sys_gov.Pmech']
            ],
            inplist=['sys_avr.u_avr', 'sys_gov.u_governor',
                     'sys_V.Vrin', 'sys_V.Viin'],
            outlist=['sys_fb.Ir', 'sys_fb.Ii']
        )

        # InputOutputオブジェクトをStateSpaceオブジェクトに変換
        ss_closed = SS(io_closed)
        # 入出力名を新たにつける
        system_inputs = ['u_avr', 'u_governor', 'Vrin', 'Viin']
        system_outputs = ['Ir', 'Ii']
        SS.set_inputs(ss_closed, system_inputs)
        SS.set_outputs(ss_closed, system_outputs)

        # ret_uの作成

        idx_u_avr: Union[int, None] = SS.find_input(ss_closed, 'u_avr')
        idx_u_gov: Union[int, None] = SS.find_input(ss_closed, 'u_governor')
        idx_u_vrin: Union[int, None] = SS.find_input(ss_closed, 'Vrin')
        idx_u_viin: Union[int, None] = SS.find_input(ss_closed, 'Viin')

        assert idx_u_avr is not None
        assert idx_u_gov is not None
        assert idx_u_viin is not None
        assert idx_u_vrin is not None

        _A: FloatArray = ss_closed.A  # type: ignore
        _B: FloatArray = ss_closed.B  # type: ignore
        _C: FloatArray = ss_closed.C  # type: ignore
        _D: FloatArray = ss_closed.D  # type: ignore

        A = _A
        B = _B[:, idx_u_avr: idx_u_gov + 1]
        C = _C
        D = _D[:, idx_u_avr: idx_u_gov + 1]

        BV = _B[:, idx_u_vrin: idx_u_viin + 1]
        DV = _D[:, idx_u_vrin: idx_u_viin + 1]

        BI = np.zeros([A.shape[0], 2])
        DI = -np.identity(2)
        R = np.array([[]]).reshape(self.nx, -1)
        S = np.array([[]]).reshape(-1, self.nx)

        return StateEquationRecord(
            nx=self.nx, nu=self.nu,
            A=A, B=B, C=C, D=D,
            BV=BV, DV=DV, BI=BI, DI=DI,
            R=R, S=S
        )

    def get_self_equilibrium(self, V: complex, I: complex):

        V_abs = abs(V)
        V_angle = phase(V)
        Pow = I.conjugate() * V
        P = Pow.real
        Q = Pow.imag

        Xd = self.parameter.Xd
        Xdp = self.parameter.Xd_prime
        Xq = self.parameter.Xq

        delta = V_angle + atan(P/(Q+(V_abs**2)/Xq))
        Enum = V_abs**4 + Q**2*Xdp*Xq + Q*V_abs**2*Xdp + Q*V_abs**2*Xq + P**2*Xdp*Xq
        Eden = V_abs*sqrt(P**2*Xq**2 + Q**2*Xq**2 + 2*Q*V_abs**2*Xq + V_abs**4)
        E = Enum/Eden

        Vfd = Xd*E/Xdp - (Xd/Xdp-1)*V_abs*cos(delta-V_angle)

        x_gen = np.array([[delta], [0], [E]])

        return x_gen, Vfd
