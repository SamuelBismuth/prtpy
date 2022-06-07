import benchmark, logging
from matplotlib import pyplot as plt
from prtpy.partitioning import steinitz
import time
import numpy as np
from operator import sub
import random

benchmark.logger.setLevel(logging.INFO)
benchmark.logger.addHandler(logging.StreamHandler())

num_of_examples = 5

start = []
finish = []

start_multiprocessing = []
finish_multiprocessing = []

start_thread = []
finish_thread = []

for i in range(num_of_examples):
    logging.info('Example number {0}'.format(i))
    num1 = random.randint(0, 3)
    num2 = random.randint(0, 3)
    A = np.array([
        [num1,num2,0,0],
        [0,0,num1,num2],
        [1,0,1,0],
        [0,1,0,1]
        ])
    c = np.array([0,0,0,0])
    capacity = int(sum(A[0])/2)
    b = np.array([capacity,capacity,1,1])

    source = '[0 0 0 0]'
    target = '[{0} {0} 1 1]'.format(capacity)

    start.append(time.perf_counter())
    steinitz.check_feasibility(steinitz.setup(A, b, c), source, target)
    finish.append(time.perf_counter())

    start_multiprocessing.append(time.perf_counter())
    steinitz.check_feasibility(steinitz.setup(A, b, c, False, True), source, target)
    finish_multiprocessing.append(time.perf_counter())

    start_thread.append(time.perf_counter())
    steinitz.check_feasibility(steinitz.setup(A, b, c, True, False), source, target)
    finish_thread.append(time.perf_counter())

total_time = list(map(sub, finish, start))
total_time_multiprocessing = list(map(sub, finish_multiprocessing, start_multiprocessing))
total_time_thread = list(map(sub, finish_thread, start_thread))

plt.plot(range(num_of_examples), total_time, "go", label='Normal')
plt.plot(range(num_of_examples), total_time_thread, "bo", label='Threads')
plt.plot(range(num_of_examples), total_time_multiprocessing, "r+", label='Multiprocessings')
plt.xlabel('Example')
plt.ylabel('Run time (in seconds)')
plt.legend()
plt.title('Runtime comparison')
plt.show()