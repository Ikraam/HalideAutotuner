import OptimizationGenerator
from OptimizationGenerator import *
import Schedule
from Schedule import ParallelOptimization, VectorizeOptimization, UnrollOptimization, TileOptimization, SplitOptimization, ComputeAtOptimization
import ComputeAtOptimizationGenerator
from ComputeAtOptimizationGenerator import ComputeAtOptimizationGenerator
import settings
from settings import *




class ParallelOptimizationGenerator(OptimizationGenerator):

   @staticmethod
   def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization):
     if index == len(schedule.optimizations):
          settings.append_and_explore(schedule, program, idProgram, setRestrictions, index_order_optimization,
                                                                                     order_optimization)
          return schedule

     else :
       if isinstance(schedule.optimizations[index], ParallelOptimization) :
              func = schedule.optimizations[index].func
              var = schedule.optimizations[index].variable
              if var.type != "RVar" :
                    schedule.optimizations[index].enable = True
                    ParallelOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)
                    schedule.optimizations[index].enable = False
              else :
                    schedule.optimizations[index].enable = False
                    ParallelOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)
       else :
              ParallelOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)



class VectorizeOptimizationGenerator(OptimizationGenerator):

    @staticmethod
    def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization):
       if index == len(schedule.optimizations):
          settings.append_and_explore(schedule, program, idProgram, setRestrictions, index_order_optimization,
                                                                                     order_optimization)
          return schedule
       else :
          if isinstance(schedule.optimizations[index], VectorizeOptimization):
               func = schedule.optimizations[index].func
               var = schedule.optimizations[index].variable
               if var.type != "RVar" :
                  # splitted variable without fixed size
                  if 'o' in var.name_var :
                     VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, \
                                                                                program, elemSupp, \
                                                                                setRestrictions, \
                                                                                idProgram, \
                                                                                index_order_optimization,\
                                                                                order_optimization)
                  else :
                     if var.name_var.count('$') >= var.name_var.count('i') :
                        VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, \
                                                                                     program, elemSupp, \
                                                                                     setRestrictions, \
                                                                                     idProgram, \
                                                                                index_order_optimization,\
                                                                                     order_optimization)
                     else :
                        if var.name_var.count('i') == 0 :
                             VectorizeOptimizationGenerator.explore_possibilities(schedule, \
                                                                                         index+1, \
                                                                                         program, \
                                                                                         elemSupp, \
                                                                                         setRestrictions,\
                                                                                         idProgram, \
                                                                                 index_order_optimization,\
                                                                                         order_optimization)
                        else :
                             schedule.optimizations[index].enable = True
                             VectorizeOptimizationGenerator.explore_possibilities(schedule, \
                                                                                         index+1, \
                                                                                         program, \
                                                                                         elemSupp, \
                                                                                         setRestrictions,\
                                                                                         idProgram, \
                                                                                 index_order_optimization, \
                                                                                         order_optimization)
                             schedule.optimizations[index].enable = False
                             VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, program,\
                                                                             elemSupp, setRestrictions, \
                                                                             idProgram, \
                                                                             index_order_optimization, \
                                                                             order_optimization)


               else :
                        schedule.optimizations[index].enable = True
                        VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, program,\
                                                                             elemSupp, setRestrictions, \
                                                                             idProgram, \
                                                                             index_order_optimization, \
                                                                             order_optimization)
                        schedule.optimizations[index].enable = False
                        VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, program,\
                                                                             elemSupp, setRestrictions, \
                                                                             idProgram, \
                                                                             index_order_optimization, \
                                                                             order_optimization)

          else :
               VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                                                                  index_order_optimization, order_optimization)







class UnrollOptimizationGenerator(OptimizationGenerator):
    @staticmethod
    def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization):

        if index == len(schedule.optimizations):
            settings.append_and_explore(schedule, program, idProgram, setRestrictions, index_order_optimization,
                                                                                     order_optimization)
            return schedule

        else :
            if isinstance(schedule.optimizations[index], UnrollOptimization):
                  var = schedule.optimizations[index].variable
                  func = schedule.optimizations[index].func
                  schedule.optimizations[index].enable = True
                  [inner1, inner2] = func.two_innermost_variable_for_unroll(schedule)
                  if inner1 == var :
                    if inner2 != None :
                     splitted_var = UnrollOptimizationGenerator.test_splitted_variable(schedule, inner2, func)
                     if (inner1.type == 'RVar') | (splitted_var == True) :
                        schedule.optimizations.append(UnrollOptimization(func, inner2, False))
                     UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)
                     if schedule.optimizations[index].enable == True:
                        [inner1, inner2] = func.two_innermost_variable_for_unroll(schedule)
                        var = schedule.optimizations[index].variable
                        if ((inner1 == var) & (inner2 != None)) & (inner2 != inner1):
                            UnrollOptimizationGenerator.remove_unroll_optimization(schedule, UnrollOptimization(func, inner2, False))
                  else :
                      if inner2 == var :
                          schedule.optimizations[index].enable = True
                          UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)

                  schedule.optimizations[index].enable = False
                  UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)

            else :
                     UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization)



    @staticmethod
    def test_splitted_variable(schedule, variable, function):
        splitted_var = False
        for optim in schedule.optimizations :
           if isinstance(optim, TileOptimization):
              if (optim.func == function) & (optim.tile_factor_in > 1) :
                   if optim.variable_in.name_var+'i' == variable.name_var :
                      splitted_var = True
                      break
                   if (optim.func == function) & (optim.tile_factor_out > 1) :
                      if optim.variable_out.name_var+'i' == variable.name_var :
                          splitted_var = True
                          break
           if isinstance(optim, SplitOptimization):
              if (optim.func == function) & (optim.split_factor > 1) :
                  if optim.variable.name_var+'i' == variable.name_var :
                     splitted_var = True
                     break
        return splitted_var

    @staticmethod
    def remove_unroll_optimization(schedule, unroll_optimization):
      '''
      ## remove the unroll optimization that has the same parameters as "optimization"
      :param optimization: the parameters of the optimization that must be deleted
      :return: None
      '''
      for optim in schedule.optimizations :
          if isinstance(optim, UnrollOptimization):
              if optim.func == unroll_optimization.func :
                  if optim.variable == unroll_optimization.variable :
                      schedule.optimizations.remove(optim)
                      return None
