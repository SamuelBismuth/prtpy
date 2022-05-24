"""
Produce an optimal partition by solving an mixed integer linear program (MILP).

Programmer: Samuel Bismuth
Since: 2022-05
"""

from typing import List, Any
from prtpy import  Bins
from ortools.linear_solver import pywraplp
import logging


# If you want the debug loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.DEBUG)


def optimal(
    bins: Bins,
    items: List[Any],
    splits: int
):
    """
    Produce a partition that minimizes the given objective, by solving an integer linear program (ILP).

    :param bins: number of bins.
    :param items: list of items.

    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> optimal(BinsKeepingContents(2), [11,11,11,11,22], 1)
    Bin 0
    Item 1 split part: 1.0, value: 11.0
    Item 2 split part: 1.0, value: 11.0
    Item 3 split part: 1.0, value: 11.0
    Packed bin value: 33.0
    Bin 1
    Item 0 split part: 1.0, value: 22.0
    Item 4 split part: 1.0, value: 11.0
    Packed bin value: 33.0

    >>> optimal(BinsKeepingContents(2), [10,5], 1)
    Bin 0
    Item 0 split part: 0.7499999999999999, value: 7.499999999999999
    Packed bin value: 7.499999999999999
    Bin 1
    Item 0 split part: 0.2500000000000001, value: 2.500000000000001
    Item 1 split part: 1.0, value: 5.0
    Packed bin value: 7.500000000000001

    The following examples are based on:
        Walter (2013), 'Comparing the minimum completion times of two longest-first scheduling-heuristics'.
    >>> walter_numbers = [46, 39, 27, 26, 16, 13, 10]
    >>> optimal(BinsKeepingContents(3), walter_numbers, 1)
    Bin 0
    Item 0 split part: 0.19565217391304385, value: 9.000000000000018
    Item 2 split part: 1.0, value: 27.0
    Item 5 split part: 1.0, value: 13.0
    Item 6 split part: 1.0, value: 10.0
    Packed bin value: 59.000000000000014
    Bin 1
    Item 0 split part: 0.7173913043478262, value: 33.0
    Item 3 split part: 1.0, value: 26.0
    Packed bin value: 59.0
    Bin 2
    Item 0 split part: 0.08695652173912996, value: 3.9999999999999782
    Item 1 split part: 1.0, value: 39.0
    Item 4 split part: 1.0, value: 16.0
    Packed bin value: 58.99999999999998

    >>> optimal(BinsKeepingContents(3), walter_numbers, 2)
    Bin 0
    Item 0 split part: 0.30434782608695643, value: 13.999999999999996
    Item 1 split part: 0.4871794871794872, value: 19.0
    Item 4 split part: 1.0, value: 16.0
    Item 6 split part: 1.0, value: 10.0
    Packed bin value: 59.0
    Bin 1
    Item 0 split part: 0.6956521739130436, value: 32.00000000000001
    Item 2 split part: 1.0, value: 27.0
    Packed bin value: 59.00000000000001
    Bin 2
    Item 1 split part: 0.5128205128205128, value: 20.0
    Item 3 split part: 1.0, value: 26.0
    Item 5 split part: 1.0, value: 13.0
    Packed bin value: 59.0

    >>> optimal(BinsKeepingContents(5), [5, 5], 3)
    Bin 0
    Item 0 split part: 0.20000000000000004, value: 1.0000000000000002
    Item 1 split part: 0.20000000000000007, value: 1.0000000000000004
    Packed bin value: 2.000000000000001
    Bin 1
    Item 1 split part: 0.39999999999999997, value: 1.9999999999999998
    Packed bin value: 1.9999999999999998
    Bin 2
    Item 0 split part: 0.39999999999999997, value: 1.9999999999999998
    Packed bin value: 1.9999999999999998
    Bin 3
    Item 1 split part: 0.39999999999999997, value: 1.9999999999999998
    Packed bin value: 1.9999999999999998
    Bin 4
    Item 0 split part: 0.39999999999999997, value: 1.9999999999999998
    Packed bin value: 1.9999999999999998

    >>> optimal(BinsKeepingContents(2), [5, 10], 1)
    Bin 0
    Item 0 split part: 0.7499999999999999, value: 7.499999999999999
    Packed bin value: 7.499999999999999
    Bin 1
    Item 0 split part: 0.2500000000000001, value: 2.500000000000001
    Item 1 split part: 1.0, value: 5.0
    Packed bin value: 7.500000000000001
    """
    data = {}
    data['values'] = sorted(items, reverse=True)
    
    data['num_items'] = len(data['values'])
    data['all_items'] = range(data['num_items'])

    data['num_bins'] = bins.num
    data['bin_capacities'] = [sum(data['values']) / data['num_bins']] * data['num_items']
    data['all_bins'] = range(data['num_bins'])

    logging.debug('items: {0}\n'.format(data['values']))

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if solver is None:
        logging.debug('SCIP solver unavailable.')
        return

    # Variables.
    # x[i, b] = 1 if item i is packed in bin b.
    x = {}
    for i in data['all_items']:
        for b in data['all_bins']:
            # TODO: Currently only the item 0 is splitted: make the largest item, or iterate over every items.
            if i < splits:  # We create the real variable.
                x[i, b] = solver.NumVar(0, 1, f'x_{i}_{b}')
            else:
                x[i, b] = solver.BoolVar(f'x_{i}_{b}')

    my_max = solver.NumVar(0, solver.infinity(), 'my_max')

    # Constraints.
    # Each item is assigned to exactly one bin.
    for i in data['all_items']:
        solver.Add(sum(x[i, b] for b in data['all_bins']) == 1)
        

    # We introduce a variable my_max to allow min max.
    for b in data['all_bins']:
        solver.Add(
            sum(x[i, b] * data['values'][i] for i in data['all_items']) <= my_max)

    # Objective.
    # Maximize total value of packed items.
    objective = solver.Objective()
    objective.SetCoefficient(my_max, 1)
    objective.SetMinimization()

    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        for b in data['all_bins']:
            print(f'Bin {b}')
            bin_value = 0
            for i in data['all_items']:
                split_part = x[i, b].solution_value()
                if split_part > 0:
                    value = split_part * data['values'][i]
                    print(f"Item {i} split part: {split_part}, value: {value}")
                    bin_value += value
            print(f'Packed bin value: {bin_value}')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == "__main__":
    import doctest

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))
