#-*- coding: utf-8 -*-
import SplitOptimizationGenerator as SOG
import ast
import re
import os
import plot_graph
from plot_graph import draw_graph_evolution

ai = u"é"
aie = u"è"

from SplitOptimizationGenerator import *
import TileOptimizationGenerator as TOG
from TileOptimizationGenerator import *
import ParallelOptimizationGenerator as POG, \
    ReorderOptimizationGenerator as ROG, \
    FuseOptimizationGenerator as FOG, \
    ComputeAtOptimizationGenerator as COG
from Schedule import *
import ScheduleExecution
from ScheduleExecution import *
import global_information
from operator import itemgetter, attrgetter, methodcaller
import time
import Heuristics.Heuristic_best_reorder
from Heuristics.Heuristic_best_reorder import extract_references



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


def indexes_to_color(indexes):
    global_information.indexes = indexes

def type_colors(types):
    global_information.types = types

def append_and_explore_optim(schedule, program, id_program, set_restrictions, \
                             index_order_optimization, order_optimizations):

  if index_order_optimization == len(order_optimizations) :
       time = schedule.test_schedule(program.args, id_program, program)
       # check if the schedule must be stored
       if get_store_schedule_bool():
           store_schedule(schedule, time)


  else :
    if order_optimizations[index_order_optimization] == 'Split' :
       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
       new_schedule = SplitOptimization.append_optimizations(schedule, new_program, set_restrictions)
       new_program = program.copy_program()
       SOG.SplitOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, \
                                                            list(), set_restrictions, \
                                                            id_program, \
                                                            index_order_optimization + 1, \
                                                            order_optimizations)

    if order_optimizations[index_order_optimization] == 'Tile' :

       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
       new_schedule = TileOptimization.append_optimizations(schedule, new_program, set_restrictions)
       new_program = program.copy_program()
       TOG.TileOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                           set_restrictions, \
                                                           id_program, \
                                                           index_order_optimization + 1, \
                                                           order_optimizations)




    if order_optimizations[index_order_optimization] == 'Reorder' :
       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
       [new_schedule, unchoosen] = ReorderOptimization.append_optimizations(schedule, new_program)
       ROG.ReorderOptimizationGenerator.explore_possibilities(new_schedule, 0, list(), unchoosen, \
                                                              new_program, set_restrictions, id_program,
                                                              index_order_optimization + 1, \
                                                              order_optimizations)

    if order_optimizations[index_order_optimization] == 'Fuse' :
        new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
        #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
        new_schedule = FuseOptimization.append_optimizations(schedule, new_program)
        FOG.FuseOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                            set_restrictions, \
                                                            id_program, \
                                                            index_order_optimization + 1, \
                                                            order_optimizations)



    if order_optimizations[index_order_optimization] == 'Parallel' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = ParallelOptimization.append_optimizations(new_program, schedule)
          POG.ParallelOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                  set_restrictions, id_program, \
                                                                  index_order_optimization + 1, order_optimizations)


    if order_optimizations[index_order_optimization] == 'Vectorize' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = VectorizeOptimization.append_optimizations(new_program, schedule)
          POG.VectorizeOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                   set_restrictions, id_program, \
                                                                   index_order_optimization + 1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Unroll' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = UnrollOptimization.append_optimizations(new_program, schedule)
          POG.UnrollOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization + 1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Compute_At' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = Schedule.ComputeAtOptimization.append_optimizations(schedule, program)
          COG.ComputeAtOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                   set_restrictions, id_program, \
                                                                   index_order_optimization + 1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Store_At' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          #new_program = FOG.FuseOptimizationGenerator.update_program_after_fuse(new_program, schedule)
          new_schedule = Schedule.StoreAtOptimization.append_optimizations(schedule, new_program)
          COG.StoreAtOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                 set_restrictions, id_program, \
                                                                 index_order_optimization + 1, order_optimizations)


    

def store_generated_schedules(store, nb_schedules) :
    global_information.store_schedules = store
    global_information.nb_schedules_to_store = nb_schedules
    global_information.stored_schedules = list()



def set_limit(limit):
    global_information.limit = limit

def get_limit():
    return global_information.limit


def get_best_schedule():
    return global_information.best_schedule

def set_best_schedule(best_schedule):
    global_information.best_schedule = best_schedule


def get_best_time_schedule():
    return global_information.best_time

def set_best_time_schedule(best_time):
    global_information.best_time = best_time


def store_schedule(schedule,time):
    if len(global_information.stored_schedules) < global_information.nb_schedules_to_store:
        global_information.stored_schedules.append([schedule, time])
    else :
        global_information.stored_schedules = sorted(global_information.stored_schedules, \
                                                     key=itemgetter(1))
        if time < global_information.stored_schedules[len(global_information.stored_schedules)-1] :
           global_information.stored_schedules.pop(len(global_information.stored_schedules)-1)
           global_information.stored_schedules.append([schedule, time])


def get_store_schedule_bool():
    return global_information.store_schedules


def get_stored_schedules():
    return global_information.stored_schedules


def set_nb_schedule_explorer(explored):
    global_information.nb_schedule_explored = explored


def get_nb_schedule_explored():
    return global_information.nb_schedule_explored


def get_total_nb_schedule():
    return global_information.total_nb_schedule


def set_total_nb_schedule(total):
    global_information.total_nb_schedule = total


def set_worst_time_schedule(time) :
    global_information.worst_time = time


def get_worst_time_schedule():
    return global_information.worst_time


def get_worst_schedule():
    return global_information.worst_schedule


def set_worst_schedule(schedule):
    global_information.worst_schedule = schedule


def get_start_time():
    return global_information.timer


def start_timer():
    start_time = time.time()
    global_information.timer = start_time


def set_schedules_id(schedules_id):
    global_information.schedules_id = schedules_id


def get_schedules_id():
    return global_information.schedules_id

'''def store_db(schedule, id_program, program):
    schedules_id = get_schedules_id()
    id_schedule = hashlib.md5(str(schedule) + id_program).hexdigest()
    if schedules_id != None :
     if id_schedule in schedules_id :
       ## A high performance schedule
       for function in program.functions :
           if function.is_consumer():
               vectorize_factor = 1
               vectorized_var = None
               unrolled_var = None
               unroll_factor = 1
               splitted_vars = list()
               original_vectorize_extent = 0
               original_unroll_extent = 0
               reorder_variables = list()
               index_vectorize = -1
               index_unroll = -1
               difference_unroll_vectorize = 0
               boolean_vectorize_unroll = 0
               level_compute = None
               nb_compute_unroll = 0
               nb_compute_vectorize = 0
               boolean_computed = 0
               nb_references_vectorize = 0
               nb_references_not_vectorize = 0
               nb_references_not_unroll = 0
               nb_references_unroll = 0

               for optim in schedule.optimizations :
                   if isinstance(optim, ReorderOptimization) :
                       if optim.func == function:
                           reorder_variables = optim.variables

                   if isinstance(optim, TileOptimization) :
                       if optim.func == function :
                           if (optim.tile_factor_out > 1) | (optim.tile_factor_in > 1) :
                               splitted_vars.append(optim.variable_in)
                               splitted_vars.append(optim.variable_out)

                   if isinstance(optim, SplitOptimization):
                       if optim.func == function :
                         if optim.split_factor > 1 :
                            splitted_vars.append(optim.variable)

                   if isinstance(optim, VectorizeOptimization):
                       if optim.func == function :
                          if optim.enable == True :
                           vectorize_factor = optim.variable.extent_var
                          else :
                              vectorize_factor = 1
                          vectorized_var = optim.variable
                          for split_var in splitted_vars :
                               if split_var.name_var+'i' == vectorized_var.name_var :
                                   original_vectorize_extent = split_var.extent_var

                   if isinstance(optim, UnrollOptimization):
                       if optim.func == function :
                          if optim.enable == True :
                           unroll_factor = optim.variable.extent_var
                          else :
                           unroll_factor = 1
                          unrolled_var  = optim.variable
                          for split_var in splitted_vars :
                               if split_var.name_var+'i' == unrolled_var.name_var :
                                   original_unroll_extent = split_var.extent_var


                   if isinstance(optim, ComputeAtOptimization):
                       if optim.consumer == function :
                           if optim.variable in reorder_variables :
                              level_compute = reorder_variables.index(optim.variable)
                              if level_compute <= index_unroll :
                                  nb_compute_unroll+=1
                              if level_compute <= index_vectorize :
                                  nb_compute_vectorize+=1
                           else :
                               level_compute = len(reorder_variables)
                       if optim.func == function :
                           if optim.variable.name_var == "root" :
                               boolean_computed = 0
                           else :
                               boolean_computed = 1
                   if len(reorder_variables) != 0 :
                      if (unrolled_var != None) & (vectorized_var != None) :
                         if unrolled_var in reorder_variables :
                          index_unroll = reorder_variables.index(unrolled_var)
                         if vectorized_var in reorder_variables :
                          index_vectorize = reorder_variables.index(vectorized_var)
                         if (index_unroll == None) | (index_vectorize == None) :
                            difference_unroll_vectorize = 0
                         else :
                             difference_unroll_vectorize = abs(index_unroll - index_vectorize)
                             if index_vectorize < index_unroll :
                                 boolean_vectorize_unroll = 1
                             else :
                                 boolean_vectorize_unroll = 0

               [function_vars, variables]=extract_references(function.instruction)
               for func in function_vars.keys() :
                   list_vars = list()
                   for expression in function_vars[func]:
                       #print func
                       #print expression
                       expression= expression.replace(" ","");
                       formula = expression
                       vars_func = [
                       node.id for node in ast.walk(ast.parse(formula))
                       if isinstance(node, ast.Name)
                       ]
                       for var in vars_func :
                           list_vars.append(var)
                   list_vars = list(set(list_vars))
                   nb_references_vectorize_old = nb_references_vectorize
                   for var in list_vars :
                     if vectorized_var != None :
                       if re.match(var+"(i)*",vectorized_var.name_var) :
                          nb_references_vectorize+=1
                          break
                   if nb_references_vectorize_old == nb_references_vectorize :
                       nb_references_not_vectorize+=1

                   nb_references_unroll_old = nb_references_unroll
                   for var in list_vars :
                     if unrolled_var != None :
                       if re.match(var+"(i)*",unrolled_var.name_var) :
                          nb_references_unroll+=1
                          break
                   if nb_references_unroll_old == nb_references_unroll :
                       nb_references_not_unroll+=1

               print schedule
               print function
               print function.instruction
               print vectorize_factor, vectorized_var
               print unroll_factor, unrolled_var
               print original_vectorize_extent, original_unroll_extent
               print boolean_vectorize_unroll
               print difference_unroll_vectorize
               print nb_references_unroll, nb_references_not_unroll
               print nb_references_vectorize, nb_references_not_vectorize
               print boolean_computed
               print nb_compute_vectorize, nb_compute_unroll
               '''

def get_naif_time():
    return global_information.naif_time

def set_naif_time(naif) :
    global_information.naif_time = naif


def get_types():
    return global_information.types

def get_indexes():
    return global_information.indexes

def get_plot_x():
    return global_information.plot_x

def get_plot_y():
    return global_information.plot_y


def add_plot_x(x) :
    global_information.plot_x.append(x)

def add_plot_y(y) :
    global_information.plot_y.append(y)

def get_time_reorder():
    return global_information.time_reorder

def get_time_unroll():
    return global_information.time_unroll


def set_time_reorder():
    global_information.time_reorder = time.time() - get_start_time()

def set_time_unroll_compute():
    global_information.time_unroll = time.time() - get_start_time()


def end_test(time_, schedule, args, id_program, program):
    if get_total_nb_schedule() != 0 :
        print '\n--------------------------------------------------------------'
        print u"➜"+'Schedule : ', get_total_nb_schedule()
        if (get_types() == None) & (get_indexes() == None) :
            print str(schedule)
        else :
          if get_indexes()!= None :
            print schedule.str_colors(get_indexes())
          else :
              if get_types() != None :
                  print schedule.str_types(get_types())

        if time_ == float('inf') :
            print u"➜"+'Temps d\'ex'+ai+'cution : '+color.RED+"infini"+" s"+color.END
            print color.RED+"Schedule invalide"+color.END
        else :
            print u"➜"+'Temps d\'ex'+ai+'cution : '+color.GREEN+str(time_)+" s"+color.END
        print '--------------------------------------------------------------'
        add_plot_x(time.time() - get_start_time())
        add_plot_y(time_)
        time.sleep(3)

    #store_db(schedule, id_program, program)
    if time_ < get_best_time_schedule():
            set_best_time_schedule(time_)
            set_best_schedule(schedule)
    if time_ > get_worst_time_schedule():
            set_worst_time_schedule(time_)
            set_worst_schedule(schedule)
    set_total_nb_schedule(get_total_nb_schedule()+1)
    finished = False
    if args.schedule_limit != None :
        if get_total_nb_schedule() >= args.schedule_limit :
            finished = True

    if args.heuristic_limit != None  :
        #print time.time() - get_start_time()
        if time.time() - get_start_time() >= args.heuristic_limit :
            finished = True

    if finished :
        finish()


def finish():
    print("\033[H\033[J")
    print u"➜"+u"➜"+u"➜"+u"➜"+"Statistiques sur l'exploration : "
    print '\n Le schedule le plus m'+ai+'diocre : ', get_worst_schedule()
    print '\n Son temps d\'ex'+ai+'cution : ', get_worst_time_schedule()
    print '\n Le meilleur schedule : ', get_best_schedule()
    print '\n Son temps d\'ex'+ai+'cution :', get_best_time_schedule()
    print '\n Le nombre de schedules testés :', get_total_nb_schedule()
    print '\n Le temps pris par l\'exploration : '+str(time.time() - get_start_time())+" seconds"
    print '\n Le temps pris pour le reorder : ', str(get_time_reorder())
    print '\n Le temps pris pour unroll et compute_at : ', str(get_time_unroll())
    print color.GREEN+"L'acc"+ai+"l"+ai+"ration du programme optimis"+ai+" par ce syst"+aie+"me :"+str(get_naif_time()/get_best_time_schedule())+color.END
    draw_graph_evolution(get_plot_x(), get_plot_y())
    exit(0)









