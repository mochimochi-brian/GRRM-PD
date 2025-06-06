#!/home5/Brian/anaconda3/envs/homcloud/bin/python


from operator import itemgetter
import numpy as np
import homcloud.interface as hc
import matplotlib.pyplot as plt
import sys
import networkx as nx

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
def process_TS_blocks(filename, reference_energy ,skip_filename="skipped_TS.log"):
    """
    TSファイルをブロックごとに読み込み、各ブロックの
    "CONNECTION" 行の接続情報が整数に変換できる場合は有効なデータとして
    valid_connections と valid_energies に追加し、
    変換できないブロックは skipped_TS.log に出力します。

    戻り値:
      valid_connections: 例 [["0", "0"], ["0", "1"], ...]
      valid_energies: 対応するエネルギー値（float）のリスト
    """
    valid_connections = []
    valid_energies = []
    skipped_blocks = []
    block_lines = []
    
    with open(filename, "r") as f:
        for line in f:
            # 新たなTSブロックの開始を検出
            if line.startswith("# Geometry of TS"):
                if block_lines:
                    # 既存ブロックの処理
                    block_text = "".join(block_lines)
                    connection_line = None
                    energy_line = None
                    for l in block_lines:
                        if l.startswith("CONNECTION"):
                            connection_line = l
                        if l.startswith("Energy"):
                            energy_line = l
                    if connection_line and energy_line:
                        parts = connection_line.split(":")[1].strip().split(" - ")
                        try:
                            # 変換可能なら有効データとして追加
                            a = int(parts[0])
                            b = int(parts[1])
                            valid_connections.append(parts)
                            energy_value = float(energy_line.split("=")[1].split("(")[0].strip())
                            energy_value = (energy_value - reference_energy) * 627.51
                            valid_energies.append(energy_value)
                        except ValueError:
                            # 変換エラーならスキップ対象として記録
                            skipped_blocks.append(block_text)
                    else:
                        # 必要な行が存在しなければスキップ
                        skipped_blocks.append(block_text)
                # 新しいブロックの開始
                block_lines = [line]
            else:
                block_lines.append(line)
        # 最後のブロックの処理
        if block_lines:
            block_text = "".join(block_lines)
            connection_line = None
            energy_line = None
            for l in block_lines:
                if l.startswith("CONNECTION"):
                    connection_line = l
                if l.startswith("Energy"):
                    energy_line = l
            if connection_line and energy_line:
                parts = connection_line.split(":")[1].strip().split(" - ")
                try:
                    a = int(parts[0])
                    b = int(parts[1])
                    valid_connections.append(parts)
                    energy_value = float(energy_line.split("=")[1].split("(")[0].strip())
                    energy_value = (energy_value - reference_energy) * 627.51
                    valid_energies.append(energy_value)
                except ValueError:
                    skipped_blocks.append(block_text)
            else:
                skipped_blocks.append(block_text)
    
    # スキップされたTSブロックをファイルに書き出し
    with open(skip_filename, "w") as skip_file:
        for block in skipped_blocks:
            skip_file.write(block)
            skip_file.write("\n")
    
    return valid_connections, valid_energies

def process_edge_data(connection_data, energy_data):
    edge_data = []
    for i, connection in enumerate(connection_data):
        # connection_data はすでに整数変換可能な文字列のリストになっています
        vertex_a = int(connection[0])
        vertex_b = int(connection[1])
        if vertex_a != vertex_b:
            energy = energy_data[i]
            edge_data.append([energy, str(min(vertex_a, vertex_b)), str(max(vertex_a, vertex_b))])
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

def check_and_modify_TS_energy(vertex_data, edge_data):
    vertex_energy_dict = {vertex[0]:vertex[1] for vertex in vertex_data}
    for edge in edge_data:
        vertex1 = int(edge[1])
        vertex2 = int(edge[2])

        vertex_E_1 = vertex_energy_dict[vertex1]
        vertex_E_2 = vertex_energy_dict[vertex2]

        if edge[0] < vertex_E_1:
            edge[0] = vertex_E_1
        if edge[0] < vertex_E_2:
            edge[0] = vertex_E_2

    return sorted(edge_data, key=itemgetter(0))



def process_triangle_data(edge_data, vertex_data):
    G = nx.Graph()    
    for vertex in vertex_data:
        node_id = int(vertex[0])
        energy = float(vertex[1])
        G.add_node(node_id, energy=energy)

    for edge in edge_data:
        G.add_edge(int(edge[1]), int(edge[2]), energy=edge[0])
    triangle_data = []
    
    seen_triangles = set()
    for node in G.nodes():
        neighbors = set(G.neighbors(node))
        for neighbor in neighbors:
            common_neighbors = neighbors & set(G.neighbors(neighbor))
            for cn in common_neighbors:
                triangle = tuple(sorted([node, neighbor, cn]))
                if triangle not in seen_triangles:
                    seen_triangles.add(triangle)
                    edges = [
                        (triangle[0], triangle[1]), 
                        (triangle[0], triangle[2]),
                        (triangle[1], triangle[2]),
                    ]
                    energies = [G[edge[0]][edge[1]]['energy'] for edge in edges]
                    triangle_energy = max(energies) + 0.0001
                    triangle_data.append([[str(triangle[0]), str(triangle[1]), str(triangle[2])], triangle_energy])

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
    plt.xlim(0,250)
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
    # TS_energy_data は process_TS_blocks で再取得するので不要なら無視

    EQ_vertex_data = process_vertex_data(EQ_filename, EQ_energy_data)
    
    # TSファイルから有効な接続情報とエネルギーデータを取得
    TS_connection_data, TS_energy_data_valid = process_TS_blocks(TS_filename, min_EQ_energy, skip_filename="skipped_TS.log")
    TS_edge_data = process_edge_data(TS_connection_data, TS_energy_data_valid)
    
    print(EQ_vertex_data)
    print(TS_edge_data)

    unique_TS_edge_data = remove_duplicate_edges(TS_edge_data)
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

    # 追加: 後で別ファイル生成に使うためのデータ書き出し
    with open("simplex_data.txt", "w") as outfile:
        outfile.write("EQ_vertex_data:\n")
        outfile.write(str(EQ_vertex_data) + "\n\n")
        outfile.write("modified_TS_edge_data:\n")
        outfile.write(str(modified_TS_edge_data) + "\n\n")
        outfile.write("Triangle_data:\n")
        outfile.write(str(Triangle_data) + "\n")


if __name__ == "__main__":
    main()

