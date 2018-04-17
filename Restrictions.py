import abc
from abc import ABCMeta


# Restriction is applied to a function to not let an optimization takes all the possible combination
class Restriction:
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      self.func = func
      # enable to indicate the enability of the optimization
      self.enable = enable


# Split Restriction is a restriction on split optimization for function func over the variable variable
class SplitRestriction(Restriction):
    def __init__(self, func, FixeSplitFactor, variable, maxNestingOfSplit, maxSplitFactor, skipOne,pow_two_split ,enable):
        super(SplitRestriction, self).__init__(func, enable)
        self.variable = variable
        # When variable must be splitted with one fixed split factor.
        self.FixeSplitFactor = FixeSplitFactor
        # When a variable can be splitted recursively.
        self.maxNestingOfSplit=maxNestingOfSplit
        # When a variable can be splitted from 1 to maxSplitFactor.
        self.maxSplitFactor = maxSplitFactor
        # When a variable is splitted from 2 to max.
        self.skipOne = skipOne
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split


    def __str__(self):
        stringToReturn = '\n split over F : '+str(self.func)+' and V :'+str(self.variable)+' with FixeSplitFactor : '+str(self.FixeSplitFactor)
        stringToReturn = stringToReturn+' with maxNesting : '+str(self.maxNestingOfSplit)+' with maxSplitFactor : '+str(self.maxSplitFactor)
        return stringToReturn


# Unroll Restriction is a restriction on unroll optimization for function func
class UnrollRestriction(Restriction):
    def __init__(self, func, twoInnermost, enable):
        super(UnrollRestriction, self).__init__(func, enable)
        self.twoInnermost = twoInnermost


# Vectorize Restriction is a restriction on vectorize optimization for function func
class VectorizeRestriction(Restriction):
    def __init__(self, func, legalInnermost, enable, fix):
        super(VectorizeRestriction, self).__init__(func, enable)
        # Indicate the legal variable to be vectorized
        self.legalInnermost = legalInnermost
        self.fix = fix

class TileRestriction(Restriction):
    def __init__(self, func, fix_factor_in, fix_factor_out , variable_in, variable_out, max_factor_in, max_factor_out,
                               skipOne_in, skipOne_out,pow_two_split, enable):
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
        self.skipOne_in = skipOne_in
        self.skipOne_out = skipOne_out
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split

    def __str__(self):
        return 'tile restriction on in : {} and out : {}, with max_in : {} , and max_out {}, with fix_in {} and fix_out {} with skip_in {}' \
               'and skip_out {}'.format(self.variable_in, self.variable_out, self.max_factor_in, self.max_factor_out\
                                        , self.fix_factor_in, self.fix_factor_out, self.skipOne_in, self.skipOne_out)

# Parallel Restriction is a restriction on parallel optimization for function func
class ParallelRestriction(Restriction):
    def __init__(self, func, enable, fix):
        super(ParallelRestriction, self).__init__(func, enable)
        # Indicate if the optimization Parallel must be setted at fix value and not varying
        self.fix = fix

# Fuse Restriction is a restriction on fuse optimization for function func
class FuseRestriction(Restriction):
    def __init__(self, func, twoInnermost, twoOutermost, enable):
        super(FuseRestriction, self).__init__(func, enable)
        # Indicate if we can fuse the two innermost variables of func
        self.twoInnermost = twoInnermost
        # Indicate if we can fuse the two outermost variables of func
        self.twoOutermost = twoOutermost


# Reorder Restriction is a restriction on reorder optimization for function func
class ReorderRestriction(Restriction):
    def __init__(self, func, fixReorder, enable):
        super(ReorderRestriction, self).__init__(func, enable)
        # fixReorder is a list of variables, for example : fixReorder = [[xi,yo], [r.x, r.y]] to say that all the reorder
        # for function func must respect that yo must appear after xi and r.y must appear after r.x
        self.fixReorder = fixReorder

    def __str__(self):
        return 'reorder fix :'+str(self.fixReorder)


# Reorder Storage Restriction is a restriction on reorder_storage optimization for function func
class ReorderStorageRestriction(Restriction):
    def __init__(self, func, fixReorderStorage, enable):
        super(ReorderStorageRestriction, self).__init__(func, enable)
        # Same as fixReorder of Reorder Restriction
        self.fixReorderStorage = fixReorderStorage



# Compute_at Restriction is a restriction on compute_at optimization for function func
class ComputeAtRestriction(Restriction):
    def __init__(self, func, consumer, fixComputeAt, hill ,enable):
        super(ComputeAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        # fixComputeAt is a variable which means that if this variable is set, compute_at for func will be setted
        # by defaut to compute_at(consumer, fixComputeAt)
        self.fixComputeAt = fixComputeAt
        # hill to search for the compute At using hill climbing method
        self.hill = hill



# Compute_at Restriction is a restriction on compute_at optimization for function func
class StoreAtRestriction(Restriction):
    def __init__(self, func, consumer, fixStoreAt, enable):
        super(StoreAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        # fixComputeAt is a variable which means that if this variable is set, store_at for func will be setted
        # by defaut to store_at(consumer, fixComputeAt)
        self.fixStoreAt = fixStoreAt
