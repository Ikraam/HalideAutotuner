import re
import abc
import Restriction_
from Restriction_ import Restriction
from GenerationOfOptimizations.ParallelOptimizationGenerator import VectorizeOptimizationGenerator



class VectorizeRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
        super(VectorizeRestriction, self).__init__(func, enable)


class VectorizeFixRestriction(VectorizeRestriction):
    def __init__(self, func, legal_innermost, fix, fixed_value, enable):
        super(VectorizeFixRestriction, self).__init__(func, enable)
        # Indicate the legal variable to be vectorized
        self.legal_innermost = legal_innermost
        self.fix = fix
        self.fixed_value = fixed_value

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
       if self.enable == True :
          optim = schedule.optimizations[index]
          if re.match(self.legal_innermost+"(i)*",optim.variable.name_var):
            if (self.fix == True) & (self.fixed_value != None) :
                    schedule.optimizations[index].enable = self.fixed_value
                    VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
                    return False
            else :
                return True
       else :
           schedule.optimizations[index].enable = False
           VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
           return False

