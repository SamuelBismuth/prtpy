""" 
Check variants of Complete Greedy algorithm on uniformly-random integers.
Aims to reproduce the results of Korf, Moffitt and Schreiber (2018), JACM paper.

Author: Erel Segal-Halevi
Since:  2022-06
"""

from typing import Callable
import numpy as np, prtpy
from prtpy.partitioning.complete_greedy import anytime as CGA
from prtpy import objectives as obj

TIME_LIMIT=30

def partition_random_items(
    numitems: int,
    bitsperitem: int,
    instance_id: int, # dummy parameter, to allow multiple instances of the same run
    **kwargs
):
    items = np.random.randint(1, 2**bitsperitem-1, numitems, dtype=np.int64)
    sums = prtpy.partition(
        algorithm=CGA,
        numbins=2,
        items=items, 
        outputtype=prtpy.out.Sums,
        time_limit=TIME_LIMIT,
        **kwargs
    )
    return {
        "diff": sums[-1]-sums[0]
    }


if __name__ == "__main__":
    import logging, experiments_csv
    experiments_csv.logger.setLevel(logging.INFO)
    experiment = experiments_csv.Experiment("results/", "check_complete_greedy_variants_5.csv", backup_folder=None)

    prt = prtpy.partitioning
    input_ranges = {
        "numitems": [10, 12, 14, 16, 18, 20, 22, 24, 26, 30, 35, 40, 45, 50],
        "bitsperitem": [16,32,48],
        "instance_id": range(10),
        "objective": [obj.MinimizeLargestSum, obj.MaximizeSmallestSum],
        "use_heuristic_2": [False, True],
        "use_heuristic_3": [True, False],
        "use_lower_bound": [False, True],
    }
    experiment.run_with_time_limit(partition_random_items, input_ranges, time_limit=TIME_LIMIT)


"""
check_complete_greedy_variants_3: minimize largest sum objective; compare lower bound, heuristic 2, and heuristic 3. 
  --  Heuristic 2 is the best, then lower bound; Heuristic 3 is not useful.

check_complete_greedy_variants_4: maximize smallest sum objective; compare lower bound and heuristic 2. 
  -- Heuristic 2 is the best, then lower bound.
  -- But lower-bound is very useful for 16 bits.

check_complete_greedy_variants_5: maximize smallest sum and minimize largest sum; stopping when an optimal solution is found.
"""