from cmath import inf
from unittest import result
import prtpy, benchmark, logging
from matplotlib import pyplot as plt
# from partition_uniform_integers import partition_and_compare_random_items
from partition_uniform_integers import partition_random_items
from prtpy.partitioning import balanced, greedy, ilp, dp, ortools_ilp, complete_greedy, roundrobin, splittings
from prtpy.bins import BinsKeepingSums, BinsKeepingContents
from partition_uniform_integers import run
import numpy as np

benchmark.logger.setLevel(logging.INFO)
benchmark.logger.addHandler(logging.StreamHandler())

algorithm_method = ortools_ilp.optimal

numbins = 10
bitsperitem=2
numitems=19
mini=90
maxi=92
# items = np.random.randint((2**bitsperitem-1 )/2, 2**bitsperitem-1, numitems, dtype=np.int64)
items = np.random.randint(mini, maxi, numitems, dtype=np.int64)

logging.info(items)
results = []

perfect_solution = sum(items)/numbins
logging.info(perfect_solution)

num_of_split_required = numbins - 1


for i in range(numbins):
    logging.info('i: {0}'.format(i))
    logging.info(prtpy.partitioning.splittings(BinsKeepingContents(numbins), items=items, splits=i, method=splittings.splittings).bins)
    result = max(prtpy.partitioning.splittings(BinsKeepingSums(numbins), items=items, splits=i, method=splittings.splittings).sums)
    logging.info(result)
    results.append(result)
    if result == perfect_solution:
        num_of_split_required = i
        break
    


plt.title('n={0}, m={1}'.format(numbins, numitems))
plt.plot(results)
plt.plot(perfect_solution)
plt.hlines(perfect_solution, 0, num_of_split_required, color='red')
plt.legend(['Optimal Solution', 'Perfect Solution'])
plt.xlabel('num of split-items')
plt.ylabel('min-max')
plt.show()

