import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.ParallelOptimizationGenerator
from GenerationOfOptimizations.ParallelOptimizationGenerator import UnrollOptimizationGenerator


class UnrollRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
        super(UnrollRestriction, self).__init__(func, enable)



class UnrollLevelsRestriction(UnrollRestriction):
    def __init__(self, func, two_innermost, enable):
        super(UnrollLevelsRestriction, self).__init__(func, enable)
        self.two_innermost = two_innermost

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        if (self.two_innermost == True) & (self.enable == True) :
           return True
        else :
            var = schedule.optimizations[index].variable
            func = schedule.optimizations[index].func
            [inner1, inner2] = func.two_innermost_variable_for_unroll(schedule)
            if inner1 == var :
              if self.enable == True :
                schedule.optimizations[index].enable = True
                UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, list()\
                                                                       , set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
              schedule.optimizations[index].enable = False
              UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, list(), \
                                                                  set_restrictions, id_program, \
                              index_order_optimization, order_optimization)
            return False
