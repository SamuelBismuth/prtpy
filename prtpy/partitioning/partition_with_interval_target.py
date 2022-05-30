from tkinter import N
from prtpy import  Bins
from typing import List, Any
import logging
from prtpy.bins import BinsKeepingSums
from prtpy.partitioning.splittings import add_split_items
from prtpy.partitioning.fptas import fptas
from prtpy.partitioning.fptas_critical_coordinate import fptas_critical_coordinate


def partition_with_D_interval_target_two_bins(
    bins: Bins,
    items: List[Any],
    t: float
) -> bool:
    '''
    '''
    n = bins.num
    assert n == 2
    largest_item = max(items)
    M = largest_item/n
    items_sum = sum(items)
    S = items_sum/n

    if max(fptas(BinsKeepingSums(2), items, t/2)) < (1 + t) * S:
        return True
    elif max(fptas_critical_coordinate(BinsKeepingSums(2), items, t/2)) < (1 + t) * S:
        return True
    else:
        return False



def partition_with_D_interval_target(
    bins: Bins,
    items: List[Any],
    d: float
) -> bool:
    '''
    '''
    n = bins.num
    m = len(items)
    largest_item = max(items)
    M = largest_item/n
    items_sum = sum(items)
    S = items_sum/n
    t = d  * M / S
    epsilon = t / (4 * m * m)
    if n == 2:
        return partition_with_D_interval_target_two_bins(bins, items, t)

    
    if max(fptas(BinsKeepingSums(n), items, epsilon)) < (1 + t) * S:
        return True
    elif max(fptas_critical_coordinate(BinsKeepingSums(2), items, epsilon)) < (1 + t) * S:
        return True
    
    big_items = n * S * (t / (n-2) - 2 * epsilon)
    B = all(item >= big_items for item in items)


    if (len(B) - 2) % n != 0:
        return False
    l = (len(B) - 2) / n 
    items.sort()
    B12 = items[:2 * l + 2 ]
    B3n = items[2 * l + 2 :]

    if max(fptas(BinsKeepingSums(n - 2), B3n, epsilon)) > (1 + t) * S:
        return False
    
    partition_bin1_and_bin2(BinsKeepingSums(2), B12)


def partition_bin1_and_bin2(
    bins: Bins,
    items: List[Any]
):
    '''
    '''

    return bins

def partition_with_split_items(
    bins: Bins,
    items: List[Any],
    splits: int=0
):
    '''
    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> partition_with_split_items(BinsKeepingContents(2), items=[1,2,3,3,5,9,9], splits=1).bins
    [[9, 2, 1, 4.0], [5, 3, 3, 5.0]]
    '''
    items.sort()
    items = items[::-1]
    entire_items = items[splits:]
    split_items = items[:splits]
    # TODO: Allow for optimization using binary search.
    # partition_with_D_interval_target(bins, entire_items)
    add_split_items(bins, split_items, sum(items)/bins.num)
    logging.debug('entire_items: {0}'.format(entire_items))
    logging.debug('split_items: {0}'.format(split_items))
    logging.debug('bins: {0}'.format(bins))
    return bins