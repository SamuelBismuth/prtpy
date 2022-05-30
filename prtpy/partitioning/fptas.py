# TODO: Check if FPTAS valid.

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
    >>> fptas(BinsKeepingContents(2), [1,1,1,1,2], 0.1).bins
    [[1, 1, 1], [1, 2]]
    >>> fptas(BinsKeepingContents(2), [1,1,1,1,2], 0.1).sums
    array([3., 3.])

    >>> fptas(BinsKeepingContents(2), [46, 39, 27, 26, 16, 13, 10], 0.1).bins
    [[46, 27, 16], [39, 26, 13, 10]]
    >>> fptas(BinsKeepingContents(2), [46, 39, 27, 26, 16, 13, 10], 0.1).sums
    array([89., 88.])

    >>> fptas(BinsKeepingContents(2), [4600, 3900, 270, 2602, 16, 1329, 109], 0.1).bins
    [[4600, 270, 16, 1329, 109], [3900, 2602]]
    >>> fptas(BinsKeepingContents(2), [4600, 3900, 270, 2602, 16, 1329, 109], 0.1).sums
    array([6324., 6502.])
    '''
    rounded_items = round_values(items, epsilon)
    item_indexes = dp.optimal(bins, rounded_items, valueof, objective, get_item_index=True)
    for item_index in item_indexes:
        bins.add_item_to_bin(items[item_index['item_index']], item_index['bin'])
    return bins


if __name__ == "__main__":
    import doctest
    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))