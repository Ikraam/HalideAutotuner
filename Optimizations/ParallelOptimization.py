import Optimization
from Optimization import Optimization
import Restrictions_.ParallelRestriction_
from Restrictions_.ParallelRestriction_ import *


class ParallelOptimization(Optimization):
    def __init__(self, func, variable, enable):
        super(ParallelOptimization, self).__init__(func)
        self.variable = variable
        self.enable = enable


    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, ParallelRestriction):
                if (restriction.func == self.func):
                    return restriction
        return None


    def __str__(self):
        if self.enable :
             return '{}.parallel({});'.format(self.func, self.variable.name_var)
        else :
            return ''

    @staticmethod
    def append_optimizations(program, schedule):
        new_schedule = schedule.copy_schedule()
        for func in program.functions :
              if func.is_consumer():
                 outermost_var = func.outermost_variable(schedule)
                 new_schedule.optimizations.append(ParallelOptimization(func, outermost_var, True))
        return new_schedule

