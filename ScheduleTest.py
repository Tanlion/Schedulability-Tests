"""G-EDF hard schedulability test
This file implement several schedulability tests:
Density Test:
Load Test:
Linear programme of Basic Bound of response time Test:

"""
import Task
from math import floor, ceil, gcd
import numpy as np
import re
import time
import gurobipy as gp
from Task import LCM




def max_density(task_set):
    max_density = max([task.density() for task in task_set])
    max_density = round(max_density, 4)
    return max_density

def sum_density(task_set):
    sum_density = sum([task.density() for task in task_set])
    sum_density = round(sum_density, 4)
    return sum_density

def max_utilization(task_set):
    max_utilization = max([task.utilization() for task in task_set])
    max_utilization = round(max_utilization, 4)
    return max_utilization

def sum_utilization(task_set):
    sum_util = sum([task.utilization() for task in task_set])
    sum_util = round(sum_util, 4)
    return sum_util

# check Sum_density <= m and Max_density <= 1
# def feasible_test(task_set, m):
#     sum_dens = sum_density(task_set)
#     max_dens = max_density(task_set)
#     if sum_dens <= m and max_dens <= 1:
#         return True
#     return False



def util_test(task_set, m):
    """
    Feasibility test for implicit deadline-task system
    :param task_set:
    :param m: number of processors
    :param totalu: total utilization of a task set.
    :return: if the task_set can pass the utilization test or not
    """
    max_util = max_utilization(task_set)
    sum_util = sum_utilization(task_set)
    print("Max_util: {}, Sum_util: {}".format(max_util, sum_util))
    if sum_util <= m - (m - 1) * max_util:
        return True
    return False




def density_test(task_set, m):
    """
    Density test for non-implicit deadline task system
    :param task_set:
    :param m: number of processors
    :return: if the task_set can pass the density test or not
    """
    max_dens = max_density(task_set)
    sum_dens = sum_density(task_set)
    print("Density Test: Max_dens: {}, Sum_dens: {}".format(max_dens, sum_dens))
    if max_dens <= 1 and sum_dens <= m - (m - 1) * max_dens:  # add feasible conditions
        return True
    return False



def load_test(task_set, m):
    """ G-EDF hard schedulability test
    Implements the model of Sanjoy Baruah and Theodore Baker in their paper " Global EDF schedulability analysis of
    arbitrary sporadic task systems"
    test each task set, if it is schedulabled.
    :param total_u: an int, total utilization.
    :param task_set: a list, a list of Task Obj of a task_set 1.
    :param m : number of processors
    :return: if the task_set can pass the load test or not
    """
    max_dens = max_density(task_set)
    sum_dens = sum_density(task_set)
    sum_u = sum_utilization(task_set)
    print("Load Test: Max_dens: {}, Sum_dens: {}, Sum_utilisation: {}".format(max_dens, sum_dens, sum_u))

    # to get LOAD of a task set
    # t is (1.0, the LCM of periods of current task set)
    period_list = []
    for task in task_set:
        period_list.append(int(task.period))
    lcm_period = LCM(period_list)
    print("lcm: {}".format(lcm_period))

    load = 0.0
    # for t in range(1, lcm_period): #t >= max(deadline)
    # # if (t * task.density() >= task.DBF(t)):
    #     sum_DBF = sum([task.DBF(t) for task in task_set]) / t
    #     # sum_DBF = sum([task.DBF(t) / t for task in task_set])
    #     if sum_DBF > load:
    #         load = sum_DBF

    for task in task_set:
        for t in np.arange(task.deadline, lcm_period + 1, task.period):
            # if (t * task.density() >= task.DBF(t)):
            sum_DBF = sum([task.DBF(t) for task in task_set]) / t
            if sum_DBF > load:
                load = sum_DBF

    load = round(load, 6)
    if load < sum_u:
        load = sum_u

    mu = round(m - (m - 1) * max_dens, 6)
    if mu <= 0:
        return False

    bound = round(mu - (ceil(mu) - 1) * max_dens, 6)
    print("mu: {},\nbound: {}\nload: {}\n".format(mu, bound, load))

    if max_dens <= 1 and load <= bound:   # add feasible conditions
        return True
    return False




def fpbasic_test(task_set, m):
    ntasks = len(task_set)
    model = gp.Model('Basic-Bound-F-P-GEDF')
    C = []
    T = []
    D = []
    U = []
    Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
    L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')

    for i in range(ntasks):
        C.append(task_set[i].wcet)
        T.append(task_set[i].period)
        D.append(task_set[i].deadline)
        tmp_u = round(task_set[i].wcet / task_set[i].period, 6)
        U.append(tmp_u)
        C_max = max(C)
        U_sum = round(sum(U), 4)
    print("C: {}, \nT: {}, \nD: {}, \nU: {}".format(C, T, D, U))
    print("C_max: {},\nU_sum: {}\nm processors: {}\n".format(C_max, U_sum, m))

    model.update()
    model.setObjective(sum(L[i] for i in range(ntasks)), sense=gp.GRB.MINIMIZE)

    model.addConstrs(L[i] >= 0 for i in range(ntasks))
    model.addConstrs(L[i] >= (T[i] - Y[i]) * U[i] for i in range(ntasks))
    model.addConstrs(Y[i] + (sum(L[i] for i in range(ntasks)) + (m - 1) * C_max - C[i]) / m + C[i] <= D[i] for i in range(ntasks))

    model.Params.LogToConsole = True
    model.optimize()
    model.write('Basic-Bound-F-P-GEDF.lp')

    if model.status == gp.GRB.Status.OPTIMAL:
        for var in model.getVars():
            print(f"{var.varName}: {round(var.X, 6)}")
        print("Fp-basic Yes\n")

    elif model.status == gp.GRB.Status.INFEASIBLE:
        # print('Optimization was stopped with status %d ' % model.status)
        print("Fp-basic No\n")

    return model.status == gp.GRB.Status.OPTIMAL



def fpimprv_test(task_set, m):
    ntasks = len(task_set)
    model = gp.Model('Improved-Bound-F-P-GEDF')
    C = []
    T = []
    D = []
    U = []
    Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
    L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')


    for i in range(ntasks):
        C.append(task_set[i].wcet)
        T.append(task_set[i].period)
        D.append(task_set[i].deadline)
        tmp_u = round(task_set[i].wcet / task_set[i].period, 6)
        U.append(tmp_u)
        C_max = max(C)
        U_sum = round(sum(U), 4)
        Lambda = ceil(U_sum)
    print("C: {}, \nT: {}, \nD: {}, \nU: {}".format(C, T, D, U))
    print("Lambda: {}, \nC_max: {},\nU_sum: {}\nm processors: {}\n".format(Lambda, C_max, U_sum, m))

    model.update()
    model.setObjective(sum(L[i] for i in range(ntasks)), sense=gp.GRB.MINIMIZE)

    model.addConstrs(L[i] >= 0 for i in range(ntasks))
    model.addConstrs(L[i] >= (T[i] - Y[i]) * U[i] for i in range(ntasks))
    model.addConstrs((U_sum/m) * Y[i] + (sum(L[i] for i in range(ntasks))/m) + (Lambda - 1)/m * C_max + (m-1)/m * C[i] <= D[i] for i in range(ntasks))

    model.Params.LogToConsole = True
    model.optimize()
    model.write('Improved-Bound-F-P-GEDF.lp')


    if model.status == gp.GRB.Status.OPTIMAL:
        for var in model.getVars():
            print(f"{var.varName}: {round(var.X, 6)}")
        print("Fp-improve Yes\n")

    elif model.status == gp.GRB.Status.INFEASIBLE:
        # print('Optimization was stopped with status %d ' % model.status)
        print("FP-improve No\n")

    return model.status == gp.GRB.Status.OPTIMAL


def npbasic_test(task_set, m):
    ntasks = len(task_set)
    model = gp.Model('Basic-Bound-N-P-GEDF')
    C = []
    T = []
    D = []
    U = []
    Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
    L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')

    for i in range(ntasks):
        C.append(task_set[i].wcet)
        T.append(task_set[i].period)
        D.append(task_set[i].deadline)
        tmp_u = round(task_set[i].wcet / task_set[i].period, 6)
        U.append(tmp_u)
        C_max = max(C)
        U_sum = round(sum(U), 4)
    print("C: {}, \nT: {}, \nD: {}, \nU: {}".format(C, T, D, U))
    print("C_max: {},\nU_sum: {}\nm processors: {}\n".format(C_max, U_sum, m))

    model.update()
    model.setObjective(sum(L[i] for i in range(ntasks)), sense=gp.GRB.MINIMIZE)

    model.addConstrs(L[i] >= 0 for i in range(ntasks))
    model.addConstrs(L[i] >= (T[i] - Y[i]) * U[i] for i in range(ntasks))
    model.addConstrs(Y[i] + sum(L[i] for i in range(ntasks)) / m + C_max + ((m-1) * C[i]) / m <= D[i] for i in range(ntasks) )

    model.Params.LogToConsole = True
    model.optimize()
    model.write('Basic-Bound-N-P-GEDF.lp')

    if model.status == gp.GRB.Status.OPTIMAL:
        for var in model.getVars():
            print(f"{var.varName}: {round(var.X, 6)}")
        print("Np-basic Yes\n")

    elif model.status == gp.GRB.Status.INFEASIBLE:
        # print('Optimization was stopped with status %d ' % model.status)
        print("Np-basic No\n")

    return model.status == gp.GRB.Status.OPTIMAL


def npimprv_test(task_set, m):
    ntasks = len(task_set)
    model = gp.Model('Improved-Bound-N-P-GEDF')
    C = []
    T = []
    D = []
    U = []
    Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
    L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')


    for i in range(ntasks):
        C.append(task_set[i].wcet)
        T.append(task_set[i].period)
        D.append(task_set[i].deadline)
        tmp_u = round(task_set[i].wcet / task_set[i].period, 6)
        U.append(tmp_u)
        C_max = max(C)
        U_sum = round(sum(U), 4)

    print("C: {}, \nT: {}, \nD: {}, \nU: {}".format(C, T, D, U))
    print("C_max: {},\nU_sum: {}\nm processors: {}\n".format(C_max, U_sum, m))

    model.update()
    model.setObjective(sum(L[i] for i in range(ntasks)), sense=gp.GRB.MINIMIZE)

    model.addConstrs(L[i] >= 0 for i in range(ntasks))
    model.addConstrs(L[i] >= (T[i] - Y[i]) * U[i] for i in range(ntasks))
    model.addConstrs((U_sum/m) * Y[i] + (sum(L[i] for i in range(ntasks))/m) + C_max + ((m-1)/m) * C[i] <= D[i] for i in range(ntasks))

    model.Params.LogToConsole = True        #显示求解过程
    model.optimize()
    model.write('Improved-Bound-N-P-GEDF.lp')


    if model.status == gp.GRB.Status.OPTIMAL:
        for var in model.getVars():
            print(f"{var.varName}: {round(var.X, 6)}")
        print("Np-improve Yes\n")

    elif model.status == gp.GRB.Status.INFEASIBLE:
        # print('Optimization was stopped with status %d ' % model.status)
        print("Np-improve No\n")

    return model.status == gp.GRB.Status.OPTIMAL


# if __name__ == "__main__":
#     """
#     total u <= m peocessors;
#     total u = 4; processors m = 8
#     """
#     m = 8
#     filename = "Task_data_4u_3_7_0.5step_3.0coe.txt"
#     start_time = time.process_time()
#     get_ratio(filename)
#     end_time = time.process_time()
#     running_time = end_time - start_time
#     print("Running time: {}s".format(running_time))








