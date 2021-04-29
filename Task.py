from math import floor, ceil, gcd


def LCM(input):
    """
    :param input: period list
    :return: an integer of longest common multiple for hyper periods
    """
    lcm = input[0]
    for i in input[1:]:
        lcm = int(lcm * i / gcd(lcm, i))
    return lcm


def uniq(seq):
    it = iter(seq)
    last = it.next()
    yield last
    for x in it:
        if x != last:
            last = x
            yield x


def list_to_obj(task_set):
    # convert list to Task object
    obj_list = []
    for i in range(0, len(task_set)):
        wcet = task_set[i][0]
        period = task_set[i][1]
        deadline = task_set[i][2]
        new_task_obj = Task(wcet, period, deadline)
        obj_list.append(new_task_obj)
    # for i in range(0, len(task_obj_list)):
    #     print(task_obj_list[i])
    # print(task_obj_list)
    return obj_list



def get_tasks(filename, start_line, end_line): #exclude start_line with single set
    task_set = []
    with open(filename) as f:
        for line in f.readlines()[start_line :end_line]:
            curline = line.strip().split(' ')
            task_line = list(map(float, curline))
            task_set.append(task_line)
    return task_set



class Task(object):

    def __init__(self, wcet, period, deadline):
        self.period = period
        self.wcet = wcet
        self.deadline = deadline # relative deadline D_i <= period
        # when: D_i != T_i, 0.8， 1.2, 1.5倍T_i，rount(, 0) 取整！然后再算load

    # def taskID(self):
    #     return self.ID

    def utilization(self):
        return (int(self.wcet / self.period * 1000000) / 1000000)   #取小数点后6位

    def density(self):
        # Sum_density <= m and Max_density <= 1
        return self.wcet / min(self.deadline, self.period)

    def DBF(self, t): #demand bound function
    # param t: any interval length time
    # t = D_i + n * T_i
        if t < 0:
            return 0
        return max(0, (int(floor((t - self.deadline) / self.period)) + 1)
                      * self.wcet)

    def priority_point(self):
        return -self.period  #negative


    ##### job level
    def release_time(self, t):  # r_{i,j}
        return t

    def absolute_deadline(self):    # d_{i,j}
        return self.release_time() + self.deadline

    def finish_time(self, t):   # f_{i,j}
        return t

    def response_time(self):    # R_{i,j}
        return self.finish_time() - self.release_time()

    def delta(self):
        return self.finish_time() - self.absolute_deadline()

    def pp(self):
        return self.release_time() + self.priority_point()

    # def is_feasible(self):
    #     return self.wcet <= min(self.deadline, self.period)

    def __repr__(self):
        return str(self.wcet) + " " + str(self.period) + " " + str(self.deadline)

    def show(self):
        print("Task(" + str(self.ID) + ", " + str(self.wcet) + ", " + str(self.period) + \
              ", " + str(self.utilization) + ", " + str(self.deadline) + " )")

    # def __repr__(self):
    #     idstr = ", id=%s" % self.id if self.id is not None else ""
    #     dstr = ", deadline=%s" % self.deadline if self.deadline != self.period else ""
    #     return "SporadicTask(%s, %s%s%s)" % (self.wcet, self.period, dstr, idstr)



# if __name__ == "__main__":
#     m = 8
#     task_set = [(0.663632, 9.0, 11.0),
#                 (0.351698, 2.0, 2.0),
#                 (1.577367, 5.0, 6.0),
#                 (0.295637, 2.0, 2.0),
#                 (0.484059, 2.0, 2.0),
#                 (0.270551, 6.0, 7.0)]
#     task_set = list_to_obj(task_set)
#     period_list = []
#     for task in task_set:
#         period_list.append(int(task.period))
#     lcm_period = LCM(period_list)
#     print("lcm: {}".format(lcm_period))
#     for task in task_set:
#         print("DFB: {}".format(task.DBF(lcm_period)))

