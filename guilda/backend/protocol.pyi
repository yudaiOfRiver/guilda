from typing import Iterable, Any, Union, Tuple, overload
from guilda.backend.types import ArrayLike, ShapeLike, NumberLike

pi: float
e: float
nan: float
inf: float
NaN: float


def array(object: ArrayLike) -> ArrayProtocol: ...


def copy(object: ArrayProtocol) -> ArrayProtocol: ...


def zeros(shape: ShapeLike) -> ArrayProtocol: ...


def ones(shape: ShapeLike) -> ArrayProtocol: ...


def identity(shape: int) -> ArrayProtocol: ...


def rvec(object: Iterable[NumberLike]) -> ArrayProtocol: ...


def cvec(object: Iterable[NumberLike]) -> ArrayProtocol: ...


def diag(object: Iterable[NumberLike]) -> ArrayProtocol: ...


@overload
def hstack(tup: Iterable[ArrayLike]) -> ArrayProtocol: ...
@overload
def hstack(tup: Iterable[ArrayProtocol]) -> ArrayProtocol: ...


@overload
def vstack(tup: Iterable[ArrayLike]) -> ArrayProtocol: ...
@overload
def vstack(tup: Iterable[ArrayProtocol]) -> ArrayProtocol: ...


@overload
def dstack(tup: Iterable[ArrayLike]) -> ArrayProtocol: ...
@overload
def dstack(tup: Iterable[ArrayProtocol]) -> ArrayProtocol: ...


def concatenate(tup: Iterable[ArrayLike], axis: int = -1) -> ArrayProtocol:
    ...


def inv(object: ArrayLike) -> ArrayProtocol: ...


def arange(start: NumberLike, stop: NumberLike, step: NumberLike) -> ArrayProtocol:
    ...


class ArrayProtocol:

    def __init__(self, iterable: Iterable) -> None: ...

    @overload
    def __getitem__(self, index: Union[int, Tuple[int, ...]]) -> Any: ...
    @overload
    def __getitem__(self, index: Union[slice, Tuple[slice, ...]]) -> Any: ...

    def __setitem__(
        self, index: Union[int, Tuple[int, ...]], value: Any) -> None: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterable: ...

    @property
    def shape(self) -> ShapeLike: ...

    def reshape(self, *shape: Union[int, ShapeLike]) -> ArrayProtocol: ...

    def flatten(self) -> ArrayProtocol: ...

    def transpose(self) -> ArrayProtocol: ...

    @overload
    def __add__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __add__(self, other: NumberLike) -> ArrayProtocol: ...

    @overload
    def __sub__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __sub__(self, other: NumberLike) -> ArrayProtocol: ...

    @overload
    def __mul__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __mul__(self, other: NumberLike) -> ArrayProtocol: ...
    
    @overload
    def __rmul__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __rmul__(self, other: NumberLike) -> ArrayProtocol: ...

    @overload
    def __div__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __div__(self, other: NumberLike) -> ArrayProtocol: ...
    
    @overload
    def __rdiv__(self, other: ArrayProtocol) -> ArrayProtocol: ...
    @overload
    def __rdiv__(self, other: NumberLike) -> ArrayProtocol: ...

    def dot(self, other: ArrayProtocol) -> ArrayProtocol: ...

    def __str__(self) -> str: ...
    
    def __neg__(self) -> ArrayProtocol: ...
    
    
    def __matmul__(self, other: ArrayProtocol) -> ArrayProtocol: ...
