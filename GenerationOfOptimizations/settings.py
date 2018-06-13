import SplitOptimizationGenerator as SOG
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


def append_and_explore_optim(schedule, program, id_program, set_restrictions, \
                             index_order_optimization, order_optimizations):

  if index_order_optimization == len(order_optimizations) :
       print '__________________tested____________\n'
       print schedule
       time = schedule.test_schedule(program.args, id_program)

       # check if the schedule must be stored
       if get_store_schedule_bool():
           store_schedule(schedule, time)

       # increase nb schedules explored since we explored one more schedule here !
       set_nb_schedule_explorer(get_nb_schedule_explored()+1)
       print time
       print '____________________________________\n'

       # set best time and best schedule among those already explored
       if time < settings.get_best_time_schedule():
           set_best_time_schedule(time)
           set_best_schedule(schedule.copy_schedule())


  else :
    if get_limit() != None :
       if get_nb_schedule_explored() == get_limit() :
           print 'end schedule generation'
           return 0
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
    return global_information.bestSchedule

def set_best_schedule(best_schedule):
    global_information.bestSchedule = best_schedule


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




