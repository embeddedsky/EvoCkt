# -*- coding:utf-8 -*-
import random
from copy import deepcopy
from GP.Utilities.SubTree import SubTree
from GP.Utilities.SubNode import SubNode
from GP.HyperParameters import HyperParameters as hp

from GP.GPrint import *


class GP:
    def __init__(self, depth_range: tuple, function_set: list,R_Set:list,C_Set:list,Not_Set:list,unitoff1_set:list,unitoff2_set:list,uniton1_set:list,uniton2_set:list,M_Set:list,P_Set:list,N_Set:list, root_function_set:list,terminal_set: list, population_size: int,
                 tournament_size: int,
                 mutation_methods: list, mutation_rate: float,value_cross_rate:float,cross_rate:float, elitism: bool,sub_tree_set:list):
        """
        :param depth_range: specifies a max depth range for initializing population and controlling depths surpass
        :param function_set: is a list of tuples which hold pairs of [(label , number_of_children)]
        :param terminal_set: is a list of terminal labels like ["X" , "Y" , "Z"]
        :param population_size: size of the population
        :param tournament_size: size of the tournament used for selection
        :param mutation_methods: a list of strings containing different types of mutation methods
        :param mutation_rate: chance of each newly born child in new population which can mutate
        :param elitism: a boolean which reserves a spot in new population for the elite member of last generation
        """

        # region Depth Range
        if depth_range[0] > depth_range[1]:
            raise Exception("Invalid Depth Range, First Value Must Be Smaller Than Second")
        elif depth_range[0] < 2:
            raise Exception("Invalid Depth Range, Minimum Depth is 2")
        else:
            self.depth_range: tuple = depth_range
            self.min_depth = self.depth_range[0]
            self.max_depth = self.depth_range[1]
        # endregion

        # region Population
        self.population: list = []  # list of trees as individuals

        if population_size < 2:
            raise Exception("population size must be greater or equal to 2")
        else:
            self.population_size: int = population_size
        # endregion

        #  region Functions and Terminals
        self.function_set: list = function_set
        self.R_Set=R_Set
        self.C_Set:list=C_Set
        self.Not_Set=Not_Set
        self.unitoff1_set=unitoff1_set
        self.unitoff2_set=unitoff2_set
        self.uniton1_set=uniton1_set
        self.uniton2_set=uniton2_set
        self.M_Set=M_Set
        self.P_Set:list=P_Set
        self.N_Set:list=N_Set
        self.root_function_set:list=root_function_set
        self.terminal_set: list = terminal_set

        #  endregion

        # region Selection
        self.tournament_size: int = tournament_size
        self.elitism: bool = elitism
        #  endregion

        #  region Mutation
        self.mutation_algorithms: list = mutation_methods
        self.mutation_rate: float = mutation_rate
        self.value_cross_rate:float=value_cross_rate
        self.cross_rate:float=cross_rate
        #  endregion

        # region Generation
        self.generation = 0
        # endregion
        self.sub_tree_set=sub_tree_set
    """ public functions """

    def initialize_population(self, initialization_method: str, shuffle: bool = False):
        if initialization_method is "grow":
            for i in range(self.population_size):
                rand_depth = random.randrange(self.depth_range[0], self.depth_range[1] + 1)
                temp_tree = Tree(rand_depth, self.function_set, self.R_Set,self.C_Set,self.Not_Set,self.unitoff1_set,self.unitoff2_set,self.uniton1_set,self.uniton2_set,self.M_Set,self.P_Set,self.N_Set,self.root_function_set,self.terminal_set,None,self.max_depth,self.sub_tree_set)
                temp_tree.populate_random_tree("grow")
                #temp_tree.adjust_depth_terminal()
                print("initial",i,"th tree：")
                temp_tree.print_tree()
                self.population.append(temp_tree)
        else:
            raise Exception("Invalid Algorithm for initializing population")
        if shuffle:
            random.shuffle(self.population)
    def mutate_all(self,new_population,mutation_algorithm):
        self.mutation_algorithms =mutation_algorithm
        temp_new = deepcopy(new_population)
        temp_new = self.mutate(temp_new)
        temp_new.update_tree()
        temp_new.terminal_node_num = 0
        temp_new.count_terminal_node(temp_new.root)
        while temp_new.terminal_node_num < 4:
            temp_new = deepcopy(new_population)
            temp_new.update_tree()
            temp_new = self.mutate(temp_new)
            temp_new.update_tree()
            temp_new.terminal_node_num = 0
            temp_new.count_terminal_node(temp_new.root)

        temp_new.update_tree()
        temp_new.adjust_depth_terminal()
        temp_new.update_tree()
        return  temp_new
    def cross_all(self,new_population,mutation_algorithm):
        self.mutation_algorithms = mutation_algorithm
        if random.random() < self.cross_rate:
            parent_1, parent_2 = self.__tournament_selection()
            temp_1 = deepcopy(parent_1)
            temp_2 = deepcopy(parent_2)

            new_population = self.__cross_over(temp_1, temp_2)
            new_population.update_tree()

            new_population.terminal_node_num = 0
            new_population.count_terminal_node(new_population.root)

            while new_population.terminal_node_num < 4:
                temp_1 = deepcopy(parent_1)
                temp_2 = deepcopy(parent_2)

                new_population = self.__cross_over(temp_1, temp_2)
                new_population.update_tree()
                new_population.terminal_node_num = 0
                new_population.count_terminal_node(new_population.root)

            new_population.update_tree()
            new_population.adjust_depth_terminal()
            new_population.update_tree()

        parent_1, parent_2 = self.__tournament_selection()
        temp_1 = deepcopy(parent_1)
        temp_2 = deepcopy(new_population)

        if random.random() < self.value_cross_rate:
            if len(temp_1.all_R) != 0 and len(temp_2.all_R) != 0:
                for node in temp_2.all_R:
                    index = random.randrange(0, len(temp_1.all_R), 1)
                    node.value_tree = self.__value_cross_over(node.value_tree, temp_1.all_R[index].value_tree)
            temp_2.update_value(temp_2.root)
            new_population = deepcopy(temp_2)

        if random.random() < self.mutation_rate:
            temp_new = deepcopy(new_population)
            self.mutate(temp_new)
            temp_new.update_tree()
            temp_new.terminal_node_num = 0
            temp_new.count_terminal_node(temp_new.root)

            while temp_new.terminal_node_num < 4:
                temp_new = deepcopy(new_population)
                temp_new.update_tree()
                self.mutate(temp_new)
                temp_new.update_tree()
                temp_new.terminal_node_num = 0
                temp_new.count_terminal_node(temp_new.root)

            temp_new.update_tree()
            temp_new.adjust_depth_terminal()
            temp_new.update_tree()
            new_population = deepcopy(temp_new)
        return new_population
    def evolve(self,iterate):
        # creating new population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        new_population=deepcopy(self.population)
        # region elitism handing
        start_index = 0
        if self.elitism:
            start_index = 1
            new_population[0] = deepcopy(max(self.population, key=lambda x: x.fitness))
        mutate_num = 0
        if iterate<500:
            mutate_num=int(0.3*self.population_size)
        else:
            mutate_num=int(0.1*self.population_size)

        results=[]
        pool = ThreadPool(processes=core)
        mutation_algorithm=["another"]
        for i in range(self.population_size-mutate_num,self.population_size):
            results.append(pool.apply_async(self.mutate_all, (new_population[i], mutation_algorithm)))
        pool.close()
        pool.join()
        for i in range(self.population_size - mutate_num, self.population_size):
            new_population[i] =deepcopy(results[i-(self.population_size - mutate_num)].get())
        results.clear()

        pool = ThreadPool(processes=core)
        for i in range(self.population_size - mutate_num, self.population_size):
            pool.apply_async(cal_fitness_main,(new_population[i], i))
        pool.close()
        pool.join()


        self.population=deepcopy(new_population)

        mutation_algorithm = ["delete","add"]
        results = []
        pool = ThreadPool(processes=core)
        for i in range(start_index, self.population_size):
            results.append(pool.apply_async(self.cross_all, (new_population[i], mutation_algorithm)))
        pool.close()
        pool.join()
        for i in range(start_index, self.population_size):
            new_population[i]=deepcopy(results[i-start_index].get())
        results.clear()

        pool = ThreadPool(processes=core)
        for i in range(start_index, self.population_size):
            pool.apply_async(cal_fitness_main, (new_population[i], i))

        pool.close()
        pool.join()

        self.population = deepcopy(new_population)
        print("适应度")
        for i in range(0,self.population_size):
            print(self.population[i].fitness)
        self.generation += 1

    def evolve_local(self):
        # creating new population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        new_population=deepcopy(self.population)
        # region elitism handing
        start_index = 0
        if self.elitism:
            start_index = 1
            new_population[0] = deepcopy(max(self.population, key=lambda x: x.fitness))

        for i in range(start_index, self.population_size):
            temp_new = deepcopy(new_population[i])
            temp_new=self.mutate(temp_new)
            temp_new.update_tree()
            temp_new.terminal_node_num = 0
            temp_new.count_terminal_node(temp_new.root)

            while temp_new.terminal_node_num <4:
                temp_new = deepcopy(new_population[i])
                temp_new.update_tree()
                temp_new = self.mutate(temp_new)
                temp_new.update_tree()
                temp_new.terminal_node_num = 0
                temp_new.count_terminal_node(temp_new.root)
            temp_new.update_tree()
            temp_new.adjust_depth_terminal()
            temp_new.update_tree()
            new_population[i] = deepcopy(temp_new)

        self.population = deepcopy(new_population)
        self.generation += 1
    def mutate(self, parent: Tree):
        if (self.mutation_algorithms is None) or (self.mutation_algorithms is []):
            return


        rand_mutation_method: str = self.mutation_algorithms[random.randrange(0, self.mutation_algorithms.__len__())]

        # todo not sure about correct names for these types of mutations
        if rand_mutation_method is "delete"and parent.depth>3:  # delete children underneath and attach random terminals to it
            self.__mutate_delete(parent)
        elif rand_mutation_method is "add":  # adds a whole new tree as one of its children
            self.__mutate_add(parent)
        elif rand_mutation_method is "change_value":  # adds a whole new tree as one of its children
           parent.change_value(parent.root)
        elif rand_mutation_method is "exchange":  # change the type (function to terminal and otherwise)
            pass  # todo implement this
        elif rand_mutation_method is "swap":
            self._mutate_swap(parent)
        elif rand_mutation_method is "another":
            temp_tree=self.__mutate_another()
            parent = deepcopy(temp_tree)
        else:
           return parent
        return   parent
        #parent.is_mutated = True

    """ private Functions """

    def __tournament_selection(self):
        temp_tournament: list = []

        while len(temp_tournament) is not self.tournament_size:
            rand_index = random.randrange(0, self.population_size)

            temp_tree: Tree = self.population[rand_index]
            if temp_tree not in temp_tournament:
                temp_tournament.append(deepcopy(temp_tree))

        temp_tournament = sorted(temp_tournament, key=lambda x: x.fitness, reverse=True)

        return deepcopy(temp_tournament[0]),deepcopy(temp_tournament[1])
    def __value_cross_over(self, parent_1: SubTree, parent_2: SubTree) -> SubTree:
        parent_1.update_tree()
        parent_2.update_tree()
        if (parent_2.get_random_node() == None):
            return
        temp_node = parent_2.get_random_node().copy()
        parent_1.select_random_node_and_replace(temp_node)

        return parent_1

    def __cross_over(self, parent_1: Tree, parent_2: Tree) -> Tree:
        # getting a random node from parent_2
        parent_1.update_tree()
        parent_2.update_tree()
        if (parent_2.get_random_node() == None):
            return
        temp_node = parent_2.get_random_node().copy()

        # region generating a index range for parent_1
        depth_min_range = hp.GP.cross_over_min_range
        depth_max_range = int(hp.GP.cross_over_min_range_multiplier * parent_1.number_of_nodes_in_tree)
        if depth_min_range >= depth_max_range:
            raise Exception("Invalid Range for crossover replacement : (", depth_min_range, " , ", depth_max_range, ")")

        if depth_max_range is 1:
            depth_max_range += 1
        depth_range = (depth_min_range, depth_max_range)
        # endregion

        parent_1.select_random_node_and_replace(depth_range, temp_node)
        # update and reshape the tree if needed

        # if parent_1.depth > self.max_depth:
        #     parent_1.reshape_max_depth(self.max_depth)
        return parent_1

    def __mutate_delete(self, parent: Tree):
        rand_node_index = random.randrange(1, parent.number_of_nodes_in_tree)
        temp_node: Node = parent.get_node(rand_node_index)
        while temp_node.type is "T":
            rand_node_index = random.randrange(1, len(parent.all_functions))
            temp_node = parent.get_node(rand_node_index)

        terminal_temp=Node(None, 0, "T", temp_node.port_list[0], None, -1)
        parent._replace_node(rand_node_index,parent.root,terminal_temp)
        if temp_node is None:
            raise Exception("Invalid Node Index")

    def __mutate_another(self):
        rand_depth = random.randrange(self.depth_range[0], self.depth_range[1] + 1)
        temp_tree = Tree(rand_depth, self.function_set, self.R_Set, self.C_Set, self.Not_Set, self.unitoff1_set,self.unitoff2_set,self.uniton1_set,self.uniton2_set,self.M_Set, self.P_Set,
                         self.N_Set,
                         self.root_function_set, self.terminal_set, None, self.max_depth,self.sub_tree_set)
        temp_tree.populate_random_tree("grow")
        return temp_tree

    def __mutate_change(self, parent: Tree):

        rand_node_index = random.randrange(0,int(len(parent.all_functions)))
        rand_node_index=parent.all_functions[rand_node_index].index_id
        temp_node: Node = parent.get_node(rand_node_index)
        while temp_node.type is "T" :
            rand_node_index = random.randrange(0, len(parent.all_functions))
            temp_node: Node = parent.get_node(rand_node_index)
        final_depth =parent.depth-temp_node.level

        if final_depth<2:
            return parent
        temp_tree = Tree(final_depth, self.function_set,self.R_Set,self.C_Set,self.Not_Set,self.unitoff1_set,self.unitoff2_set,self.uniton1_set,self.uniton2_set,self.M_Set,self.P_Set,self.N_Set, self.root_function_set,self.terminal_set,None,final_depth,self.sub_tree_set)
        temp_tree.populate_random_tree2("grow")
        temp_node.children_list[random.randrange(0, temp_node.max_num_of_children)] = deepcopy(temp_tree.root)

        return parent
    def    __mutate_add(self, parent: Tree):
        rand_node_index = random.randrange(0,len(parent.all_functions))
        temp_node: Node = parent.get_node(rand_node_index)
        while temp_node.type is "T" :
            rand_node_index = random.randrange(0, len(parent.all_functions))
            temp_node: Node = parent.get_node(rand_node_index)
        final_depth =parent.max_depth-temp_node.level

        if final_depth<2:
            return parent
        rand_depth = random.randrange(2, final_depth + 1)
        temp_tree = Tree(rand_depth, self.function_set,self.R_Set,self.C_Set,self.Not_Set,self.unitoff1_set,self.unitoff2_set,self.uniton1_set,self.uniton2_set,self.M_Set,self.P_Set,self.N_Set, self.root_function_set,self.terminal_set,None,rand_depth,self.sub_tree_set)
        temp_tree.populate_random_tree2("grow")
        temp_node.children_list[random.randrange(0, temp_node.max_num_of_children)] = temp_tree.root


    def _mutate_swap(self,parent:Tree):
        rand_node_index= random.randrange(1, parent.number_of_nodes_in_tree)
        node1: Node = parent.get_node(rand_node_index)
        rand_node_index = random.randrange(1, parent.number_of_nodes_in_tree)
        node2: Node = parent.get_node(rand_node_index)
        while node2==node1:
            rand_node_index = random.randrange(1, parent.number_of_nodes_in_tree)
            node2: Node = parent.get_node(rand_node_index)
        temp_type=node1.type
        temp_lable=node1.label
        temp_max_num=node1.max_num_of_children
        temp_value=node1.value
        temp_child=[]
        for i in range(temp_max_num):
            temp_child.append(node1.children_list[i])
        #node1
        node1.type=node2.type
        node1.label=node2.label
        node1.value=node2.value
        node1.max_num_of_children=node2.max_num_of_children
        node1.children_list.clear()
        if node1.max_num_of_children!=0:
            for i in range(node1.max_num_of_children):
                node1.children_list.append(node2.children_list[i])
        #node2
        node2.type =temp_type
        node2.label = temp_lable
        node2.value=temp_value
        node2.max_num_of_children = temp_max_num
        node2.children_list.clear()
        if node2.max_num_of_children!=0:
            for i in range(node2.max_num_of_children):
                node2.children_list.append(temp_child[i])

    def __mutate_exchange(self, parent: Tree):
        pass


