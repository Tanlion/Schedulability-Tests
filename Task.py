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
    

    def utilization(self):
        return (int(self.wcet / self.period * 1000000) / 1000000)   

    def density(self):
        # Sum_density <= m and Max_density <= 1
        return self.wcet / min(self.deadline, self.period)

    def DBF(self, t): #demand bound function
        if t < 0:
            return 0
        return max(0, (int(floor((t - self.deadline) / self.period)) + 1)
                      * self.wcet)

    def __repr__(self):
        return str(self.wcet) + " " + str(self.period) + " " + str(self.deadline)

    def show(self):
        print("Task(" + str(self.ID) + ", " + str(self.wcet) + ", " + str(self.period) + \
              ", " + str(self.utilization) + ", " + str(self.deadline) + " )")





