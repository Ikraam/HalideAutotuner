import Optimization
from Optimization import Optimization
import Restrictions_.FuseRestriction_
from Restrictions_.FuseRestriction_ import *




#Wa can have a fuse optimization
class FuseOptimization(Optimization):
    def __init__(self, func, variable1, variable2, fused_var, enable):
        super(FuseOptimization, self).__init__(func)
        self.variable1 = variable1
        self.variable2 = variable2
        self.fused_var = fused_var
        self.enable = enable

    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, FuseRestriction):
                if restriction.func == self.func:
                    return restriction
        return None


    def __str__(self):
        if self.enable :
            return '{}.fuse({}, {} , {});'.format(self.func, self.variable1, self.variable2, self.fused_var)
        else :
            return ''

    @staticmethod
    def append_optimizations(schedule, program):


       def list_vars_of_func_after_reorder(func, schedule):
        '''
        :param schedule: the schedule applied to the program
        :return: the order of 'self' function loops
        '''
        list_of_vars = list()
        # get the reorder contained in function listVariables
        for var in func.list_variables :
            list_of_vars.append(var)

        # find the reorder optimization applied to function 'self' and
        for optim in schedule.optimizations :
            if isinstance(optim, ReorderOptimization):
                if optim.func == func :
                    list_of_vars = list()
                    for var in optim.variables :
                        list_of_vars.append(var)
        return list_of_vars

       new_schedule = schedule.copy_schedule()
       new_program = program.copy_program()
       for func in new_program.functions :
         if func.is_consumer():
              inner_permit = False
              outer_permit = True
              #list_vars = list_vars_of_func_after_reorder(func, new_schedule)
              list_vars = func.list_variables
              if inner_permit :
                 if len(list_vars) > 1 :
                     if list_vars[0].type_of_var() == list_vars[1].type_of_var():
                        name_var1 = list_vars[0].name_var
                        name_var2 = list_vars[1].name_var
                        name_var_fused = name_var1+name_var2+'$'
                        extent_var_fused = list_vars[0].extent_var * list_vars[1].extent_var
                        new_schedule.optimizations.append(FuseOptimization(func, list_vars[0], \
                                                                           list_vars[1], Variable(name_var_fused, \
                                                                           extent_var_fused, list_vars[0].type_of_var()), False))
              if outer_permit :
                 if len(list_vars)  > 1 :
                     if list_vars[len(list_vars)-1].type_of_var() == list_vars[len(list_vars) - 2].type_of_var():
                        name_var1 = list_vars[len(list_vars)-1].name_var
                        name_var2 = list_vars[len(list_vars)-2].name_var
                        name_var_fused = name_var1+name_var2+'$'
                        extent_var_fused = list_vars[len(list_vars)-1].extent_var * list_vars[len(list_vars)-2].extent_var
                        new_schedule.optimizations.append(FuseOptimization(func, list_vars[len(list_vars)-1], \
                                                                               list_vars[len(list_vars)-2], \
                                                                           Variable(name_var_fused, extent_var_fused, \
                                                                           list_vars[len(list_vars)-1].type_of_var()), False))


       return new_schedule
