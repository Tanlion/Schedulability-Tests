import gurobipy as gp
import numpy as np
import re
import sys
import time
from math import floor, ceil, gcd
import Task
import ScheduleTest
import subprocess



class Logger(object):
	def __init__(self, filename='default.log', stream=sys.stdout):
		self.terminal = stream
		self.log = open(filename, 'w')

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

	def flush(self):
		pass

log_file = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
sys.stdout = Logger('./log/' + 'writeFile_' + log_file + '.log', sys.stdout)



def write_file(read_filename, m):
    """
    :param filename:
    :return: get the schedulable ratio of a file.
    """
    file = open(read_filename, 'r')
    max_line = len(file.readlines())
    print("max_line is: {} ".format(max_line))
    file.seek(0)

    line = file.readline().strip()
    totalu = int(re.findall(r"\d+", line)[0])
    nsets = int(re.findall(r"\d+", line)[1])
    ntasks = int(re.findall(r"\d+", line)[2])

    u_block = nsets * (ntasks + 1)
    print("total U: {}, nsets: {}, ntasks: {}, m: {}".format(totalu, nsets, ntasks, m))

    # find utilization listf
    util_lines = file.read()
    u_list = re.findall(r'(?<=Utilization : )\d+\.?\d*', util_lines)
    u_list = list(map(float, u_list))
    print("utilization list: {}".format(u_list))
    file.seek(0)

    u_start_line = 2
    u_end_line = u_start_line + u_block

    dens_ratio_list = []
    load_ratio_list = []
    fpbasic_ratio_list = []
    fpimprv_ratio_list = []
    npbasic_ratio_list = []
    npimprv_ratio_list = []


    for line in file.readlines()[u_start_line: u_end_line]:  # all sets loop u-block
        if u_end_line > max_line:
            break

        print("\n" + "=" * 10 + "U_block range: {} to {}:".format(u_start_line, u_end_line))
        set_start_line = u_start_line + 1
        set_end_line = set_start_line + ntasks

        cnt_dens_test = 0
        cnt_load_test = 0
        cnt_fpbasic_test = 0
        cnt_fpimprv_test = 0
        cnt_npbasic_test = 0
        cnt_npimprv_test = 0

        for j in range(nsets):
            task_set = Task.get_tasks(filename, set_start_line, set_end_line)
            task_set = Task.list_to_obj(task_set)  # convert to Task object
            print("-" * 20 + "Task Set {0} - line {1} to {2}: \n{3}".format(j + 1, set_start_line, set_end_line, task_set))

            is_dens = ScheduleTest.density_test(task_set, m)
            is_load = ScheduleTest.load_test(task_set, m)
            is_fpbasic = ScheduleTest.fpbasic_test(task_set, m)
            is_fpimprv = ScheduleTest.fpimprv_test(task_set, m)
            is_npbasic = ScheduleTest.npbasic_test(task_set, m)
            is_npimprv = ScheduleTest.npimprv_test(task_set, m)

            print("Density Test: {}".format(is_dens))
            print("Load Test: {}".format(is_load))
            print("Fpbasic Test: {}".format(is_fpbasic))
            print("Fpimprv Test: {}".format(is_fpimprv))
            print("Npbasic Test: {}".format(is_npbasic))
            print("Npimprv Test: {}".format(is_npimprv))
            print("\n")

            if is_dens == True:
                cnt_dens_test += 1
            
            if is_load == True:
                cnt_load_test += 1

            if is_fpbasic == True:
                cnt_fpbasic_test += 1

            if is_fpimprv == True:
                cnt_fpimprv_test += 1

            if is_npbasic == True:
                cnt_npbasic_test += 1

            if is_npimprv == True:
                cnt_npimprv_test += 1


            set_start_line = set_end_line + 1
            set_end_line = set_start_line + ntasks
            j += 1

        dens_ratio = round(cnt_dens_test * 100 / nsets, 2)
        load_ratio = round(cnt_load_test * 100 / nsets, 2)
        fpbasic_ratio = round(cnt_fpbasic_test * 100 / nsets, 2)
        fpimprv_ratio = round(cnt_fpimprv_test * 100 / nsets, 2)
        npbasic_ratio = round(cnt_npbasic_test * 100 / nsets, 2)
        npimprv_ratio = round(cnt_npimprv_test * 100 / nsets, 2)

        dens_ratio_list.append(dens_ratio)
        load_ratio_list.append(load_ratio)
        fpbasic_ratio_list.append(fpbasic_ratio)
        fpimprv_ratio_list.append(fpimprv_ratio)
        npbasic_ratio_list.append(npbasic_ratio)
        npimprv_ratio_list.append(npimprv_ratio)

        print("Denst cnt: {} / {}, ratio {}".format(cnt_dens_test, nsets, dens_ratio))
        print("Load cnt: {} / {}, ratio {}".format(cnt_load_test, nsets, load_ratio))
        print("Fpbasic cnt: {} / {}, ratio {}".format(cnt_fpbasic_test, nsets, fpbasic_ratio))
        print("Fpimprv cnt: {} / {}, ratio {}".format(cnt_fpimprv_test, nsets, fpimprv_ratio))
        print("Npbasic cnt: {} / {}, ratio {}".format(cnt_npbasic_test, nsets, npbasic_ratio))
        print("Npimprv cnt: {} / {}, ratio {}".format(cnt_npimprv_test, nsets, npimprv_ratio))

        u_start_line = u_end_line + 1
        u_end_line = u_start_line + u_block
    file.close()

    ## FP VS density and load
    new_file = open("./output/Ratio_{}".format(filename.lstrip('./output/Task_data')), "w")
    new_file.writelines("Util\t dens\t load\t fpbasic\t fpimprv\n")
    for i in range (len(u_list)):
        new_file.writelines("{0}\t {1}\t {2}\t {3}\t {4}\n".format\
                            (u_list[i], dens_ratio_list[i], load_ratio_list[i],\
                             fpbasic_ratio_list[i], fpimprv_ratio_list[i]))
    
        print("Utilization: {0}, dens_ratio: {1}, load_ratio: {2}, fpbasic_ratio: {3}, fpimprv_ratio: {4}"\
              .format(u_list[i], dens_ratio_list[i], load_ratio_list[i], fpbasic_ratio_list[i], fpimprv_ratio_list[i]))
        i += 1
    
    new_file.close()

    ### FP VS NP
#     new_file = open("./output/Ratio_FpNp_{}".format(filename.lstrip('./output/Task_data')), "w")
#     new_file.writelines("Util\t fpbasic\t fpimprv\t npbasic\t npimprv\n")
#     for i in range (len(u_list)):
#         new_file.writelines("{0}\t {1}\t {2}\t {3}\t {4}\n".format\
#                             (u_list[i], fpbasic_ratio_list[i], fpimprv_ratio_list[i],\
#                             npbasic_ratio_list[i], npimprv_ratio_list[i]))

#         print("Utilization: {0},  fpbasic_ratio: {1}, fpimprv_ratio: {2}, npbasic_ratio: {3}, npimprv_ratio: {4}"\
#               .format(u_list[i], fpbasic_ratio_list[i], fpimprv_ratio_list[i], npbasic_ratio_list[i], npimprv_ratio_list[i]))
#         i += 1

#     new_file.close()



if __name__ == "__main__":
    m = 16
    filename = "Task_data_16u_1000_50_2.0coe_6000lcm.txt"
    start_time = time.process_time()
    write_file(filename, m)
    end_time = time.process_time()
    running_time = end_time - start_time
    print("Running time: {}s".format(running_time))
    audio_file = "./notification_sound.mp3"
    return_code = subprocess.call(["afplay", audio_file])

