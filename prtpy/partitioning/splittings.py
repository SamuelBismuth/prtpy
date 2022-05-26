from typing import Callable, List, Any
from prtpy import outputtypes as out, objectives as obj, Bins
import logging

# If you want the debug loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.DEBUG)


def splittings(
    bins: Bins,
    items: List[Any],
    splits: int,
    algorithm: Any
):
    '''
    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> from prtpy.partitioning import greedy    
    >>> splittings(BinsKeepingContents(2), items=[1,2,3,3,5,9,9], splits=1, algorithm=greedy.greedy).bins
    [[9, 2, 1, 4.0], [5, 3, 3, 5.0]]
    
    >>> list(splittings(BinsKeepingContents(2), items=[1,2,3,3,5,9,9], splits=1, algorithm=greedy.greedy).sums)
    [16.0, 16.0]

    >>> splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=1, algorithm=greedy.greedy).bins
    [[9, 1.666666666666666], [5, 2, 3.666666666666666], [3, 3, 1, 3.666666666666666]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=1, algorithm=greedy.greedy).sums)
    [10.666666666666666, 10.666666666666666, 10.666666666666666]

    >>> splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=2, algorithm=greedy.greedy).bins
    [[5, 5.666666666666666], [3, 2, 5.666666666666666], [3, 1, 6.666666666666666]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=2, algorithm=greedy.greedy).sums)
    [10.666666666666666, 10.666666666666666, 10.666666666666666]

    >>> splittings(BinsKeepingContents(3), items=[1,2,5,5,5,5,5], splits=1, algorithm=greedy.greedy).bins
    [[5, 5], [5, 2, 2.0], [5, 1, 3.0]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,5,5,5,5,5], splits=1, algorithm=greedy.greedy).sums)
    [10.0, 9.0, 9.0]

    >>> from prtpy.partitioning import dp
    >>> splittings(BinsKeepingContents(2), items=[1,2,3,3,5,9,9], splits=1, algorithm=dp.optimal).bins
    [[9, 3, 4.0], [5, 3, 2, 1, 5.0]]
    
    >>> list(splittings(BinsKeepingContents(2), items=[1,2,3,3,5,9,9], splits=1, algorithm=dp.optimal).sums)
    [16.0, 16.0]

    >>> splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=1, algorithm=dp.optimal).bins
    [[9, 1.666666666666666], [5, 2, 3.666666666666666], [3, 3, 1, 3.666666666666666]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=1, algorithm=dp.optimal).sums)
    [10.666666666666666, 10.666666666666666, 10.666666666666666]

    >>> splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=2, algorithm=dp.optimal).bins
    [[5, 5.666666666666666], [3, 1, 6.666666666666666], [3, 2, 5.666666666666666]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,3,3,5,9,9], splits=2, algorithm=dp.optimal).sums)
    [10.666666666666666, 10.666666666666666, 10.666666666666666]

    >>> splittings(BinsKeepingContents(3), items=[1,2,5,5,5,5,5], splits=1, algorithm=dp.optimal).bins
    [[5, 2, 2.0], [5, 5], [5, 1, 3.0]]
    
    >>> list(splittings(BinsKeepingContents(3), items=[1,2,5,5,5,5,5], splits=1, algorithm=dp.optimal).sums)
    [9.0, 10.0, 9.0]
    '''
    items.sort(reverse=True)
    entire_items = items[splits:]
    split_items = items[:splits]
    algorithm(bins, entire_items)
    add_split_items(bins, split_items, sum(items)/bins.num)
    logging.debug('entire_items: {0}'.format(entire_items))
    logging.debug('split_items: {0}'.format(split_items))
    logging.debug('bins: {0}'.format(bins))
    return bins


def add_split_items(
    bins: Bins,
    split_items: List[Any],
    average: float
):
    '''
    Add the split items
    '''
    splittings = sum(split_items)
    overflow = 0
    overflowed_bins = 0
    for bin_sum in bins.sums:
        if bin_sum > average:
            overflow += bin_sum - average
            overflowed_bins += 1
    overflow = overflow / (bins.num - overflowed_bins)

    logging.debug('average: {0}'.format(average))
    logging.debug('bins.sums: {0}'.format(bins.sums))
    logging.debug('overflow: {0}'.format(overflow))

    for i in range(bins.num):
        # If every bin is smaller than the average, there exists a perfect solution.
        # Then, divide the split-items to increase every bin under the average to average - (overflow / bins.num)
        if bins.sums[i] < average:
            split_item = (average - overflow) - bins.sums[i]
            splittings -= split_item
            bins.add_item_to_bin(split_item, i)

    logging.debug('splittings: {0}'.format(splittings))

    assert int(splittings) == 0.0
   

if __name__ == "__main__":
    import doctest

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))