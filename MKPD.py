#!/share/apps/opt/intel/intelpython3/envs/homcloud/bin/python

 
from operator import itemgetter
import copy
import subprocess
import struct
import numpy as np
import homcloud.interface as hc
import matplotlib.pyplot as plt
import sys

plt.rcParams["font.size"] = 18
plt.rcParams['figure.subplot.bottom'] = 0.15



args = sys.argv
EQfilename=args[1]
TSfilename=args[2]

eq = 0
EQnumber = []
EQenergy = []
with open(EQfilename, "rt") as rfile:
    for line in rfile:
        if line[:6] == "Energy":
            EQenergy.append(float(line.split("=")[1].split("(")[0].strip()))
            EQnumber.append(eq)
            eq += 1
    Min_EQenergy = min(EQenergy)
    for i in range(len(EQnumber)):
        EQenergy[i] = (EQenergy[i]-Min_EQenergy)*627.51 
#print(EQnumber)
#print(EQenergy)

ts = 0
TSnumber = []
TSenergy = []
TSconnection = []
with open(TSfilename, "rt") as rfile:
    for line in rfile:
        if line[:6] == "Energy":
            TSenergy.append(float(line.split("=")[1].split("(")[0].strip()))
            TSnumber.append(ts)
            ts += 1
        elif line[:10] == "CONNECTION":
              TSconnection.append(line.split(":")[1].strip().split(" - "))
    for i in range(len(TSnumber)):
        TSenergy[i] = (TSenergy[i]-Min_EQenergy)*627.51
#print(TSnumber)
#print(TSenergy)
#print(TSconnection)

EQdictionary =[]
for i in range(eq):
    EQdictionary.append([EQnumber[i],EQenergy[i]])
#print(EQdictionary)

EQlist = sorted(EQdictionary,key=itemgetter(1))
for i in range(len(EQlist)):
    EQlist[i].append("EQ")
#print(EQlist)


TSdictionary =[]
for i in range(ts):
    TSdictionary.append([TSnumber[i],TSenergy[i]])
#print(TSdictionary)

TSlist = sorted(TSdictionary,key=itemgetter(1))
for i in range(len(TSlist)):
    TSlist[i].append("TS")
#print(TSlist)

Vertexlist = EQlist
Vertexlist = sorted(Vertexlist, key = itemgetter(1))
for i in range(len(Vertexlist)):
    Vertexlist[i].insert(0,i)
print(Vertexlist)

f = open("Vertexlist.txt","w")
for i in Vertexlist:
    f.write(str(i) + "\n")
f.close()


Edgelist = []
poplist = []
for i in range(len(TSconnection)):
    try:
        int(TSconnection[i][0])
    except ValueError:
        continue
    try:
        int(TSconnection[i][1])
    except ValueError:
        continue
    if TSconnection[i][0] != TSconnection[i][1]:
        Edgelist.append([TSenergy[i]+0.0001,str(min(int(TSconnection[i][0]),int(TSconnection[i][1]))),str(max(int(TSconnection[i][0]),int(TSconnection[i][1])))])
              
for i in range(len(Edgelist)):
    for j in range(i+1,len(Edgelist)):
        if Edgelist[i][1] == Edgelist[j][1] and Edgelist[i][2] == Edgelist[j][2]:
            if Edgelist[i][0] >= Edgelist[j][0]:
                poplist.append(i)
            if Edgelist[i][0] <= Edgelist[j][0]:
                poplist.append(j)

for i in range(len(Edgelist)):
    for j in range(i+1,len(Edgelist)):
        if Edgelist[i][2] == Edgelist[j][1] and Edgelist[i][1] == Edgelist[j][2]:
            if Edgelist[i][0] >= Edgelist[j][0]:
                poplist.append(i)
            if Edgelist[i][0] <= Edgelist[j][0]:
                poplist.append(j)

i = 0
VertexE_A = 0
VertexE_B = 0
for Edge in Edgelist:
    for Vertex in Vertexlist:
        if Vertex[1] == int(Edge[1]):
            VertexE_A = Vertex[2]
        elif Vertex[1] == int(Edge[2]):
            VertexE_B = Vertex[2]
    print(Edge[0], VertexE_A, VertexE_B)
    if Edge[0] < VertexE_A or Edge[0] < VertexE_B:
        poplist.append(i)
    i += 1
"""
j = 0
for Edge in Edgelist:
    if Edge[1] == "DC":
        poplist.append(j)
    elif Edge[2] == "DC":
        poplist.append(j)
    j += 1
"""
"""
VertexA = [V for V in Vertexlist if V[1] == int(Edge[1])]
VertexB = [V for V in Vertexlist if V[1] == int(Edge[2])]
"""
for i in sorted(list(set(poplist)),reverse=True):
    Edgelist.pop(i)


Edgelist = sorted(Edgelist, key = itemgetter(0))
print(Edgelist)


f = open("Edgelist.txt","w")
for i in Edgelist:
    f.write(str(i) + "\n")
f.close()



Trianglelist=[]
"""
conectA=[]
conectB=[]
for i in range(len(Edgelist)):
    conectA.append(Edgelist[i][1]) 
    conectB.append(Edgelist[i][2])
print(conectA)
print(conectB)
for i in range(len(Edgelist)):
    "count_" + str(i) = conectA.count(str(i))+conect.count(str(i))
    print("count_" + str(i))
"""
"""
for edge in Edgelist:
    edgeA = int(edge[1])
    edgeB = int(edge[2])
    for vertex in Vertexlist:
        edgeC = vertex[1]
        if edgeC != edgeA and edgeC != edgeB:
            A = len([edge[1:2] for edge in Edgelist if (edgeA==1 and edgeB==3) or (edgeB==1 and edgeA==3)])
            B = [edge[1:2] for edge in Edgelist if (edgeA==2 and edgeB==3) or (edgeB==2 and edgeA==3)]

print(A,B)
"""
edge_list = []
for edge in Edgelist:
    edge_list.append(edge[1:3])
print(edge_list)

Trianglelist = []

for edge in Edgelist:
    edgeA = edge[1]
    edgeB = edge[2]
    for vertex in Vertexlist:
        edgeC = str(vertex[1])
        if edgeC != edgeA and edgeC != edgeB and int(edgeC)>int(edgeB):
            A= [edgeA,edgeC] in edge_list or [edgeC,edgeA] in edge_list
            B= [edgeB,edgeC] in edge_list or [edgeC,edgeB] in edge_list

            if A == True and B == True:
                if [edgeA,edgeB] in edge_list:
                    i = edge_list.index([edgeA, edgeB])
                else:
                    i = edge_list.index([edgeB, edgeA])
                Enargy_x = Edgelist[i][0]

                if [edgeA,edgeC] in edge_list:
                    j = edge_list.index([edgeA, edgeC])
                else:
                    j = edge_list.index([edgeC, edgeA])
                Enargy_y = Edgelist[j][0]

                if [edgeB,edgeC] in edge_list:
                    k = edge_list.index([edgeB, edgeC])
                else:
                    k = edge_list.index([edgeC, edgeB])
                Enargy_z = Edgelist[k][0]

                Trianglelist.append([[edgeA, edgeB, edgeC], max(float(Enargy_x), float(Enargy_y), float(Enargy_z))+0.0002])
Trianglelist = sorted(Trianglelist, key = itemgetter(1))

print(Trianglelist)


#ここからinputの作成

boundary = []
levels_list = []
"""
for i in range(len(Vertexlist)):
    boundary.append([0,[],[]])
    levels_list.append(Vertexlist[i][2])
"""
#Vertexnumber = []
#for i in range(len(Vertexlist)):
 #   Vertexnuber.append(Vertexlist[i][1])
Vertexnumber = [Vertexlist[i][1] for i in range(len(Vertexlist))]
Vertex2Boundary = {}
Edge2Boundary = {}
i_vertex = 0
i_edge = 0
i_triangle = 0
i_boundary = 0
lev_vertex = Vertexlist[i_vertex][2]
lev_edge = Edgelist[i_edge][0]
if len(Trianglelist) != 0:
    lev_triangle = Trianglelist[i_triangle][1]
else:
    lev_triangle = 10 ** 10


while i_vertex < len(Vertexlist) or i_edge < len(Edgelist) or i_triangle < len(Trianglelist):
    minlevel = min(lev_vertex, lev_edge, lev_triangle)
    if minlevel == lev_vertex:
        boundary.append([0,[],[]])
        levels_list.append(minlevel)
        Vertex2Boundary.update([(Vertexnumber[i_vertex],i_boundary)])
        i_vertex += 1
        i_boundary += 1
        if i_vertex < len(Vertexlist):
            lev_vertex = Vertexlist[i_vertex][2]
        else:
            lev_vertex = 10 ** 10
    elif minlevel == lev_edge:
       # print(i_edge)
       # print(Edgelist)
       # print(Vertex2Boundary)
        V_1 = Vertex2Boundary[int(Edgelist[i_edge][1])]
        V_2 = Vertex2Boundary[int(Edgelist[i_edge][2])]
        boundary.append([1,[V_1,V_2],[1.0,1.0]])
        levels_list.append(minlevel)
       #Edge2Boundary.update([([int(Edgelist[i_edge][1]),int(Edgelist[i_edge][2])],i_boundary)])
        Edge2Boundary.update([(Edgelist[i_edge][1]+"-"+Edgelist[i_edge][2],i_boundary)])
        i_edge += 1
        i_boundary += 1
        if i_edge < len(Edgelist):
            lev_edge = Edgelist[i_edge][0]
        else:
            lev_edge = 10**10
    else:
        E_1 = Edge2Boundary[Trianglelist[i_triangle][0][0]+"-"+Trianglelist[i_triangle][0][1]]
        E_2 = Edge2Boundary[Trianglelist[i_triangle][0][1]+"-"+Trianglelist[i_triangle][0][2]]
        E_3 = Edge2Boundary[Trianglelist[i_triangle][0][0]+"-"+Trianglelist[i_triangle][0][2]]
        boundary.append([2,[E_1,E_2,E_3], [1.0,1.0,1.0]])
        levels_list.append(minlevel)
        i_triangle += 1
        i_boundary += 1
        if i_triangle < len(Trianglelist):
            lev_triangle = Trianglelist[i_triangle][1]
        else:
            lev_triangle = 10**10




  
"""
for i in range(len(Edgelist)):
    V_1=Vertexnumber.index(int(Edgelist[i][1]))
    V_2=Vertexnumber.index(int(Edgelist[i][2]))
    boundary.append([1,[V_1,V_2],[1.0,1.0]])
    levels_list.append(Edgelist[i][0])

Edgenumber = [[int(Edge[1]),int(Edge[2])] for Edge in Edgelist]

for i in range(len(Trianglelist)):
    E_1=Edgenumber.index([int(Trianglelist[i][0][0]),int(Trianglelist[i][0][1])]) +len(Vertexlist)
    E_2=Edgenumber.index([int(Trianglelist[i][0][1]),int(Trianglelist[i][0][2])]) +len(Vertexlist)
    E_3=Edgenumber.index([int(Trianglelist[i][0][0]),int(Trianglelist[i][0][2])]) +len(Vertexlist)
    boundary.append([2,[E_1,E_2,E_3],[1.0,1.0,1.0]])
    levels_list.append(Trianglelist[i][1])
"""
levels = levels_list

print(boundary)
print(levels)

hc.PDList.from_boundary_information(boundary, levels, save_to="output0")

PD_list = hc.PDList.from_boundary_information(boundary, levels)

for i in range(3):
    print(i)
    print("b",PD_list.dth_diagram(i).births)
    print("d",PD_list.dth_diagram(i).deaths)
    print("e",PD_list.dth_diagram(i).essential_births)

    plt.scatter(PD_list.dth_diagram(i).births, PD_list.dth_diagram(i).deaths, label="PD"+str(i))
    plt.plot([0,50], [0,50], color="black", linewidth = 1)
    plt.xlabel("Birth")
    plt.ylabel("Death")
    plt.xlim([0, 50])
    plt.ylim([0, 50])
    plt.axis("square")
    plt.savefig("plot_"+str(i)+".png")
    plt.savefig("plot_"+str(i)+".pdf")
    plt.clf()

print(0)
print("b",PD_list.dth_diagram(0).births)
print("d",PD_list.dth_diagram(0).deaths)
print("e",PD_list.dth_diagram(0).essential_births)

print(1)
print("b",PD_list.dth_diagram(1).births)
print("d",PD_list.dth_diagram(1).deaths)
print("e",PD_list.dth_diagram(1).essential_births)

plt.scatter(PD_list.dth_diagram(0).births, PD_list.dth_diagram(0).deaths, label="PD"+str(i), color='blue')
plt.scatter(PD_list.dth_diagram(0).essential_births,[70]*len(PD_list.dth_diagram(0).essential_births), color='blue')
plt.scatter(PD_list.dth_diagram(1).deaths, PD_list.dth_diagram(1).births, label="PD"+str(i), color='red')
plt.scatter([70]*len(PD_list.dth_diagram(1).essential_births),PD_list.dth_diagram(1).essential_births, color='red')
plt.plot([0,70], [0,70], color="black", linewidth = 1)
plt.xticks([0,10,20,30,40,50,70],["0","10","20","30","40","50","∞",])
plt.yticks([0,10,20,30,40,50,70],["0","10","20","30","40","50","∞",])
plt.xlabel("Birth/Death [kcal/mol]" ,size=24)
plt.ylabel("Death/Birth [kcal/mol]" ,size=24)
plt.xlim([0, 70])
plt.ylim([0, 70])
plt.axis("square")
plt.tick_params(labelsize=20)
plt.text(5,40, "$\mathcal{D}_{0}$",fontname="Caladea", color="blue", size=20)
plt.text(40,5, "$\mathcal{D}_{1}$",fontname="Caladea", color="red", size=20)
plt.savefig("plot_PD0PD1.png")
plt.savefig("plot_PD0PD1.pdf")
plt.clf()

plt.scatter(PD_list.dth_diagram(0).births, PD_list.dth_diagram(0).deaths-PD_list.dth_diagram(0).births, color='#1f77b4')
plt.scatter(PD_list.dth_diagram(0).essential_births,[70]*len(PD_list.dth_diagram(0).essential_births), color='#1f77b4')
plt.xticks([0,10,20,30,40,50],["0","10","20","30","40","50"])
plt.yticks([0,10,20,30,40,50,70],["0","10","20","30","40","50","∞",])
plt.xlabel("Birth")
plt.ylabel("Death-Birth")
plt.xlim([0, 50])
plt.ylim([0, 70])
#plt.axis("square")
plt.savefig("plot_PD0_lifespan.pdf")
plt.clf()



with open ("graph.gv", "w") as f:
    f.write("graph G { \n" )
    f.write("    layout=neato \n")
    for Vertex in Vertexlist:
        f.write("    node[shape=ellipse,label=\"" + format(Vertex[2],".1f") + "\"];EQ_" + str(Vertex[1]) + "; \n")
    for Edge in Edgelist:
        f.write("    EQ_"+str(Edge[1]) +" -- EQ_"+ str(Edge[2])+" [label=\""+format(Edge[0],".1f")+"\",fontsize=12]; \n")
    f.write("}")
"""
with open ("PH.txt", "w") as f:
    try:
        f.write("0\n")
        f.write("b")
        f.write(str(PD_list.dth_diagram(0).births)+"\n")
        f.write("d")
        f.write(str(PD_list.dth_diagram(0).deaths)+"\n")
        f.write("d-b")
        f.write(str(PD_list.dth_diagram(0).deaths-PD_list.dth_diagram(0).births)+"\n")
        f.write("e")
        f.write(str(PD_list.dth_diagram(0).essential_births)+"\n")

        f.write("1\n")
        f.write("b")
        f.write(str(PD_list.dth_diagram(1).births)+"\n")
        f.write("d")
        f.write(str(PD_list.dth_diagram(1).deaths)+"\n")
        f.write("d-b")
        f.write(str(PD_list.dth_diagram(1).deaths-PD_list.dth_diagram(1).births)+"\n")
        f.write("e")
        f.write(str(PD_list.dth_diagram(1).essential_births)+"\n")

        f.write("2\n")
        f.write("b")
        f.write(str(PD_list.dth_diagram(2).births)+"\n")
        f.write("d")
        f.write(str(PD_list.dth_diagram(2).deaths)+"\n")
        f.write("d-b")
        f.write(str(PD_list.dth_diagram(2).deaths-PD_list.dth_diagram(2).births)+"\n")
        f.write("e")
        f.write(str(PD_list.dth_diagram(2).essential_births)+"\n")
        f.write("\n")

    finally:
        f.write("Vertex_list\n")
        f.write("[number,original_number,Energy,EQ]\n")
        f.write(str(Vertexlist)+"\n")

        f.write("Edge_list\n")
        f.write("[Energy,connectionA,connectionB]\n")
        f.write(str(Edgelist)+"\n")

        f.write("Triangle_list\n")  
        f.write("[[EdgeA,EdgeB,EdgeC],Energy]\n")
        f.write(str(Trianglelist)+"\n")
"""
"""
num_Es0 = len(PD_list.dth_diagram(0).essential_births)
meansE0 = (PD_list.dth_diagram(0).essential_births + 1000)/2
half_rangeE0 = 1000 - meansE0
plt.errorbar(meansE0, -np.arange(num_Es0)-1, xerr=half_rangeE0, ls='', elinewidth=4, capsize=5, color='blue')

num_PD0 = len(PD_list.dth_diagram(0).births)
means0 = (PD_list.dth_diagram(0).births + PD_list.dth_diagram(0).deaths)/2
half_range0 = PD_list.dth_diagram(0).deaths - means0
plt.errorbar(means0, -np.arange(num_PD0)-num_Es0-1, xerr=half_range0, ls='', elinewidth=4, capsize=5, color='blue')

num_Es1 = len(PD_list.dth_diagram(1).essential_births)
meansE1 = (PD_list.dth_diagram(1).essential_births + 1000)/2
half_rangeE1 = 1000 - meansE1
plt.errorbar(meansE1, -np.arange(num_Es1)-num_Es0-num_PD0-1, xerr=half_rangeE1, ls='', elinewidth=4, capsize=5, color='red')

num_PD1 = len(PD_list.dth_diagram(1).births)
means1 = (PD_list.dth_diagram(1).births + PD_list.dth_diagram(1).deaths)/2
half_range1 = PD_list.dth_diagram(1).deaths - means1
plt.errorbar(means1, -np.arange(num_PD1)-num_Es0-num_PD0-num_Es1-1, xerr=half_range1, ls='', elinewidth=4, capsize=5, color='red')

ax = plt.gca()
ax.axes.yaxis.set_visible(False)
ax.grid(which="major", axis="x", alpha=0.8, linestyle="--", linewidth=1)
plt.ylim(-num_Es0-num_Es1-num_PD0-num_PD1-20,0)
#plt.ylim(50,0)
plt.xlim(-2,50)
plt.xlabel("Energy [kcal/mol]")
plt.savefig("barcode.png")
"""

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
#means0 = (PD_list.dth_diagram(0).births + PD_list.dth_diagram(0).deaths)/2
#half_range0 = PD_list.dth_diagram(0).deaths - means0
plt.errorbar(means0, -np.arange(num_PD0)-num_Es0-1, xerr=half_range0, ls='', elinewidth=4, capsize=5, color='blue')

"""
num_PD0 = len(PD_list.dth_diagram(0).births)
means0 = (PD_list.dth_diagram(0).births + PD_list.dth_diagram(0).deaths)/2
half_range0 = PD_list.dth_diagram(0).deaths - means0
plt.errorbar(means0, -np.arange(num_PD0)-num_Es0-1, xerr=half_range0, ls='', elinewidth=4, capsize=5, color='blue')
"""
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
#means1 = (PD_list.dth_diagram(1).births + PD_list.dth_diagram(1).deaths)/2
#half_range1 = PD_list.dth_diagram(1).deaths - means1
plt.errorbar(means1, -np.arange(num_PD1)-num_Es0-num_PD0-num_Es1-1, xerr=half_range1, ls='', elinewidth=4, capsize=5, color='red')


"""
num_PD1 = len(PD_list.dth_diagram(1).births)
means1 = (PD_list.dth_diagram(1).births + PD_list.dth_diagram(1).deaths)/2
half_range1 = PD_list.dth_diagram(1).deaths - means1
plt.errorbar(means1, -np.arange(num_PD1)-num_Es0-num_PD0-num_Es1-1, xerr=half_range1, ls='', elinewidth=4, capsize=5, color='red')
"""


ax = plt.gca()
ax.axes.yaxis.set_visible(False)
ax.grid(which="major", axis="x", alpha=0.8, linestyle="--", linewidth=1)
#ax.set_aspect("equal")
plt.tick_params(labelsize=22)
plt.ylim(-num_Es0-num_Es1-num_PD0-num_PD1-1,0)
plt.xlim(0,50)
plt.xlabel("Energy [kcal/mol]",size=24)
plt.savefig("barcode.png", bbox_inches='tight', pad_inches=0.1)

"""
num_Es0 = len(PD_list.dth_diagram(0).essential_births)
meansE0 = (PD_list.dth_diagram(0).essential_births + 1000)/2
half_rangeE0 = 1000 - meansE0
plt.errorbar(meansE0, -np.arange(num_Es0)-1, xerr=half_rangeE0, ls='', elinewidth=4, capsize=5, color='blue')

num_PD0 = len(PD_list.dth_diagram(0).births)
means0 = (PD_list.dth_diagram(0).births + PD_list.dth_diagram(0).deaths)/2
half_range0 = PD_list.dth_diagram(0).deaths - means0
plt.errorbar(means0, -np.arange(num_PD0)-num_Es0-1, xerr=half_range0, ls='', elinewidth=4, capsize=5, color='blue')

num_Es1 = len(PD_list.dth_diagram(1).essential_births)
meansE1 = (PD_list.dth_diagram(1).essential_births + 1000)/2
half_rangeE1 = 1000 - meansE1
plt.errorbar(meansE1, -np.arange(num_Es1)-num_Es0-num_PD0-1, xerr=half_rangeE1, ls='', elinewidth=4, capsize=5, color='red')

num_PD1 = len(PD_list.dth_diagram(1).births)
means1 = (PD_list.dth_diagram(1).births + PD_list.dth_diagram(1).deaths)/2
half_range1 = PD_list.dth_diagram(1).deaths - means1
plt.errorbar(means1, -np.arange(num_PD1)-num_Es0-num_PD0-num_Es1-1, xerr=half_range1, ls='', elinewidth=4, capsize=5, color='red')

ax = plt.gca()
ax.axes.yaxis.set_visible(False)
ax.grid(which="major", axis="x", alpha=0.8, linestyle="--", linewidth=1)
plt.ylim(-num_Es0-num_Es1-num_PD0-num_PD1-1,0)
plt.xlim(-2,50)
plt.xlabel("Energy [kcal/mol]")
plt.savefig("barcode.png")


"""
"""
    Histogram = PD_list.dth_diagram(i).histogram(x_range=[0.0, 50.0], x_bins=64)
    Histogram.plot(colorbar={"min":0, "max":3},font_size=16)
    plt.savefig("histogram_" +str(i)+".png")

"""

"""
Dummy_Edgelist = copy.deepcopy(Edgelist)
for i in range(len(Edgelist)):
    for j in range(len(Vertexlist)):
        if int(Dummy_Edgelist[i][1]) == Vertexlist[j][1] and Vertexlist[j][3] == "EQ":
            Edgelist[i][1] = Vertexlist[j][0]        
         Dummy_Edgelist[i][2] == Vertexlist[j][1] and Vertexlist[j][3] == "TS":
            Edgelist[i][2] = Vertexlist[j][0]

print(Edgelist)
"""
"""
dlist = [[2.]*len(Vertexlist) for i in range(len(Vertexlist))]
for i in range(len(Edgelist)):
    dlist[Edgelist[i][1]][Edgelist[i][2]] = 2 - 1/(1+Edgelist[i][0])
    dlist[Edgelist[i][2]][Edgelist[i][1]] = 2 - 1/(1+Edgelist[i][0])
for i in range(len(Vertexlist)):
    for j in range(len(Vertexlist)):
        if i == j:
            dlist[i][j] = 0.
print(dlist)



   
filename = "distance_matrix"

with open(filename, "wb") as f:
    f.write((8067171840).to_bytes(8,"little"))
    f.write((7).to_bytes(8,"little"))
    f.write((len(Vertexlist)).to_bytes(8,"little"))
    for i in range(len(Vertexlist)):
        for j in range(len(Vertexlist)):
            f.write(struct.pack('<d', dlist[i][j]))


"""
"""

subgraphs = []
sorted_graph = []
#print(sorted(EQenergy+TSenergy))
for energy_th in sorted(EQenergy+TSenergy):
    for i in range(len(EQenergy+TSenergy)):
        if Vertexlist[i][2] == energy_th:
            sorted_graph.append(Vertexlist[i])
   # print(sorted_graph)
    a = sorted_graph.copy()
    subgraphs.append(a)
print(subgraphs)
"""
"""
i = 0
l = 0
for energy_th in sorted(EQenergy + TSenergy):
    with open( "chomp_" + str(i).zfill(5) + ".txt" , mode = "w") as wfile:
        num_edge = 0
        for k in range(len(Edgelist)):
            if energy_th >= Edgelist[k][0]:
                num_edge += 1
       # wfile.write(str(i+1) + " " + str(num_edge) + "\n")      # for eis
        for n in range(i + 1):
            wfile.write("{" + str(n) + "}\n")

                wfile.write("{" + str(Edgelist[j][1]) + "," + str(Edgelist[j][2]) + "}\n") 
               # wfile.write(str(Edgelist[j][1])+ " " +str(Edgelist[j][2]) + "\n")       #for eis
    subprocess.call(["/opt/chomp/bin/homsimpl", "chomp_" + str(i).zfill(5) + ".txt", "-g", "chomp_" + str(i).zfill(5) + ".out"])

    i += 1
"""


#with open("eis_test.txt" , mode = "w") as wfile:
    #wfile.write(str(len(Vertexlist)) + " " + str(len(Edgelist))+"\n")
    #for i in range(len(Edgelist)):
        #wfile.write(str(Edgelist[i][1]) + " " + str(Edgelist[i][2])+ "\n")

