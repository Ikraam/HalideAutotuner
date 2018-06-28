import hashlib
import Restrictions_.ReorderRestriction_ as RR
import Restrictions_.ParallelRestriction_ as PR
import Restrictions_.SplitRestriction_ as SR
import Restrictions_.TileRestriction_ as TR
import Restrictions_.ComputeAtRestriction_ as CR
import Restrictions_.StoreAtRestriction_ as StR
import Restrictions_.VectorizeRestriction_ as VR
import Restrictions_.UnrollRestriction_ as UR
import Restrictions_.FuseRestriction_ as FR
import GenerationOfOptimizations.settings
from GenerationOfOptimizations.settings import *
import Schedule
from Schedule import *

def generate_schedules_heuristic(program, args):
    order_optimizations = list()

    # define the order of optimizations for your generated schedules
    order_optimizations.append("Tile")
    order_optimizations.append("Split")
    order_optimizations.append("Reorder")
    order_optimizations.append("Fuse")
    order_optimizations.append("Parallel")
    order_optimizations.append("Vectorize")
    order_optimizations.append("Unroll")
    order_optimizations.append("Compute_At")
    order_optimizations.append("Store_At")

    # calcule the program's id : needed by other functions
    id_program = hashlib.md5(str(program)).hexdigest()

    # A dictionary containing the best reorder optimization for each function
    best_reorder_functions = get_best_reorder(program, id_program, args, order_optimizations, 3)

    # Get restrictions to the next exploration phase
    restrictions = define_restrictions_phase_02(program, best_reorder_functions)
    settings.set_limit(100)
    settings.set_nb_schedule_explorer(0)
    # Launch exploration with restrictions
    schedule = Schedule(list(), args)
    settings.set_best_schedule(schedule)
    settings.set_best_time_schedule(schedule.test_schedule(program.args, id_program))
    append_and_explore_optim(schedule, program, id_program, restrictions, 0, order_optimizations)

    # Get restrictions for the final exploration phase
    restrictions = define_restrictions_phase_03(program, best_reorder_functions)
    settings.set_limit(None)
    # Launch exploration with restrictions
    schedule = Schedule(list(), args)
    settings.set_best_schedule(schedule)
    settings.set_best_time_schedule(schedule.test_schedule(program.args, id_program))
    append_and_explore_optim(schedule, program, id_program, restrictions, 0, order_optimizations)


def get_best_reorder(program, id_program, args, order_optimizations, limit):
    best_reorder_function = dict()
    for function in program.functions :
      if function.is_consumer():
        # put conditions on the number of schedules to generate to pick the best reorder
        # from the best schedule encountered
        settings.set_limit(limit)
        # number of schedules already generated and tested
        settings.set_nb_schedule_explorer(0)
        # set the best schedule to the naive reorder
        schedule = Schedule(list(), args)
        schedule.optimizations.append(ReorderOptimization(function, function.list_variables, True))
        settings.set_best_schedule(schedule)
        # set the best execution time to the execution time of the naive reorder
        settings.set_best_time_schedule(schedule.test_schedule(program.args, id_program))
        # define my restrictions : enable only ReorderOptimization for the current function
        restrictions = define_restrictions_phase_01(program.args, function)
        # initialize an empty schedule to start the exploration
        schedule = Schedule(list(), args)
        # start the exhaustive exploration but with the restrictions defined above
        append_and_explore_optim(schedule, program, id_program, restrictions, 0, order_optimizations)
        # get the best schedule
        best_schedule = get_best_schedule().copy_schedule()
        # search for the reorder optimization
        best_reorder = function.list_variables
        for optim in best_schedule.optimizations :
            if isinstance(optim, ReorderOptimization) :
                if optim.func == function :
                    best_reorder = optim
        best_reorder_function[function.name_function] = best_reorder
    return best_reorder_function


def define_restrictions_phase_03(program, best_reorder_function):
    '''
    enable only significant optimizations, for example, we split only the vectorizable loop
    nest level and the unrollable one, we explore compute_at optimization using hill climbing
    strategy.
    :return: list of restrictions
    '''
    restrictions = list()
    for function in program.functions :
        if function.is_consumer():
            splitted_variables = list()
            dict_vars_name_vars = function.vars_of_func_dict()


            tiled_variables = list()
            # tile when there's a data reuse
            if len(function.reuses) >= 2 :
               variable_in_tile = function.reuses[0]
               variable_out_tile = function.reuses[1]
               tile_res = TR.TileFactorsRestriction(function, None, None, dict_vars_name_vars[variable_in_tile], \
                                                               dict_vars_name_vars[variable_out_tile],\
                                                               None, None, True, True, None, None, True)

               restrictions.append(tile_res)
               tiled_variables.append(dict_vars_name_vars[variable_in_tile])
               tiled_variables.append(dict_vars_name_vars[variable_out_tile])

            # split vectorizable loop nest level
            if (function.legal_vectorize != None) & (function.legal_vectorize not in function.reuses) :
               variable_to_vectorize = dict_vars_name_vars[function.legal_vectorize]
               split_res = SR.SplitFactorRestriction(function, None, variable_to_vectorize, 1, None, True, \
                                                True, True)
               restrictions.append(split_res)
               splitted_variables.append(variable_to_vectorize)


            # split unrollable level
            reorder_variables = best_reorder_function[function.name_function].variables
            # check if the first level is vectorized or not
            if reorder_variables[0].name_var == function.legal_vectorize :
                variable_to_unroll = None
                if len(reorder_variables) >= 2 :
                   variable_to_unroll = reorder_variables[1]
            else :
                variable_to_unroll = reorder_variables[0]

            if (variable_to_unroll != None) & (variable_to_unroll not in tiled_variables) :

               split_res = SR.SplitFactorRestriction(function,None, variable_to_unroll, 1, None, True, \
                                                True, True)
               restrictions.append(split_res)
               splitted_variables.append(variable_to_unroll)


            # need to modify the reorder
            # extract name of each variable
            reorder_variable_names = list()
            for var in reorder_variables :
                reorder_variable_names.append(var.name_var)

            if len(tiled_variables) >= 2:
                index_var_in_tile = reorder_variable_names.index(function.reuses[0])
                index_var_out_tile = reorder_variable_names.index(function.reuses[1])
                reorder_variable_names_new = reorder_variable_names[:index_var_in_tile]
                reorder_variable_names_new.append(function.reuses[0]+'i')
                reorder_variable_names_new.append(function.reuses[1]+'i')
                reorder_variable_names_new = reorder_variable_names_new + \
                                         reorder_variable_names[index_var_in_tile+1:index_var_out_tile]
                reorder_variable_names_new.append(function.reuses[0]+'o')
                reorder_variable_names_new.append(function.reuses[1]+'o')
                reorder_variable_names_new = reorder_variable_names_new + reorder_variable_names\
                                             [index_var_out_tile+1:]
                reorder_variable_names = reorder_variable_names_new
            for var in splitted_variables :
                index_var_splitted = reorder_variable_names.index(var.name_var)
                reorder_variable_names_new = reorder_variable_names[:index_var_splitted]
                reorder_variable_names_new.append(var.name_var+'i')
                reorder_variable_names_new.append(var.name_var+'o')
                reorder_variable_names_new = reorder_variable_names_new + reorder_variable_names[\
                                                                          index_var_splitted+1:]
                reorder_variable_names = reorder_variable_names_new



            # modify reorder_restriction
            reorder_restriction = RR.ReorderFixRestriction(function, reorder_variable_names,True)
            restrictions.append(reorder_restriction)

            # set a Hill climbing restriction to compute_at and disable store_at optimization
            for producer in program.functions :
             if producer.name_function in function.list_producers :
                compute_res = CR.ComputeAtHillClimbing(producer, function, True, True)
                restrictions.append(compute_res)
                store_res = StR.StoreAtEnableRestriction(producer, function, False)
                restrictions.append(store_res)

    return restrictions


def define_restrictions_phase_02(program, best_reorder_function):
    '''
    enable only significant optimizations, for example, we explore compute_at optimization using
    hill climbing strategy, we explore parallel and fuse optimizations
    :return: list of restrictions
    '''
    restrictions = list()
    for function in program.functions :
        if function.is_consumer():
            reorder_variables = best_reorder_function[function.name_function].variables
            # extract variables name
            reorder_variable_names = list()
            for variable in reorder_variables :
                reorder_variable_names.append(variable.name_var)
                split_res = SR.SplitFactorRestriction(function, 1, variable, 0, None, None, None, False)
                restrictions.append(split_res)
                for var in reorder_variables :
                    tile_res = TR.TileFactorsRestriction(function, 1, 1, variable, var, 1, 1, None, None, None, None,
                                               False)
                    restrictions.append(tile_res)
            reorder_restriction = RR.ReorderFixRestriction(function, reorder_variable_names,True)
            restrictions.append(reorder_restriction)

            # set a Hill climbing restriction to compute_at and disable store_at optimization
            for producer in program.functions :
             if producer.name_function in function.list_producers :
                compute_res = CR.ComputeAtHillClimbing(producer, function, True, True)
                restrictions.append(compute_res)
                store_res = StR.StoreAtEnableRestriction(producer, function, False)
                restrictions.append(store_res)

    return restrictions


def define_restrictions_phase_01(program, current_function):
    '''
       enable reorder's optimization for the current_function and disable all the other optimizations
       even reorders applied to other functions than the current_function
       :return: list of restrictions
    '''
    # list to contain all the restrictions defined over the search space of optimizations
    restrictions = list()

    for function in program.functions :
        Rvars = list()
        for var in function.list_variables :

            # split restrictions : disable all the split optimizations
            split_res = SR.SplitFactorRestriction(function, None, var, None, None, None, None, False)
            restrictions.append(split_res)

            # define tile restrictions : disable all of tile optimizations
            for variable in function.list_variables :
                tile_res = TR.TileFactorsRestriction(function, None, None, var, variable, None, None, None, None, \
                                   None, None, False)
                restrictions.append(tile_res)

            # get list of RVar variables to keep them ordered
            if var.type == 'RVar' :
                Rvars.append(var.name_var)

        # reorder restrictions
        if function == current_function :
            reorder_res = RR.ReorderFixRestriction(function, [Rvars], True)
        else :
            reorder_res = RR.ReorderFixRestriction(function, [Rvars], False)
        restrictions.append(reorder_res)

        # disable unrolling
        unroll_res = UR.UnrollLevelsRestriction(function, None, False)
        restrictions.append(unroll_res)

        # disable vectorizing
        vectorize_res = VR.VectorizeFixRestriction(function, None, None, None, False)
        restrictions.append(vectorize_res)

        # disable parallelizing
        parallel_res = PR.ParallelFixRestriction(function, True, False, True)
        restrictions.append(parallel_res)

        # disable fusion
        fuse_res = FR.FuseLevelRestriction(function,False, False, False)
        restrictions.append(fuse_res)

        # disable compute_at and store_at optimisations
        for producer in program.functions :
            if producer.name_function in function.list_producers :
                compute_res = CR.ComputeAtHillClimbing(producer, function, False, False)
                restrictions.append(compute_res)
                store_res = StR.StoreAtEnableRestriction(producer, function, False)
                restrictions.append(store_res)
    return restrictions

