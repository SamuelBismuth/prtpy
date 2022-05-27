import prtpy, benchmark, logging
from matplotlib import pyplot as plt
from partition_uniform_integers import partition_and_compare_random_items
from prtpy.partitioning import balanced, greedy    
from prtpy.partitioning import dp    
from prtpy.partitioning import complete_greedy    
from prtpy.partitioning import roundrobin    


benchmark.logger.setLevel(logging.INFO)
benchmark.logger.addHandler(logging.StreamHandler())


data_splittings = []

for i in range(20):
    logging.info('i: {0}'.format(i))
    for j in range(i):
        results_splittings = benchmark.find_max_solvable_size(
            partition_and_compare_random_items,
            "numitems",
            range(5000, 5500, 100),
            max_time_in_seconds=10,
            algorithm1=prtpy.partitioning.splittings,
            algorithm1_args={'method':roundrobin.roundrobin, 'splits':j},
            algorithm2=prtpy.partitioning.roundrobin,
            algorithm2_args={},
            numbins=i,
            bitsperitem=32
        )
        if all(result['algorithm1']['diff'] == 0 for result in results_splittings.func_result):
            data_splittings.append(
                {
                    'numbins':i,
                    'splittings': j,
                }
            )
            break


plt.plot([data_splitting['numbins'] for data_splitting in data_splittings], [data_splitting['splittings'] for data_splitting in data_splittings], 'bo')
plt.xlabel('num of bins')
plt.ylabel('num of splittings')
plt.legend()
plt.show()


# results_splittings.compare_diff_plot(plt)