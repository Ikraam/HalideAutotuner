import Optimization
from Optimization import Optimization
import Restrictions_.ReorderRestriction_
from Restrictions_.ReorderRestriction_ import *




#We can have a reorder optimization
class ReorderOptimization(Optimization):
    def __init__(self, func, variables, enable):
        super(ReorderOptimization, self).__init__(func)
        self.variables = variables
        self.enable = enable


    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, ReorderRestriction):
                if restriction.func == self.func:
                    return restriction
        return None


    def __str__(self):
      if self.enable :
        str_to_return = '\n'+str(self.func)
        str_to_return = str_to_return+'.reorder('
        for var in self.variables :
            if var.name_var.count('.') == 1 :
                # I need to count the number of letters after this point
                length = 0
                for index in xrange(0, len(var.name_var)):
                    if var.name_var[index] == '.' :
                        length = len(var.name_var[index+1:])
                variable_without_dot = var.name_var
                if length > 1 :
                    ## I need to delete the . from var
                    for char in variable_without_dot :
                        if char == '.':
                            variable_without_dot = variable_without_dot.replace(char, '')
                str_to_return=str_to_return+variable_without_dot+','

            else :
              if var.name_var.count('.') > 1 :
                for char in variable_without_dot :
                        if char == '.':
                            variable_without_dot = variable_without_dot.replace(char, '')
                str_to_return=str_to_return+variable_without_dot+','
              else :
                str_to_return=str_to_return+str(var)+','
        str_to_return = str_to_return[0:len(str_to_return)-1]
        str_to_return = str_to_return+');'
        return str_to_return
      else :
          return ''

    @staticmethod
    def append_optimizations(schedule, program):
      first = False
      # unchoosen : represents the list of variables of the first func consumer
      unchoosen = list()
      # new_schedule : is a copy of schedule
      new_schedule = schedule.copy_schedule()
      for func in program.functions:
         if func.is_consumer():
               #if func.permit_optimization(setRestrictions, ReorderRestriction):
               reorderOptim = ReorderOptimization(func, list(), True)
               # Add to schedule all the reorder optimizations
               new_schedule.optimizations.append(reorderOptim)
               if first == False :
                   # we are on the first consumer
                   first = True
                   list_vars = list()
                   for variable in func.list_variables :
                       list_vars.append(variable)
                   # set unchoosen to the list variables of reorder optimizations for function func
                   unchoosen = list_vars
      return [new_schedule, unchoosen]

