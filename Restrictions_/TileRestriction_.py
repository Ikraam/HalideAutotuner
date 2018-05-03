import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.TileOptimizationGenerator
from GenerationOfOptimizations.TileOptimizationGenerator import *
import math



class TileRestriction(Restriction) :
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      super(TileRestriction, self).__init__(func, enable)



class TileFactorsRestriction(TileRestriction):
    def __init__(self, func, fix_factor_in, fix_factor_out, variable_in, variable_out, max_factor_in, max_factor_out,
                 skip_one_in, skip_one_out, pow_two_split, nesting, enable):
        super(TileFactorsRestriction, self).__init__(func, enable)
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
        self.nesting = nesting


    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
          if self.enable == True :
            func = schedule.optimizations[index].func
            var_in = schedule.optimizations[index].variable_in
            var_out = schedule.optimizations[index].variable_out
            dim_in = var_in.extent_var
            dim_out = var_out.extent_var
            max_factor_in = dim_in // 2
            max_factor_out = dim_out // 2
            first_factor_in = 1
            first_factor_out = 1
            nesting = 1
            if self.nesting != None :
               nesting = self.nesting
            if self.skip_one_out :
                first_factor_out = 2
            if self.skip_one_in :
                first_factor_in = 2
            if self.max_factor_in != None :
                max_factor_in = self.max_factor_in
            if self.max_factor_out != None :
                max_factor_out = self.max_factor_out

            if self.fix_factor_out :
               first_factor_out = self.fix_factor_out
               max_factor_out = first_factor_out
            if self.fix_factor_in :
                first_factor_in = self.fix_factor_in
                max_factor_in = first_factor_in


            if self.pow_two_split :
                list_values_in = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_in, 2)),\
                                                                  int(math.log(max_factor_in, 2)+1))))
                list_values_out = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_out, 2)),\
                                                                  int(math.log(max_factor_out, 2)+1))))

            else :
                list_values_in = [x for x in range(first_factor_in, max_factor_in) if x is not 0 and dim_in % x == 0 \
                                       and x <= max_factor_in//2]
                list_values_out = [x for x in range(first_factor_out, max_factor_out) \
                                   if x is not 0 and dim_out % x == 0 \
                                       and x <= max_factor_out//2]


            if (dim_in >= 4) & (nesting > 0)  :
             if (dim_out >= 4) & (nesting > 0) :
              for tile_factor_in in list_values_in:
               for tile_factor_out in list_values_out:
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                dim_in = var_in.extent_var
                dim_out = var_out.extent_var
                TileOptimizationGenerator.replace_var_split(program, func, var_in, tile_factor_in)
                TileOptimizationGenerator.replace_var_split(program, func, var_out, tile_factor_out)

                elem_supp = list()
                schedule.optimizations = TileOptimizationGenerator.update_optim__after_tile(\
                                                                            schedule.optimizations,\
                                                                            func ,var_in, var_out ,\
                                                                            tile_factor_in,tile_factor_out,\
                                                                            index, elem_supp, program, \
                                                                            set_restrictions)
                to_remember = [dim_in, dim_out, elem_supp]
                TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, to_remember, \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, order_optimization)
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                TileOptimizationGenerator.update_cfg_undo_tile(schedule.optimizations, func, var_in, var_out, index, to_remember[2], set_restrictions)
                TileOptimizationGenerator.replace_var_un_split(program, func, var_in, to_remember[0])
                TileOptimizationGenerator.replace_var_un_split(program, func, var_out, to_remember[1])
            return False

          else :
              TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, order_optimization)
              return False


    def __str__(self):
        return 'tile restriction on in : {} and out : {}, with max_in : {} , and max_out {}, with fix_in {} and fix_out {} with skip_in {}' \
               'and skip_out {}'.format(self.variable_in, self.variable_out, self.max_factor_in, self.max_factor_out \
                                        , self.fix_factor_in, self.fix_factor_out, self.skip_one_in, self.skip_one_out)
