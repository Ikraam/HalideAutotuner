import settings
from settings import *
import OptimizationGenerator
from OptimizationGenerator import *
import Schedule


class ReorderOptimizationGenerator(OptimizationGenerator):


    @staticmethod
    def explore_possibilities(schedule, index, choosen, unchoosen, program, set_restrictions, id_program, \
                              index_order_optimization, order_optimization):

      '''

      :param schedule: the current list of optimizations
      :param index: the index of the current optimization in listCfg
      :param choosen: the variables used in the Reorder list
      :param unchoosen: the variables unused in the Reorder list
      :param program: the program instance to optimize
      :return: a valid configuration which contains : split, reorder
      '''


      if (index == len(schedule.optimizations)):
          settings.append_and_explore_optim(schedule, program, id_program, set_restrictions, index_order_optimization, \
                                            order_optimization)
          return schedule
      else :
        if (isinstance(schedule.optimizations[index], Schedule.ReorderOptimization)) :
          if len(unchoosen) == 0:
             schedule.optimizations[index].variables = list()
             for elem in choosen :
                 schedule.optimizations[index].variables.append(elem)
             if (index+1 != len(schedule.optimizations)):
                unchoosen = list()
                for var in schedule.optimizations[index+1].func.list_variables :
                    unchoosen.append(var)
             choosen = list()
             ReorderOptimizationGenerator.explore_possibilities(schedule, index + 1, choosen, unchoosen, \
                                                                program, set_restrictions, id_program,
                                                                index_order_optimization, order_optimization)
          else :
             restriction = schedule.optimizations[index].there_are_restrictions(set_restrictions)
             back_execution = True
             if restriction != None :
                info = dict()
                info['unchoosen'] = unchoosen
                info['choosen'] = choosen
                back_execution = restriction.restrict(schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization, info)
             if back_execution == True :
               func = schedule.optimizations[index].func
               for i in xrange(0, len(unchoosen)):
                    var = unchoosen[i]                                ## choose the variable to add in list of Reorder
                    choosen.append(var)                               ## delete it from unchoosen
                    ReorderOptimizationGenerator.explore_possibilities(schedule, index, choosen, \
                                                                 unchoosen[:i] +unchoosen[i+1:], \
                                                                 program, set_restrictions, id_program, \
                                                                 index_order_optimization, \
                                                                 order_optimization)
                    choosen.remove(var)
        else :
            ReorderOptimizationGenerator.explore_possibilities(schedule, index + 1, choosen, unchoosen, \
                                                               program, set_restrictions, id_program, \
                                                               index_order_optimization, \
                                                               order_optimization)





    @staticmethod
    def update_program_after_reorder(program, schedule):
        def list_vars_of_func_after_reorder(func, schedule):
         '''
        :param schedule: the schedule applied to the program
        :return: the order of 'self' function loops
         '''
         list_of_vars = list()
         # get the reorder contained in function listVariables
         for var in func.list_variables :
            list_of_vars.append(var)

         # find the reorder optimization applied to function 'self' and
         for optim in schedule.optimizations :
            if isinstance(optim, Schedule.ReorderOptimization):
                if optim.func == func :
                    list_of_vars = list()
                    for var in optim.variables :
                        list_of_vars.append(var)
         return list_of_vars

        new_program = program.copy_program()
        for function in new_program.functions :
             new_list_vars_function = list_vars_of_func_after_reorder(function, schedule)
             function.list_variables = new_list_vars_function

        return new_program







