from Schedule import *
import settings
from GenerationOfOptimizations.OptimizationGenerator import *


class FuseOptimizationGenerator(OptimizationGenerator):

  @staticmethod
  def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization):
      """
      Generate the 'fuse' optimizations
      :param schedule: the current list of optimizations
      :param index: the index of the current optimization in schedule
      :param program: an object describing all the functions and their variables
      :param elemSupp: the deleted elements once fuse = True
      :return: a valid schedule which contains split, reorder and fuse optimizations
      """

      if index == len(schedule.optimizations) :
          settings.append_and_explore_optim(schedule, program, idProgram, setRestrictions, index_order_optimization \
                                            , order_optimization)

          return schedule
      else:
        if isinstance(schedule.optimizations[index], FuseOptimization) :
          schedule.optimizations[index].enable = True
          FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), setRestrictions, idProgram, \
                                                          index_order_optimization, order_optimization)
          schedule.optimizations[index].enable = False
          FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), setRestrictions, idProgram, \
                                                          index_order_optimization, order_optimization)
        else :
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), setRestrictions, idProgram, \
                                                            index_order_optimization, order_optimization)








  @staticmethod
  def update_program(program, schedule):
     new_program = program.copy_program()
     return new_program


