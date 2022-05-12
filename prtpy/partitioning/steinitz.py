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


<<<<<<< HEAD
<<<<<<< HEAD
import numpy as np
import networkx as nx
from itertools import product
import logging


# If you want the debug loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.DEBUG)

# If you want the info loggings to be printed in the terminal, uncomment this line.
logging.basicConfig(level=logging.INFO)


# TODO: Move the test in the integer_programming_partitionning file and test here some general IP equations.
# TODO: Remove any partition dependency in this file. 

def steinitz_ip(c:np.ndarray, A:np.ndarray, b:np.ndarray)->str:
    '''
    Given the matrix A and the vectors b and c, this function return the result of the integer programming.

    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> from prtpy.integer_programing_partitionning import build_A_for_partition, build_b_for_partition, build_c_for_partition

    >>> steinitz_ip(build_c_for_partition(4), build_A_for_partition(BinsKeepingContents(2), [1,1]), build_b_for_partition(BinsKeepingContents(2), [1,1]))
    '[1 0 1 0]'
    
    >>> steinitz_ip(build_c_for_partition(4), build_A_for_partition(BinsKeepingContents(2), [3,1]), build_b_for_partition(BinsKeepingContents(2), [3,1]))
    'Not feasible'
    '''
    G = setup(A, b, c)

    logging.debug('nodes:{0}'.format(G.nodes))
    logging.debug('edges:{0}'.format(G.edges))

    source = str(np.array([0]*len(b), dtype=np.int8))
    target = np.array2string(b)
    if check_feasibility(G, source, target):
        longest_path = tackle_optimization(G, source, target)
        logging.info('Longest path from 0 to b: {0}'.format(longest_path))
        z_star = longest_path[0][1]
        return z_star
    else:
        return 'Not feasible'


def setup(A:np.ndarray, b:np.ndarray, c:np.ndarray)->nx.DiGraph:
    '''
    This method set up all the variable requested by the algorithm.
    '''
    n = len(A)
    m = len(b)

    Delta = max([max(map(float, entry)) for entry in np.absolute(A)])
    logging.info('Delta:{0} '.format(Delta))
    upper_bound = int(2 * m * Delta)
    logging.info('upper_bound:{0} '.format(upper_bound))

    fancy_S = build_fancy_S(b, m, upper_bound)
    logging.debug('fancy_S:{0}'.format(fancy_S))
    
    G = nx.DiGraph()
    build_graph(fancy_S, n, A, G, upper_bound, c)
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


def build_graph(fancy_S:np.ndarray, n:int, A:np.ndarray, G:nx.digraph, upper_bound:int, c:np.ndarray):
    '''
    This method create the digraph used to resolve the IP.
    '''
    G.add_nodes_from(map(str, fancy_S))
    columns = []
    for i in range(n):
        columns.append(np.array([row[i] for row in A], dtype=np.int8))
    logging.debug('columns: {0}'.format(columns))
    for i in range(n):
        for x in fancy_S:
            y = x + columns[i]
            if np.linalg.norm(y, np.inf) < upper_bound:
                logging.debug('x: {0}'.format(x))
                logging.debug('y: {0}'.format(y))
                G.add_edge(str(x), str(y), weight=c[i])
    

def check_feasibility(G:nx.DiGraph, source:str, target:str)->bool:
    '''
    Given the graph, this function return if the integer programming is feasible or not.

    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> from prtpy.integer_programing_partitionning import build_A_for_partition, build_b_for_partition, build_c_for_partition

    >>> check_feasibility(setup(build_A_for_partition(BinsKeepingContents(2), [1,1]), build_b_for_partition(BinsKeepingContents(2), [1,1]), build_c_for_partition(4)), '[0 0 0 0]', '[1 1 1 1]')
    True
    
    >>> check_feasibility(setup(build_A_for_partition(BinsKeepingContents(2), [3,1]), build_b_for_partition(BinsKeepingContents(2), [3,1]), build_c_for_partition(4)), '[0 0 0 0]', '[2 2 1 1]')
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
    The path is the solution of the proble,.
    """
    if is_the_graph_dag(G):
        return max([(path, sum(G.edges[pair]['weight'] for pair in list(nx.utils.pairwise(path)))) for path in nx.all_simple_paths(G, source, target)], key=lambda x: x[1])
    else:
        return 'Unbounded'
=======
=======
import numpy as np
import networkx as nx
import itertools
>>>>>>> 1de29d8 (Building the skeleton of the algorithm, there are a lot of things to fix.)
from typing import Callable, List, Any
from prtpy import outputtypes as out, objectives as obj, Bins
from typing import List, Callable, Any
from math import inf
import logging


def optimal(
    bins: Bins,
    items: List[Any],
    valueof: Callable[[Any], float] = lambda x: x,
    objective: obj.Objective = obj.MinimizeDifference,
    copies=1,
    max_seconds=inf,
    additional_constraints:Callable=lambda sums:[],
    weights:List[float]=None,
    verbose=0
):
    """
    The function signature and the doctest is implemented by Erel Segal-Halevi in the ilp.py file.

    Produce a partition that minimizes the given objective, by solving an integer linear program (ILP).

    :param numbins: number of bins.
    :param items: list of items.
    :param valueof: a function that maps an item from the list `items` to a number representing its value.
    :param objective: whether to maximize the smallest sum, minimize the largest sum, etc.
    :param outputtype: whether to return the entire partition, or just the sums, etc.
    :param copies: how many copies there are of each item. Default: 1.
    :param max_seconds: stop the computation after this number of seconds have passed.
    :param additional_constraints: a function that accepts the list of sums in ascending order, and returns a list of possible additional constraints on the sums.
    :param weights: if given, must be of size bins.num. Divides each sum by its weight before applying the objective function.

    >>> from prtpy.bins import BinsKeepingContents, BinsKeepingSums
    >>> optimal(BinsKeepingContents(2), [10,10], objective=obj.MaximizeSmallestSum).sums
    array([10., 10.])
    
    # >>> optimal(BinsKeepingContents(2), [15,5], objective=obj.MaximizeSmallestSum).sums
    # array([33., 33.])

    # >>> optimal(BinsKeepingContents(2), [11.1,11,11,11,22], objective=obj.MaximizeSmallestSum).sums
    # array([33. , 33.1])

    # >>> optimal(BinsKeepingContents(2), [11,11,11,11,22], objective=obj.MaximizeSmallestSum).sums
    # array([33., 33.])


    # The following examples are based on:
    #     Walter (2013), 'Comparing the minimum completion times of two longest-first scheduling-heuristics'.
    # >>> walter_numbers = [46, 39, 27, 26, 16, 13, 10]
    # >>> optimal(BinsKeepingContents(3), walter_numbers, objective=obj.MinimizeDifference).sort()
    # Bin #0: [39, 16], sum=55.0
    # Bin #1: [46, 13], sum=59.0
    # Bin #2: [27, 26, 10], sum=63.0
    # >>> optimal(BinsKeepingContents(3), walter_numbers, objective=obj.MinimizeLargestSum).sort()
    # Bin #0: [27, 26], sum=53.0
    # Bin #1: [46, 16], sum=62.0
    # Bin #2: [39, 13, 10], sum=62.0
    # >>> optimal(BinsKeepingContents(3), walter_numbers, objective=obj.MaximizeSmallestSum).sort()
    # Bin #0: [46, 10], sum=56.0
    # Bin #1: [27, 16, 13], sum=56.0
    # Bin #2: [39, 26], sum=65.0
    # >>> optimal(BinsKeepingContents(3), walter_numbers, objective=obj.MinimizeLargestSum, additional_constraints=lambda sums: [sums[0]==0]).sort()
    # Bin #0: [], sum=0.0
    # Bin #1: [39, 26, 13, 10], sum=88.0
    # Bin #2: [46, 27, 16], sum=89.0
    # >>> optimal(BinsKeepingContents(3), walter_numbers, objective=obj.MaximizeSmallestSum).sums
    # array([56., 56., 65.])

    # >>> items = [11.1, 11, 11, 11, 22]
    # >>> optimal(BinsKeepingContents(2), items, objective=obj.MaximizeSmallestSum, weights=[1,1]).sums
    # array([33. , 33.1])
    # >>> optimal(BinsKeepingContents(2), items, objective=obj.MaximizeSmallestSum, weights=[1,2]).sums
    # array([22. , 44.1])
    # >>> optimal(BinsKeepingContents(2), items, objective=obj.MaximizeSmallestSum, weights=[10,2]).sums
    # array([55. , 11.1])

    # >>> from prtpy import partition
    # >>> partition(algorithm=optimal, numbins=3, items={"a":1, "b":2, "c":3, "d":3, "e":5, "f":9, "g":9})
    # [['a', 'g'], ['c', 'd', 'e'], ['b', 'f']]
    # >>> partition(algorithm=optimal, nummipbins=2, items={"a":1, "b":2, "c":3, "d":3, "e":5, "f":9, "g":9}, outputtype=out.Sums)
    # array([16., 16.])
    """
    # If you want the info and debug loggings to be printed in the terminal, uncomment this line.
    logging.basicConfig(level=logging.DEBUG)

    len_items = len(items)
    bins_num = bins.num
    n = bins_num * len_items
    m = bins_num + len_items

    A = build_A(n, m, items, len_items)
    b = np.array([sum(items) / 2] * bins_num + [1] * len_items)
    logging.debug('A:{0}'.format(A))
    logging.debug('b:{0}'.format(b))
    
    Delta = max([max(map(float, entry)) for entry in np.absolute(A)])
    logging.debug('Delta:{0} '.format(Delta))
    
    fancy_S = build_fancy_S(b, m, Delta)
    logging.debug('fancy_S:{0}'.format(fancy_S))
    
    G = nx.DiGraph()
    create_graph(fancy_S, n, A, G)

    logging.debug('nodes:{0}'.format(G.nodes))
    logging.debug('edges:{0}'.format(G.edges))

    # print(nx.shortest_path(G, source='[0.]', target=np.array2string(b)))

    return bins  # Empty implementation.
>>>>>>> e65a86c (Changing filename.)


def build_A(n, m, items, len_items):
    '''
    Function that builds the matrix A.
    '''
    A = []
    for i in range(0, m, len_items):
        line = [0] * i + items + [0]*(len_items-i)  
        # logging.debug('line:{0}'.format(line))
        A.append(line)
    for i in range(0, len_items):
        line = [0]*n
        for j in range(i, n, len_items):
            line[j] = 1
        # logging.debug('line:{0}'.format(line))
        A.append(line)
    return np.array(A)


def build_fancy_S(b, m, Delta):
    '''
    The set fancy_S consists of all points x in Z^m for which there exists a j in {1,...,t} with:
    ||x-(j/t).b||_\infinity <= 2m . \Delta. 
    '''
    fancy_S = []
    t = 5  # TODO: What is t???
    x = np.array([0.] * m)
    solution_exists = True
    while solution_exists:
        for j in range(1,t+1):
            # logging.debug('j:{0}'.format(j))
            # logging.debug('||x-(j/t)*b||_infinity:{0}'.format(np.linalg.norm(x - ((j/t) * b), np.inf)))
            if np.linalg.norm(x - ((j/t) * b), np.inf) <= 2 * m * Delta:
                fancy_S.append(x.copy())
                # TODO: How to increment x?
                x=x+1
                break
            elif j == t:
                solution_exists = False
    return np.array(fancy_S)


def create_graph(fancy_S, n, A, G):
    '''
    This method create the digraph used to resolve the IP.
    '''
    G.add_nodes_from(map(str, fancy_S))
    columns = []
    for i in range(n):
        columns.append(np.array([row[i] for row in A]))
    # logging.debug('columns: {0}'.format(columns))
    for x,y in itertools.product(fancy_S, repeat=2):
        # logging.debug('y:{0}, x:{1}'.format(y,x))
        # logging.debug('y - x: {0}'.format(y-x))
        for i in range(n):
            # logging.debug('columns[i]: {0}'.format(columns[i]))
            if (y - x == columns[i]).all():
                G.add_edge(str(x), str(y))
                break


if __name__ == "__main__":
    import doctest

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))