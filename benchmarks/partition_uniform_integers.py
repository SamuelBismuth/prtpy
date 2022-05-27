""" 
Check partitioning algorithms on uniformly-random integers.
Aims to reproduce the results of Korf, Moffitt and Schreiber (2018), JACM paper.

Author: Erel Segal-Halevi
Since:  2022-05
"""

from typing import Callable
import numpy as np, prtpy
from time import perf_counter


def run(items, algorithm, numbins, **kwargs):
    start = perf_counter()
    sums = prtpy.partition(
        algorithm=algorithm,
        numbins=numbins,
        items=items, 
        outputtype=prtpy.out.Sums,
        **kwargs,
    )
    end = perf_counter()
    max_sums = max(sums)
    min_sums = min(sums)
    algorithm_name = algorithm.__name__
    if algorithm_name == 'splittings':
        algorithm_name += '(_{0}_split(s))'.format(kwargs['splits'])
    return {
        'algorithm_name': algorithm_name,
        'runtime': end-start,
        'diff': max_sums-min_sums,
        'max_sums': max_sums,
        'min_sums': min_sums,
    }


def partition_random_items(
    algorithm: Callable,
    numbins: int,
    numitems: int,
    bitsperitem: int,
    instance_id: int = 0,
    **kwargs,
):
    return run(np.random.randint(1, 2**bitsperitem-1, numitems, dtype=np.int64), algorithm, numbins, **kwargs)


def partition_and_compare_random_items(
    algorithm1: Callable,
    algorithm1_args: dict,
    algorithm2: Callable,
    algorithm2_args: dict,
    numbins: int,
    numitems: int,
    bitsperitem: int,
    instance_id: int = 0,
):
    items = np.random.randint(1, 2**bitsperitem-1, numitems, dtype=np.int64)
    # items = np.random.randint((2**bitsperitem-1 )/2, 2**bitsperitem-1, numitems, dtype=np.int64)
    # items = np.random.randint((2**bitsperitem-1 ) - 100, 2**bitsperitem-1, numitems, dtype=np.int64)
    compare = {}
    compare['numbins'] = numbins
    compare['optimal'] = {
        'diff': 0,
        'max_sums': sum(items)/numbins,
        'min_sums': sum(items)/numbins
        }
    compare['algorithm1'] = run(items, algorithm1, numbins, **algorithm1_args)
    compare['algorithm2'] = run(items, algorithm2, numbins, **algorithm2_args)

    return compare


if __name__ == "__main__":
    import logging, experiments_csv
    experiments_csv.logger.setLevel(logging.INFO)
    experiment = experiments_csv.Experiment("results/", "partition_uniform_integers.csv", backup_folder=None)

    input_ranges = {
        "algorithm": [prtpy.partitioning.greedy, prtpy.partitioning.roundrobin, prtpy.partitioning.multifit],
        "numbins": [2],
        "numitems": [10,20,30,40,50,60,70,80],
        "bitsperitem": [16,32,48],
        "instance_id": range(11)
    }
    experiment.run(partition_random_items, input_ranges)
