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



def append_and_explore_optim(schedule, program, idProgram, set_restrictions, \
                             index_order_optimization, order_optimizations):
  if index_order_optimization == len(order_optimizations) :
       print schedule
       sched_exec = ScheduleExecution(program.args, 1000)
       time = sched_exec.test_schedule(schedule, idProgram)
       print time
  else :
    if order_optimizations[index_order_optimization] == 'Split' :
       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       new_schedule = SplitOptimization.append_optimizations(schedule, new_program, set_restrictions)
       new_program = program.copy_program()
       SOG.SplitOptimizationGenerator.explore_possibilities(new_schedule,0, new_program,\
                                                                            list(), set_restrictions,\
                                                                            idProgram,\
                                                                            index_order_optimization+1,\
                                                                            order_optimizations)

    if order_optimizations[index_order_optimization] == 'Tile' :
       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       new_schedule = TileOptimization.append_optimizations(schedule, new_program, set_restrictions)
       new_program = program.copy_program()
       TOG.TileOptimizationGenerator.explore_possibilities(new_schedule,0, new_program,list(), \
                                                                           set_restrictions,\
                                                                           idProgram,\
                                                                           index_order_optimization+1,\
                                                                           order_optimizations)



    if order_optimizations[index_order_optimization] == 'Reorder' :
       new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
       [new_schedule, unchoosen] = ReorderOptimization.append_optimizations(schedule, new_program)
       ROG.ReorderOptimizationGenerator.explore_possibilities(new_schedule,0,list(),unchoosen,\
                                                              new_program,set_restrictions,idProgram,
                                                              index_order_optimization+1, \
                                                              order_optimizations)

    if order_optimizations[index_order_optimization] == 'Fuse' :
        new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
        new_schedule = FuseOptimization.append_optimizations(schedule, new_program)
        FOG.FuseOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(),\
                                                                             set_restrictions, \
                                                                             idProgram, \
                                                                             index_order_optimization+1, \
                                                                             order_optimizations)



    if order_optimizations[index_order_optimization] == 'Parallel' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = ParallelOptimization.append_optimizations(new_program, schedule)
          POG.ParallelOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                              set_restrictions, idProgram, \
                                                        index_order_optimization+1, order_optimizations)


    if order_optimizations[index_order_optimization] == 'Vectorize' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = VectorizeOptimization.append_optimizations(new_program, schedule)
          POG.VectorizeOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                              set_restrictions, idProgram, \
                                                        index_order_optimization+1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Unroll' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = UnrollOptimization.append_optimizations(new_program, schedule)
          POG.UnrollOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                              set_restrictions, idProgram, \
                                                        index_order_optimization+1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Compute_At' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = ComputeAtOptimization.append_optimizations(schedule, program)
          COG.ComputeAtOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                                   set_restrictions, idProgram, \
                                                              index_order_optimization+1, order_optimizations)

    if order_optimizations[index_order_optimization] == 'Store_At' :
          new_program = ROG.ReorderOptimizationGenerator.update_program_after_reorder(program, schedule)
          new_program = FOG.FuseOptimizationGenerator.update_program(new_program, schedule)
          new_schedule = StoreAtOptimization.append_optimizations(schedule, new_program)
          COG.StoreAtOptimizationGenerator.explore_possibilities(new_schedule, 0, new_program, list(), \
                                                               set_restrictions, idProgram, \
                                                              index_order_optimization+1, order_optimizations)


    






