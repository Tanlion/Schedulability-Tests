"""G-EDF hard schedulability test
This module implements Sanjoy Baruah's G-EDF schedulability test as presented

"""

import Task
from math import floor, ceil, gcd
import numpy as np
import re
import time


# ntasks: boolean schedulable or not
# nsets: float as a ratio of how many sets can be scheduled.

def LCM(input): 
    """
    :param input: period list
    :return: an integer of longest common multiple for hyper periods
    """
    lcm = input[0]
    for i in input[1:]:
        lcm = int(lcm * i / gcd(lcm, i))
    return lcm


def max_density(task_set):
    max_density = max([task.density() for task in task_set])
    max_density = round(max_density, 4)
    return max_density

def sum_density(task_set):
    sum_density = sum([task.density() for task in task_set])
    sum_density = round(sum_density, 4)
    return sum_density

def density_test(task_set, m):
    """
    Feasibility test for non-implicit deadline task system
    :param task_set:
    :param m: number of processors
    :return: otal utilization of a task set.
    """
    max_den = max_density(task_set)
    sum_den = sum_density(task_set)
    if sum_den <= m - (m - 1) * max_den:
        return True
    return False

def max_utilization(task_set):
    max_utilization = max([task.utilization() for task in task_set])
    max_utilization = round(max_utilization, 4)
    return max_utilization

def sum_utilization(task_set):
    sum_util = sum([task.utilization() for task in task_set])
    return sum_util


# def util_test(task_set, m):
#     """
#     Feasibility test for implicit deadline-task system
#     :param task_set:
#     :param m: number of processors
#     :param totalu: total utilization of a task set.
#     :return:
#     """
#     sum_util = sum_utilization(task_set)
#     max_util = max_utilization(task_set)
#     if sum_util <= m - (m - 1) * max_util:
#         return True
#     return False
#
#
# def util_test(totalu, task_set, m):
#     """
#     Feasibility test for implicit deadline-task system
#     :param task_set:
#     :param m: number of processors
#     :param totalu: total utilization of a task set.
#     :return:
#     """
#     # sum_util = sum_utilization(task_set)
#     max_util = max_utilization(task_set)
#     if totalu <= m - (m - 1) * max_util:
#         return True
#     return False



def load_test(task_set, m):  # task_set: [() () ()...]
    """ G-EDF hard schedulability test
    Implements the model of Sanjoy Baruah and Theodore Baker in their paper " Global EDF schedulability analysis of
    arbitrary sporadic task systems"
    test each task set, if it is schedulabled.
    :param total_u: an int, total utilization.
    :param task_set: a list, a list of Task Obj of a task_set 1.
    :param m : number of processors
    :return: boolean. If this task set can be schedulabled or not.
    """

    max_den = max_density(task_set)

    # to get LOAD of a task set
    # t is (1.0, the LCM of periods of current task set)
    period_list = []
    for task in task_set:
        period_list.append(int(task.period))
    lcm_period = LCM(period_list)
    # print("lcm: {}".format(lcm_period))

    load = 0
    for t in range(1, lcm_period):
        if (t * task.density() >= task.DBF(t)):
            sum_DBF = sum([task.DBF(t) for task in task_set]) / t
            if sum_DBF  > load:
                load = sum_DBF

    load = round(load, 6)
    mu = round(m - (m - 1) * max_den, 6)
    bound = round(mu - (ceil(mu) - 1) * max_den, 6)
    print("mu: {}".format(mu))
    print("bound: {}".format(bound))
    print("load: {}".format(load))

    if load <= bound:
        return True
    return False







# def get_ratio(read_filename):
#     """
#     :param filename:
#     :return: get the schedulable ratio of a file.
#     total_u: 1 - 10
#     strip() 移除字符串头尾指定的字符（默认为空格）或字符序列。
#     split() 通过指定分隔符对字符串进行切片，如果第二个参数 num 有指定值，则分割为 num+1 个子字符串。
#     """
#     file = open(read_filename, 'r')
#     max_line = len(file.readlines())
#     print("max_line is: {} ".format(max_line))
#     file.seek(0)
#
#     line = file.readline().strip()
#     totalu = int(re.findall(r"\d+", line)[0])
#     nsets = int(re.findall(r"\d+", line)[1])
#     ntasks = int(re.findall(r"\d+", line)[2])
#     u_block = nsets * (ntasks + 1)  #25
#     print("total U: {} nsets: {} ntasks: {}".format(totalu, nsets, ntasks))
#
#     # find utilization list
#     util_lines = file.read()
#     u_list = re.findall(r'(?<=Utilization : )\d+\.?\d*', util_lines)
#     u_list = list(map(float, u_list))
#     print("utilization list: {}".format(u_list))
#     file.seek(0)
#
#     u_start_line = 2
#     u_end_line = u_start_line + u_block
#     dens_ratio_list = []
#     sche_ratio_list = []
#     ratio_list = []
#
#     for line in file.readlines()[u_start_line: u_end_line]:  # all sets loop u-block
#         if u_end_line > max_line:
#             break
#
#         print("\nU_block range: {} to {}".format(u_start_line, u_end_line))
#         set_start_line = u_start_line + 1
#         set_end_line = set_start_line + ntasks
#
#         cnt_dens_test = 0
#         cnt_sche_test = 0
#         cnt = 0
#         for j in range(nsets):
#             task_set = Task.get_tasks(filename, set_start_line, set_end_line)
#             print("1st task set {}".format(task_set))
#             task_set = Task.list_to_obj(task_set)  # convert to Task object
#             print("2nd tasl set: {}".format(task_set))
#             print("Task Set {0} - line {1} to {2}: {3}".format(j + 1, set_start_line, set_end_line, task_set))
#
#             is_dens = density_test(task_set, m)
#             is_sche = schedulable_test(task_set, m)
#             print("density test: {}".format(is_dens))
#             print("Schedulable: {}".format(is_sche))
#
#             if is_dens == True:
#                 cnt_dens_test += 1
#
#             if is_sche == True:
#                 cnt_sche_test += 1
#
#             if is_dens == True or is_sche == True:
#                 cnt += 1
#
#             set_start_line = set_end_line + 1
#             set_end_line = set_start_line + ntasks
#             j += 1
#
#         dens_ratio = cnt_dens_test * 100 / nsets
#         sche_ratio = cnt_sche_test * 100 / nsets
#         ratio = cnt * 100 / nsets
#         dens_ratio_list.append(dens_ratio)
#         sche_ratio_list.append(sche_ratio)
#         ratio_list.append(ratio)
#
#         print("denst cnt: {} / {}, ratio {}".format(cnt_dens_test, nsets, dens_ratio))
#         print("sche cnt: {} / {}, ratio {}".format(cnt_sche_test, nsets, sche_ratio))
#         print("both cnt: {} / {}, ratio {}".format(cnt, nsets, ratio))
#
#         u_start_line = u_end_line + 1
#         u_end_line = u_start_line + u_block
#     file.close()
#
#     # print(dens_ratio_list)
#     # print(sche_ratio_list)
#     # print(ratio_list)
#
#     new_file = open("Ratio_{0}_{1}_{2}_{3}m.txt".format(totalu, nsets, ntasks, m), "w")
#     for i in range (len(u_list)):
#         new_file.writelines("{} {} {} {}\n".format(u_list[i], dens_ratio_list[i], sche_ratio_list[i], ratio_list[i]))
#         print("Utilization: {0}, ratio_dens: {1}, ratio_shce: {2}, ratio: {3} "
#               .format(u_list[i], dens_ratio_list[i], sche_ratio_list[i], ratio_list[i]))
#         i += 1
#
#     new_file.close()



# if __name__ == "__main__":
#     """
#     total u <= m peocessors;
#     total u = 4; processors m = 8
#     """
#     m = 8
#     # filename = "Task_List_4_100_20_1-10.txt"
#     filename = "Task_Listttt_4_10_6_1-10.txt"
#     start_time = time.process_time()
#     get_ratio(filename)
#     end_time = time.process_time()
#     running_time = end_time - start_time
#     print("Running time: {}s".format(running_time))








