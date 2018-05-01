import abc
import math
from abc import ABCMeta
import GenerationOfOptimizations.SplitOptimizationGenerator
import GenerationOfOptimizations.ParallelOptimizationGenerator
from GenerationOfOptimizations.ParallelOptimizationGenerator import *


# Restriction is applied to a function to not let an optimization takes all the possible combination
class Restriction:
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      self.func = func
      # enable to indicate the enability of the optimization
      self.enable = enable


# Split Restriction is a restriction on split optimization for function func over the variable variable
class SplitRestriction(Restriction):
    def __init__(self, func, fixe_split_factor, variable, max_nesting_of_split, max_split_factor, skip_one, pow_two_split, enable):
        super(SplitRestriction, self).__init__(func, enable)
        self.variable = variable
        # When variable must be splitted with one fixed split factor.
        self.fixe_split_factor = fixe_split_factor
        # When a variable can be splitted recursively.
        self.max_nesting_of_split=max_nesting_of_split
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




# Unroll Restriction is a restriction on unroll optimization for function func
class UnrollRestriction(Restriction):
    def __init__(self, func, two_innermost, enable):
        super(UnrollRestriction, self).__init__(func, enable)
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






# Vectorize Restriction is a restriction on vectorize optimization for function func
class VectorizeRestriction(Restriction):
    def __init__(self, func, legal_innermost, enable, fix):
        super(VectorizeRestriction, self).__init__(func, enable)
        # Indicate the legal variable to be vectorized
        self.legal_innermost = legal_innermost
        self.fix = fix

class TileRestriction(Restriction):
    def __init__(self, func, fix_factor_in, fix_factor_out, variable_in, variable_out, max_factor_in, max_factor_out,
                 skip_one_in, skip_one_out, pow_two_split, enable):
        super(TileRestriction, self).__init__(func, enable)
        self.variable_in = variable_in
        self.variable_out = variable_out
        # When variable must be splitted with one fixed split factor.
        self.fix_factor_in = fix_factor_in
        self.fix_factor_out = fix_factor_out
        # When a variable can be splitted recursively.
        self.max_factor_in=max_factor_in
        self.max_factor_out=max_factor_out
        # When a variable is splitted from 2 to max.
        self.skip_one_in = skip_one_in
        self.skip_one_out = skip_one_out
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split

    def __str__(self):
        return 'tile restriction on in : {} and out : {}, with max_in : {} , and max_out {}, with fix_in {} and fix_out {} with skip_in {}' \
               'and skip_out {}'.format(self.variable_in, self.variable_out, self.max_factor_in, self.max_factor_out \
                                        , self.fix_factor_in, self.fix_factor_out, self.skip_one_in, self.skip_one_out)

# Parallel Restriction is a restriction on parallel optimization for function func
class ParallelRestriction(Restriction):
    def __init__(self, func, enable, fix):
        super(ParallelRestriction, self).__init__(func, enable)
        # Indicate if the optimization Parallel must be setted at fix value and not varying
        self.fix = fix

# Fuse Restriction is a restriction on fuse optimization for function func
class FuseRestriction(Restriction):
    def __init__(self, func, two_innermost, two_outermost, enable):
        super(FuseRestriction, self).__init__(func, enable)
        # Indicate if we can fuse the two innermost variables of func
        self.two_innermost = two_innermost
        # Indicate if we can fuse the two outermost variables of func
        self.two_outermost = two_outermost


# Reorder Restriction is a restriction on reorder optimization for function func
class ReorderRestriction(Restriction):
    def __init__(self, func, fix_reorder, enable):
        super(ReorderRestriction, self).__init__(func, enable)
        # fix_reorder is a list of variables, for example : fix_reorder = [[xi,yo], [r.x, r.y]] to say that all the reorder
        # for function func must respect that yo must appear after xi and r.y must appear after r.x
        self.fix_reorder = fix_reorder

    def __str__(self):
        return 'reorder fix :'+str(self.fix_reorder)


# Reorder Storage Restriction is a restriction on reorder_storage optimization for function func
class ReorderStorageRestriction(Restriction):
    def __init__(self, func, fix_reorder_storage, enable):
        super(ReorderStorageRestriction, self).__init__(func, enable)
        # Same as fix_reorder of Reorder Restriction
        self.fix_reorder_storage = fix_reorder_storage



# Compute_at Restriction is a restriction on compute_at optimization for function func
class ComputeAtRestriction(Restriction):
    def __init__(self, func, consumer, fix_compute_at, hill, enable):
        super(ComputeAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        # fix_compute_at is a variable which means that if this variable is set, compute_at for func will be setted
        # by defaut to compute_at(consumer, fix_compute_at)
        self.fix_compute_at = fix_compute_at
        # hill to search for the compute At using hill climbing method
        self.hill = hill



# Compute_at Restriction is a restriction on compute_at optimization for function func
class StoreAtRestriction(Restriction):
    def __init__(self, func, consumer, fixStoreAt, enable):
        super(StoreAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        # fix_compute_at is a variable which means that if this variable is set, store_at for func will be setted
        # by defaut to store_at(consumer, fix_compute_at)
        self.fix_store_at = fixStoreAt
