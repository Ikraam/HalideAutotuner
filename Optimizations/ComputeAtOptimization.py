import Optimization
from Optimization import Optimization
import Restrictions_.ComputeAtRestriction_
from Restrictions_.ComputeAtRestriction_ import *

class ComputeAtOptimization(Optimization):
    def __init__(self, func, variable, consumer, enable):
        super(ComputeAtOptimization, self).__init__(func)
        if consumer == None :
            self.variable = 'root'
        else :
            # The consumer function
            self.consumer = consumer
            # The variable concerned by compute_at optimization
            self.variable = variable
            self.enable = enable

    def __str__(self):
      consumer_name = self.consumer.name_function
      producer_name = self.func.name_function
      if 'update' in producer_name :
            producer_name = producer_name.split(".")[0]
      if 'update' in consumer_name :
            consumer_name = consumer_name.split(".")[0]
      if self.enable :
        if self.variable.name_var == 'root':
            return '{}.compute_root();'.format(producer_name)
        name_var = self.variable.name_var
        return '{}.compute_at({},{});'.format(producer_name, consumer_name, name_var)
      else :
          return ''


    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, ComputeAtRestriction):
                if (restriction.func == self.func) & (restriction.consumer == self.consumer):
                    return restriction
        return None


    @staticmethod
    def append_optimizations(schedule, program):
        new_schedule = schedule.copy_schedule()
        dict_func = program.functions_of_program()
        for func in program.functions :
          if func.is_consumer():
             for producer in func.list_producers:
                 if dict_func[producer].is_consumer():
                    new_schedule.optimizations.append(ComputeAtOptimization(dict_func[producer], \
                                                                            Variable('root',0, "Var")\
                                                                            ,func, True))
        return new_schedule
