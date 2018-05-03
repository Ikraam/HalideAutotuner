import Optimization
from Optimization import *
import Restrictions_.VectorizeRestriction_
from Restrictions_.VectorizeRestriction_ import *
from Optimizations.TileOptimization import *
from Optimizations.SplitOptimization import *


# We can have a vectorize optimization
class VectorizeOptimization(Optimization):

    def __init__(self, func, variable, enable):
        super(VectorizeOptimization, self).__init__(func)
        # The variable on which we apply a vectorization
        self.variable = variable
        # enable == True if the optimization is setted, False otherwise
        self.enable = enable

    def __str__(self):
        if self.enable :
            var_name = self.variable.name_var
            if self.variable.type_of_var() == "RVar":
               if '.' in var_name :
                index_dot = var_name.index('.')
                if len(var_name[index_dot+1:]) > 1 :
                    var_name = var_name.replace('.','')
            return '{}.vectorize({});'.format(self.func, var_name)
        else :
            return ''

    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, VectorizeRestriction):
                if (restriction.func == self.func):
                    return restriction
        return None

    @staticmethod
    def append_optimizations(program, schedule):
      new_schedule = schedule.copy_schedule()
      new_program = program.copy_program()
      for func in new_program.functions :
       if func.is_consumer():
        if func.legal_vectorize not in func.vars_of_func_dict().keys() :
            innermostVar_vectorize = func.search_for_inner(func.legal_vectorize)
        else :
            innermostVar_vectorize = func.vars_of_func_dict()[func.legal_vectorize]
        ## We must check if it is the inner variable of a splitted one, or it's a RVar
        splitted_var = False
        for optim in new_schedule.optimizations :
            if isinstance(optim, TileOptimization):
               if (optim.func == func) & (optim.tile_factor_in > 1) :
                  if optim.variable_in.name_var+'i' == innermostVar_vectorize.name_var :
                     splitted_var = True
                     break
               if (optim.func == func) & (optim.tile_factor_out > 1) :
                  if optim.variable_out.name_var+'i' == innermostVar_vectorize.name_var :
                     splitted_var = True
                     break

            if isinstance(optim, SplitOptimization):
               if (optim.func == func) & (optim.split_factor > 1) :
                  if optim.variable.name_var+'i' == innermostVar_vectorize.name_var :
                     splitted_var = True
                     break

        if (innermostVar_vectorize.type == 'RVar') | (splitted_var == True) :
           new_schedule.optimizations.append(VectorizeOptimization(func, innermostVar_vectorize, False))
      return new_schedule

