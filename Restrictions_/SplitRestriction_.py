import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.SplitOptimizationGenerator
import math
import abc



class SplitRestriction(Restriction) :
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      super(SplitRestriction, self).__init__(func, enable)


# Split Factor Restriction is a restriction on split optimization for function func over the variable
# variable. It aims to define the set of factors that a split optimization can take

class SplitHillRestriction(SplitRestriction):
    def __init__(self, func,hill, enable):
        super(SplitHillRestriction, self).__init__(func, enable)
        self.hill = hill

    '''def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):'''


class SplitFactorRestriction(SplitRestriction):
    def __init__(self, func, fixe_split_factor, variable, max_nesting_of_split, max_split_factor, skip_one, pow_two_split, enable):
        super(SplitFactorRestriction, self).__init__(func, enable)
        self.variable = variable
        # When variable must be splitted with one fixed split factor.
        self.fixe_split_factor = fixe_split_factor
        # When a variable can be splitted recursively.
        self.max_nesting_of_split = max_nesting_of_split
        # When a variable can be splitted from 1 to max_split_factor.
        self.max_split_factor = max_split_factor
        # When a variable is splitted from 2 to max.
        self.skip_one = skip_one
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split


    def __str__(self):
        string_to_return = '\n split over F : '+str(self.func)+' and V :'+str(self.variable)+' with fixe_split_factor : '+str(self.fixe_split_factor)
        string_to_return = string_to_return +' with maxNesting : ' + str(self.max_nesting_of_split) + ' with max_split_factor : ' + str(self.max_split_factor)
        return string_to_return


    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        func = self.func
        var = self.variable
        dim = self.variable.extent_var
        first_factor = 1
        last_factor = var.extent_var // 2
        nesting = 1
        if self.max_split_factor != None :
           last_factor = self.max_split_factor
        if self.skip_one == True :
           first_factor = 2
        if self.max_nesting_of_split != None :
            nesting = self.max_nesting_of_split

        if self.fixe_split_factor != None :
           if self.fixe_split_factor <= dim // 2 :
               first_factor = self.fixe_split_factor
           else :
               first_factor = dim // 2
           last_factor = first_factor


        if self.pow_two_split :
            list_values = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor, 2)),\
                                                                  int(math.log(last_factor, 2)+1))))
        else :
            list_values = [x for x in range(first_factor, last_factor) if x is not 0 and dim % x == 0 \
                                       and x <= last_factor//2]

        if ((dim >= 4) & (nesting > 0)) & (self.enable == True):
              for split_factor in list_values:
                func = self.func
                var = self.variable
                dim = self.variable.extent_var
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.replace_var_split(program, func, var, split_factor)
                elemSupp = list()
                schedule.optimizations = GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.update_optim__after_split(\
                    schedule.optimizations, func ,var ,split_factor,index, elemSupp, program, \
                    set_restrictions,nesting)
                toRemember = [dim, elemSupp]
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.explore_possibilities(schedule, index + 1, program, toRemember, \
                                                                 set_restrictions, id_program \
                                                                 , index_order_optimization, \
                                                                 order_optimization)
                func = schedule.optimizations[index].func
                var = schedule.optimizations[index].variable
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.update_cfg_undo_split(schedule.optimizations, func, var, \
                                                                 index, toRemember[1], set_restrictions,\
                                                                 nesting)
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.replace_var_un_split(program, func, var, toRemember[0])
        else :
              GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.explore_possibilities(schedule, index + 1, program, None, \
                                                               set_restrictions, \
                                                               id_program, index_order_optimization, \
                                                               order_optimization)

        return False

