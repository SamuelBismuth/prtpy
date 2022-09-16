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

# If you want the info loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.INFO)


def optimal(
    bins: Bins,
    items: List[Any],
):
    """
    Produce a partition that minimizes the given objective, by solving an integer linear program (ILP).

    :param bins: number of bins.
    :param items: list of items.

    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> optimal(BinsKeepingContents(2), [11.1,11,11,11,22])
    Bin 0
    Item 0 value: 11.1
    Item 2 value: 11
    Item 3 value: 11
    Packed bin value: 33.1
    Bin 1
    Item 1 value: 11
    Item 4 value: 22
    Packed bin value: 33

    >>> optimal(BinsKeepingContents(2), [11,11,11,11,22])
    Bin 0
    Item 0 value: 11
    Item 2 value: 11
    Item 3 value: 11
    Packed bin value: 33
    Bin 1
    Item 1 value: 11
    Item 4 value: 22
    Packed bin value: 33

    The following examples are based on:
        Walter (2013), 'Comparing the minimum completion times of two longest-first scheduling-heuristics'.
    >>> walter_numbers = [46, 39, 27, 26, 16, 13, 10]
    >>> optimal(BinsKeepingContents(3), walter_numbers)
    Bin 0
    Item 1 value: 39
    Item 5 value: 13
    Item 6 value: 10
    Packed bin value: 62
    Bin 1
    Item 2 value: 27
    Item 3 value: 26
    Packed bin value: 53
    Bin 2
    Item 0 value: 46
    Item 4 value: 16
    Packed bin value: 62
    """
    
    data = {}
    data['values'] = items
    
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
                if x[i, b].solution_value() > 0:
                    print(
                        f"Item {i} value: {data['values'][i]}"
                    )
                    bin_value += data['values'][i]
            print(f'Packed bin value: {bin_value}')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == "__main__":
    import doctest

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))
