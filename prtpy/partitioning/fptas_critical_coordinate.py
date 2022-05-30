# TODO: How to implement?
from prtpy import objectives as obj, Bins
from typing import Callable, List, Any


def fptas_critical_coordinate(
    bins: Bins,
    items: List[Any],
    epsilon: float,
    valueof: Callable[[Any], float] = lambda x: x,
    objective: obj.Objective = obj.MinimizeDifference
):
    raise NotImplementedError("FPTAS with CC.")
