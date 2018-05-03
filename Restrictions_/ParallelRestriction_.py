import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.ParallelOptimizationGenerator
from GenerationOfOptimizations.ParallelOptimizationGenerator import ParallelOptimizationGenerator


class ParallelRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
        super(ParallelRestriction, self).__init__(func, enable)


class ParallelFixRestriction(ParallelRestriction):
    def __init__(self, func, fix, fixed_value, enable):
        super(ParallelFixRestriction, self).__init__(func, enable)
        # Indicate if the optimization Parallel must be setted to True or False and not varying
        self.fix = fix
        self.fixed_value = fixed_value

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
       if self.enable == True :
            optim = schedule.optimizations[index]
            if (self.fix == True) & (self.fixed_value != None) :
                    optim.enable = self.fixed_value
                    ParallelOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
                    return False
            else :
                    return True
       else :
           schedule.optimizations[index].enable = False
           ParallelOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
           return False
