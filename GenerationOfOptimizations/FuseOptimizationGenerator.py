import Schedule
import settings
from GenerationOfOptimizations.OptimizationGenerator import *
from Program import Variable


class FuseOptimizationGenerator(OptimizationGenerator):

  @staticmethod
  def explore_possibilities(schedule, index, program, elemSupp, set_restrictions, id_program, \
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
          settings.append_and_explore_optim(schedule, program, id_program, set_restrictions, index_order_optimization \
                                            , order_optimization)

          return schedule
      else:
        if isinstance(schedule.optimizations[index], Schedule.FuseOptimization) :
          restriction = schedule.optimizations[index].there_are_restrictions(set_restrictions)
          back_execution = True
          if restriction != None :
             back_execution = restriction.restrict(schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization)
          if back_execution == True :
            schedule.optimizations[index].enable = True
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
            schedule.optimizations[index].enable = False
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
        else :
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)




  @staticmethod
  def update_program_after_fuse(program, schedule):
      new_program = program.copy_program()
      for optim in schedule.optimizations :
         if isinstance(optim, Schedule.FuseOptimization) :
           if optim.enable == True :
             for function in new_program.functions :
                 if function == optim.func :
                     break
             if optim.variable1 in function.list_variables :
                 index_1 = function.list_variables.index(optim.variable1)
             else :
                 index_1 = len(function.list_variables)-1
             if optim.variable2 in function.list_variables :
                 index_2 = function.list_variables.index(optim.variable2)
             else :
                 index_2 = len(function.list_variables)-2

             max_index = max(index_1, index_2)
             min_index = min(index_1, index_2)
             function.list_variables[max_index] = Variable(optim.variable1.name_var+\
                                                             optim.variable2.name_var+'$', \
                                                             optim.variable1.extent_var*\
                                                             optim.variable2.extent_var, \
                                                             optim.variable1.type)
             function.list_variables.pop(min_index)

      return new_program



  @staticmethod
  def update_program(program, schedule):
     new_program = program.copy_program()
     '''for optim in schedule.optimizations :
         if isinstance(optim, Schedule.FuseOptimization) :
           if optim.enable == True :
             for function in new_program.functions :
                 if function == optim.func :
                     break
             if optim.variable1 in function.list_variables :
                 index_1 = function.list_variables.index(optim.variable1)
             else :
                 index_1 = len(function.list_variables)-1
             if optim.variable2 in function.list_variables :
                 index_2 = function.list_variables.index(optim.variable2)
             else :
                 index_2 = len(function.list_variables)-2

             max_index = max(index_1, index_2)
             min_index = min(index_1, index_2)
             function.list_variables[max_index] = Variable(optim.variable1.name_var+\
                                                             optim.variable2.name_var+'$', \
                                                             optim.variable1.extent_var*\
                                                             optim.variable2.extent_var, optim.variable1.type)
             function.list_variables.pop(min_index)'''

     return new_program


