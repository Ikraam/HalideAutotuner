import Optimization
from Optimization import Optimization
import Restrictions_.TileRestriction_
from Restrictions_.TileRestriction_ import *



class TileOptimization(Optimization):
    def __init__(self, func, tile_factor_in, tile_factor_out, variable_in, variable_out):
        super(TileOptimization, self).__init__(func)
        # The factors of the tile optimization
        self.tile_factor_in = tile_factor_in
        self.tile_factor_out = tile_factor_out
        # Two tiled variable loops
        self.variable_in = variable_in
        self.variable_out = variable_out


    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, TileRestriction):
                if (restriction.func == self.func) & (restriction.variable_in == self.variable_in):
                  if restriction.variable_out == self.variable_out :
                    return restriction
        return None


    def __str__(self):
        if (self.tile_factor_in > 1) | (self.tile_factor_out > 1):
            if self.variable_in.type_of_var() == 'Var':
                return '\n {}.tile({}, {} ,{}, {} ,{}, {}, {}, {});'.format(self.func, \
                                                                            self.variable_in.name_var, \
                                                                            self.variable_out.name_var,\
                                                                            self.variable_in.name_var+'o',\
                                                                            self.variable_out.name_var+'o',\
                                                                            self.variable_in.name_var+'i',\
                                                                            self.variable_out.name_var+'i',
                                                                            self.tile_factor_in, \
                                                                            self.tile_factor_out)
            else :
                tiled_var_in = self.variable_in.name_var
                tiled_var_out = self.variable_out.name_var
                for char in tiled_var_in :
                    if char == '.':
                        tiled_var_in = tiled_var_in.replace(char, '')
                for char in tiled_var_out :
                    if char == '.':
                        tiled_var_out = tiled_var_out.replace(char, '')
                return '\n {}.tile({}, {} ,{}, {} ,{}, {}, {}, {});'.format(self.func, \
                                                                            tiled_var_in, \
                                                                            tiled_var_out,\
                                                                            tiled_var_in+'o',\
                                                                            tiled_var_out+'o',\
                                                                            tiled_var_in+'i',\
                                                                            tiled_var_out+'i',\
                                                                            self.tile_factor_in, \
                                                                            self.tile_factor_out)
        else :
            return ''

    @staticmethod
    def append_optimizations(schedule, program, setRestrictions):
      set_of_optimizations = schedule.optimizations
      for func in program.functions :
        # Check if function is a consumer
        if func.is_consumer() :
            function = func
            if len(function.reuses) == 2 :
                list_vars = function.vars_of_func_dict()
                tile_optimization=TileOptimization(function, 1, 1, list_vars[function.reuses[0]], list_vars[function.reuses[1]])
                set_of_optimizations.append(tile_optimization)
      # Create the schedule object
      schedule.optimizations = set_of_optimizations
      return schedule
