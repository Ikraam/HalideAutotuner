import ComputeAtOptimization
from ComputeAtOptimization import *
import Optimization
from Optimization import Optimization
import Restrictions_.StoreAtRestriction_
from Restrictions_.StoreAtRestriction_ import *

class StoreAtOptimization(Optimization):
    def __init__(self, func, variable, consumer, enable):
        super(StoreAtOptimization, self).__init__(func)
        if consumer == None :
            self.variable = 'root'
        else :
            self.consumer = consumer
            self.variable = variable
        self.enable = enable

    def __str__(self):
       if self.enable :
        consumer_name = self.consumer.name_function
        producer_name = self.func.name_function
        if 'update' in producer_name :
            producer_name = producer_name.split(".")[0]
        if 'update' in consumer_name :
            consumer_name = consumer_name.split(".")[0]
        if self.variable.name_var == 'root':
            return '{}.store_root();'.format(producer_name)
        name_var = self.variable.name_var
        return '{}.store_at({},{});'.format(producer_name, consumer_name, name_var)
       else :
           return ''

    @staticmethod
    def append_optimizations(schedule, program):
        new_schedule = schedule.copy_schedule()
        for optim in new_schedule.optimizations :
            if isinstance(optim, ComputeAtOptimization):
                new_schedule.optimizations.append(StoreAtOptimization(optim.func, optim.variable,\
                                                                      optim.consumer, True))
        return new_schedule


    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, StoreAtRestriction):
                if (restriction.func == self.func) & (restriction.consumer == self.consumer):
                    return restriction
        return None
