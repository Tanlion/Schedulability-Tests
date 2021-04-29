"""
Implements UUniFast Discard model to generate taskset and task data file.
"""
import numpy as np
import random
from math import floor, ceil, gcd
from Task import LCM
from Task import Task
import time
import subprocess

def UUniFastDiscard(totalu, nsets, ntasks): #ntasks > totalu
    """
        Generate utilizations.
        The UUniFast algorithm was proposed by Bini for generating task
        utilizations on uniprocessor architectures.

        The UUniFast-Discard algorithm extends it to multiprocessor by
        discarding task sets containing any utilization that exceeds 1.

        This algorithm is easy and widely used. However, it suffers from very
        long computation times when n is close to u. Stafford's algorithm is
        faster.
        Args:
            - `ntasks`: The number of tasks in a task set.
            - `totalu`: Total utilization of the task set.
            - `nsets`: Number of sets to generate.

        Returns a list of `nsets` of `ntasks` task utilizations.
    """
    if ntasks < totalu:
        print("Invaild Condition: Total utilization should less tasks amount.")
        return None

    usets = [] # sets of untilizations for each task set
    while len(usets) < nsets:
        # Classic UUniFast algorithm:
        utilizations = []
        sumU = totalu
        for i in range(1, ntasks):
            nextSumU = sumU * random.random() ** (1.0 / (ntasks - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        # If no task utilization exceeds 1:
        if all(ut <= 1 for ut in utilizations):
            usets.append(utilizations)
    return usets



def gen_periods_loguniform(nsets, ntasks, min_, max_, round_to_int=False):
    """
    Generate a list of `nsets` sets containing each `n` random periods using a
    loguniform distribution.

    Args:
        - `ntasks`: The number of tasks in a task set.
        - `nsets`: Number of sets to generate.
        - `min_`: Period min.
        - `max_`: Period max.
    """
    periods = np.exp(np.random.uniform(low=np.log(min_), high=np.log(max_),
                                       size=(nsets, ntasks)))
    if round_to_int:
        return np.rint(periods).tolist()
    else:
        return periods.tolist()


def gen_periods(nsets, ntasks):
    psets = []
    random_list = [80, 200, 240, 420, 560, 700, 1200]
    while len(psets) < nsets:
        periods = []
        for i in range(0, ntasks):
            period = random.choice(random_list)
            periods.append(period)
        psets.append(periods)
    return psets

def gen_tasksets(utilizations, periods):
    """
    Take a list of task utilization sets and a list of task period sets and
    return a list of couples (c, p) sets. The computation times are truncated
    at a precision of 10^-10 to avoid floating point precision errors.

    Args:
        - `utilization`: The list of task utilization sets. For example::

            [[0.3, 0.4, 0.8], [0.1, 0.9, 0.5]]
        - `periods`: The list of task period sets. For examples::

            [[100, 50, 1000], [200, 500, 10]]

    Returns: (wcxt, period)
        For the above example, it returns::

            [[(30.0, 100), (20.0, 50), (800.0, 1000)],
             [(20.0, 200), (450.0, 500), (5.0, 10)]]
    """

    def trunc(x, p):
        return int(x * 10 ** p) / float(10 ** p)

    return [[(trunc(ui * pi, 6), trunc(pi, 6)) for ui, pi in zip(us, ps)]
            for us, ps in zip(utilizations, periods)]



def write_to_file(m, nsets, ntasks):
    totalu = m
    step = m / 16     # utilization increment step
    coe = 2.0        # [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
    # coe_list = [0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
    # random_list = [80, 200, 240, 420, 560, 700, 1200]
    # random_list = [200, 300, 400, 500, 600, 700, 800, 900, 1000]
    random_list = [300, 400, 500, 600]
    lcm = LCM(random_list)

    file = open("Task_data_{0}u_{1}_{2}_{3}coe_{4}lcm.txt".
                format(totalu, nsets, ntasks, coe, lcm), "w")
    configuration_data = ("Total Util: {}, Nsets: {}, Ntasks: {}".format(totalu, nsets, ntasks))
    file.write(configuration_data)
    file.write("\n")

    for u in np.arange(step, totalu + step, step):  # np.arange(start, stop, step), exclude stop
        file.write("Utilization : {0}\n".format(round(u, 4)))
        util_set = UUniFastDiscard(u, nsets, ntasks) ###
        # task_sets = []
        for i in range(0, nsets):
            file.write("Task_Set : " + str(i + 1) + "\n")
            task_set = []
            for j in range(0, ntasks):
                utilization = util_set[i][j]
                period = random.choice(random_list)
                wcet = utilization * period
                # coe = random.choice(coe_list)
                deadline = round(coe * period)
                new_task = Task(wcet, period, deadline)
                task_set.append(new_task)
                # print(Task.__repr__(new_task))      ####
                file.writelines(Task.__repr__(new_task))
                file.write("\n")
            # task_sets.append(task_set)
    file.close()


if __name__ == "__main__":
    """
    total u <= m peocessors; u = 4, m = 8 (lower bound)
    density_sum <= m (upper bound)
    total u < ntasks
    """
    m = 16      # m equals to total util 4, 8, 16
    nsets = 1000     # 500 1000,
    ntasks = 100     # ntasks >= 2 * m : 30, 50, 80, 100
    start_time = time.process_time()
    write_to_file(m, nsets, ntasks)
    end_time = time.process_time()
    running_time = end_time - start_time
    print("Running time: {}s".format(running_time))



