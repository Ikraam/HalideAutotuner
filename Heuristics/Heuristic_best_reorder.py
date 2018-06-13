import Schedule
from Schedule import *
import re
import string
import ast
import StorageManager
from StorageManager import *
from ast import walk, Name
import numpy as np
from scipy.optimize import minimize
from sympy.parsing.sympy_parser import parse_expr
from operator import itemgetter, attrgetter, methodcaller



def reorder_heuristique(tiled_vars_factor, splitted_vars_factor, instruction, cache_line_size, \
                        functions, args, consumer, constantes, idProgram):
    '''

    :param tiled_vars_factor: tiled variables
    :param splitted_vars_factor: splitted variables
    :param instruction: the correspondant instruction
    :param cache_line_size:
    :param functions: functions of the program
    :param args:
    :param consumer: the function concerned about the reorder optimization
    :return: the best reorder of consumer loop nests
    '''
    print constantes

    # Find the best reorder but the reorder can be invalid
    [best_reorder, final_costs] = find_approximative_best_reorder(instruction, cache_line_size, functions, consumer, constantes)
    ## check the correctness of this reorder
    schedule = Schedule.Schedule(list(), args)
    ## If we have tile or split optimization, just add them to the schedule
    if bool(tiled_vars_factor) == True :
       for var in tiled_vars_factor.keys():
         schedule.optimizations.append(SplitOptimization(consumer,tiled_vars_factor[var], var))
    if bool(splitted_vars_factor) == True :
        for var in splitted_vars_factor.keys():
         schedule.optimizations.append(SplitOptimization(consumer,splitted_vars_factor[var], var))

    # func, variables
    list_reorder_object_var = list()

    # dict_list_vars = {name_var1 : obj_var1, name_var2 : obj_var2}
    dict_list_vars = consumer.vars_of_func_dict()
    for var in best_reorder :
        list_reorder_object_var.append(dict_list_vars[var])


    # add reorder and parallel optimizations to the schedule
    reorder_optimization = ReorderOptimization(consumer, list_reorder_object_var, True)
    parallel_optimization = ParallelOptimization(consumer, list_reorder_object_var[len(list_reorder_object_var)-1], True)
    schedule.optimizations.append(reorder_optimization)
    schedule.optimizations.append(parallel_optimization)
    # contains all the possible reorders with their execution time
    list_reorders = list()
    storage = StorageManager()
    # May be this schedule has been already executed, so check for it on the database
    time = schedule.test_schedule(args,idProgram)
    if time == float('inf'):
       schedule.optimizations.remove(parallel_optimization)
       time = schedule.test_schedule(args,idProgram)
    # if the schedule gives an invalid program or gives a timeout execution
    if time == float('inf') :
        # let's change the reorder optimization
        schedule.optimizations.remove(reorder_optimization)
        #schedule.optimizations.remove(parallel_optimization)
        ## Heuristic from Kennedy, K., & Allen, J. R. (2001). Optimizing compilers for modern architectures: a dependence-based approach. Morgan Kaufmann Publishers Inc.. Page 540
        L = list()
        # L contains the variable of consumer functions in their valid initial order
        for var in consumer.list_variables:
            L.append(var.name_var)
        # O contains the approximative best reorder
        O = best_reorder
        P = list()
        # P should contain the alternatives to find the best valid reorder optimization
        # Let's init P with elements of L : naive reorder
        for l in L :
            P.append(l)
        # P_modif will contain the current reorder configuration
        # Please check the heuristic for further details
        P_modif = list()
        for p in P :
            P_modif.append(p)
        while len(O) != 0 :
            for j in xrange(0, len(P)):
                # try to put in position j, one of the elements of the approximative best reorder (the first valid starting from
                # the first one
                for elem in O :
                    if elem in P_modif :
                       index_elem_P = P_modif.index(elem)
                       P_modif.remove(elem)
                       P_modif = P_modif[:j]+[elem]+P_modif[j:]
                       ## Let s create and test the schedule
                       list_reorder_object_var = list()
                       dict_list_vars = consumer.vars_of_func_dict()
                       for var in P_modif :
                           list_reorder_object_var.append(dict_list_vars[var])
                       reorder_optimization = ReorderOptimization(consumer, list_reorder_object_var, True)
                       schedule.optimizations.append(reorder_optimization)
                       parallel_optimization = ParallelOptimization(consumer,consumer.vars_of_func_dict()[P_modif[len(P_modif)-1]]
                                                                    ,True)
                       schedule.optimizations.append(parallel_optimization)
                       # test the schedule
                       time = schedule.test_schedule(args,id_program=idProgram)
                       schedule.optimizations.remove(reorder_optimization)
                       schedule.optimizations.remove(parallel_optimization)
                       # if it was a valid schedule (a valide reorder) so let's append it to list_reorders
                       if (time != None) & (time != float('inf')):
                          # list_reorders contains all the valid schedule with their execution time
                          list_reorders.append([P_modif[:], time])
                          O.remove(elem)
                          break
                       P_modif.remove(elem)
                       # let's reset P_modif
                       P_modif = P_modif[:index_elem_P]+[elem]+P_modif[index_elem_P:]
    else :
        return best_reorder
    list_reorders = sorted(list_reorders, key=itemgetter(1))
    return list_reorders[0][0]
    ## Get the best reorder
    ## We have a list of valid reorder optimizations

    return 1




def find_approximative_best_reorder(instruction, cache_line_size, functions, consumer, constantes):
        '''
    :param instruction: the analysed instruction
    :param cacheLineSize: size of one cache line
    :param functions: functions of the program
    :return: the best loop nest order for instruction
        '''
        ## I have to identify all the functions and their variables
        [function_vars, variables]=extract_references(instruction)
        ## Group all equivalent function references : same reference with distance access < cache_line_size
        group_references=relevant_references(function_vars, variables, cache_line_size, consumer.vars_of_func_dict(), constantes)
        ## name_considered_functions contains the relevant references
        name_considered_functions=list()
        for group_ref in group_references :
            name_considered_functions.append(group_ref[0])
        ## Heuristic from Kennedy, K., & Allen, J. R. (2001). Optimizing compilers for modern architectures: a dependence-based
        # approach. Morgan Kaufmann Publishers Inc.. Page 537

        ## The initial cost for each induction variable
        cost_for_each_loop_nest = dict()
        for loop_nest_level in consumer.list_variables :
            cost_for_each_loop_nest[loop_nest_level.name_var] = dict()
            for ref in function_vars.keys() :
                # check if the reference is relevant
                # if yes give a cost for each reference according to the loop nest level considered
                if ref in name_considered_functions :
                    cost_for_each_loop_nest[loop_nest_level.name_var][ref] = cost_ref_loop(ref, function_vars, \
                                                                                          loop_nest_level.name_var,
                                                                                          consumer, cache_line_size, constantes)


        ## Multiply the initial costs by other costs : to get the cost of a loop nest for each reference
        for loop_nest_level in consumer.list_variables :
            for ref in function_vars.keys() :
                if ref in name_considered_functions :
                   for other_loop_nest in consumer.list_variables :
                     if other_loop_nest.name_var != loop_nest_level.name_var :
                        cost_for_each_loop_nest[loop_nest_level.name_var][ref] = cost_for_each_loop_nest[loop_nest_level.name_var]\
                                                                                [ref]* cost_ref_loop_multiply(ref, variables, \
                                                                                function_vars,other_loop_nest.name_var, consumer)


        ## final costs for every relevant loop nest (all the references are grouped)
        final_costs = dict()
        for loop_nest_level in consumer.list_variables :
            final_costs[loop_nest_level.name_var] = 0
            for ref in function_vars.keys() :
                if ref in name_considered_functions :
                    final_costs[loop_nest_level.name_var]+= cost_for_each_loop_nest[loop_nest_level.\
                        name_var][ref]

        somme_val = 0
        for val in final_costs.values():
            somme_val+=val

        ## get the propability for every loop nest to be at the innermost side
        for loop_nest in final_costs.keys():
            final_costs[loop_nest] = float(somme_val - final_costs[loop_nest]) / float(somme_val)

        final_reorder = list()
        store_final_cost = dict()
        for cost in final_costs.keys():
            store_final_cost[cost] = final_costs[cost]

        # get the best reorder by starting with the loop nest (variables) that have the biggest cost
        final_costs_tuples = list()
        for var in final_costs :
            final_costs_tuples.append((var,final_costs[var]))
        newlist = sorted(final_costs_tuples, key=itemgetter(1), reverse=True)
        print newlist

        for tuple in newlist :
            final_reorder.append(tuple[0])

        return [final_reorder, store_final_cost]


def extract_references(instruction):
        '''

    :param instruction: a Halide instruction like : f(x,y) = g(x,z)+x
    :return: references that figure out in instruction : f and g
        '''
        def extract_variables_instruction(consumer, producers):
            '''
        :param consumer: func(x,y,z,n)
        :param producers: producers of func, for example : prod1(x,y), prod2(x+r.x,y,z,n)
        :return: functions_with_vars : {1,func : [x,y,z,n], 2,prod1 : [x,y], 3,prod2 : [x+r.x,y,z,n]} and
                 a list which contains all the variables that appeared at least once in consumer and producers subscripts.
        '''

        ## extract all the variables of consumer
            functions_with_vars = dict()
            list_vars_instruction = list()
            consumer_vars_List = re.split("\(*\)*",consumer)[1]
            consumer_vars = re.split(",",consumer_vars_List)
        ## extract each variable of consumer
            vars = re.split("\,*\**\+*\-*\/*\%*",consumer_vars_List)
            for var in vars :
                var = string.replace(var,' ', '')
                if var not in list_vars_instruction :
                    list_vars_instruction.append(var)
            functions_with_vars['1'+","+re.split("\(*\)*",consumer)[0]] = consumer_vars
        ## extract all the variables of producer
            num_producer = 2
            for producer in producers :
                producer_vars_list = re.split("\(*\)*",producer)[1]
                producer_vars = re.split(",",producer_vars_list)
                vars = re.split("\,*\**\+*\-*\/*\%*",producer_vars_list)
                for var in vars :
                    var = string.replace(var,' ', '')
                    if var not in list_vars_instruction :
                        list_vars_instruction.append(var)
                functions_with_vars[str(num_producer)+","+re.split("\(*\)*",producer)[0]]= producer_vars
                num_producer+=1
            return [functions_with_vars, order_variables_list(list_vars_instruction)]


        producers = list()
        ## separate the producers and the consumer
        producers_consumers = instruction.split("=")
        consumer = producers_consumers[0]
        ## separate the producers
        all_producers=re.split("\)+\s*[\+\-\*\%*]*\s*",producers_consumers[1])
        for index in xrange(0,len(all_producers)):
            if index != len(all_producers) -1 :
                current_producer = all_producers[index]+")"
            else :
                current_producer = all_producers[index]
            cleaned_producer = str()
            for letter in current_producer :
                if letter != ' ':
                    cleaned_producer += letter
            producers.append(cleaned_producer)
            for producer in producers :
                if producer == '':
                    producers.remove(producer)

        [function_vars, variables]=extract_variables_instruction(consumer, producers)
        return [function_vars, variables]




def relevant_references(function_vars, variables, cache_line_size, consumerVarsDict, constantes):
    '''
    ## extract the relevant references in
    :param function_vars: {f1 : [x1,x2], f2 : [y,x]}
    :param variables:
    :param cache_line_size:
    :param consumerVarsDict:
    :return:
    '''
    affected_ref = dict()
    group_references = list()
    for func in function_vars.keys():
        affected_ref[func] = False
    for func in function_vars.keys():
        if affected_ref[func] == True :
            continue
        else :
            affected_ref[func] = True
            new_ref_group = list()
            new_ref_group.append(func)
            current_function_name = re.split(",",func)[1]
            for function in function_vars.keys():
                 function_name = re.split(",",function)[1]
                 if function_name == current_function_name :
                     if affected_ref[function] == False :
                         if small_threshold(function_vars, variables, function, func, cache_line_size, \
                                            consumerVarsDict, constantes):
                             new_ref_group.append(function)
                             affected_ref[function] = True
            group_references.append(new_ref_group)
    return group_references





def stride_loop_iteration(ref, function_vars, loop_nest_level, constantes):
    # extract vars that appear in the first subscript of function ref
    vars = re.split("\,*\**\+*\-*\/*\%*",function_vars[ref][0])
    for var in vars :
        if '.' in var :
            var = var.replace('.','')
        result = re.match(r"[a-z]+",var)
        # set all the variables = 0
        if result != None :
           exec(var+"= 0")

    # execute then interation of loop_nest_level
    for loop_index in xrange(0, 10):
        if '.' in loop_nest_level :
            loop_nest_level = loop_nest_level.replace('.','')
        result = re.match(r"[a-z]+",loop_nest_level)
        if result != None :
           exec(loop_nest_level+"= "+str(loop_index))

        # expression_to_Evaluate is the subscript of function ref with loop_nest_level setted to loop_index [1..10]
        expression_to_Evaluate = function_vars[ref][0]
        if '.' in expression_to_Evaluate :
            expression_to_Evaluate = expression_to_Evaluate.replace('.','')


        for var in constantes.keys() :
            exec(var+"= "+str(constantes[var]))

        if loop_index == 0 :
            # old : old stride between two iterations over loop_nest_level for function ref
            old = eval(expression_to_Evaluate)
        else :
            new = eval(expression_to_Evaluate)
            if loop_index == 1 :
                strideOld = new - old
            else :
                strideNew = new - old
                # If we don't get the same stride, return None
                if (strideNew != strideOld):
                    return None
                # else continue to test all the strides over 10 iterations
            old = new
    return strideNew




def cost_ref_loop(ref, function_vars, loop_nest_level, consumer, cache_line_size, constantes):
    '''

    :param ref:
    :param function_vars:
    :param loop_nest_level:
    :param consumer:
    :param cache_line_size:
    :return: the first cost (check ken kennedy Heuristic) associated to ref function and the loop nest level loop_nest_level
    '''
    loop_nest_level_exist = False
    index_function_field = 0
    # for every subscript of function 'ref'
    for function_field in function_vars[ref] :
        # extract its variables
        vars = re.split("\,*\**\+*\-*\/*\%*",function_field)
        for var in vars :
            ## If the extracted string doesn't contain any alphabetic letter (not a variable)
            if re.match(r"([a-z])+",var) == None :
                # remove it
                vars.remove(var)
        # if loop_nest_level in variables list of the current subscript
        if loop_nest_level in vars :
            if index_function_field > 0 :
                # if loop_nest_level
                return consumer.vars_of_func_dict()[loop_nest_level].extent_var
            else :
                stride = stride_loop_iteration(ref, function_vars, loop_nest_level, constantes)
                if stride == None :
                    return consumer.vars_of_func_dict()[loop_nest_level].extent_var
                else :
                    return consumer.vars_of_func_dict()[loop_nest_level].extent_var * stride // cache_line_size
        index_function_field+=1
    if loop_nest_level_exist == False :
       return 1


def cost_ref_loop_multiply(ref, variables, function_vars, other_loop_nest, consumer):
    ## Need to check the variables (loops) that precede other_loop_nest
    precedent_vars = list()
    for var in variables :
       # check if var is a variable
       if re.match(r"([a-z])+",var) == None :
          variables.remove(var)
    # figure out all the variables that preceed other_loop_nest level
    for var in variables :
        if var == other_loop_nest:
            break
        precedent_vars.append(var)
    precedent_vars.append(other_loop_nest)
    # all_subscrit_vars contain all the variables that appear in ref subscripts
    all_subscript_vars = set()
    # get all the subscripts of ref function
    for subscript_value in function_vars[ref] :
        # get variables of subscript
        vars_subscript = re.split("\,*\**\+*\-*\/*\%*",subscript_value)
        for var in vars_subscript :
            all_subscript_vars.add(var)
    # intersection contain all the variables that appeared in ref subscripts and their loop preceed other_loop_nest loop
    intersection = list(all_subscript_vars & set(precedent_vars))
    # the cost is = 1 if no intersection. Means that ref doesn't involve with the loops that preceed other_other_nest loop
    if len(intersection) == 0 :
        return 1
    else :
        # If ref subscripts contain at least one of the loop indexes that preceed other_loop_nest, so the cost of
        # will be the extent of other_loop_nest
        return consumer.vars_of_func_dict()[other_loop_nest].extent_var







def small_threshold(function_vars, variables, function1, function2, cache_line_size, \
                    consumer_vars_dict,\
                    constantes):

    def objective(x):
        '''

        :param x:
        :return: define the objective of a function to minimize
        '''
        index = 0
        for elem in list_zeros :
            exec("x"+str(index)+" = x["+str(index)+"]") in globals(), locals()
            index+=1
        diff_expr = str(parse_expr(difference_expr))
        for k,v in dict_vars.items():
            diff_expr = re.sub(r'\b' + k + r'\b', v, diff_expr)
        return eval(diff_expr)


    '''

    :param function_vars: all functions (arrays) with their subscript expressions
    :param variables: the manipulated variables in the current loop body
    :param function1 : the first reference to array A for example. 
    :param function2 : the second reference to Array A
    :param cache_line_size: the cache line size
    :return: True if there's small threshold between function1 and function2. False otherwise. 
     function1 and function2 are two references to the same array but with not necessarily the same subscripts   
    '''
    # The first subscript of the first reference
    expression_function1_contiguous = function_vars[function1][0]
    # The first subscript of the second reference
    expression_function2_contiguous = function_vars[function2][0]

    # if the subscripts contain RVars, let's delete the '.' from their variable names.
    if '.' in expression_function1_contiguous :
        expression_function1_contiguous = expression_function1_contiguous.replace('.', '')
    if '.' in expression_function2_contiguous :
        expression_function2_contiguous = expression_function2_contiguous.replace('.','')

    ## Identify the manipulated variables in expression_functionx_contiguous using ast module (without using split)
    formula = expression_function2_contiguous
    vars_func = [
    node.id for node in ast.walk(ast.parse(formula))
    if isinstance(node, ast.Name)
    ]
    formula = expression_function1_contiguous
    vars_function = [
    node.id for node in ast.walk(ast.parse(formula))
    if isinstance(node, ast.Name)
    ]

    ## used_variables contains all the variables manipulated in both references, omitting '.' from RVars
    used_variables = list()
    # unrectified_var contains all the unrectified vars, (that don't have an "." )
    unrectified_var = dict()
    for variable in variables :
        if '.' in variable :
            var_rectified = variable.replace('.','')
            unrectified_var[var_rectified] = variable
        else :
            var_rectified = variable
        if (var_rectified in vars_func) | (var_rectified in vars_function) :
            used_variables.append(variable)

    # Check the threshold between function1 accesses and function2 accesses.
    difference_expr = '-('+expression_function2_contiguous+'-('+ expression_function1_contiguous+'))'
    # Try to get the maximum difference that can exist between two different accesses to the same ref : function1 and function2
    # Need to maximize '-difference_expr'
    function_to_minimize = parse_expr(difference_expr)
    formula = str(function_to_minimize)
    vars_function_to_minimize = [
    node.id for node in ast.walk(ast.parse(formula))
    if isinstance(node, ast.Name)
    ]
    if len(vars_function_to_minimize) == 0 : ## We have only constants
        # if the difference gives us only constants expression
        # check if the difference is bigger than the cache_line_size
        if eval(str(function_to_minimize)) > cache_line_size :
            # if yes so we have a long threshold
            return False
        else :
            # we have a small threshold
            return True

    ## We have variables, so we need to maximize our expression to find the biggest threshold between references
    ## to function1 and function2
    # list_vars contains the variables that figure out in difference expression
    list_vars = list()
    # list_zero is a list of '0' which has the same length as list_vars
    # need to use list_zero to define the objective of minimizing the difference expression (look objective(x))
    list_zeros = list()
    # all the variables will be named as x0, x1, x2, it depends on their index in vars_function_to_minimize
    # so for example, vars_function_to_minimize=[x,y,z] so dict_vars={x:x0, y:x1, z:x2}
    dict_vars = dict()
    index = 0
    for var in vars_function_to_minimize :
        if var not in list_vars :
            list_vars.append(var)
            list_zeros.append(0)
            dict_vars[var] = "x"+str(index)

    # Let's initialize the first value that can take our vector or variables so [0,0,0]
    # if we had [x,y,z]
    x0 = np.array(list_zeros)
    bounds = list()
    for var in list_vars :
        if var in consumer_vars_dict.keys():
            # to say that the range of values that can take the variable var is between 0 and its extent
            bounds.append([0, consumer_vars_dict[var].extent_var])
        else : ## It should be a rectified variable or a constante
          if var in constantes.keys(): # if var is constant
              bounds.append([constantes[var], constantes[var]])
          else :
            bounds.append([0, consumer_vars_dict[unrectified_var[var]].extent_var])



    # res contain the minimum value of difference expression
    res = minimize(objective, x0, method='SLSQP', bounds = bounds,options={'xtol': 1e-8, 'disp': True})
    if abs(res.fun) > cache_line_size :
        return  False
    else :
        return True





def order_variables_list(list_vars):
        '''

    :param list_vars: list of variables manipulated within a loop
    :return: an ordered list of list_vars which starts with RVar and then Var
    '''
        ## Start with RVars and then Vars
        ordered_list = list()
        for var in list_vars :
            if var.count('.') >= 1 :
                ordered_list.append(var)
        for var in list_vars :
            if var.count('.') == 0 :
                ordered_list.append(var)
        return ordered_list
