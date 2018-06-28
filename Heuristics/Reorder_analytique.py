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
import Schedule
from Schedule import *
import Heuristics.Heuristic_best_reorder
from Heuristics.Heuristic_best_reorder import reorder_heuristique
import GenerationOfOptimizations.settings
from GenerationOfOptimizations.settings import *



def generate_schedules_heuristic(program, args, cache_line_size):
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
    # Launch exploration with restrictions
    schedule = Schedule.Schedule(list(), args)
    settings.set_best_schedule(schedule)
    settings.set_best_time_schedule(schedule.test_schedule(program.args, program.id))
    restrictions=define_restrictions_phase_01(program, cache_line_size)
    settings.set_limit(None)
    settings.set_nb_schedule_explorer(0)
    append_and_explore_optim(schedule, program, program.id, restrictions, 0, order_optimizations)



def define_restrictions_phase_01(program, cache_line_size):
    restrictions = list()
    best_reorder_function = dict()
    for function in program.functions :
        if function.is_consumer() :
            unroll_res = UnrollLevelsRestriction(function, False, True)
            restrictions.append(unroll_res)
            best_reorder_function[function.name_function] = reorder_heuristique(dict(), dict(), \
                                                         function.instruction, cache_line_size, \
                        program.functions, program.args, function, program.constantes, program.id, program)

            splitted_variables = list()
            tiled_variables = list()
            dict_vars_name_vars = function.vars_of_func_dict()
            # tile when there's a data reuse
            enable_reorder = True
            if len(function.reuses) >= 2 :
               variable_in_tile = function.reuses[0]
               variable_out_tile = function.reuses[1]
               tile_res = TR.TileFactorsRestriction(function, None, None, dict_vars_name_vars[variable_in_tile], \
                                                               dict_vars_name_vars[variable_out_tile],\
                                                               None, None, True, True, None, 1, True)
               restrictions.append(tile_res)
               tiled_variables.append(dict_vars_name_vars[variable_in_tile])
               tiled_variables.append(dict_vars_name_vars[variable_out_tile])
               if tile_res.nesting > 1 :
                   enable_reorder = False


            # split vectorizable loop nest level
            if (function.legal_vectorize != None) & (function.legal_vectorize not in function.reuses) :
               variable_to_vectorize = dict_vars_name_vars[function.legal_vectorize]
               split_res = SR.SplitFactorRestriction(function, min(16, variable_to_vectorize.extent_var //2\
                                                                   ), variable_to_vectorize, 1, None,\
                                                     True, True, True)
               restrictions.append(split_res)
               splitted_variables.append(variable_to_vectorize)


            # split unrollable level
            reorder_variables = best_reorder_function[function.name_function]
            # check if the first level is vectorized or not
            if reorder_variables[0] == function.legal_vectorize :
                variable_to_unroll = None
                if len(reorder_variables) >= 2 :
                   variable_to_unroll = dict_vars_name_vars[reorder_variables[1]]
            else :
                variable_to_unroll = dict_vars_name_vars[reorder_variables[0]]

            if (variable_to_unroll != None) & (variable_to_unroll not in tiled_variables) :

               split_res = SR.SplitFactorRestriction(function,min(16, variable_to_unroll.extent_var //2\
                                                                   ), variable_to_unroll, 1, None, True, \
                                                True, True)
               restrictions.append(split_res)
               splitted_variables.append(variable_to_unroll)


            # need to modify the reorder
            # extract name of each variable
            reorder_variable_names = reorder_variables
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
            reorder_restriction = RR.ReorderFixRestriction(function, [reorder_variable_names],\
                                                           enable_reorder)
            restrictions.append(reorder_restriction)





            # set a Hill climbing restriction to compute_at and disable store_at optimization
            for producer in program.functions :
             if producer.name_function in function.list_producers :
                compute_res = CR.ComputeAtHillClimbing(producer, function, True, True)
                restrictions.append(compute_res)
                store_res = StR.StoreAtEnableRestriction(producer, function, False)
                restrictions.append(store_res)


    return restrictions





