### What this is?
Experiment on schedulability tests with G-EPPF tests compare to Density test and Load test. 

G-EPPF (global earliest-priority-point-first) scheduling include a basic bound and an improved bound for fully preemptive and non-preemptive cases separately. 

### System Characteristics
| Property | Description |
| ---------| ----------- |
|  m | Number of processors. For eachprocessor i (1 <= i <= m).  |
|  s = 1.0 |  Speed of each processor is 1.0 for identical multiprocessors system. |
| u | Total utilization of a taskset.|
|  nsets |  Cardinality of tasksets. |
| ntasks | Cardinality of tasks in each set|
| task set  |C_i, T_i, D_i, Y_i  |
| C_i | Worst case execution time of a task |
| T_i   | Minimum inter-arrival time between two successive jobs. (e.g. 1ms – 10ms, 10ms – 100ms, 100ms – 1s ) |
| U_i  | Utilisation of a task : C_i = U_i * T_i. Use U_i to calculate C_i.|
| D_i | Relative deadline of a task |
| Y_i | Relative priority point of a task ~ D_i|
| Li | Difference between period and priority point of a task. Li = U_i * max(0, (T_i - Y_i))|
| r_{i,j} | Release time of a job |
| d_{i,j} | Absolute deadline of a job: d_{i,j} = r_{i,j} + D_i |
| f_{i, j} | Finish execution time: ~ C_i |
| R_{i,j} | Response time, executing period R_{i,j} = f_{i,j} - r_{i,j} |
| ∆_{i,j} |  Difference between finish time and absolute deadline: Delta_{i,j} = f_{i,j} - d_{i,j}  |
| y_{i,j}   | Absolute priority point: y_{i,j} = r_{i,j} + Y_i  |



