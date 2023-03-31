from abc import ABC, abstractmethod as AM
from typing import Optional, Tuple
import numpy as np

from guilda.utils.typing import FloatArray
from guilda.base.types import StateEquationRecord


class Component(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """

    def __init__(self):
        self.__v_eq: complex = 0
        self.__i_eq: complex = 0

    @property
    def x_equilibrium(self) -> FloatArray:
        return np.zeros((0, 1))
    
    @property
    def V_equilibrium(self) -> complex:
        return self.__v_eq
    
    @property
    def I_equilibrium(self) -> complex:
        return self.__i_eq

    def set_equilibrium(self, V: complex, I: complex) -> None:
        """_summary_

        Args:
            V (complex): voltage at equilibrium
            I (complex): current at equilibrium
        """        
        self.__v_eq = V
        self.__i_eq = I

    @AM
    def get_nx(self) -> int:
        """Returns the dimension of the component's state.
        """

    @AM
    def get_nu(self) -> int:
        """Returns the dimension of the component's input.
        """

    @AM
    def get_linear_matrix(self, V: complex = 0, x: Optional[FloatArray] = None) -> StateEquationRecord:
        """_summary_

        Args:
            v: voltage at equilibrium.
            x: state at equilibrium.
        """

    @AM
    def get_dx_constraint(
        self,
        V: complex = 0,
        I: complex = 0,
        x: Optional[FloatArray] = None,
        u: Optional[FloatArray] = None,
        t: float = 0) -> Tuple[FloatArray, FloatArray]:
        """_summary_

        Args:
            V (complex, optional): _description_. Defaults to 0.
            I (complex, optional): _description_. Defaults to 0.
            x (Optional[NDArray], optional): _description_. Defaults to None.
            u (Optional[NDArray], optional): _description_. Defaults to None.
            t (float, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
    @AM
    def get_dx_constraint_linear(
        self,
        V: complex = 0,
        I: complex = 0,
        x: Optional[FloatArray] = None,
        u: Optional[FloatArray] = None,
        t: float = 0) -> Tuple[FloatArray, FloatArray]:
        """_summary_

        Args:
            V (complex, optional): _description_. Defaults to 0.
            I (complex, optional): _description_. Defaults to 0.
            x (Optional[NDArray], optional): _description_. Defaults to None.
            u (Optional[NDArray], optional): _description_. Defaults to None.
            t (float, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        
    def get_dx_con_func(self, linear: bool):
        return self.get_dx_constraint_linear if linear else self.get_dx_constraint


class ComponentEmpty(Component):

    def get_nx(self) -> int:
        return 0

    def get_nu(self) -> int:
        return 0

    def get_dx_constraint(
        self,
        V: complex = 0,
        I: complex = 0,
        x: Optional[FloatArray] = None,
        u: Optional[FloatArray] = None,
        t: float = 0) -> Tuple[FloatArray, FloatArray]:
        dx: FloatArray = np.array([], dtype=np.float64).reshape(-1, 1)
        constraint: FloatArray = np.zeros([2, 1], dtype=np.float64)
        return (dx, constraint)

    def get_dx_constraint_linear(
        self,
        V: complex = 0,
        I: complex = 0,
        x: Optional[FloatArray] = None,
        u: Optional[FloatArray] = None,
        t: float = 0) -> Tuple[FloatArray, FloatArray]:
        return self.get_dx_constraint(V, I, x, u, t)

    def get_linear_matrix(self, V: complex = 0, x: Optional[FloatArray] = None) -> StateEquationRecord:
        A = np.array([]).reshape(-1, 1)
        B = np.array([]).reshape(-1, 1)
        C = np.zeros([2, 0])
        D = np.zeros([2, 0])
        BV = np.zeros([0, 2])
        DV = np.zeros([2, 2])
        R = np.array([]).reshape(-1, 1)
        S = np.array([]).reshape(-1, 1)
        DI = -np.identity(2)
        BI = np.zeros([0, 2])

        return StateEquationRecord(
            n_x=self.get_nx(), n_u=self.get_nu(),
            A=A, B=B, C=C, D=D,
            BV=BV, DV=DV, BI=BI, DI=DI,
            R=R, S=S
        )
