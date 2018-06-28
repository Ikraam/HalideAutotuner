# -*- coding: utf-8 -*-
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

ai = u"é"
aie = u"è"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


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
    settings.set_worst_schedule(schedule)
    time_naif = schedule.test_schedule(program.args, program.id, program)
    settings.set_best_time_schedule(time_naif)
    settings.set_worst_time_schedule(time_naif)
    settings.set_naif_time(time_naif)
    restrictions=define_restrictions_phase_01(program, 4)
    settings.set_time_reorder()
    settings.set_limit(None)
    settings.set_nb_schedule_explorer(0)
    print("\033[H\033[J")
    print u"➜"+u"➜"+u"➜"+u"➜"+' Etage 02 : Le choix du d'+ai+'roulage avec une recherche exhaustive et de la granularit'+ai+' de calcul en utilisant le Hill Climbing'+color.END
    print '\n '
    time.sleep(7)
    settings.type_colors([Schedule.UnrollOptimization])
    settings.store_generated_schedules(True, 10)
    settings.append_and_explore_optim(schedule,program, program.id, restrictions,0,order_optimizations)
    settings.type_colors(None)
    settings.set_time_unroll_compute()
    print '\n \n \n'
    print("\033[H\033[J")
    print u"➜"+u"➜"+u"➜"+u"➜"+' Etage 03 : Le choix des facteurs de tuilage et de d'+ai+'coupage en bandes en utilisant le Hill Climbing'
    time.sleep(7)
    for schedule_time in settings.get_stored_schedules() :
        schedule = schedule_time[0]
        hill_climbing_tile_factors(schedule, program, len(schedule.optimizations)-1)



def go_left_right(schedule, program, index, type_factor) :
    optim = schedule.optimizations[index]
    settings.indexes_to_color([index])
    time.sleep(5)
    print '--------------------------------------------------------------'
    print 'Schedule m'+ai+'dian :'
    time_middle = schedule.test_schedule(program.args,program.id, program)
    print '--------------------------------------------------------------'
    time.sleep(5)
    if type_factor == "tile_one" :
        factor_in = optim.tile_factor_in
        factor_out = optim.tile_factor_out
        if (factor_out > 1) | (factor_in // 2 > 1) :
            optim.tile_factor_in = factor_in // 2
            print 'Schedule gauche :'
            time_left = schedule.test_schedule(program.args,program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_left = float('inf')

        if factor_in * 2 <= optim.variable_in.extent_var // 2  :
            optim.tile_factor_in = factor_in * 2
            print 'Schedule droit :'
            time_right = schedule.test_schedule(program.args, program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_right = float('inf')

        #print '(Time middle : {}), (Time right : {}), (Time left : {})'.format(time_middle, time_right, time_left)
        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.tile_factor_in = factor_in
           print color.GREEN+'(Temps m'+ai+'dian : '+str(time_middle)+')'+color.END+', (Temps droit : {}), (Temps gauche : {})'.format(time_right, time_left)
           time.sleep(5)
           settings.indexes_to_color(None)
           return None
        else :
           if time_right <= time_left :
              optim.tile_factor_in = factor_in * 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), '+color.GREEN+'(Temps droit : '+str(time_right)+')'+color.END+', (Temps gauche : '+str(time_left)+')'
              time.sleep(5)
              settings.indexes_to_color(None)
              return "right"
           else :
              optim.tile_factor_in = factor_in // 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), (Temps droit : '+str(time_right)+'), '+color.GREEN+'(Temps gauche : '+str(time_left)+')'+color.END
              time.sleep(5)
              settings.indexes_to_color(None)
              return "left"

    if type_factor == "tile_two" :
        factor_out = optim.tile_factor_out
        factor_in = optim.tile_factor_in
        if (factor_out // 2 > 1) | (factor_in > 1) :
            optim.tile_factor_out = factor_out // 2
            print 'Schedule gauche :'
            time_left = schedule.test_schedule(program.args, program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_left = float('inf')

        if factor_out * 2 <= optim.variable_out.extent_var // 2  :
            optim.tile_factor_out = factor_out * 2
            print 'Schedule droit :'
            time_right = schedule.test_schedule(program.args, program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_right = float('inf')


        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.tile_factor_out = factor_out
           print color.GREEN+'(Temps m'+ai+'dian : '+str(time_middle)+')'+color.END+', (Temps droit : {}), (Temps gauche : {})'.format(time_right, time_left)
           time.sleep(5)
           settings.indexes_to_color(None)
           return None
        else :
           if time_right <= time_left :
              optim.tile_factor_out = factor_out * 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), '+color.GREEN+'(Temps droit : '+str(time_right)+')'+color.END+', (Temps gauche : '+str(time_left)+')'
              time.sleep(5)
              settings.indexes_to_color(None)
              return "right"
           else :
              optim.tile_factor_out = factor_out // 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), (Temps droit : '+str(time_right)+'), '+color.GREEN+'(Temps gauche : '+str(time_left)+')'+color.END
              time.sleep(5)
              settings.indexes_to_color(None)
              return "left"

    if type_factor == "split" :
        factor = optim.split_factor
        if factor // 2 > 1 :
            optim.split_factor = factor // 2
            print 'Schedule gauche : '
            time_left = schedule.test_schedule(program.args, program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_left = float('inf')

        if factor * 2 <= optim.variable.extent_var // 2  :
            optim.split_factor = factor * 2
            print 'Schedule droit : '
            time_right = schedule.test_schedule(program.args, program.id, program)
            print '--------------------------------------------------------------'
            time.sleep(5)
        else :
            time_right = float('inf')


        if (time_middle <= time_left) & (time_middle <= time_right) :
           optim.split_factor = factor
           print color.GREEN+'(Temps m'+ai+'dian : '+str(time_middle)+')'+color.END+', (Temps droit : {}), (Temps gauche : {})'.format(time_right, time_left)
           settings.indexes_to_color(None)
           return None
        else :
           if time_right <= time_left :
              optim.split_factor = factor * 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), '+color.GREEN+'(Temps droit : '+str(time_right)+')'+color.END+', (Temps gauche : '+str(time_left)+')'
              settings.indexes_to_color(None)
              return "right"
           else :
              optim.split_factor = factor // 2
              print '(Temps m'+ai+'dian : '+str(time_middle)+'), (Temps droit : '+str(time_right)+'), '+color.GREEN+'(Temps gauche : '+str(time_left)+')'+color.END
              settings.indexes_to_color(None)
              return "left"




def hill_climbing_tile_factors(schedule, program, index):
    if index == -1 :
        #print schedule
        #time = schedule.test_schedule(program.args, program.id, program)
        #print time
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

    print("\033[H\033[J")
    print u"➜"+u"➜"+u"➜"+u"➜"+' Etage 01 : Mod'+aie+'le analytique pour le choix d\'une bonne interversion de boucles pour chaque fonction Halide du programme'
    time.sleep(5)
    list_functions = list()
    for function in program.functions :
        if function.is_consumer() :
            list_functions.append(function.name_function)
    print '\n Les fonctions sont : ', list_functions
    print '---------------------------------'
    time.sleep(3)


    for function in program.functions :
        if function.is_consumer() :
            # disable fuse optimization
            fuse_res = FuseLevelRestriction(function, False, False, False)
            restrictions.append(fuse_res)

            # disable the unrolling optimization
            unroll_res = UnrollLevelsRestriction(function,False,True)
            restrictions.append(unroll_res)

            # set reorder restriction
            # search for the best reorder
            best_reorder_function[function.name_function] = reorder_heuristique(dict(), dict(), \
                                                         function.instruction, cache_line_size, \
                        program.functions, program.args, function, program.constantes, program.id, program)
            time.sleep(2)
            print '\n>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            print 'L\'interversion maintenue : '
            print '{}.reorder{}'.format(function.name_function, tuple(best_reorder_function[function.name_function]))
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            time.sleep(7)
            print("\033[H\033[J")
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
            if (function.legal_vectorize != None) :
               # search for the variable to vectorize
               variable_to_vectorize = dict_vars_name_vars[function.legal_vectorize]
               # vectorize only the variable with an extent bigger than 4
               if variable_to_vectorize.extent_var > 4  :
                  # fix vectorize to True
                  vectorize_res = VR.VectorizeFixRestriction(function, variable_to_vectorize.name_var ,\
                                                             True, True, True)
                  restrictions.append(vectorize_res)
                  # define a split restriction over the vectorized variable : split with a default factor
                  if function.legal_vectorize not in function.reuses :
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

    print("\033[H\033[J")
    print '------------------- R'+ai+'sum'+ai+' des interversions maintenues -------------------------\n \n'
    for function in program.functions :
        if function.is_consumer() :
            print '{}.reorder{}'.format(function.name_function, tuple(best_reorder_function[function.name_function]))
            time.sleep(1)
            print '\n \n'
    time.sleep(4)
    return restrictions





