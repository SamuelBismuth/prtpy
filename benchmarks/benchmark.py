from typing import Any, Callable, List
from time import perf_counter, sleep
from matplotlib import pyplot as plt
import logging

logger = logging.getLogger(__name__)


class BenchmarkResults:
    def __init__(
        self,
        func: Callable,
        name_of_argument_to_modify: str,
        sizes_checked: List[int],
        runtimes_found: List[float],
        func_result: Any
    ):
        self.func = func
        self.name_of_argument_to_modify = name_of_argument_to_modify
        self.sizes_checked = sizes_checked
        self.runtimes_found = runtimes_found
        self.func_result = func_result

    def max_solvable_size(self):
        return self.sizes_checked[-1]

    def print(self):
        print(f"Sizes checked: {self.sizes_checked}. Run-times found: {self.sizes_checked}")
        return self

    def tabulate(self):
        print(f"{self.name_of_argument_to_modify}\t\t\tRun-time")
        for size, runtime in zip(self.sizes_checked, self.runtimes_found):
            print(f"{size}\t\t\t{runtime}")
        return self

    def plot(self, ax):
        ax.plot(self.sizes_checked, self.runtimes_found)
        ax.xlabel(self.name_of_argument_to_modify)
        ax.ylabel("Run-time [sec]")
        ax.show()
        return self

    def compare_plot(self, to_compare, ax):
        algorithm1_name = self.func_result[0]['algorithm1']['algorithm_name']
        algorithm2_name = self.func_result[0]['algorithm2']['algorithm_name']
        numbins = self.func_result[0]['numbins']
        fig = ax.gcf()
        fig.canvas.set_window_title('{0}_and_{1}_comparison_by_{2}'.format(algorithm1_name, algorithm2_name, to_compare))
        ax.plot(self.sizes_checked, [result['algorithm1'][to_compare] for result in self.func_result], label='{0} {1}'.format(to_compare, algorithm1_name))
        ax.plot(self.sizes_checked, [result['algorithm2'][to_compare] for result in self.func_result], label='{0} {1}'.format(to_compare, algorithm2_name))
        ax.plot(self.sizes_checked, [result['optimal'][to_compare] for result in self.func_result], 'bo', label='{0} {1}'.format(to_compare, 'optimal'))
        ax.xlabel(self.name_of_argument_to_modify)
        ax.ylabel(to_compare)
        ax.legend()
        ax.title('{0} bin(s)'.format(numbins))
        ax.show()
        return self
    
    def compare_diff_plot(self, ax):
        return self.compare_plot('diff', ax)

    def compare_max_plot(self, ax):
        return self.compare_plot('max_sums', ax)

    def compare_min_plot(self, ax):
        return self.compare_plot('min_sums', ax)

    def compare_all_plots(self, ax):
        self.compare_diff_plot(ax)
        self.compare_max_plot(ax)
        self.compare_min_plot(ax)
        return self


def find_max_solvable_size(
    func: Callable,
    name_of_argument_to_modify: str,
    sizes_to_check: List[int],
    max_time_in_seconds: float,
    *args,
    **kwargs,
) -> BenchmarkResults:
    """
    Run a given function on inputs of increasingly larger size. Measure the run time.
    Stop when the run time exceeds the given threshold.

    :param func - the function to check.
    :param name_of_argument_to_modify - the name of the argument that will be modified
        (the argument that represents the 'size' of the input).
    :param sizes_to_check - a list (possibly infinite) of values that will be given to the above argument.
    :param max_time_in_seconds - the run-time threshold. Once the run-time exceeds this threshold, the test terminates.
    :param args - other arguments to func.
    :param kwargs - other keyword arguments to func.

    :return (sizes, run_times):
         sizes is the list of sizes (the last one of them is the largest);
         run_times is the list of all run-times for the different sizes.
    """
    runtimes_found = []
    sizes_checked = []
    kwargs = dict(kwargs)
    func_result = []
    for size in sizes_to_check:
        start = perf_counter()
        kwargs[name_of_argument_to_modify] = size
        func_result.append(func(*args, **kwargs))
        run_time = perf_counter() - start
        logger.info("  %s=%s, run-time=%s", name_of_argument_to_modify, size, run_time)
        sizes_checked.append(size)
        runtimes_found.append(run_time)
        if run_time > max_time_in_seconds:
            break
    return BenchmarkResults(func, name_of_argument_to_modify, sizes_checked, runtimes_found, func_result)


def find_max_splittings(
    sizes_to_check: List[int],
    max_time_in_seconds: float,
    *args,
    **kwargs,
) -> BenchmarkResults:
    """
    Run a given function on inputs of increasingly larger size. Measure the run time.
    Stop when the run time exceeds the given threshold.

    :param func - the function to check.
    :param name_of_argument_to_modify - the name of the argument that will be modified
        (the argument that represents the 'size' of the input).
    :param sizes_to_check - a list (possibly infinite) of values that will be given to the above argument.
    :param max_time_in_seconds - the run-time threshold. Once the run-time exceeds this threshold, the test terminates.
    :param args - other arguments to func.
    :param kwargs - other keyword arguments to func.

    :return (sizes, run_times):
         sizes is the list of sizes (the last one of them is the largest);
         run_times is the list of all run-times for the different sizes.
    """
    runtimes_found = []
    sizes_checked = []
    kwargs = dict(kwargs)
    func_result = []
    for size in sizes_to_check:
        start = perf_counter()
        kwargs["splittings"] = size
        func_result.append(func(*args, **kwargs))
        run_time = perf_counter() - start
        logger.info("  %s=%s, run-time=%s", "splittings", size, run_time)
        sizes_checked.append(size)
        runtimes_found.append(run_time)
        if run_time > max_time_in_seconds:
            break
    return BenchmarkResults(func, "splittings", sizes_checked, runtimes_found, func_result)


if __name__ == "__main__":

    import itertools

    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    def func(agents: int, items: int):
        sleep(agents * items / 100)

    find_max_solvable_size(
        func,
        name_of_argument_to_modify="agents",
        sizes_to_check=map(lambda i: 1.5**i, itertools.count()),
        max_time_in_seconds=1,
        items=2,
    ).tabulate().plot(plt)
