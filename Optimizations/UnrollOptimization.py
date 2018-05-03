import Optimization
from Optimization import Optimization

import Restrictions_.UnrollRestriction_
from Restrictions_.UnrollRestriction_ import *

import Optimizations.TileOptimization
from Optimizations.TileOptimization import *

import Optimizations.SplitOptimization
from Optimizations.SplitOptimization import *

class UnrollOptimization(Optimization):
    def __init__(self, func, variable, enable):
        super(UnrollOptimization, self).__init__(func)
        # The variable on which we apply an unroll optimization
        self.variable = variable
        # enable == True if the optimization is setted
        self.enable = enable

    def __str__(self):
        if self.enable :
            var_name = self.variable.name_var
            if self.variable.type_of_var() == "RVar":
               if '.' in var_name :
                index_dot = var_name.index('.')
                if len(var_name[index_dot+1:]) > 1 :
                    var_name = var_name.replace('.','')
            return '{}.unroll({});'.format(self.func, var_name)
        else:
            return ''

    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, UnrollRestriction):
                if restriction.func == self.func:
                    return restriction
        return None


    @staticmethod
    def append_optimizations(program, schedule):
        new_schedule = schedule.copy_schedule()
        for func in program.functions :
            if func.is_consumer():
                [inner1, inner2] = func.two_innermost_variable_for_unroll(schedule)
                splitted_var = False
                for optim in new_schedule.optimizations :
                   if isinstance(optim, TileOptimization):
                      if (optim.func == func) & (optim.tile_factor_in > 1) :
                                if optim.variable_in.name_var+'i' == inner1.name_var :
                                    splitted_var = True
                                    break
                      if (optim.func == func) & (optim.tile_factor_out > 1) :
                                if optim.variable_out.name_var+'i' == inner1.name_var :
                                    splitted_var = True
                                    break
                   if isinstance(optim, SplitOptimization):
                      if (optim.func == func) & (optim.split_factor > 1) :
                         if optim.variable.name_var+'i' == inner1.name_var :
                           splitted_var = True
                           break
                if (inner1.type == 'RVar') | (splitted_var == True) :
                   new_schedule.optimizations.append(UnrollOptimization(func, inner1, False))
        return new_schedule

