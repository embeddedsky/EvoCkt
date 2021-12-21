# -*- coding:utf-8 -*-
import re
from GP.Utilities.Node import Node
from GP.Utilities.Tree import Tree
from GP.Utilities.raw_read import rawread


import subprocess as sp
import pandas
import numpy as np
#并行计算所需库
from multiprocessing.dummy import Pool as ThreadPool

spicepath = r'/rds/bear-apps/2019b/EL7-haswell/software/ngspice/31-foss-2019b/bin/ngspice'    #location of ngspice terminal on computer
tem_targetpath='none'
filename='circuit'
targetpath='rawfile'
refpath='reffile.raw'

fitness_file="fitness_record"
ref_path='vout-t.xlsx'
excel_file=pandas.read_excel(ref_path,sheet_name=[0])
ref_matrix=excel_file[0].values.transpose()
ref_v=ref_matrix[1]
#程序参数
depth_range = (4,7)
max_depth=depth_range[1]
port_num=30
R_range=[1,200000]
C_range=[1,1000]
NMOS=" "
PMOS=" "
Not_Gate="inverter"
MEMRISTOR=([1000,99999],'memristor')
MODUEL1=([1.0,3.0],[1.0,10.0],'unitoff1')
MODUEL2=([1.0,3.0],[1.0,10.0],'unitoff2')
MODUEL3=([1.0,3.0],[1.0,10.0],'uniton1')
MODUEL4=([1.0,3.0],[1.0,10.0],'uniton2')
root_function_set = [("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("P",3,PMOS),("N",3,NMOS)]
function_set = [("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("R", 2,R_range),("P",3,PMOS),("N",3,NMOS)]
sub_tree_set=[("+", 2),("-",2),("*", 2)]

R_Set=[("R", 2,R_range)]

unitoff1_set=[("UOFF1",2,MODUEL1),("UOFF1_P",2,MODUEL1)]
unitoff2_set=[("UOFF2",2,MODUEL2),("UOFF2_P",2,MODUEL2)]
uniton1_set=[("UON1",2,MODUEL3),("UON1_P",2,MODUEL3)]
uniton2_set=[("UON2",2,MODUEL4),("UON2_P",2,MODUEL4)]
Not_Set=[("Not",2,Not_Gate),("Not_p",2,Not_Gate)]
C_Set=[("C",2,C_range),("C_P",2,C_range)]


#单个mos类型
P_Set=[("P_2_1",3,PMOS),("P_2_2",3,PMOS),("P_2_3",3,PMOS),("P_2_4",3,PMOS),("P_2_5",3,PMOS),("P_2_6",3,PMOS)]
N_Set=[("N_2_1",3,NMOS),("N_2_2",3,NMOS),("N_2_3",3,NMOS),("N_2_4",3,NMOS),("N_2_5",3,NMOS),("N_2_6",3,NMOS)]

M_Set=[("Mem", 2,MEMRISTOR),("Mem_P", 2,MEMRISTOR)]
# 0:接地
#1：VSS
#2:-VSS
#3:INPUT
#4:OUPUT
terminal_set = [None]*port_num
for i in range(port_num):
  terminal_set[i]=i

cross_rate =0.8
pop_init_method = "grow"
pop_size = 100
mutation_rate =0.2

mutation_methods = ["delete","add","another","change_value"]
tournament_size =int(0.2*pop_size)
value_cross_rate=0.2


core=1

elitism = True
found_solution = False

file_name_add=[]
for i in range(0,pop_size):
    file_name_add.append(i)

class Instruc:
    def __init__(self,label=None,port_num=0,port_list=[],other=[],value=[],index=0):
        self.label=label
        self.port_num=port_num
        self.port_list=port_list
        self.other=other
        self.value=value
        self.index=index
def create_instruction(population:Tree):
    function_dic={'xmem':0,'R':0,'xng':0,'xuoffone':0,'xuofftwo':0,'xuonone':0,'xuontwo':0,'C':0,'Q':0}
    Instruc_Set=[]
    root=population.root
    create_instruction_recursively(root,Instruc_Set,function_dic)
    return Instruc_Set
def create_instruction_recursively(parent:Node,Instruct_Set:list,function_dic:dict):
    if parent is not None:

        if parent.type=='F':
            ins = Instruc(None,0,[],[],[])
            if parent.label=='R':
                ins.label = 'R'
            elif parent.label=='C' or parent.label=='C_P':
                ins.label ='C'
            elif parent.label == 'Not' or parent.label == 'Not_p':
                ins.label = 'xng'
            elif parent.label == 'UOFF1' or parent.label == 'UOFF1_P':
                ins.label = 'xuoffone'
            elif parent.label == 'UOFF2' or parent.label == 'UOFF2_P':
                ins.label = 'xuofftwo'
            elif parent.label == 'UON1' or parent.label == 'UON1_P':
                ins.label = 'xuonone'
            elif parent.label == 'UON2' or parent.label == 'UON2_P':
                ins.label = 'xuontwo'
            elif parent.label == 'Mem' or parent.label == 'Mem_P':
                ins.label = 'xmem'
            elif re.match(r"P_.*",parent.label) or re.match(r"N_.*",parent.label):
                ins.label = 'Q'
            else:
                ins.label='none'
            function_dic[ins.label]+=1
            ins.index=function_dic[ins.label]
            ins.port_num=parent.max_num_of_children
            ins.value=parent.value

            for i in range(parent.max_num_of_children):
                if parent.label == 'C_P'or parent.label == 'Mem_P'or parent.label == 'Not_p' or parent.label == 'UOFF1_P' or parent.label == 'UOFF2_P' or parent.label == 'UON1_P' or parent.label == 'UON2_P':
                    ins.port_list.append(parent.port_list[(i + 1) % parent.max_num_of_children])
                elif re.match(r"._.*_1$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[0])
                    if i == 1:
                        ins.port_list.append(parent.port_list[1])
                    if i == 2:
                        ins.port_list.append(parent.port_list[2])
                elif re.match(r"._.*_2$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[2])
                    if i == 1:
                        ins.port_list.append(parent.port_list[0])
                    if i == 2:
                        ins.port_list.append(parent.port_list[1])
                elif re.match(r"._.*_3$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[1])
                    if i == 1:
                        ins.port_list.append(parent.port_list[2])
                    if i == 2:
                        ins.port_list.append(parent.port_list[0])
                elif re.match(r"._.*_4$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[0])
                    if i == 1:
                        ins.port_list.append(parent.port_list[2])
                    if i == 2:
                        ins.port_list.append(parent.port_list[1])
                elif re.match(r"._.*_5$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[2])
                    if i == 1:
                        ins.port_list.append(parent.port_list[1])
                    if i == 2:
                        ins.port_list.append(parent.port_list[0])
                elif re.match(r"._.*_6$",parent.label):
                    if i == 0:
                        ins.port_list.append(parent.port_list[1])
                    if i == 1:
                        ins.port_list.append(parent.port_list[0])
                    if i == 2:
                        ins.port_list.append(parent.port_list[2])
                else:
                    ins.port_list.append(parent.port_list[i])
            if ins.label=="xmem":
                ins.other.append(str(ins.value[1])+" "+"Rinit="+str(ins.value[0])+" ")
            elif re.match("xuo.*",ins.label):
                ins.other.append(str(ins.value[2]) + " " + "ta=" + str(ins.value[0]) + " "+ "tb=" + str(ins.value[1]))
            elif ins.label=="R":
                ins.other.append(str(ins.value))
            elif ins.label=="C":
                ins.other.append(str(ins.value)+"nf")
            else:
                ins.other.append(str(ins.value))
            if re.match("P_.*_.", parent.label):
                ins.other.append('BC856B')
            if re.match("N_.*_.", parent.label):
                ins.other.append('BC846B')


            Instruct_Set.append(ins)
            for i in range(parent.max_num_of_children):
                create_instruction_recursively(parent.children_list[i],Instruct_Set,function_dic)
        else:
            return


def print_file(filename,instruction_set,index):
    with open(filename, "w+") as f:
        f.truncate()

        fixed_content = ['guess generator', '',
                         '.MODEL BC846B NPN','+IS=1.822e-14 NF=0.9932','+ISE=2.894e-16 NE=1.4','+BF=324.4 IKF=0.109 VAF=82','+NR=0.9931 ISC=9.982e-12','+NC=1.763 BR=8.29 IKR=0.09','+VAR=17.9 RB=10 IRB=5e-06','+RBM=5 RE=0.649 RC=0.7014',
                         '+XTB=0 EG=1.11 XTI=3','+CJE=1.244e-11 VJE=0.7579','+MJE=0.3656 TF=4.908e-10','+XTF=9.51 VTF=2.927','+ITF=0.3131 PTF=0','+CJC=3.347e-12 VJC=0.5463','+MJC=0.391 XCJC=0.6193','+TR=9e-08 CJS=0 VJS=0.75','+MJS=0.333 FC=0.979',
                         '.MODEL BC856B PNP','+IS=2.014e-14 NF=0.9974','+ISE=6.578e-15 NE=1.45 BF=315.3','+IKF=0.079 VAF=39.15 NR=0.9952','+ISC=1.633e-14 NC=1.15 BR=8.68','+IKR=0.09 VAR=9.5 RB=10','+IRB=5e-06 RBM=5 RE=0.663','+RC=0.718 XTB=0 EG=1.11 XTI=3',
                         '+CJE=1.135e-11 VJE=0.7071','+MJE=0.3808 TF=6.546e-10','+XTF=5.387 VTF=6.245 ITF=0.2108','+PTF=0 CJC=6.395e-12 VJC=0.4951','+MJC=0.44 XCJC=0.6288 TR=5.5e-08','+CJS=0 VJS=0.75 MJS=0.333','+FC=0.9059',
                         '*embryo', '*****input***********', 'vc 1001 0 dc 5', 'rc 1001 2 1k',
                         '********output**********************', 'rl 3 0 10k','vtemp 3 333 dc 0',
                         '*******generate circuit*****************']

        instruct_content = []
        for j in range(len(instruction_set)):
            temp_str = ""
            temp_str += instruction_set[j].label + str(instruction_set[j].index) + "  "
            for k in range(len(instruction_set[j].port_list)):
                temp_str += str(instruction_set[j].port_list[k]) + " "
            for k in range(len(instruction_set[j].other)):
                temp_str += instruction_set[j].other[k] + " "
            instruct_content.append(temp_str)
        other_content = ['.save time', '.save v(1)', '.save v(2)', '.save v(3)', '.save @vc[i]', '.save @vtemp[i]',
                         '*control output', '.control',
                         'run', 'op', 'dc vc 4 6 0.1 temp 0 100 25',
                         'write rawfile' + str(index) + '.raw', '.endc', '',
                         '.end']
        all = fixed_content + instruct_content + other_content
        for line in all:
            f.write(line)
            f.write('\n')
        f.close()

def cal_fitness(spicepath,filename,targetpath,tem_targetpath,circuit_area,index):
    with open(targetpath,"w+") as ft:
        ft.truncate()
    p=sp.Popen(["%s" % (spicepath), '-b','-r',tem_targetpath+str(index)+'.raw',filename])
    try:
        p.communicate(timeout=1000)
    except:
        p.kill()
        print("program run error")
        return  -99999999999999999, -99999999999999999,  -99999999999999999,  -99999999999999999
    [arrs, plots] = rawread(targetpath)  # arrs is the voltages'n'currents
    if np.where(arrs!=0)[0].shape[0]==0:
        p.kill()
        print("shape[0]==0")
        return  -99999999999999999,  -99999999999999999,  -99999999999999999,  -99999999999999999
    elif arrs.shape[0]<6:
        p.kill()
        print("shape[0]<6")
        return  -99999999999999999,  -99999999999999999,  -99999999999999999,  -99999999999999999
    else:

        v_in=arrs[3]

        i_in=arrs[1]

        v_out=arrs[5]

        i_out = arrs[2]


        v_ref =np.load('ref.npy')


        if len(v_out)!=len(v_ref):
            return -99999999999999999,  -99999999999999999,  -99999999999999999,  -99999999999999999

        deta_t = 1/ len(i_out)

        power_in = abs(np.sum(abs(v_in * i_in)) * deta_t)
 
        power_out = abs(np.sum(abs(v_out * i_out)) * deta_t)


        #output error
        error_a=np.zeros(len(v_out))
        for i in range(0,len(v_out)):
            if np.abs(v_out[i]-v_ref[i])>=0.01:
                error_a[i]=pow(v_out[i]-v_ref[i],2)
            else:
                error_a[i]=0.0
        error_a = np.sum(error_a)

        # power error

        power_use = abs(power_out - power_in)
        power_use=power_use
        error_b=power_use*1e8
        if np.all( np.all(abs(v_in) == 0.00)) or np.all( np.all(abs(v_out) == 0.00)):
            print("v==0")
            return -99999999999999999,  -99999999999999999,  -99999999999999999,  -99999999999999999
        #size error
        error_c=circuit_area/2000000.0

        fitness = -error_a
        # fitness = -100 * ( error_a )
        p.kill()
    return fitness,error_a,error_b,error_c

def value_element_index(root:Node,index:[]):
    if root != None:
        if root.type == 'T':
            return
        else:
            if root.label == 'R':
                index.append(root.index_id)
            elif root.label == 'C' or root.label == 'C_P':
                index.append(root.index_id)
            elif root.label == 'Mem' or root.label == 'Mem_P':
                index.append(root.index_id)
            for i in range(root.max_num_of_children):
                value_element_index(root.children_list[i],index)


def ref_create(t,vin):
    x = []
    y = []
    vref = np.zeros((1000))
    fisrt = False
    starti = 0
    endi = 0
    for i in range(0, 1000):
        if vin[i] == 0:
            vref[i] = 0
        if vin[i] == 0 and fisrt == True:
            fisrt = False

            x.append(t[i])
            y.append(5)
            x.append(2 * x[0] - x[1])
            y.append(5)
            f1 = np.polyfit(x, y, 3)
            p = np.poly1d(f1)
            x.clear()
            y.clear()
            endi = i
            for j in range(starti, endi):
                vref[j] = p(t[j])
        if vin[i] != 0 and fisrt == False:
            fisrt = True
            x.append(t[i])
            y.append(2.5)
            starti = i
    return vref
def cal_fitness_main(population,index):
    instruction_set = create_instruction(population)
    print_file(filename+str(index)+'.cir', instruction_set,index)

    circuit_area = float(population.area)
    population.fitness, population.error_a,population.error_b, population.error_c= cal_fitness(spicepath, filename+str(index)+'.cir', targetpath+str(index)+'.raw', tem_targetpath, circuit_area,index)