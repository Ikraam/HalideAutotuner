import abc
import Restriction_
from Restriction_ import Restriction
from GenerationOfOptimizations.ComputeAtOptimizationGenerator import StoreAtOptimizationGenerator

# Store_at Restriction is a restriction on store_at optimization for function func

class StoreAtRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, consumer, enable):
        super(StoreAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer


class StoreAtEnableRestriction(StoreAtRestriction):
    def __init__(self, func, consumer, enable):
        super(StoreAtEnableRestriction, self).__init__(func, consumer, enable)

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):

             schedule.optimizations[index].enable = self.enable
             StoreAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                       list(), set_restrictions, \
                                                                       id_program, \
                                                                       index_order_optimization, \
                                                                       order_optimization)
             return False



