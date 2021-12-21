
from GP.Utilities.SubNode import SubNode
from GP.HyperParameters import HyperParameters as hp
import random
import queue
from copy import deepcopy
import numpy as np
import pandas
import re

class SubTree:
    """
    this class is representing an individual
    """

    def __init__(self, function_set: list, root: SubNode = None,max_depth:int=0):
        """
        :param depth: tha maximum depth of the tree
        :param function_set: is a list of tuples which hold pairs of [(label , number_of_children)]
        :param terminal_set: is a list of terminal labels like ["left" , "right" , "stay"]
        """

        if max_depth < 2:
            raise Exception("minimum value for depth is 2")

        self.max_depth=max_depth

        self.depth = 0
        self.width = 0
        self.area=0.0

        self.all_terminals: list = []  # contains all terminals in the tree
        self.all_functions: list = []  # contains all functions in the tree
        self.all_node:list=[]
        self.functions = function_set

        self.root = root
        self.number_of_nodes_in_tree = 0

        self.current_terminal_node=0
    """public functions"""

    def generate_random_function(self) -> SubNode:
        rand_label = self.functions[random.randrange(0, len(self.functions))]
        return SubNode(None, rand_label[1], "F", rand_label[0],None, -1)




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

    def populate_random_tree(self):
        """
        this function populate our tree randomly with tow different methods
        :param method: "full" a full tree which has (2^depth)-1 nodes , "grow" which is a randomly positioned tree
        :return:
        """
        if self.max_depth < 2:
            raise Exception("minimum depth for creating tree is 2")

        else:
            if self.root is None:
                self.root = self.generate_random_function()
            self.__populate_grow_tree(self.root, 1)
        self.update_tree()
        self.cal_value(self.root)

    def update_tree(self):
        """
        this function will zero out all properties and recalculates them
        :return:
        """
        self.number_of_nodes_in_tree = 0
        self.depth = 0
        self.width = 0
        self.update_nodes()
        self.__update_index_ids()  # update indexes level-order
        self.calculate_width()
        self.calculate_depth()



    def get_random_node(self) -> SubNode:
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
                    print("no find")
                    break
                while q.qsize() > 0:
                    temp_node: SubNode = q.get()
                    if temp_node.index_id ==rnd_num:
                        return temp_node

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])
        else:
            return None





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

    def get_node(self, level_order_index_id: int) -> SubNode:
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
                    temp_node: SubNode = q.get()
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
        self.all_node.clear()
        self.root.parent = None
        self.__update_nodes_recursively(self.root, 1)

    """ private functions """
    def count_terminal_node(self,parent_node:SubNode):
        if parent_node is not None:
            if parent_node.type=='T':
                self.terminal_node_num+=1
            for i in range(parent_node.max_num_of_children):
            # add a function
                self.count_terminal_node(parent_node.children_list[i])
    def __populate_grow_tree(self, parent_node: SubNode, current_depth: int):
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
                #子树终端值
                value=random.uniform(-1.0,1.0)
                parent_node.children_list[i] = SubNode(None, 0, "T", value,value)
        else:
            for i in range(parent_node.max_num_of_children):
                # add a function
                if random.random() < hp.Tree.populate_grow_probability:
                    parent_node.children_list[i] = self.generate_random_function()
                    self.__populate_grow_tree(parent_node.children_list[i], current_depth + 1)
                else:
                    # 子树终端值
                    value = random.uniform(-1.0, 1.0)
                    parent_node.children_list[i]=SubNode(None, 0, "T", value,value)



    def get_value(self,root:SubNode,R_value_record:list,C_value_record:list):
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
    def change_value(self,root:SubNode):
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
                    temp_node: SubNode = q.get()
                    temp_node.index_id = inc
                    self.number_of_nodes_in_tree += 1
                    inc += 1

                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q.put(temp_node.children_list[i])

    def __calculate_width(self, node: SubNode, widths: list, current_level: int):
        if node is not None:
            for i in range(node.max_num_of_children):
                widths[current_level] += 1
                self.__calculate_width(node.children_list[i], widths, current_level + 1)

    def __reshape_depth(self, parent_node: SubNode, current_depth: int, new_depth: int):
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

    def __find_node(self, node_index: int, current_node: SubNode):
        if current_node is None:
            return
        else:
            for i in range(current_node.max_num_of_children):
                if current_node.children_list[i].index_id is node_index:
                    return  current_node.children_list[i]
                else:
                    self.__replace_node(node_index, current_node.children_list[i])

    def _replace_node(self, node_index: int, current_node: SubNode, new_node: SubNode):
        if current_node is None:
            return
        else:
            for i in range(current_node.max_num_of_children):
                if current_node.children_list[i].index_id == node_index:
                    current_node.children_list[i] = deepcopy(new_node)
                    return current_node.children_list[i]
                else:
                    self._replace_node(node_index, current_node.children_list[i],new_node)
    def __update_nodes_recursively(self, parent_node: SubNode, current_depth: int):

        if parent_node is not None:

            if parent_node.type is "F":
                self.all_functions.append(parent_node)
            else:
                self.all_terminals.append(parent_node)
            self.all_node.append(parent_node)
            parent_node.level = current_depth
            if parent_node.max_num_of_children!=0:
                for i in range(parent_node.max_num_of_children):
                    parent_node.children_list[i].parent = parent_node
                    self.__update_nodes_recursively(parent_node.children_list[i], current_depth + 1)

#左孩子的最左，右孩子的最左，端口赋值
    def init_port_list(self,parent:SubNode):
        if parent is not None:
            if parent.type=='T':
                parent.port_list.clear()
            else:
                for i in range(parent.max_num_of_children):
                    parent.port_list.clear()
                    self.init_port_list(parent.children_list[i])
    def left_left(self,parent:SubNode):
        if parent is not None:
            if parent.type=='F' :
                for i in range(parent.max_num_of_children):
                        self.left_left(parent.children_list[i])
                        if parent.children_list[i].type=='T':
                            parent.port_list.append(parent.children_list[i].label)
                        else:
                            parent.port_list.append(parent.children_list[i].port_list[0])

    def print_tree(self) -> str:
        if self.root is not None:
            q_parent = queue.Queue()
            q_son = queue.Queue()
            q_parent.put(self.root)
            while True:
                if q_parent.empty():
                    break
                while q_parent.qsize() > 0:
                    temp_node: SubNode = q_parent.get()
                    print(temp_node.label,"("+str(temp_node.value)+")",end='  ')
                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q_son.put(temp_node.children_list[i])
                print("\n",end='')
                while q_son.qsize() > 0:
                    temp_node: SubNode = q_son.get()
                    print(temp_node.label,"("+str(temp_node.value)+")",end='  ')
                    if temp_node.children_list is not None:
                        for i in range(len(temp_node.children_list)):
                            q_parent.put(temp_node.children_list[i])
                print("\n",end='')
        else:
            return
    def cal_value(self,root):
        if root==None:
            return
        elif root.type=="T":
            return
        else:
            for i in range(0,root.max_num_of_children):
                self.cal_value(root.children_list[i])
            if root.label=="+":
                root.value =float(root.children_list[0].value+root.children_list[1].value)
            elif root.label=='-':
                root.value =float( root.children_list[0].value -root.children_list[1].value)
            elif root.label=='*':
                root.value = float(root.children_list[0].value * root.children_list[1].value)
            elif root.label=="/":
                root.value = float(root.children_list[0].value/ root.children_list[1].value)
    def select_random_node_and_replace(self, node: SubNode):
        """
        this function replaces a node with a randomly selected node
        :param rand_range: specifies the range of random number which can be from (0 to number_of_nodes_in_tree)
        :param node: the new Node to be replaced with old selected Node
        :return:
        """
        if len(self.all_functions)<=1:
            return
        rnd_num = random.randrange(1, len(self.all_functions), 1)

        rnd_num = self.all_functions[rnd_num].index_id
        #old_node=self.__find_node(rnd_num,self.root)
        #self.update_terminal_count(old_node,'CUT')
        self._replace_node(rnd_num, self.root, node)
        #self.update_terminal_count(node,'ADD')

