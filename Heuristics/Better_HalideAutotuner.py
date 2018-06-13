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

    # Launch exploration with restrictions
    schedule = Schedule.Schedule(list(), args)
    settings.set_best_schedule(schedule)
    settings.set_best_time_schedule(schedule.test_schedule(program.args, program.id))
    restrictions=define_restrictions_phase_01(program, 4)
    settings.set_limit(None)
    settings.set_nb_schedule_explorer(0)
    settings.store_generated_schedules(True, 10)
    settings.append_and_explore_optim(schedule,program, program.id, restrictions,0,order_optimizations)


    for schedule_time in settings.get_stored_schedules() :
        schedule = schedule_time[0]
        hill_climbing_tile_factors(schedule, program, len(schedule.optimizations)-1)



def go_left_right(schedule, program, index, type_factor) :
    optim = schedule.optimizations[index]
    print 'schedule medium :\n', schedule
    time_middle = schedule.test_schedule(program.args,program.id)
    print 'time_middle', time_middle
    if type_factor == "tile_one" :
        factor_in = optim.tile_factor_in
        factor_out = optim.tile_factor_out
        if (factor_out > 1) | (factor_in // 2 > 1) :
            optim.tile_factor_in = factor_in // 2
            print 'schedule left : \n',schedule
            time_left = schedule.test_schedule(program.args,program.id)
        else :
            time_left = float('inf')

        print 'time_left', time_left

        if factor_in * 2 <= optim.variable_in.extent_var // 2  :
            optim.tile_factor_in = factor_in * 2
            print 'schedule right : \n', schedule
            time_right = schedule.test_schedule(program.args, program.id)
            print 'time_right', time_right
        else :
            time_right = float('inf')

        print 'time_middle :{}, time_right :{}, time_left : {}'.format(time_middle, time_right, time_left)
        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.tile_factor_in = factor_in
           return None
        else :
           if time_right <= time_left :
              optim.tile_factor_in = factor_in * 2
              return "right"
           else :
              optim.tile_factor_in = factor_in // 2
              return "left"

    if type_factor == "tile_two" :
        factor_out = optim.tile_factor_out
        factor_in = optim.tile_factor_in
        if (factor_out // 2 > 1) | (factor_in > 1) :
            optim.tile_factor_out = factor_out // 2
            print 'schedule left : \n', schedule
            time_left = schedule.test_schedule(program.args, program.id)
        else :
            time_left = float('inf')

        if factor_out * 2 <= optim.variable_out.extent_var // 2  :
            optim.tile_factor_out = factor_out * 2
            print 'schedule right : \n', schedule
            time_right = schedule.test_schedule(program.args, program.id)
        else :
            time_right = float('inf')

        print 'time_middle :{}, time_right :{}, time_left : {}'.format(time_middle, time_right, time_left)
        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.tile_factor_out = factor_out
           return None
        else :
           if time_right <= time_left :
              optim.tile_factor_out = factor_out * 2
              return "right"
           else :
              optim.tile_factor_out = factor_out // 2
              return "left"

    if type_factor == "split" :
        factor = optim.split_factor
        if factor // 2 > 1 :
            optim.split_factor = factor // 2
            time_left = schedule.test_schedule(program.args, program.id)
        else :
            time_left = float('inf')

        if factor * 2 <= optim.variable.extent_var // 2  :
            optim.split_factor = factor * 2
            time_right = schedule.test_schedule(program.args, program.id)
        else :
            time_right = float('inf')

        print 'time_middle :{}, time_right :{}, time_left : {}'.format(time_middle, time_right, time_left)
        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.split_factor = factor
           return None
        else :
           if time_right <= time_left :
              optim.split_factor = factor * 2
              return "right"
           else :
              optim.split_factor = factor // 2
              return "left"




def hill_climbing_tile_factors(schedule, program, index):
    if index == -1 :
        print schedule
        time = schedule.test_schedule(program.args, program.id)
        print time
        return 'valide schedule'
    if isinstance(schedule.optimizations[index], TileOptimization):
        while (True):
            direction = go_left_right(schedule, program, index, "tile_one")
            if direction == None :
               break
        while (True):
            direction = go_left_right(schedule, program, index, "tile_two")
            if direction == None :
               break
        hill_climbing_tile_factors(schedule, program, index-1)
    else :
      if isinstance(schedule.optimizations[index], SplitOptimization):
        if schedule.optimizations[index].split_factor > 1 :
            while (True) :
               direction = go_left_right(schedule,program, index,"split")
               if direction == None :
                  break
        hill_climbing_tile_factors(schedule, program, index-1)
      else :
        hill_climbing_tile_factors(schedule, program, index-1)







def define_restrictions_phase_01(program, cache_line_size):
    restrictions = list()
    best_reorder_function = dict()
    # define restrictions over each consumer function
    for function in program.functions :
        if function.is_consumer() :

            # disable fuse optimization
            fuse_res = FuseLevelRestriction(function, False, False, False)
            restrictions.append(fuse_res)

            # disable the unrolling optimization
            unroll_res = UnrollLevelsRestriction(function, False, False)
            restrictions.append(unroll_res)

            # set reorder restriction
            # search for the best reorder
            best_reorder_function[function.name_function] = reorder_heuristique(dict(), dict(), \
                                                         function.instruction, cache_line_size, \
                        program.functions, program.args, function, program.constantes, program.id)
            splitted_variables = list()
            tiled_variables = list()

            # dictionary of : {var_name : var_object}
            dict_vars_name_vars = function.vars_of_func_dict()

            # tile when there's a data reuse
            enable_reorder = True
            if len(function.reuses) >= 2 :
               variable_in_tile = function.reuses[0]
               variable_out_tile = function.reuses[1]
               # Tile with a fix tile factor = 16
               tile_res = TR.TileFactorsRestriction(function, 16, 16, \
                                                           dict_vars_name_vars[variable_in_tile], \
                                                           dict_vars_name_vars[variable_out_tile],\
                                                           None, None, True, True, None, \
                                                           function.tile_level\
                                                           , True)
               restrictions.append(tile_res)
               # add tiled variables to tiled_variables list
               tiled_variables.append(dict_vars_name_vars[variable_in_tile])
               tiled_variables.append(dict_vars_name_vars[variable_out_tile])

               # if nesting is bigger than 1 we disable the reordering for that specific function
               '''if tile_res.nesting > 1 :
                   enable_reorder = False'''


            # split vectorizable loop nest level
            if (function.legal_vectorize != None) & (function.legal_vectorize not in function.reuses) :
               # search for the variable to vectorize
               variable_to_vectorize = dict_vars_name_vars[function.legal_vectorize]
               # vectorize only the variable with an extent bigger than 4
               if variable_to_vectorize.extent_var > 4  :
                  # fix vectorize to True
                  vectorize_res = VR.VectorizeFixRestriction(function, variable_to_vectorize.name_var ,\
                                                             True, True, True)
                  restrictions.append(vectorize_res)
                  # define a split restriction over the vectorized variable : split with a default factor
                  split_res = SR.SplitFactorRestriction(function, 16, variable_to_vectorize, 1, None,\
                                                     True, True, True)
                  restrictions.append(split_res)
                  # add the splitted variable
                  splitted_variables.append(variable_to_vectorize)


            # split unrollable level
            reorder_variables = best_reorder_function[function.name_function]
            # check if the first level is vectorized. If it is so unroll it, otherwise unroll the second level
            if reorder_variables[0] == function.legal_vectorize :
                variable_to_unroll = None
                if len(reorder_variables) >= 2 :
                   variable_to_unroll = dict_vars_name_vars[reorder_variables[1]]
            else :
                variable_to_unroll = dict_vars_name_vars[reorder_variables[0]]

            if (variable_to_unroll != None) & (variable_to_unroll not in tiled_variables) :

               if variable_to_unroll.extent_var > 4 :
                  split_res = SR.SplitFactorRestriction(function,16, variable_to_unroll, 1, None, True, \
                                                     True, True)
                  restrictions.append(split_res)
                  splitted_variables.append(variable_to_unroll)



            # update the best reorder configuration with tiled variables
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

            # update the best reorder configuration with splitted variables
            for var in function.list_variables :
                if var not in splitted_variables :
                    split_restriction = SR.SplitFactorRestriction(function,None, var, 1, None, True, \
                                                     True, False)
                    restrictions.append(split_restriction)


            for var in splitted_variables :
                index_var_splitted = reorder_variable_names.index(var.name_var)
                reorder_variable_names_new = reorder_variable_names[:index_var_splitted]
                reorder_variable_names_new.append(var.name_var+'i')
                reorder_variable_names_new.append(var.name_var+'o')
                reorder_variable_names_new = reorder_variable_names_new + reorder_variable_names[\
                                                                          index_var_splitted+1:]
                reorder_variable_names = reorder_variable_names_new


            # set the reorder_restriction
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





