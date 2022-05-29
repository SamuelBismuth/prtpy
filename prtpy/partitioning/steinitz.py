"""
Produce an optimal partition by solving an integer program (IP) using Eisenbrand and Weismantel' algorithm for IP using Steinitz Lemma.
It is known that IP solves numerous combinatorial problems.
As a warm-up, I will focus on the classic k-way number partitionning problem. 
In the future, it will be interesting to use this algorithm to solve harder problem including fair-division problem.
Programmer: Samuel Bismuth
Since: 2022-04
Credit:
The algorithm comes from the paper entitled: "Proximity results and faster algorithms for Integer Programming using the Steinitz Lemma".
The authors of the paper are: Friedrich Eisenbrand and Robert Weismantel.
The paper was published in 2019.
Link of the paper: https://arxiv.org/abs/1707.00481
In the paper, two algorithms are designed to solved IP problems. We decide to implements the first algorithm designed in the paper.
The algorithm is essentially based on the Steinitz Lemma. This is the starting point of the IP solver improvement.
"""


import numpy as np
import networkx as nx
from itertools import product
import logging
import time
import threading
from multiprocessing import Pool
from multiprocessing import freeze_support


# If you want the debug loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.DEBUG)

# If you want the info loggings to be printed in the terminal, uncomment this line.
logging.basicConfig(level=logging.INFO)

# These variables allow us to compare the runtime when using threads or multiprocessings or nothing.
# THREADS = True
# THREADS = False
# MUTLIPROCESSING = True
# MUTLIPROCESSING = False

def steinitz_ip(c:np.ndarray, A:np.ndarray, b:np.ndarray)->str:
    '''
    Given the matrix A and the vectors b and c, this function return the result of the integer programming.

    # >>> steinitz_ip(np.array([0,0,0,0]), np.array([[1,1,0,0],[0,0,1,1],[1,0,1,0],[0,1,0,1]]), np.array([1,1,1,1]))
    # '[1 0 1 0]'

    # >>> steinitz_ip(np.array([0,0,0,0]), np.array([[3, 1, 0, 0], [0, 0, 3, 1], [1, 0, 1, 0], [0, 1, 0, 1]]), np.array([2,2,1,1]))
    # 'Not feasible'
    '''
    G = setup(A, b, c)

    source = str(np.array([0]*len(b), dtype=np.int8))
    target = np.array2string(b)
    if check_feasibility(G, source, target):
        longest_path = tackle_optimization(G, source, target)
        logging.info('Longest path from 0 to b: {0}'.format(longest_path))
        z_star = longest_path[0][1]
        return z_star
    else:
        return 'Not feasible'


def setup(A:np.ndarray, b:np.ndarray, c:np.ndarray, THREADS=False, MUTLIPROCESSING=False)->nx.DiGraph:
    '''
    This method set up all the variable requested by the algorithm.
    '''
    n = len(A)
    m = len(b)

    logging.info('A:{0} '.format(A))
    logging.info('b:{0} '.format(b))
    logging.info('c:{0} '.format(c))

    Delta = max([max(map(float, entry)) for entry in np.absolute(A)])
    logging.info('Delta:{0} '.format(Delta))
    upper_bound = int(2 * m * Delta)
    logging.info('upper_bound:{0} '.format(upper_bound))

    start_fancy_S = time.perf_counter()

    fancy_S = build_fancy_S(b, m, upper_bound)
    logging.debug('fancy_S:{0}'.format(fancy_S))

    finish_fancy_S= time.perf_counter()
    logging.info(f'Finished fancy_S in {round(finish_fancy_S-start_fancy_S,2)} second(s)')

    start_build_graph = time.perf_counter()
    G = nx.DiGraph()
    build_graph(fancy_S, n, A, G, upper_bound, c, THREADS, MUTLIPROCESSING)
    finish_build_graph= time.perf_counter()
    logging.info(f'Finished build_graph in {round(finish_build_graph-start_build_graph,2)} second(s)')

    logging.debug('nodes:{0}'.format(G.nodes))
    logging.debug('edges:{0}'.format(G.edges))

    return G


def build_fancy_S(b:np.ndarray, m:int, upper_bound:int)->np.ndarray:
    '''
    The set fancy_S consists of all points x in Z^m for which there exists a j in {1,...,t} with:
    ||x-(j/t).b||_\infinity <= 2m . \Delta. 
    '''
    fancy_S = []
    t = int(np.linalg.norm(b, ord=1))
    logging.debug('t:{0}'.format(t))
    x = np.array([0.] * m, dtype=np.int8)
    possible_x = [vector for vector in product(range(0, upper_bound + 1), repeat = m)]
    logging.debug('possible_x:{0}'.format(possible_x))
    for x in possible_x:
        for j in range(1,t+1):
            logging.debug('j:{0}'.format(j))
            logging.debug('||x-(j/t)*b||_infinity:{0}'.format(np.linalg.norm(x - ((j/t) * b), np.inf)))
            if np.linalg.norm(x - ((j/t) * b), np.inf) <= upper_bound:
                logging.debug('x:{0}'.format(x))
                fancy_S.append(x)
                break
    return np.array(fancy_S, dtype=np.int8)


def run_multiprocessing(func, n_processors, data):
    '''
    Define function to run mutiple processors and pool the results together
    '''
    with Pool(processes=n_processors) as pool:
        return pool.starmap(func, data)


def build_graph(fancy_S:np.ndarray, n:int, A:np.ndarray, G:nx.digraph, upper_bound:int, c:np.ndarray, THREADS=False, MUTLIPROCESSING=False):
    '''
    This method create the digraph used to resolve the IP.
    '''
    G.add_nodes_from(map(str, fancy_S))
    columns = []
    for i in range(n):
        columns.append(np.array([row[i] for row in A], dtype=np.int8))
    logging.debug('columns: {0}'.format(columns))

    # Here the use of threads is not efficient since the time to create the threads is longer than the execution.
    start = time.perf_counter()
    if THREADS:
        threads = []
        for i in range(n):
            t = threading.Thread(target = add_edge_to_G ,args = [G, fancy_S, columns, i, upper_bound, c])
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
    # Here the use of multiprocessing: this is more efficient.
    elif MUTLIPROCESSING:
        freeze_support()
        n_processors = 6
        data = [(G, fancy_S, columns, i, upper_bound, c) for i in range(n)]
        edges = run_multiprocessing(collect_edge_to_G, n_processors, data)
        for i in range(n):
            for edge in edges[i]:
                G.add_edge(edge[0], edge[1], weight=edge[2])
    else:
        for i in range(n):
            add_edge_to_G(G, fancy_S, columns, i, upper_bound, c)
    finish = time.perf_counter()
    logging.info(f'Finished in {round(finish-start,2)} second(s)')


def add_edge_to_G(G, fancy_S, columns, i, upper_bound, c):
    for x in fancy_S:
        y = x + columns[i]
        if np.linalg.norm(y, np.inf) < upper_bound:
            logging.debug('x: {0}'.format(x))
            logging.debug('y: {0}'.format(y))
            G.add_edge(str(x), str(y), weight=c[i])


def collect_edge_to_G(G, fancy_S, columns, i, upper_bound, c):
    edges = []
    for x in fancy_S:
        y = x + columns[i]
        if np.linalg.norm(y, np.inf) < upper_bound:
            logging.debug('x: {0}'.format(x))
            logging.debug('y: {0}'.format(y))
            edges.append([str(x), str(y), c[i]])
    return edges
    

def check_feasibility(G:nx.DiGraph, source:str, target:str)->bool:
    '''
    Given the graph, this function return if the integer programming is feasible or not.

    >>> check_feasibility(setup(np.array([[1,1,0,0],[0,0,1,1],[1,0,1,0],[0,1,0,1]]), np.array([1,1,1,1]), np.array([0,0,0,0])), '[0 0 0 0]', '[1 1 1 1]')
    True

    >>> check_feasibility(setup(np.array([[3, 1, 0, 0], [0, 0, 3, 1], [1, 0, 1, 0], [0, 1, 0, 1]]), np.array([2,2,1,1]), np.array([0,0,0,0])), '[0 0 0 0]', '[2 2 1 1]')
    False
    '''
    try:
        shortest_path = nx.shortest_path(G, source=source, target=target)
        logging.info('shortest_path:{0}'.format(shortest_path))
        return True
    except Exception as error:
        logging.info(error)
        return False


def is_the_graph_dag(G:nx.digraph)->bool:
    '''
    This method check if the graph contains any cycle.
    '''
    try:
        nx.find_cycle(G)
        return False
    except Exception as error:
        logging.info('error'.format(error))
        return True


def tackle_optimization(G:nx.digraph, source, target)->str:
    """
    This function tackle the optimization of the problem by search for the longest path from 0 to b.
    The path is the solution of the problem.
    """
    if is_the_graph_dag(G):
        return max([(path, sum(G.edges[pair]['weight'] for pair in list(nx.utils.pairwise(path)))) for path in nx.all_simple_paths(G, source, target)], key=lambda x: x[1])
    else:
        return 'Unbounded'


if __name__ == "__main__":
    import doctest

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))