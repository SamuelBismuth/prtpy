# TODO: Wait for edut code.

from prtpy.partitioning import dp
from prtpy import objectives as obj, Bins
from typing import Callable, List, Any
from math import ceil


def rounding_factor(values:List[float], epsilon:float)->float:
    '''
    Return the rounding factor for the given epsilon.
    values:List[float], values of the items in problem instance.
    epsilon:float, expected score epsilon.
    '''
    return epsilon * max(values) / (2*len(values))


def round_values(values:List[float], epsilon:float)->List[float]:
    '''
    Return the rounded values for the given epsilon.
    values:List[float], values of the items in problem instance.
    epsilon:float, expected score epsilon.
    '''
    b = rounding_factor(values, epsilon)
    return [
        ceil(v/b)*b
        for v in values
    ]


def fptas(
    bins: Bins,
    items: List[Any],
    epsilon: float,
    valueof: Callable[[Any], float] = lambda x: x,
    objective: obj.Objective = obj.MinimizeDifference
):
    '''
    Fully polynomial-time approximation scheme method for solving knapsack problem
    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> fptas(BinsKeepingContents(2), [1,1,1,1,2], 0.1)
    Bin #0: [1.0, 1.0, 1.0], sum=3.0
    Bin #1: [1.0, 2.0], sum=3.0

    >>> fptas(BinsKeepingContents(2), [46, 39, 27, 26, 16, 13, 10], 0.5)

    >>> fptas(BinsKeepingContents(2), [4600, 3900, 270, 2602, 16, 1329, 109], 0.1)
    
    '''
    print(items)
    rounded_items = round_values(items, epsilon)
    print(rounded_items)
    return dp.optimal(bins, rounded_items, valueof, objective)


if __name__ == "__main__":
    import doctest
    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))
