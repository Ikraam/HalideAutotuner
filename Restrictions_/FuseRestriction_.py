import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.FuseOptimizationGenerator
from GenerationOfOptimizations.FuseOptimizationGenerator import *




class FuseRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
        super(FuseRestriction, self).__init__(func, enable)


class FuseLevelRestriction(FuseRestriction):
    def __init__(self, func, two_innermost, two_outermost, enable):
        super(FuseLevelRestriction, self).__init__(func, enable)
        # Indicate if we can fuse the two innermost variables of func
        self.two_innermost = two_innermost
        # Indicate if we can fuse the two outermost variables of func
        self.two_outermost = two_outermost

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        if self.enable == False :
            schedule.optimizations[index].enable = False
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
        else :
            if (self.two_outermost) & (self.two_innermost == False) :
                return True
            else:
                if (self.two_outermost == False) & (self.two_innermost == False) :
                    FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
                    return False
                else :
                   if (self.two_outermost == True) & (self.two_innermost == True):
                    return True
                   else :
                      return True
                      # only innermost is True
