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


class TileHillClimbing(TileRestriction) :
    def __init__(self, func, variable_in, variable_out, hill, enable):
        super(TileHillClimbing, self).__init__(func, enable)
        self.hill = hill
        self.variable_in = variable_in
        self.variable_out = variable_out

    @staticmethod
    def go_left_right(schedule, program, index, type_factor) :
        optim = schedule.optimizations[index]
        time_middle = schedule.test_schedule(program.args, program.id)
        print 'time_middle', time_middle
        if type_factor == "tile_one" :
            factor_in = optim.tile_factor_in
            if factor_in // 2 > 1 :
                    optim.tile_factor_in = factor_in // 2
                    time_left = schedule.test_schedule(program.args, program.id)
            else :
                    time_left = float('inf')

            print 'time_left', time_left

            if factor_in * 2 <= optim.variable_in.extent_var // 2  :
                optim.tile_factor_in = factor_in * 2
                time_right = schedule.test_schedule(program.args, program.id)
                print 'time_right', time_right
            else :
                time_right = float('inf')

            print 'time_middle :{}, time_right :{}, time_left : {}'.format(time_middle, time_right, time_left)
            if (time_middle <= time_left) & (time_middle <= time_right) :
                optim.tile_factor_in = factor_in
                return None
            else :
                if time_right <= time_left :
                    optim.tile_factor_in = factor_in * 2
                    return "right"
                else :
                    optim.tile_factor_in = factor_in // 2
                    return "left"
        if type_factor == "tile_two" :
            factor_out = optim.tile_factor_out
            if factor_out // 2 > 1 :
                optim.tile_factor_out = factor_out // 2
                time_left = schedule.test_schedule(program.args, program.id)
            else :
                time_left = float('inf')

            if factor_out * 2 <= optim.variable_out.extent_var // 2  :
                optim.tile_factor_out = factor_out * 2
                time_right = schedule.test_schedule(program.args, program.id)
            else :
                time_right = float('inf')

            print 'time_middle :{}, time_right :{}, time_left : {}'.format(time_middle, time_right, time_left)
            if (time_middle <= time_left) & (time_middle <= time_right) :
                optim.tile_factor_out = factor_out
                return None
            else :
                if time_right <= time_left :
                    optim.tile_factor_out = factor_out * 2
                    return "right"
                else :
                    optim.tile_factor_out = factor_out // 2
                    return "left"


    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):

        func = schedule.optimizations[index].func
        var_in = schedule.optimizations[index].variable_in
        var_out = schedule.optimizations[index].variable_out
        dim_in = var_in.extent_var
        dim_out = var_out.extent_var
        [tile_factor_in, tile_factor_out]=TileHillClimbing.hill_climbing_tile(schedule, index, program)

        TileOptimizationGenerator.replace_var_tile(program, func, var_in, tile_factor_in, var_out,\
                                                           tile_factor_out)
        toRemember = [dim_in, dim_out, list()]
        TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, toRemember, \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization)
        func = schedule.optimizations[index].func
        var_in = schedule.optimizations[index].variable_in
        var_out = schedule.optimizations[index].variable_out
        TileOptimizationGenerator.update_cfg_undo_tile(schedule.optimizations, func, var_in, var_out, index, toRemember[2], set_restrictions)
        TileOptimizationGenerator.replace_var_un_split(program, func, var_in, toRemember[0])
        TileOptimizationGenerator.replace_var_un_split(program, func, var_out, toRemember[1])
        return False




    @staticmethod
    def hill_climbing_tile(schedule, index, program):

        #if index < 0 :
        #    return 'finish'
        if isinstance(schedule.optimizations[index], Schedule.TileOptimization) :
           extent_in = schedule.optimizations[index].variable_in.extent_var
           extent_out = schedule.optimizations[index].variable_out.extent_var
           schedule.optimizations[index].tile_factor_in = extent_in // 2
           schedule.optimizations[index].tile_factor_out = extent_out // 2
        while (True):
           direction = TileHillClimbing.go_left_right(schedule, program, index, "tile_one")
           if direction == None :
              break
        while (True):
           direction = TileHillClimbing.go_left_right(schedule, program, index, "tile_two")
           if direction == None :
              break
        return [schedule.optimizations[index].tile_factor_in, \
        schedule.optimizations[index].tile_factor_out]
            #TileHillClimbing.hill_climbing_tile(schedule, index+1, program.id)
        #else :
            #TileHillClimbing.hill_climbing_tile(schedule, index+1, program.id)





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

            if self.fix_factor_out != None :
               if self.fix_factor_out <= max_factor_out :
                first_factor_out = self.fix_factor_out
               else :
                   first_factor_out = max_factor_out
               max_factor_out = first_factor_out

            if self.fix_factor_in != None :
              if self.fix_factor_in <= max_factor_in :
                first_factor_in = self.fix_factor_in
              else :
                first_factor_in = max_factor_in
              max_factor_in = first_factor_in


            list_values_in = [x for x in range(first_factor_in, max_factor_in+1) if x is not 0 \
                                                                                     and x <= max_factor_in]
            list_values_out = [x for x in range(first_factor_out, max_factor_out+1) if x is not 0 \
                                                                                      and x <= max_factor_out]


            if self.pow_two_split :
                list_values_in = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_in, 2)),\
                                                                  int(math.log(max_factor_in, 2)+1))))
                list_values_out = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_out, 2)),\
                                                                  int(math.log(max_factor_out, 2)+1))))



            if (dim_in >= 4) & (nesting > 0)  :
             if (dim_out >= 4) & (nesting > 0) :
              for tile_factor_in in list_values_in:
               for tile_factor_out in list_values_out:
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                dim_in = var_in.extent_var
                dim_out = var_out.extent_var
                TileOptimizationGenerator.replace_var_tile(program, func, var_in, tile_factor_in, \
                                                           var_out, tile_factor_out)

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
