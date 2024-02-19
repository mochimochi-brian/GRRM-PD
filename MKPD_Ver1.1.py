#!/share/apps/opt/intel/intelpython3/envs/homcloud/bin/python


from operator import itemgetter
import numpy as np
import homcloud.interface as hc
import matplotlib.pyplot as plt
import sys

plt.rcParams["font.size"] = 18
plt.rcParams['figure.subplot.bottom'] = 0.15


def read_energy_file(filename):
    energy_data = []
    with open(filename, "rt") as file:
        for line in file:
            if line[:6] == "Energy":
                energy = float(line.split("=")[1].split("(")[0].strip())
                energy_data.append(energy)
    return energy_data


def convert_energy_units(energy_data, reference_energy):
    return [(energy - reference_energy) * 627.51 for energy in energy_data]

def process_vertex_data(filename, energy_data):
    vertex_data = []
    energy_iter = iter(energy_data)

    with open(filename, "rt") as file:
        eq_number = None
        for line in file:
            line = line.strip()
            if line.startswith("# Geometry of EQ"):
                eq_number = int(line.split()[4].rstrip(','))  
            elif line.startswith("Energy"):
                energy = next(energy_iter)
                vertex_data.append([eq_number, energy])  
    vertex_data.sort(key=itemgetter(1)) 
    return vertex_data

def read_connection_data(filename):
    connection_data = []
    with open(filename, "rt") as rfile:
        for line in rfile:
            if line[:10] == "CONNECTION":
                connection_data.append(line.split(":")[1].strip().split(" - "))
    return connection_data

def process_edge_data(connection_data, energy_data):
    edge_data = []
    for i, connection in enumerate(connection_data):
        try:
            vertex_a = int(connection[0])
            vertex_b = int(connection[1])
            if vertex_a != vertex_b:
                energy = energy_data[i] + 0.0001
                edge_data.append([energy, str(min(vertex_a, vertex_b)), str(max(vertex_a, vertex_b))])
        except ValueError:
            pass
    return sorted(edge_data, key=itemgetter(0))

def remove_duplicate_edges(edge_data):
    unique_edges = []
    edge_set = set()

    for edge in edge_data:
        edge_key = tuple(sorted(edge[1:]))
        if edge_key not in edge_set:
            edge_set.add(edge_key)
            unique_edges.append(edge)

    return sorted(unique_edges, key=itemgetter(0))
"""
def remove_duplicate_edges(edge_data):
    unique_edges = []
    for i in range(len(edge_data)):
        edge_i = edge_data[i]
        duplicate = False
        for j in range(i+1, len(edge_data)):
            edge_j = edge_data[j]
            if edge_i[1:] == edge_j[1:] or edge_i[1:] == edge_j[2:]:
                if edge_i[0] >= edge_j[0]:
                    duplicate = True
                    break
                else:
                    edge_data.pop(j)
                    break
        if not duplicate:
            unique_edges.append(edge_i)
    return sorted(unique_edges, key=itemgetter(0))
"""

def check_and_modify_TS_energy(vertex_data, edge_data):
    for edge in edge_data:
        vertex_E_1 = None # Initialize the vertex_E_1 and vertex_E_2 variables
        vertex_E_2 = None

        for vertex in vertex_data:
            if vertex[0] == int(edge[1]):
                vertex_E_1 = vertex[1]
            elif vertex[0] == int(edge[2]):
                vertex_E_2 = vertex[1]
        if vertex_E_1 is not None and vertex_E_2 is not None:
            if edge[0] < vertex_E_1:
                edge[0] = vertex_E_1
            if edge[0] < vertex_E_2:
                edge[0] = vertex_E_2

    return sorted(edge_data, key=itemgetter(0))



def process_triangle_data(edge_data, vertex_data):
    triangle_data = []
    edge_list = [edge[1:3] for edge in edge_data]
    for edge in edge_data:
        edge_a = edge[1]
        edge_b = edge[2]
        for vertex in vertex_data:
            edge_c = str(vertex[0])
            if edge_c != edge_a and edge_c != edge_b and float(edge_c) > float(edge_b):
                is_edge_a_c = [edge_a, edge_c] in edge_list or [edge_c, edge_a] in edge_list
                is_edge_b_c = [edge_b, edge_c] in edge_list or [edge_c, edge_b] in edge_list
                if is_edge_a_c == True and is_edge_b_c == True:
                    energy_x = next(ed for ed in edge_data if ed[1:] == [edge_a, edge_b])[0]
                    energy_y = next(ed for ed in edge_data if ed[1:] == [edge_a, edge_c])[0]
                    energy_z = next(ed for ed in edge_data if ed[1:] == [edge_b, edge_c])[0]
                    triangle_data.append([[edge_a, edge_b, edge_c], max(float(energy_x), float(energy_y), float(energy_z)) + 0.0002])
    return sorted(triangle_data, key=itemgetter(1))

def create_boundary_data(vertex_data, edge_data, triangle_data):
    boundary_data = []
    levels_list = []
    vertex_numbers =[vertex[0] for vertex in vertex_data]
    vertex_to_boundary = {}
    edge_to_boundary = {}
    i_vertex = 0
    i_edge = 0
    i_triangle = 0
    i_boundary = 0
    lev_vertex = vertex_data[i_vertex][1] if vertex_data else 10 ** 10
    lev_edge = edge_data[i_edge][0] if edge_data else 10 ** 10
    lev_triangle = triangle_data[i_triangle][1] if triangle_data else 10 ** 10

    while i_vertex < len(vertex_data) or i_edge < len(edge_data) or i_triangle < len(triangle_data):
        min_level = min(lev_vertex, lev_edge, lev_triangle)
        if min_level == lev_vertex:
            boundary_data.append([0, [], []])
            levels_list.append(min_level)
            vertex_to_boundary.update([(vertex_numbers[i_vertex], i_boundary)])
            print(vertex_to_boundary)
            i_vertex += 1
            i_boundary += 1
            lev_vertex = vertex_data[i_vertex][1] if i_vertex < len(vertex_data) else 10 ** 10
        elif min_level == lev_edge:
            v1 = vertex_to_boundary[int(edge_data[i_edge][1])]
            v2 = vertex_to_boundary[int(edge_data[i_edge][2])]
            boundary_data.append([1, [v1, v2], [1.0, 1.0]])
            levels_list.append(min_level)
            edge_to_boundary.update([(edge_data[i_edge][1] + "-" + edge_data[i_edge][2], i_boundary)])
            i_edge += 1
            i_boundary += 1
            lev_edge = edge_data[i_edge][0] if i_edge < len(edge_data) else 10 ** 10
        else:
            e1 = edge_to_boundary[triangle_data[i_triangle][0][0] + "-" + triangle_data[i_triangle][0][1]]
            e2 = edge_to_boundary[triangle_data[i_triangle][0][1] + "-" + triangle_data[i_triangle][0][2]]
            e3 = edge_to_boundary[triangle_data[i_triangle][0][0] + "-" + triangle_data[i_triangle][0][2]]
            boundary_data.append([2, [e1, e2, e3], [1.0, 1.0, 1.0]])
            levels_list.append(min_level)
            i_triangle += 1
            i_boundary += 1
            lev_triangle = triangle_data[i_triangle][1] if i_triangle < len(triangle_data) else 10 ** 10

    return boundary_data, levels_list


def save_boundary_data(boundary_data, levels_list, filename):
    hc.PDList.from_boundary_information(boundary_data, levels_list, save_to=filename)


def plot_diagrams(PD_list):
    for i in range(3):
        print(i)
        print("b", PD_list.dth_diagram(i).births)
        print("d", PD_list.dth_diagram(i).deaths)
        print("e", PD_list.dth_diagram(i).essential_births)

        plt.scatter(PD_list.dth_diagram(i).births, PD_list.dth_diagram(i).deaths, label="PD"+str(i))
        plt.plot([0, 50], [0, 50], color="black", linewidth=1)
        plt.xlabel("Birth")
        plt.ylabel("Death")
        plt.xlim([0, 50])
        plt.ylim([0, 50])
        plt.axis("square")
        plt.savefig("plot_"+str(i)+".png")
        plt.savefig("plot_"+str(i)+".pdf")
        plt.clf()


def plot_combined_diagram(PD_list):
    plt.scatter(PD_list.dth_diagram(0).births, PD_list.dth_diagram(0).deaths, label="PD0", color='blue')
    plt.scatter(PD_list.dth_diagram(0).essential_births, [70]*len(PD_list.dth_diagram(0).essential_births), color='blue')
    plt.scatter(PD_list.dth_diagram(1).deaths, PD_list.dth_diagram(1).births, label="PD1", color='red')
    plt.scatter([70]*len(PD_list.dth_diagram(1).essential_births), PD_list.dth_diagram(1).essential_births, color='red')
    plt.plot([0, 70], [0, 70], color="black", linewidth=1)
    plt.xticks([0, 10, 20, 30, 40, 50, 70], ["0", "10", "20", "30", "40", "50", "∞"])
    plt.yticks([0, 10, 20, 30, 40, 50, 70], ["0", "10", "20", "30", "40", "50", "∞"])
    plt.xlabel("Birth/Death [kcal/mol]", size=24)
    plt.ylim([0, 70])
    plt.axis("square")
    plt.tick_params(labelsize=20)
    plt.text(5, 40, "$\mathcal{D}_{0}$", fontname="Caladea", color="blue", size=20)
    plt.text(40, 5, "$\mathcal{D}_{1}$", fontname="Caladea", color="red", size=20)
    plt.savefig("plot_PD0PD1.png")
    plt.savefig("plot_PD0PD1.pdf")
    plt.clf()

def plot_barcode(PD_list):
    num_Es0 = len(PD_list.dth_diagram(0).essential_births)
    meansE0 = (PD_list.dth_diagram(0).essential_births + 1000)/2
    half_rangeE0 = 1000 - meansE0
    plt.errorbar(meansE0, -np.arange(num_Es0)-1, xerr=half_rangeE0, ls='', elinewidth=4, capsize=5, color='blue')

    num_PD0 = len(PD_list.dth_diagram(0).births)
    PD0=[]
    for i in range(num_PD0):
        PD0.append([PD_list.dth_diagram(0).births[i], PD_list.dth_diagram(0).deaths[i]])
    PD0.sort(key=lambda x: x[0])
    means0 = [sum(x)/2 for x in PD0]
    deaths = [x[1] for x in PD0]
    half_range0 = [x-y for (x, y) in zip(deaths, means0)]
    plt.errorbar(means0, -np.arange(num_PD0)-num_Es0-1, xerr=half_range0, ls='', elinewidth=4, capsize=5, color='blue')

    num_Es1 = len(PD_list.dth_diagram(1).essential_births)
    meansE1 = (PD_list.dth_diagram(1).essential_births + 1000)/2
    half_rangeE1 = 1000 - meansE1
    plt.errorbar(meansE1, -np.arange(num_Es1)-num_Es0-num_PD0-1, xerr=half_rangeE1, ls='', elinewidth=4, capsize=5, color='red')

    num_PD1 = len(PD_list.dth_diagram(1).births)
    PD1=[]
    for i in range(num_PD1):
        PD1.append([PD_list.dth_diagram(1).births[i], PD_list.dth_diagram(1).deaths[i]])
    PD1.sort(key=lambda x: x[0])
    means1 = [sum(x)/2 for x in PD1]
    deaths = [x[1] for x in PD1]
    half_range1 = [x-y for (x, y) in zip(deaths, means1)]
    plt.errorbar(means1, -np.arange(num_PD1)-num_Es0-num_PD0-num_Es1-1, xerr=half_range1, ls='', elinewidth=4, capsize=5, color='red')

    ax = plt.gca()
    ax.axes.yaxis.set_visible(False)
    ax.grid(which="major", axis="x", alpha=0.8, linestyle="--", linewidth=1)
    plt.tick_params(labelsize=22)
    plt.ylim(-num_Es0-num_Es1-num_PD0-num_PD1-1,0)
    plt.xlim(0,50)
    plt.xlabel("Energy [kcal/mol]",size=24)
    plt.savefig("barcode.png", bbox_inches='tight', pad_inches=0.1)

def save_graph(filename, vertex_data, edge_data):
    with open(filename, "w") as file:
        file.write("graph G { \n")
        file.write("    layout=neato \n")
        for vertex in vertex_data:
            file.write(f"    node[shape=ellipse,label=\"{format(vertex[1],'.1f')}\"];EQ_{vertex[0]}; \n")
        for edge in edge_data:
            file.write(f"    EQ_{edge[1]} -- EQ_{edge[2]} [label=\"{format(edge[0],'.1f')}\",fontsize=12]; \n")
        file.write("}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python MKPD.py *_EQ_list.log *_TS_list.log")
        return

    EQ_filename = sys.argv[1]
    TS_filename = sys.argv[2]

    EQ_energy_data = read_energy_file(EQ_filename)
    TS_energy_data = read_energy_file(TS_filename)

    min_EQ_energy = min(EQ_energy_data)

    EQ_energy_data = convert_energy_units(EQ_energy_data, min_EQ_energy)
    TS_energy_data = convert_energy_units(TS_energy_data, min_EQ_energy)

    EQ_vertex_data = process_vertex_data(EQ_filename, EQ_energy_data)
    TS_connection_data = read_connection_data(TS_filename)
    TS_edge_data = process_edge_data(TS_connection_data, TS_energy_data)    
    print(EQ_vertex_data)
   # print(TS_edge_data)
    unique_TS_edge_data = remove_duplicate_edges(TS_edge_data)
   # print(unique_TS_edge_data)
    modified_TS_edge_data = check_and_modify_TS_energy(EQ_vertex_data, unique_TS_edge_data)    
    print(modified_TS_edge_data)

    Triangle_data = process_triangle_data(modified_TS_edge_data, EQ_vertex_data)
    print(Triangle_data)

    boundary_data, levels_list = create_boundary_data(EQ_vertex_data, modified_TS_edge_data, Triangle_data)

    save_boundary_data(boundary_data, levels_list, "pd.pdgm")

    PD_list = hc.PDList.from_boundary_information(boundary_data, levels_list)

    for d in range(2):
        with open(str(d) + "th_diagram", "w") as file:
            file.write(str(PD_list.dth_diagram))

    plot_diagrams(PD_list)

    plot_combined_diagram(PD_list)

    plot_barcode(PD_list)

    save_graph("graph.gv", EQ_vertex_data, unique_TS_edge_data)


if __name__ == "__main__":
    main()

