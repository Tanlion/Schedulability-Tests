import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import ticker

def to_percent(y, position):
    return str(y) + '%'



def gen_plot(filename):
    file = open(filename, "r")
    file.readline()     # skip first line
    x = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    for line in file.readlines():
        line = line.strip().split('\t')
        line = list(map(float, line))
        x.append(line[0])
        y1.append(line[1]/100.0)
        y2.append(line[2]/100.0)
        y3.append(line[3]/100.0)
        y4.append(line[4]/100.0)


    """
    https://stackoverflow.com/questions/8409095/set-markers-for-individual-points-on-a-line-in-matplotlib
    plt.plot(arguments):
    color = 'b', 'g', 'r', 'y', 'k'(black),'w',  
    marker = '.', ',', 'o', 's', 'p', '*', '+', 'x', 'D',
    linestyle = '-', '--', '-.', ':', 
    # """
    # plt.plot(x, y1, color='green', marker='x', linestyle=":", label='density')
    # plt.plot(x, y2, color='steelblue', marker='>',linestyle=":", label='load')
    plt.plot(x, y1, color='orange', marker='^', linestyle="--", label='fpbasic')
    plt.plot(x, y2, color='red', marker='o', linestyle="--", label='fpimprv')
    plt.plot(x, y3, color='gray', marker='d', linestyle="-.", label='npbasic')
    plt.plot(x, y4, color='darkviolet', marker='s', linestyle="-.", label='npimprv')


    # plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent()))
    plt.ylim(0.0, 1.0)
    plt.margins(0)
    plt.xlabel("Utilization")
    plt.ylabel("Schedulability Ratio")
    plt.tick_params(axis ="y")
    plt.legend(loc='lower left')            # draw legend 图例  upper right / lower left

    filename = filename.lstrip('./output/Ratio_')
    plt.savefig("./output/Pic_{}.pdf".format(filename.strip('.txt')))
    plt.show()

if __name__ == "__main__":
    filename = "./output/" + "Ratio_FpNp_4u_1000_50_1.0coe_6000lcm.txt"
    gen_plot(filename)

