from cProfile import label
import prtpy, benchmark, logging
from matplotlib import pyplot as plt
from partition_uniform_integers import partition_and_compare_random_items
from prtpy.partitioning import balanced, greedy, ilp, dp, ortools_ilp, complete_greedy, roundrobin


benchmark.logger.setLevel(logging.INFO)
benchmark.logger.addHandler(logging.StreamHandler())


data_splittings = []

algorithm1_method = balanced.bidirectional_balanced
algorithm2_method = greedy.greedy

BINS_NUMBER = 50

for i in range(BINS_NUMBER):
    logging.info('i: {0}'.format(i))
    algorithm1 = True
    algorithm2 = True
    splittings_algorithm1 = 0
    splittings_algorithm2 = 0
    for j in range(i):
        results_splittings = benchmark.find_max_solvable_size(
            partition_and_compare_random_items,
            "numitems",
            range(50, 57, 1),
            max_time_in_seconds=10,
            algorithm1=prtpy.partitioning.splittings,
            algorithm1_args={'method':algorithm1_method, 'splits':j},
            algorithm2=prtpy.partitioning.splittings,
            algorithm2_args={'method':algorithm2_method, 'splits':j},
            numbins=i,
            bitsperitem=32
        )

        if algorithm1 and all(result['algorithm1']['diff'] == 0 for result in results_splittings.func_result):
            splittings_algorithm1 = j
            algorithm1 = False

        if algorithm2 and all(result['algorithm2']['diff'] == 0 for result in results_splittings.func_result):
            splittings_algorithm2 = j
            algorithm2 = False
        
        if not algorithm1 and not algorithm2:
            data_splittings.append(
                {
                    'algorithm1':
                        {
                            'numbins':i,
                            'splittings': splittings_algorithm1,
                        },
                    'algorithm2':
                        {
                            'numbins':i,
                            'splittings': splittings_algorithm2,
                        }
                }
            )
            break


plt.plot([data_splitting['algorithm1']['numbins'] for data_splitting in data_splittings], [data_splitting['algorithm1']['splittings'] for data_splitting in data_splittings], 'bo', label=algorithm1_method.__name__)
plt.plot([data_splitting['algorithm2']['numbins'] for data_splitting in data_splittings], [data_splitting['algorithm2']['splittings'] for data_splitting in data_splittings], 'rv', label=algorithm2_method.__name__)
plt.xlabel('num of bins')
plt.ylabel('num of splittings')
plt.legend()
plt.show()


# results_splittings.compare_diff_plot(plt)