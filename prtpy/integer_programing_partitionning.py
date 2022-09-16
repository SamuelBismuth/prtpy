'''
This file contains some methods that build a partitionning problem to a standard IP form.
'''

import logging
from prtpy import outputtypes as Bins
from typing import List, Any
import numpy as np


# If you want the debug loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.DEBUG)

# If you want the info loggings to be printed in the terminal, uncomment this line.
# logging.basicConfig(level=logging.INFO)


def build_A_for_partition(bins: Bins, items: List[Any])->np.ndarray:
    '''
    Function that builds the matrix A.
    '''
    len_items = len(items)
    bins_num = bins.num

    n = bins_num * len_items
    m = bins_num + len_items
    logging.info('n:{0}'.format(n))
    logging.info('m:{0}'.format(m))

    A = []

    for i in range(0, m, len_items):
        line = [0] * i + items + [0]*(len_items-i)  
        logging.debug('line:{0}'.format(line))
        A.append(line)

    for i in range(0, len_items):
        line = [0]*n
        for j in range(i, n, len_items):
            line[j] = 1
        logging.debug('line:{0}'.format(line))
        A.append(line)
    logging.info('A:{0}'.format(A))
    return np.array(A, dtype=np.int8)


def build_b_for_partition(bins: Bins, items: List[Any])->np.ndarray:
    '''
    Function that builds the vector b.
    '''
    len_items = len(items)
    bins_num = bins.num
    b = np.array([sum(items) / 2] * bins_num + [1] * len_items, dtype=np.int8)
    logging.info('b:{0}'.format(b))
    return b


def build_c_for_partition(n)->np.ndarray:
    '''
    Function that builds the vector c.
    '''
    c = np.array([0] *  n, dtype=np.int8)
    logging.info('c:{0}'.format(c))
    return c