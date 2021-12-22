# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
from matplotlib import pyplot
from GP.GPrint import *
from GP.GP import GP

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

def find_best_value(tree:Tree):
    current_fitness=tree.fitness
    change_value_element=[]
    value_element_index(tree.root,change_value_element)
    for i in change_value_element:
        node=tree.get_node(i)
        if node.label=='R':
            value_lin=np.linspace(tree.R_Set[0][2][0],tree.R_Set[0][2][1],50)
            best_value=node.value
            for value in value_lin:
                node.value=value
                instruction_set = create_instruction(tree)
                print_file(filename, instruction_set)

                circuit_area = float(tree.area)
                fitness, error_a, error_b, error_c = cal_fitness(spicepath, filename, targetpath, tem_targetpath,
                                                                 circuit_area)
                tree.fitness = fitness
                if fitness>current_fitness:
                    current_fitness=fitness
                    best_value=value
                    print("value local optimization：", current_fitness)
                    fitness_record[0].append(fitness)
                    fitness_record[1].append(error_a)
                    fitness_record[2].append(error_b)
                    fitness_record[3].append(error_c)
                    fit_file.writelines(
                        str(fitness) + " " + str(error_a) + " " + str(error_b) + " " + str(error_c) + "\n")
                    fit_file.flush()

            node.value=best_value

        if node.label=='C' or node.label=='C_P':
            value_lin = np.linspace(tree.C_Set[0][2][0], tree.C_Set[0][2][1],10)

            for value in value_lin:
                node.value = value
                instruction_set = create_instruction(tree)
                print_file(filename, instruction_set)

                circuit_area = float(tree.area)
                fitness, error_a, error_b, error_c = cal_fitness(spicepath, filename, targetpath, tem_targetpath,
                                                                 circuit_area)
                tree.fitness = fitness
                if fitness > current_fitness:
                    current_fitness = fitness
                    best_value = value
                    print("value optimization:", current_fitness)
                    fitness_record[0].append(fitness)
                    fitness_record[1].append(error_a)
                    fitness_record[2].append(error_b)
                    fitness_record[3].append(error_c)
                    fit_file.writelines(
                        str(fitness) + " " + str(error_a) + " " + str(error_b) + " " + str(error_c) + "\n")
                    fit_file.flush()
            node.value = best_value



fit_file=open(fitness_file,"w+")
fit_file.truncate()


for i in range(0,pop_size):
    filename1=filename+str(i)+'.cir'
    filename2=targetpath+str(i)+'.raw'
    with open(filename1, "w+") as f1:
        f1.truncate()
    with open(filename2, "w+") as f2:
        f2.truncate()

marker=['1','2','>','<','D','+','^','v','*','o']

pyplot.figure(1)

if __name__ == '__main__':
    for zhixing in range(0,1):
        best_path = 'output'+str(zhixing)+'.cir'
        gp = GP(depth_range, function_set,R_Set,C_Set,Not_Set,unitoff1_set,unitoff2_set,uniton1_set,uniton2_set,M_Set,P_Set,N_Set,root_function_set, terminal_set, pop_size, tournament_size, mutation_methods, mutation_rate,value_cross_rate, cross_rate,elitism,sub_tree_set)
        gp.initialize_population(pop_init_method,False)

        iterate=0
        fitness_record=[[],[],[],[]]

        max_fitness =  -99999999999999999
        best_error_a = -99999999999999999
        best_error_b =  -99999999999999999
        best_error_c = -99999999999999999

        pool = ThreadPool(processes=core)

        for i in range(0,gp.population_size):
            pool.apply_async(cal_fitness_main,(gp.population[i],i))

        pool.close()
        pool.join()

        while True:
            all_tree_instruction = []

            for i in range(gp.population_size):
                if gp.population[i].fitness > max_fitness:
                    max_fitness = gp.population[i].fitness
                    best_error_a = gp.population[i].error_a
                    best_error_b = gp.population[i].error_b
                    best_error_c = gp.population[i].error_c
            fitness_record[0].append(max_fitness)
            fitness_record[1].append(best_error_a)
            fitness_record[2].append(best_error_b)
            fitness_record[3].append(best_error_c)

            fit_file.writelines(str(max_fitness)+" "+str(best_error_a)+" "+str(best_error_b)+" "+str(best_error_c)+"\n")
            fit_file.flush()
            best_fitness = float("-inf")
            best_tree = gp.population[0]
            for tree in gp.population:
                if tree.fitness > best_fitness:
                    best_tree = tree
                    best_fitness = tree.fitness
            instruction_set = create_instruction(best_tree)
            print_file(best_path, instruction_set,0)
            if found_solution or iterate>=1000:
                best_fitness = float("-inf")
                best_tree = gp.population[0]
                for tree in gp.population:
                    if tree.fitness > best_fitness:
                        best_tree = tree
                        best_fitness = tree.fitness
                instruction_set = create_instruction(best_tree)
                print_file(best_path, instruction_set,0)
                break

            print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
            print("No.", iterate, "iterate")

            gp.evolve(iterate)
            iterate += 1
            print("best fitness:",max_fitness)
            print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
        # gp.population.sort(key=lambda x: x.fitness, reverse=True)
        # find_best_value(gp.population[0])
        # instruction_set = create_instruction(gp.population[0])
        # print_file(best_path, instruction_set)
        #
        # fit_file.writelines("\n")


    fit_file.close()