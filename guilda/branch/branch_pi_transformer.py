import numpy as np
from numpy import exp

from guilda.branch.branch import Branch
from guilda.utils.typing import ComplexArray

class BranchPiTransformer(Branch):
    '''
モデル：対地静電容量をもつ送電線のπ型回路モデルに位相調整変圧器が組み込まれたモデル
親クラス：conntroller
実行方法：obj = branch_pi_transformer(from, to, x, y, tap, phase)
引数：・from,to: 接続する母線番号
    ・ x：complex値。インピーダンスの実部、虚部を並べた配列。
    ・ y：double値。対地静電容量の値
    ・ tap：double値。電圧の絶対値の変化率
    ・ phase：double値。電圧の偏角の変化量
出力：branchクラスのインスタンス
restrictions: SetAccess = public

    Args:
        Branch (_type_): _description_
    '''

    def __init__(self, bus1: int, bus2: int, z: complex, y: float, tap: float, phase: float):
        super().__init__(bus1, bus2, z, y)
        
        self.tap: float = tap
        self.phase: float = phase

    def get_admittance_matrix(self) -> ComplexArray:
        x = self.z
        y = self.y
        t = self.tap
        p = self.phase
        Y = np.array((
            [(complex(1/x, y)) / t**2         , - 1 / (x * t * exp(complex(0,-p)))],
            [-1 / (x * t * exp(complex(0, p))), complex(1/x, y)                   ]
        ))
        return Y
