"""
Implement Linear Programming optimizer Guribo


"""
import gurobipy as gp
import Task
import re
import sys
import time


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
sys.stdout = Logger('./log/' + 'LP_' + log_file + '.log', sys.stdout)




def get_sets(filename):
	file = open(filename, 'r')
	max_line = len(file.readlines())
	print("max_line is: {} ".format(max_line))
	file.seek(0)

	line = file.readline().strip()
	totalu = int(re.findall(r"\d+", line)[0])
	nsets = int(re.findall(r"\d+", line)[1])
	ntasks = int(re.findall(r"\d+", line)[2])
	u_block = nsets * (ntasks + 1)
	print("total U: {} nsets: {} ntasks: {}".format(totalu, nsets, ntasks))

	# find utilization list
	util_lines = file.read()
	u_list = re.findall(r'(?<=Utilization : )\d+\.?\d*', util_lines)
	u_list = list(map(float, u_list))
	print("utilization list: {}".format(u_list))
	file.seek(0)

	u_start_line = 2
	u_end_line = u_start_line + u_block
	task_set = []


	for line in file.readlines()[u_start_line: u_end_line]:  # all sets loop u-block
		if u_end_line > max_line:
			break

		print("\n" + "=" * 15 + "U_block range: {} to {}: ".format(u_start_line, u_end_line))
		set_start_line = u_start_line + 1
		set_end_line = set_start_line + ntasks

		for j in range(nsets):
			task_set = Task.get_tasks(filename, set_start_line, set_end_line)
			task_set = Task.list_to_obj(task_set)  # convert to Task object
			print("Task Set {0} - line {1} to {2}: {3}".format(j + 1, set_start_line, set_end_line, task_set))

			lp_test2(task_set, m)

			set_start_line = set_end_line + 1
			set_end_line = set_start_line + ntasks
			j += 1

		u_start_line = u_end_line + 1
		u_end_line = u_start_line + u_block

	file.close()

	return task_set



def lp_test1(task_set, m):

	ntasks = len(task_set)
	# task_set = Task.list_to_obj(task_set)
	# try:

	model = gp.Model('Basic-Bound-F-P-GEDF')
	C = []
	T = []
	D = []
	U = []
	Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
	L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')
	# maxobj = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name='maxobj')
	# diff_ty = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name='diff_ty')

	for i in range(ntasks):
		C.append(task_set[i].wcet)
		T.append(task_set[i].period)
		D.append(task_set[i].deadline)
		tmp_u = round(task_set[i].wcet / task_set[i].period, 6)
		U.append(tmp_u)
		C_max = max(C)
		U_sum = round(sum(U), 4)
	print("C: {}, \nT: {}, \nD: {}, \nU: {}".format(C, T, D, U))
	print("C_max: {},\tU_sum: {},\tm processors: {}\n".format(C_max, U_sum, m))

	model.update()
	model.setObjective(sum(L[i] for i in range(ntasks)), sense=gp.GRB.MINIMIZE)

	# model.addConstrs(diff_ty[i] == T[i] - Y[i] for i in range(ntasks))
	# model.addConstrs(maxobj[i] == gp.max_(0, diff_ty[i]) for i in range(ntasks))
	# model.addConstrs(L[i] == (U[i] * maxobj[i]) for i in range(ntasks))
	model.addConstrs(L[i] >= 0 for i in range(ntasks))
	model.addConstrs(L[i] >= (T[i] - Y[i]) * U[i] for i in range(ntasks))
	model.addConstrs(Y[i] + (sum(L[i] for i in range(ntasks)) + (m - 1) * C_max - C[i]) / m + C[i] <= D[i] for i in range(ntasks))

	model.Params.LogToConsole = True		#显示求解过程
	model.optimize()
	model.write('Basic-Bound-F-P-GEDF.lp')

	cnt_y = 0
	cnt = 0

	if model.status == gp.GRB.Status.OPTIMAL:
		cnt_y += 1
		cnt += 1
		for var in model.getVars():
			print(f"{var.varName}: {round(var.X, 6)}")
		print("Yes\n")


	elif model.status == gp.GRB.Status.INFEASIBLE:
		# print('Optimization was stopped with status %d ' % model.status)
		cnt += 1
		print("No\n")

	# print("Lpbb ratio: {}\n".format(cnt_y/cnt))
	return model.status == gp.GRB.Status.OPTIMAL

	# except gp.GurobiError as e:
	# 	print('Error code ' + str(e.errno) + ": " + str(e))
	#
	# except AttributeError:
	# 	print('Encountered an attribute error')

def lp_test2(task_set, m):
	ntasks = len(task_set)
	task_set = Task.list_to_obj(task_set)
	model = gp.Model('Improved-Bound-F-P-GEDF')
	C = []
	T = []
	D = []
	U = []
	Y = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'Y')
	L = model.addVars(ntasks, vtype=gp.GRB.CONTINUOUS, name = 'L')
	# Lambda = model.addVar(lb=1, ub=m, vtype=gp.GRB.CONTINUOUS, name = 'Lambda')


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
	# model.addConstr( U_sum <= Lambda)
	# model.addConstr( Lambda <= U_sum + 1)
	model.addConstrs((U_sum/m) * Y[i] + (sum(L[i] for i in range(ntasks))/m) + (U_sum- 1)/m * C_max + (m-1)/m * C[i] <= D[i] for i in range(ntasks))

	model.Params.LogToConsole = True		#显示求解过程
	model.optimize()
	model.write('Basic-Bound-F-P-GEDF.lp')

	cnt_y = 0
	cnt = 0

	if model.status == gp.GRB.Status.OPTIMAL:
		cnt_y += 1
		cnt += 1
		for var in model.getVars():
			print(f"{var.varName}: {round(var.X, 6)}")
		print("Yes\n")


	elif model.status == gp.GRB.Status.INFEASIBLE:
		# print('Optimization was stopped with status %d ' % model.status)
		cnt += 1
		print("No\n")

	return model.status == gp.GRB.Status.OPTIMAL

if __name__ == "__main__":
	m = 10
	filename = "Task_data_10u_300_50_0.5step_3.0coe_10lcm.txt"
	# get_sets(filename)
	task_set = [(0.663632, 9.0, 11.0),
				(0.351698, 2.0, 2.0),
				(1.577367, 5.0, 6.0),
				(0.295637, 2.0, 2.0),
				(0.484059, 2.0, 2.0),
				(0.270551, 6.0, 7.0)]

	lp_test2(task_set, m)





