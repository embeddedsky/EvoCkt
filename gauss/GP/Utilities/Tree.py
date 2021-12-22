from GP.Utilities.Node import Node
from GP.Utilities.SubTree import SubTree
from GP.Utilities.SubNode import SubNode
from GP.HyperParameters import HyperParameters as hp
import random
import queue
from copy import deepcopy
import numpy as np
import pandas
import re

class Tree:
    """
    this class is representing an individual
    """

    def __init__(self, depth: int, function_set: list,R_Set:list,C_Set:list,Not_Set:list,unitoff1_set:list,unitoff2_set:list,uniton1_set:list,uniton2_set:list,M_Set:list,P_Set:list,N_Set:list,root_functions:list, terminal_set: list, root: Node,max_depth:int,sub_tree_functions:list):
        """
        :param depth: tha maximum depth of the tree
        :param function_set: is a list of tuples which hold pairs of [(label , number_of_children)]
        :param terminal_set: is a list of terminal labels like ["left" , "right" , "stay"]
        """

        if depth < 2:
            raise Exception("minimum value for depth is 2")
        self.depth = depth
        self.width = 0
        self.area=0.0
        self.terminal_set = terminal_set
        self.terminal_count_set = [0] * len(self.terminal_set)


        self.all_terminals: list = []  # contains all terminals in the tree
        self.all_functions: list = []  # contains all functions in the tree
        self.all_Node:list=[]
        self.all_R: list = []  # contains all functions in the tree
        self.all_Mem:list=[]
        self.all_UOFF1:list=[]
        self.all_UOFF2:list=[]
        self.all_UON1:list=[]
        self.all_UON2:list=[]
        self.functions = function_set
        self.R_Set=R_Set
        self.C_Set=C_Set
        self.Not_Set=Not_Set
        self.unitoff1_set = unitoff1_set
        self.unitoff2_set = unitoff2_set
        self.uniton1_set = uniton1_set
        self.uniton2_set = uniton2_set
        self.M_Set=M_Set
        self.P_Set=P_Set
        self.N_Set=N_Set
        self.root_functions=root_functions
        self.root = root
        self.number_of_nodes_in_tree = 0
        self.fitness: float = 0.0
        self.error_a: float = 0.0
        self.error_b: float = 0.0
        self.error_c: float = 0.0
        #self.is_answer: bool = False
       # self.is_mutated: bool = False
        self.c_num_1=False
        self.terminal_node_num=0

        self.max_depth=max_depth
        self.is_right=False
        """"  private vars """
        # this list keeps track of random terminal and makes sure that all terminals are included at the beginning
        # because of randomness effect , we can miss a terminal , so we should keep an eye on non-included terminals
        self.__temp_terminals: list = []  # todo might break at some situations, find and fix them
        self.only_has_one:list=[]
        self.only_has_one_pos:list=[]

        self.current_terminal_node=0

        self.sub_tree_function=sub_tree_functions

    """public functions"""

    def generate_random_function(self) -> Node:
        """
        this function generates a random node with type of "F" and a random label from self.functions
        :return: a randomly generated function node with empty children_list
        """
        # rand_label is a tuple (node_label , number_of_children)
        rand_label = self.functions[random.randrange(0, len(self.functions))]
        if rand_label[0]=='C':
            rand_label = self.C_Set[random.randrange(0, len(self.C_Set))]
        if rand_label[0]=='P':
            rand_label = self.P_Set[random.randrange(0, len(self.P_Set))]
        if rand_label[0]=='Not':
            rand_label = self.Not_Set[random.randrange(0, len(self.Not_Set))]
        if rand_label[0]=='UOFF1':
            rand_label = self.unitoff1_set[random.randrange(0, len(self.unitoff1_set))]
        if rand_label[0]=='UOFF2':
            rand_label = self.unitoff2_set[random.randrange(0, len(self.unitoff2_set))]
        if rand_label[0]=='UON1':
            rand_label = self.uniton1_set[random.randrange(0, len(self.uniton1_set))]
        if rand_label[0]=='UON2':
            rand_label = self.uniton2_set[random.randrange(0, len(self.uniton2_set))]
        if rand_label[0]=='Mem':
            rand_label = self.M_Set[random.randrange(0, len(self.M_Set))]
        if rand_label[0]=='N':
            rand_label = self.N_Set[random.randrange(0, len(self.N_Set))]
        if rand_label[0]=='R':
            value_tree=SubTree(self.sub_tree_function,None,7)
            value_tree.populate_random_tree()

            value=value_tree.root.value
            value=pow(10,value)*10000
            if value < 1000:
                value = 1000
            if value > 2000000:
                value = 2000000
            # value=random.randint(rand_label[2][0],rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0],value, -1,None,value_tree)
        elif  rand_label[0] == 'C' or rand_label[0] == 'C_P':
            value = random.randint(rand_label[2][0], rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0], value, -1)
        elif  rand_label[0]=='Mem' or  rand_label[0]=='Mem_P':
            value = random.choice(rand_label[2][0])
            temp_value:tuple=(value,rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0], temp_value, -1)
        elif  re.match("UO.*",rand_label[0]):
            value_b = random.uniform(rand_label[2][0][0],rand_label[2][0][1])
            value_a=value_b+random.random()*(rand_label[2][1][1]-value_b)
            if value_a>rand_label[2][1][1]:
                value_a=rand_label[2][1][1]
            if value_a<value_b:
                raise Exception("valuea larger than valueb")
            temp_value:tuple=(value_a,value_b,rand_label[2][2])
            return Node(None, rand_label[1], "F", rand_label[0], temp_value, -1)
        else:
            return Node(None, rand_label[1], "F", rand_label[0], rand_label[2], -1)

    def generate_random_root_function(self) -> Node:
        """
        this function generates a random node with type of "F" and a random label from self.functions
        :return: a randomly generated function node with empty children_list
        """
        # rand_label is a tuple (node_label , number_of_children)
        rand_label = self.root_functions[random.randrange(0, len(self.root_functions))]
        if rand_label[0]=='C':
            rand_label = self.C_Set[random.randrange(0, len(self.C_Set))]
        if rand_label[0]=='P':
            rand_label = self.P_Set[random.randrange(0, len(self.P_Set))]
        if rand_label[0]=='Not':
            rand_label = self.Not_Set[random.randrange(0, len(self.Not_Set))]
        if rand_label[0]=='UOFF1':
            rand_label = self.unitoff1_set[random.randrange(0, len(self.unitoff1_set))]
        if rand_label[0]=='UOFF2':
            rand_label = self.unitoff2_set[random.randrange(0, len(self.unitoff2_set))]
        if rand_label[0]=='UON1':
            rand_label = self.uniton1_set[random.randrange(0, len(self.uniton1_set))]
        if rand_label[0]=='UON2':
            rand_label = self.uniton2_set[random.randrange(0, len(self.uniton2_set))]
        if rand_label[0]=='Mem':
            rand_label = self.M_Set[random.randrange(0, len(self.M_Set))]
        if rand_label[0]=='N':
            rand_label = self.N_Set[random.randrange(0, len(self.N_Set))]
        if rand_label[0] == 'R' :
            value_tree = SubTree(self.sub_tree_function, None, 7)
            value_tree.populate_random_tree()

            value = value_tree.root.value
            value = pow(10, value) * 10000
            if value < 1000:
                value = 1000
            if value > 2000000:
                value = 2000000
            # value=random.randint(rand_label[2][0],rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0], value, -1, None, value_tree)
        elif  rand_label[0] == 'C' or rand_label[0] == 'C_P':
            value = random.randint(rand_label[2][0], rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0], value, -1)
        elif  rand_label[0]=='Mem' or  rand_label[0]=='Mem_P':
            # value_tree = SubTree(self.sub_tree_function, None, 7)
            # value_tree.populate_random_tree()
            #
            # value = value_tree.root.value
            # value = pow(10, value) * 10000
            # if value>199999.999:
            #     value=199999.999
            # if value<20000.000:
            #     value=20000.000
            # # value=random.randint(rand_label[2][0],rand_label[2][1])
            # temp_value: tuple = (value, rand_label[2][1])
            # return Node(None, rand_label[1], "F", rand_label[0], temp_value, -1, None, value_tree)
            value = random.choice(rand_label[2][0])
            temp_value:tuple=(value,rand_label[2][1])
            return Node(None, rand_label[1], "F", rand_label[0], temp_value, -1)
        elif  re.match("UO.*",rand_label[0]):
            value_b = random.uniform(rand_label[2][0][0],rand_label[2][0][1])
            value_a=value_b+random.random()*(rand_label[2][1][1]-value_b)
            if value_a>rand_label[2][1][1]:
                value_a=rand_label[2][1][1]
            if value_a<value_b:
                raise Exception("valuea larger than valueb")
            temp_value:tuple=(value_a,value_b,rand_label[2][2])
            return Node(None, rand_label[1], "F", rand_label[0], temp_value, -1)
        else:
            return Node(None, rand_label[1], "F", rand_label[0], rand_label[2], -1)
    def generate_power_function(self) -> Node:
        """
        this function generates a random node with type of "F" and a random label from self.functions
        :return: a randomly generated function node with empty children_list
        """
        # rand_label is a tuple (node_label , number_of_children)
        # rand_label = self.functions[random.randrange(0, len(self.functions))]
        return Node(None, 2, "F", 'Power', None, -1)
    def generate_random_terminal_value_full(self) -> Node:
        node_num=2**(self.depth-1)
        for i in range(node_num):
            if i==0:
                self.__temp_terminals.append('in')
            elif i==1:
                self.__temp_terminals.append('ou')
            else:
                self.only_has_one.clear()
                self.only_has_one_pos.clear()
                for i in range(len(self.terminal_set)):
                    if (self.terminal_set[i] not in self.in_out_gnd) and self.terminal_count_set[i] == 1:
                        self.only_has_one.append(self.terminal_set[i])
                        self.only_has_one_pos.append(i)
                if len(self.only_has_one) != 0:
                    random_pos1 = random.randrange(0, len(self.only_has_one))
                    rand_terminal = self.only_has_one[random_pos1]
                    self.terminal_count_set[self.only_has_one_pos[random_pos1]] += 1
                else:
                    random_pos2 = random.randrange(1, len(self.terminal_set))
                    rand_terminal = self.terminal_set[random_pos2]
                    self.terminal_count_set[random_pos2] += 1
                self.__temp_terminals.append(rand_terminal)

        self.only_has_one.clear()
        self.only_has_one_pos.clear()
        for i in range(len(self.terminal_set)):
            if (self.terminal_set[i] not in self.in_out_gnd) and self.terminal_count_set[i]==1:
                self.only_has_one.append(self.terminal_set[i])
                self.only_has_one_pos.append(i)
        if len(self.only_has_one)!=0:
            self.__temp_terminals[-1]= random.randrange(0, len(self.__temp_terminals))
        random.shuffle(self.__temp_terminals)


    def generate_random_terminal_value(self) -> Node:
        self.only_has_one.clear()
        self.only_has_one_pos.clear()
        if len(self.__temp_terminals)==0:
            self.__temp_terminals.append('in')
        elif len(self.__temp_terminals)==1:
            self.__temp_terminals.append('ou')
        else:
            for i in range(len(self.terminal_set)):
                if (self.terminal_set[i] not in self.in_out_gnd) and self.terminal_count_set[i]==1:
                    self.only_has_one.append(self.terminal_set[i])
                    self.only_has_one_pos.append(i)
            if len(self.only_has_one)!=0:
                random_pos1=random.randrange(0, len(self.only_has_one))
                rand_terminal = self.only_has_one[random_pos1]
                self.terminal_count_set[self.only_has_one_pos[random_pos1]]+=1
            else:
                random_pos2 = random.randrange(0, len(self.terminal_set))
                rand_terminal = self.terminal_set[random_pos2]
                self.terminal_count_set[random_pos2] += 1
            self.__temp_terminals.append(rand_terminal)

    def terminal_update(self):
        temp=[]
        for value in self.__temp_terminals:
            if value=='in' or value=='ou':
                temp.append(value)
            else:
                if self.terminal_count_set[value]!=0:
                    temp.append(value)
        self.__temp_terminals=temp



    def calculate_depth(self) -> int:
        """ calculate depth of the tree from starting at root node """
        self.depth = 0 if self.root is None else self.root.depth()
        return self.depth

    def calculate_width(self) -> int:
        """ calculates the width of each level and return the maximum one which is denoted as width of the tree"""
        __height: int = self.root.depth()  # finding how many levels we have
        __width_of_each_level: list = [0] * __height  # generating a list for holding each level's width
        self.__calculate_width(self.root, __width_of_each_level, 0)
        self.width = max(__width_of_each_level)  # selecting the maximum width for our purpose
        return self.width

    def populate_random_tree(self, method: str):
        """
        this function populate our tree randomly with tow different methods
        :param method: "full" a full tree which has (2^depth)-1 nodes , "grow" which is a randomly positioned tree
        :return:
        """
        if self.depth < 2:
            raise Exception("minimum depth for creating tree is 2")

        else:
            if self.root is None:
                self.root = self.generate_random_root_function()
            if method is "full":
                self.__populate_full_tree(self.root, 1,0)
            elif method is "grow":
                while self.terminal_node_num<=4 :
                    self.terminal_node_num=0
                    self.root = self.generate_random_root_function()
                    self.__populate_grow_tree(self.root, 1)
                    self.update_tree()
                self.__temp_terminals=self.create_terminal()
                self.current_terminal_node=0
                self.terminal_value(self.root)
                #self.left_left(self.root)
        # update information of the tree
        self.update_tree()
        self.adjust_depth_terminal()
        # self.adapt_c(self.root)
        # self.add_c()
        self.update_tree()
    def populate_random_tree2(self, method: str):
        """
                this function populate our tree randomly with tow different methods
                :param method: "full" a full tree which has (2^depth)-1 nodes , "grow" which is a randomly positioned tree
                :return:
                """
        if self.depth < 2:
            raise Exception("minimum depth for creating tree is 2")

        else:
            if self.root is None:
                self.root = self.generate_random_root_function()
            if method is "full":
                self.__populate_full_tree(self.root, 1, 0)
            elif method is "grow":
                self.terminal_node_num = 0
                self.root = self.generate_random_root_function()
                self.__populate_grow_tree(self.root, 1)
                self.update_tree()

                self.__temp_terminals = self.create_terminal()
                self.current_terminal_node = 0
                self.terminal_value(self.root)
        self.update_tree()

    def print_graph(self) -> str:
        """
        this functions generates a string which we can feed it to GraphViz Library
        to draw this tree
        :return:
        """
        if self.root is not None:
            return self.__print_graph()

    def print_tree(self) -> str:
        if self.root is not None:
            q_parent = queue.Queue()
            q_son = queue.Queue()
            q_parent.put(self.root)
            while True:
                if q_parent.empty():
                    break
                while q_parent.qsize() > 0:
                    temp_node: Node = q_parent.get()
                    print(temp_node.label,end='  ')
                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q_son.put(temp_node.children_list[i])
                print("\n",end='')
                while q_son.qsize() > 0:
                    temp_node: Node = q_son.get()
                    print(temp_node.label,end='  ')
                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q_parent.put(temp_node.children_list[i])
                print("\n",end='')
        else:
            return

    def update_tree(self):
        """
        this function will zero out all properties and recalculates them
        :return:
        """
        self.number_of_nodes_in_tree = 0
        self.depth = 0
        self.width = 0
        self.c_num_1=False
        self.update_nodes()
        self.update_value(self.root)
        self.__update_index_ids()  # update indexes level-order
        self.calculate_width()
        self.calculate_depth()

        self.init_port_list(self.root)
        self.left_left(self.root)

        self.terminal_count_set = [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)

        self.area=0.0
        for element in self.all_functions:
            if element.label =="R":
                self.all_R.append(element)
                self.area+=2025
            if re.match("._.*_.",element.label):
                self.area += 11117.25
            if element.label =="Mem" or element.label =="Mem_P":
                self.all_Mem.append(element)
                self.area += 9
            if element.label =="UOFF1" or element.label =="UOFF1_P":
                self.all_UOFF1.append(element)
            if element.label =="UOFF2" or element.label =="UOFF2_P":
                self.all_UOFF2.append(element)
            if element.label =="UON1" or element.label =="UON1_P":
                self.all_UON1.append(element)
            if element.label =="UON2" or element.label =="UON2_P":
                self.all_UON2.append(element)
            if element.label == "C" or element.label == "C_P":
                self.area += 6075
            if element.label =="Not" or element.label =="Not_p":
                self.area += 22234.5
            if element.label =="Not" or element.label =="Not_p":
                self.area += 22234.5
            if re.match("UO.*",element.label):
                self.area +=(9+11117.25*4)

    def adjust_depth_terminal(self):

        if self.depth>self.max_depth:
            self.adjust_depth(self.root)

        self.check_terminal()
    def adapt_c(self,parent:Node):
        if parent!=None:
            if parent.type=='T':
                return
            else:
                if parent.label=='C'or parent.label=='C_P':
                    if self.c_num_1==True:
                        parent.label='R'
                        value =random.randint(self.R_Set[0][2][0],self.R_Set[0][2][1])
                        parent.value=value
                    self.c_num_1 = True
                for i in range(parent.max_num_of_children):
                    self.adapt_c(parent.children_list[i])
    def check_out_0(self):
        self.is_right=False
        for element in self.all_functions:
            if element.max_num_of_children==2:
                if element.port_list[0]==0 and element.port_list[1]==4:
                    self.is_right= False
                    break
                elif  element.port_list[1]==0 and element.port_list[0]==4:
                    self.is_right = False
                    break
                else:
                    self.is_right = True
            else:
                self.is_right = True

    def add_c(self):
        if self.c_num_1==False:
            node=self.get_random_node()
            while node.label=='R':
                node = self.get_random_node()
            randindex=random.randrange(0, len(self.C_Set), 1)
            node.label =self.C_Set[randindex][0]
            value = random.randint(self.C_Set[0][2][0],self.C_Set[0][2][1])
            node.value = value





    def adjust_depth(self,current_node:Node):
        if current_node.type=='T':
            return
        else:
            for i in range(current_node.max_num_of_children):
                if current_node.children_list[i].level==self.max_depth:
                    if   current_node.children_list[i].type=='T':
                        continue
                    else:
                        value=current_node.children_list[i].port_list[0]
                        current_node.children_list[i] =deepcopy(Node(None, 0, "T", value, None, -1))
                else:
                    self.adjust_depth( current_node.children_list[i])


    def get_random_node(self) -> Node:
        """
        this function returns a random node with level-order traversal in our tree
        :return:
        """

        rnd_num = random.randrange(0, len(self.all_functions), 1)

        rnd_num=self.all_functions[rnd_num].index_id

        if self.root is not None:
            q = queue.Queue()
            q.put(self.root)

            while True:
                if q.empty():
                    print("no found")

                    break
                while q.qsize() > 0:
                    temp_node: Node = q.get()
                    if temp_node.index_id ==rnd_num:
                        return temp_node

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])
        else:
            return None

    def select_random_node_and_replace(self, rand_range: tuple, node: Node):
        """
        this function replaces a node with a randomly selected node
        :param rand_range: specifies the range of random number which can be from (0 to number_of_nodes_in_tree)
        :param node: the new Node to be replaced with old selected Node
        :return:
        """
        rnd_num = random.randrange(rand_range[0], rand_range[1], 1)
        # old_node=self.__find_node(rnd_num,self.root)
        # self.update_terminal_count(old_node,'CUT')
        self._replace_node(rnd_num, self.root, node)
        # self.update_terminal_count(node,'ADD')

    def check_not_one(self):
        self.terminal_count_set = [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)

        IS_CORRET=True

        for i in range(len(self.__temp_terminals)):
            if (self.terminal_count_set[self.__temp_terminals[i]] == 1 and
                    self.__temp_terminals[i] != 1 and
                    self.__temp_terminals[i] != 2 and
                    self.__temp_terminals[i] != 3 and
                    self.__temp_terminals[i] != 4 and
                    self.__temp_terminals[i] != 5
            ):
                IS_CORRET=False
                break
        if self.terminal_count_set[1]==0:
            IS_CORRET=False
        if self.terminal_count_set[2]==0:
            IS_CORRET=False
        if self.terminal_count_set[3]==0:
            IS_CORRET=False
        if self.terminal_count_set[4]==0:
            IS_CORRET=False
        if self.terminal_count_set[5]==0:
            IS_CORRET=False

        return IS_CORRET

    def check_terminal(self):
        self.terminal_count_set= [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)


        # ------------------0-------------------------#

        if self.terminal_count_set[0] == 0:
            not_must_pos=[]
            for i in range(0,len(self.__temp_terminals)):
                if (self.terminal_count_set[self.__temp_terminals[i]]>=2 or(
                        self.__temp_terminals[i] != 0 and
                        self.__temp_terminals[i] != 2 and
                        self.__temp_terminals[i] != 3 and
                        self.__temp_terminals[i] != 4 )
                    ):
                    not_must_pos.append(i)
            if len(not_must_pos)==0:
                self.print_tree()
                print(not_must_pos)
                print("")
            rand_index=random.randrange(0,len(not_must_pos))
            self.__temp_terminals[not_must_pos[rand_index]]=0
        self.current_terminal_node = 0
        self.terminal_value(self.root)
        self.init_port_list(self.root)
        self.left_left(self.root)
        self.update_terminal_count_set(self.root,False)
        # ------------------2-------------------------#
        self.terminal_count_set= [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)
        if self.terminal_count_set[2] == 0:
            not_must_pos = []
            for i in range(0, len(self.__temp_terminals)):
                if (self.terminal_count_set[self.__temp_terminals[i]] >= 2 or (
                        self.__temp_terminals[i] != 0 and
                        self.__temp_terminals[i] != 2 and
                        self.__temp_terminals[i] != 3 and
                        self.__temp_terminals[i] != 4 )
                ):
                    not_must_pos.append(i)
            if len(not_must_pos)==0:
                self.print_tree()
                print(not_must_pos)
                print("")
            rand_index = random.randrange(0, len(not_must_pos))
            self.__temp_terminals[not_must_pos[rand_index]] = 2
        self.current_terminal_node = 0
        self.terminal_value(self.root)
        self.init_port_list(self.root)
        self.left_left(self.root)
        self.update_terminal_count_set(self.root,False)
        # ------------------3-------------------------#
        self.terminal_count_set= [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)
        if self.terminal_count_set[3] == 0:
            not_must_pos = []
            for i in range(0, len(self.__temp_terminals)):
                if (self.terminal_count_set[self.__temp_terminals[i]] >= 2 or (
                        self.__temp_terminals[i] != 0 and
                        self.__temp_terminals[i] != 2 and
                        self.__temp_terminals[i] != 3 and
                        self.__temp_terminals[i] != 4 )
                ):
                    not_must_pos.append(i)
            if len(not_must_pos)==0:
                self.print_tree()
                print(not_must_pos)
                print("")
            rand_index = random.randrange(0, len(not_must_pos))
            self.__temp_terminals[not_must_pos[rand_index]] = 3
        self.current_terminal_node = 0
        self.terminal_value(self.root)
        self.init_port_list(self.root)
        self.left_left(self.root)
        self.update_terminal_count_set(self.root,False)
        # ------------------4-------------------------#
        self.terminal_count_set= [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,False)
        if self.terminal_count_set[4] == 0:
            not_must_pos = []
            for i in range(0, len(self.__temp_terminals)):
                if (self.terminal_count_set[self.__temp_terminals[i]] >= 2 or (
                        self.__temp_terminals[i] != 0 and
                        self.__temp_terminals[i] != 2 and
                        self.__temp_terminals[i] != 3 and
                        self.__temp_terminals[i] != 4 )
                ):
                    not_must_pos.append(i)
            if len(not_must_pos)==0:
                self.print_tree()
                print(not_must_pos)
                print("")
            rand_index = random.randrange(0, len(not_must_pos))
            self.__temp_terminals[not_must_pos[rand_index]] = 4
        self.current_terminal_node = 0
        self.terminal_value(self.root)
        self.init_port_list(self.root)
        self.left_left(self.root)
        self.update_terminal_count_set(self.root,False)

        self.terminal_count_set= [0] * len(self.terminal_set)
        self.__temp_terminals.clear()
        self.update_terminal_count_set(self.root,True)

        only_one_pos=[]
        only_one=queue.Queue()
        not_one=[]
        temp=[]
        for i in range(len(self.__temp_terminals)):
            if (self.terminal_count_set[self.__temp_terminals[i]]==1 and
                    self.__temp_terminals[i] != 0 and
                    self.__temp_terminals[i] != 2 and
                    self.__temp_terminals[i] != 3 and
                    self.__temp_terminals[i] != 4
            ) :
                only_one_pos.append(i)
            else:
                not_one.append(self.__temp_terminals[i])
        not_one=list(set(not_one))
        if len(only_one_pos)==0:
            return
        elif len(only_one_pos)==1:
            value = not_one[random.randrange(0, len(not_one))]
            temp.append(value)
        else:
            only_one.put(self.__temp_terminals[only_one_pos[0]])
            temp.append(self.__temp_terminals[only_one_pos[0]])
            for i in range(1,len(only_one_pos)):
                if only_one.empty():
                    if i==len(only_one_pos)-1:
                        temp_quchong=not_one+temp
                        temp_quchong=list(set(temp_quchong))
                        value=temp_quchong[random.randrange(0,len(temp_quchong))]
                    else:
                        only_one.put(self.__temp_terminals[only_one_pos[i]])
                        value=self.__temp_terminals[only_one_pos[i]]
                    temp.append(value)
                else:
                    value=only_one.get()
                    temp.append(value)
            random.shuffle(temp)
        for i  in range(0,len(only_one_pos)):
            self.__temp_terminals[only_one_pos[i]]=temp[i]


        self.current_terminal_node = 0
        self.terminal_value(self.root)
        self.init_port_list(self.root)
        self.left_left(self.root)
        self.update_terminal_count_set(self.root,False)




    def update_terminal_count_opt(self,parent:Node,operate:None):
        if parent is not None:
            if parent.type=='T':
                if operate =='CUT':
                    self.terminal_count_set[parent.label]-=1
                elif operate =='ADD':
                    self.terminal_count_set[parent.label]+=1
                else:
                    raise Exception('what the operation is?')
            else:
                for i in range(parent.max_num_of_children):
                    self.update_terminal_count_opt(parent.children_list[i])


    def update_terminal_set(self):
        not_one = []
        not_one_pos = []

        self.__temp_terminals.clear()
        for i in range(len(self.terminal_count_set)):
            self.terminal_count_set[i]=0
        self.only_has_one_pos.clear()
        self.only_has_one.clear()
        q= q_parent = queue.Queue()
        if self.root is None:
            raise Exception("Tree is null")
        else:
            q.put(self.root)
            while True:
                if q.empty():
                    break
                while q.qsize()>0:
                    temp_node=q.get()
                    if temp_node.max_num_of_children==0:
                        self.__temp_terminals.append(temp_node.label)
                        if temp_node.label !='in' and temp_node.label!='ou':
                            self.terminal_count_set[temp_node.label]+=1
                    else:
                        for node in temp_node.children_list:
                            q.put(node)
        for i in range(len(self.__temp_terminals)):
            if self.__temp_terminals[i]!='in' and self.__temp_terminals[i]!='ou' :
                if self.terminal_count_set[self.__temp_terminals[i]]==1:
                    self.only_has_one.append(self.__temp_terminals[i])
                    self.only_has_one_pos.append(i)
                elif self.terminal_count_set[self.__temp_terminals[i]]>1:
                    not_one.append(self.__temp_terminals[i])
                    not_one_pos.append(i)
        for i in range(len(self.only_has_one)):
                random_pos1 = random.randrange(0, len(not_one))
                self.__temp_terminals[self.only_has_one_pos[i]]=not_one[random_pos1]
                self.terminal_count_set[not_one[random_pos1]]+=1
                self.terminal_count_set[self.only_has_one[i]]-=1



    def reshape_max_depth(self, new_depth: int):
        """
        this functions can perform branch-cutting if depth of the tree goes higher than max_depth
        all depth-crossed Nodes get deleted and replaced by a terminal in last level
        :param new_depth: the new depth to reshape the tree
        :return:
        """
        self.__temp_terminals.clear()
        self.__reshape_depth(self.root, 1, new_depth)
        self.update_tree()

    def get_node(self, level_order_index_id: int) -> Node:
        """
        this function returns a node by index , it uses level-order tree traversal
        :param level_order_index_id: target index
        :return: a node with given index or None if it doesn't exist
        """

        if level_order_index_id > self.number_of_nodes_in_tree:
            raise Exception("the Index is higher than total number of nodes in the tree")

        if self.root is not None:
            q = queue.Queue()
            q.put(self.root)

            while True:

                if q.empty():
                    break

                while q.qsize() > 0:
                    temp_node: Node = q.get()
                    if temp_node.index_id == level_order_index_id:
                        return temp_node

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])
        else:
            raise Exception("Tree is not initialized for accessing a node. ** root is None **")

    def update_nodes(self):
        """
        this function updates 3 thing :
            1 => level of each node
            2 => parent of each node
            3 => list of all_terminals and all_functions
        it uses a recursive function to traverse the tree
        :return:
        """
        if self.root is None:
            raise Exception("tree is not initi alized , root node must not be None")

        self.all_terminals.clear()
        self.all_functions.clear()
        self.all_Node.clear()
        self.all_R.clear()
        self.all_Mem.clear()
        self.all_UOFF1.clear()
        self.all_UOFF2.clear()
        self.all_UON1.clear()
        self.all_UON2.clear()

        self.root.parent = None
        self.__update_nodes_recursively(self.root, 1)

    """ private functions """
    def count_terminal_node(self,parent_node:Node):
        if parent_node is not None:
            if parent_node.type=='T':
                self.terminal_node_num+=1
            for i in range(parent_node.max_num_of_children):
            # add a function
                self.count_terminal_node(parent_node.children_list[i])
    def __populate_grow_tree(self, parent_node: Node, current_depth: int):
        """
        this function decides weather add a node by 65 percent chance or not
        it perform this action recursively
        :param parent_node:
        :param current_depth:
        :return:
        """
        # add terminal for the last level

        if current_depth is self.max_depth - 1:
            for i in range(parent_node.max_num_of_children):
                self.terminal_node_num += 1
                # self.generate_random_terminal_value()
                parent_node.children_list[i] = Node(None, 0, "T", 0, None, -1)
        else:
            for i in range(parent_node.max_num_of_children):
                # add a function
                if random.random() < hp.Tree.populate_grow_probability:
                    parent_node.children_list[i] = self.generate_random_function()
                    self.__populate_grow_tree(parent_node.children_list[i], current_depth + 1)
                else:
                    self.terminal_node_num+=1
                    # self.generate_random_terminal_value()
                    parent_node.children_list[i]= Node(None, 0, "T", 0, None, -1)

    def create_terminal(self):
        temp_terminals=[]
        self.terminal_node_num=0
        self.update_terminal_node_num(self.root)

        only_one=queue.Queue()

        for i in range(0,self.terminal_node_num):
            random_value=self.terminal_set[random.randrange(0,len(self.terminal_set))]
            temp_terminals.append(random_value)
        #随机打乱
        random.shuffle(temp_terminals)
        return temp_terminals
    def create_terminal2(self):
        temp_terminals=[]
        self.terminal_node_num=0
        self.update_terminal_node_num(self.root)

        only_one=queue.Queue()

        for i in range(0,self.terminal_node_num):
            if only_one.empty():
                if i!=self.terminal_node_num-1:
                    random_value=self.terminal_set[random.randrange(0,len(self.terminal_set))]
                    only_one.put(random_value)
                else:
                    random_value = temp_terminals[random.randrange(0, len(temp_terminals))]
            else:
                random_value=only_one.get()
            temp_terminals.append(random_value)

        random.shuffle(temp_terminals)
        return temp_terminals

    def update_terminal_count_set(self,parent:Node,CalParent:bool):
        if parent!=None:
            if parent.type=='T':
                self.__temp_terminals.append(parent.label)
                if CalParent==False:
                    self.terminal_count_set[parent.label]+=1
            elif parent.type=='F':
                for i in range(parent.max_num_of_children):
                    self.update_terminal_count_set(parent.children_list[i],CalParent)
                if CalParent==True:
                    for port in parent.port_list:
                        self.terminal_count_set[port] += 1
            else:
                return

    def update_terminal_node_num(self,parent:Node):
        if parent!=None:
            if parent.type=='T':
                self.terminal_node_num+=1
            elif parent.type=='F':
                for i in range(parent.max_num_of_children):
                    self.update_terminal_node_num(parent.children_list[i])
            else:
                return


    def terminal_value(self, parent_node: Node):
        if parent_node !=None:
            if parent_node.max_num_of_children == 0:
                parent_node.label=self.__temp_terminals[self.current_terminal_node]
                self.current_terminal_node+=1
            else:
                for i in range(parent_node.max_num_of_children):
                    self.terminal_value(parent_node.children_list[i])
    def __populate_full_tree(self, parent_node: Node, current_depth: int,current_child_node:int):
        """
        this function populates a Full tree recursively
        :param parent_node:
        :param current_depth:
        :return:
        """
        # add terminal for the last level
        if current_depth is self.depth - 1:
            for i in range(parent_node.max_num_of_children):
                parent_node.children_list[i] = Node(None, 0, "T", self.__temp_terminals[current_child_node], None, -1)
                current_child_node+=1
        else:
            for i in range(parent_node.max_num_of_children):
                parent_node.children_list[i] = self.generate_random_function()
                self.__populate_grow_tree(parent_node.children_list[i], current_depth + 1)
    def __print_graph(self) -> str:
        result: str = ""
        if self.root is not None:
            q = queue.Queue()
            q.put(self.root)

            while True:
                if q.empty():
                    break
                while q.qsize() > 0:
                    temp_node: Node = q.get()

                    for i in range(len(temp_node.children_list)):
                        if temp_node.children_list[i] is None:
                            continue
                        result += '"{0}_{1}" -> "{2}_{3}";\n"{0}_{1}" [label="{4}"];\n"{2}_{3}" [label="{5}"];\n' \
                            .format(
                            temp_node.index_id, temp_node.label,
                            temp_node.children_list[i].index_id, temp_node.children_list[i].label,
                            temp_node.label,
                            temp_node.children_list[i].label
                        )
                        if temp_node.children_list[i].type is "T":
                            result += '"{0}_{1}" [shape="box"];\n' \
                                .format(
                                temp_node.children_list[i].index_id,
                                temp_node.children_list[i].label
                            )

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])
            return result

        else:
            return result

    def get_value(self,root:Node,R_value_record:list,C_value_record:list):
        if root!=None:
            if root.type=='T':
                return
            else:
                if root.label=='R':
                    R_value_record.append(root.index_id)
                elif root.label=='C' or root.label=='C_P':
                    C_value_record.append(root.index_id)
                for i in range(root.max_num_of_children):
                    self.get_value(root.children_list[i],R_value_record,C_value_record)
    def change_value(self,root:Node):
        if root!=None:
            if root.type=='T':
                return
            else:
                if root.label=='R':
                    value = random.randint(self.R_Set[0][2][0],self.R_Set[0][2][1])
                    root.value=value
                elif root.label=='C' or root.label=='C_P':
                    value = random.randint(self.C_Set[0][2][0], self.C_Set[0][2][1])
                    root.value = value
                elif root.label=='Mem' or root.label=='Mem_P':
                    value = random.choice(self.M_Set[0][2][0])
                    root_value1=root.value[1]
                    root.value=(value,root_value1)
                for i in range(root.max_num_of_children):
                    self.change_value(root.children_list[i])



    def __update_index_ids(self):
        if self.root is not None:
            inc = 0
            q = queue.Queue()
            q.put(self.root)

            while True:

                if q.empty():
                    break

                while q.qsize() > 0:
                    temp_node: Node = q.get()
                    temp_node.index_id = inc
                    self.number_of_nodes_in_tree += 1
                    inc += 1

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])

    def __calculate_width(self, node: Node, widths: list, current_level: int):
        if node is not None:
            for i in range(node.max_num_of_children):
                widths[current_level] += 1
                self.__calculate_width(node.children_list[i], widths, current_level + 1)

    def __reshape_depth(self, parent_node: Node, current_depth: int, new_depth: int):
        if (parent_node.type is "T") and (parent_node.label not in self.__temp_terminals):
            self.__temp_terminals.append(parent_node.label)

        elif current_depth is new_depth - 1:
            for i in range(parent_node.max_num_of_children):
                if parent_node.children_list[i].type is "T":
                    if parent_node.children_list[i].label in self.__temp_terminals:
                        continue
                    else:
                        self.__temp_terminals.append(parent_node.children_list[i].label)
                else:
                    parent_node.children_list[i] = self.generate_random_terminal_value()

        else:
            for node in parent_node.children_list:
                if node is not None:
                    self.__reshape_depth(node, current_depth + 1, new_depth)

    def __find_node(self, node_index: int, current_node: Node):
        if current_node is None:
            return
        else:
            for i in range(current_node.max_num_of_children):
                if current_node.children_list[i].index_id is node_index:
                    return  current_node.children_list[i]
                else:
                    self.__replace_node(node_index, current_node.children_list[i])

    def _replace_node(self, node_index: int, current_node: Node, new_node: Node):
        if current_node is None:
            return
        else:
            for i in range(current_node.max_num_of_children):
                if current_node.children_list[i].index_id == node_index:
                    current_node.children_list[i] = deepcopy(new_node)
                    return current_node.children_list[i]
                else:
                    self._replace_node(node_index, current_node.children_list[i],new_node)
    def __update_nodes_recursively(self, parent_node: Node, current_depth: int):

        if parent_node is not None:

            if parent_node.type is "F":
                self.all_functions.append(parent_node)
            else:
                self.all_terminals.append(parent_node)
            self.all_Node.append(parent_node)
            parent_node.level = current_depth
            if parent_node.max_num_of_children!=0:
                for i in range(parent_node.max_num_of_children):
                    parent_node.children_list[i].parent = parent_node
                    self.__update_nodes_recursively(parent_node.children_list[i], current_depth + 1)
    def update_value(self, parent_node: Node):
        if parent_node is not None:
            if parent_node.type is "F":
                if parent_node.label=="R":
                    parent_node.value_tree.update_tree()
                    parent_node.value_tree.cal_value( parent_node.value_tree.root)
                    parent_node.value=pow(10,parent_node.value_tree.root.value)*10000
                    if parent_node.value<1000:
                        parent_node.value=1000
                    if parent_node.value>2000000:
                        parent_node.value=2000000
                # if parent_node.label=="Mem" or parent_node.label=="Mem_P" :
                #     parent_node.value_tree.update_tree()
                #     parent_node.value_tree.cal_value( parent_node.value_tree.root)
                #     value=pow(10,parent_node.value_tree.root.value)*10000
                #     if value > 199999.999:
                #         value = 199999.999
                #     if value < 20000.000:
                #         value = 20000.000
                #     temp_value: tuple = (value, parent_node.value[1])
                #     parent_node.value=temp_value
                for i in range(parent_node.max_num_of_children):
                    self.update_value(parent_node.children_list[i])

    def init_port_list(self,parent:Node):
        if parent is not None:
            if parent.type=='T':
                parent.port_list.clear()
            else:
                for i in range(parent.max_num_of_children):
                    parent.port_list.clear()
                    self.init_port_list(parent.children_list[i])
    def left_left(self,parent:Node):
        if parent is not None:
            if parent.type=='F' :
                for i in range(parent.max_num_of_children):
                        self.left_left(parent.children_list[i])
                        if parent.children_list[i].type=='T':
                            parent.port_list.append(parent.children_list[i].label)
                        else:
                            parent.port_list.append(parent.children_list[i].port_list[0])
