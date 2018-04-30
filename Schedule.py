import abc
import Program
from Program import *
import Restrictions
from Restrictions import *

class Schedule:
    def __init__(self, optimizations, args):
        self.optimizations = optimizations
        self.args = args

    def __str__(self):
        '''

        :return: the schedule source
        '''
        string_to_return = ''
        for optim in self.optimizations :
            if str(optim) != '':
                string_to_return=string_to_return+str(optim)
        return string_to_return



    def vars_of_func(self, func):
        '''

        :param schedule:
        :return: extract the loop nest indexes of func 'func' in the suitable order : from innermost to outermost
        '''
        list_of_variables = func.list_variables
        list_vars = list()
        for var in list_of_variables :
            list_vars.append(var)
        for optim in self.optimizations :
            if optim.func == func :
                if isinstance(optim, ReorderOptimization):
                    list_vars = optim.variables

        list_of_variables = list()
        for var in list_vars :
            list_of_variables.append(var)
        list_vars_name = list()
        for variable in list_of_variables :
            list_vars_name.append(variable.name_var)
        for optim in self.optimizations :
            if optim.func == func :
                if isinstance(optim, FuseOptimization):
                    if optim.enable :
                        if optim.func.name_function == func.name_function :
                            var1 = optim.variable1.name_var
                            type_var_var1 = optim.variable1.type
                            vardim1 = optim.variable1.extent_var
                            var2 = optim.variable2.name_var
                            vardim2 = optim.variable2.extent_var
                            index1 = list_vars_name.index(var1)
                            index2 = list_vars_name.index(var2)
                            min_index = min(index1, index2)
                            max_index = max(index1, index2)
                            list_of_variables.remove(list_of_variables[min_index])
                            list_of_variables[max_index-1]=Variable(var1+var2+'$',vardim1*vardim2, type_var_var1)
        return list_of_variables















    def copy_schedule(self):
      '''
    # Create another instance of schedule which contains the same properties as schedule
    :param self: the coppied schedule
    :return: the new instance of schedule
      '''
      list_of_optim = list()
      for optim in self.optimizations :
        if isinstance(optim, SplitOptimization):
            new_optim = SplitOptimization(optim.func, optim.split_factor, optim.variable)
        if isinstance(optim, TileOptimization):
            new_optim = TileOptimization(optim.func, optim.tile_factor_in, optim.tile_factor_out, optim.variable_in, \
                                        optim.variable_out)
        if isinstance(optim, ReorderOptimization):
            new_optim = ReorderOptimization(optim.func, optim.variables[:])
        if isinstance(optim, UnrollOptimization):
            new_optim = UnrollOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, ParallelOptimization):
            new_optim = ParallelOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, VectorizeOptimization):
            new_optim = VectorizeOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, ReorderStorageOptimization):
            new_optim = ReorderStorageOptimization(optim.func, optim.variables)
        if isinstance(optim, FuseOptimization):
            new_optim = FuseOptimization(optim.func, optim.variable1, optim.variable2, optim.fused_var, optim.enable)
        if isinstance(optim, ComputeAtOptimization):
            new_optim = ComputeAtOptimization(optim.func, optim.variable, optim.consumer)
        if isinstance(optim, StoreAtOptimization):
            new_optim = StoreAtOptimization(optim.func, optim.variable, optim.consumer)
        list_of_optim.append(new_optim)
      new_schedule = Schedule(list_of_optim, self.args)
      return new_schedule



class Optimization():
  __metaclass__ = abc.ABCMeta
  def __init__(self, func):
      ## An optimization is applied on a function
      self.func = func




class TileOptimization(Optimization):
    def __init__(self, func, tile_factor_in, tile_factor_out, variable_in, variable_out):
        super(TileOptimization, self).__init__(func)
        # The factors of the tile optimization
        self.tile_factor_in = tile_factor_in
        self.tile_factor_out = tile_factor_out
        # Two tiled variable loops
        self.variable_in = variable_in
        self.variable_out = variable_out


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


class SplitOptimization(Optimization):

    def __init__(self, func, split_factor, variable):
        super(SplitOptimization, self).__init__(func)
        # The factor of the split optimization
        self.split_factor = split_factor
        # The variable of func on which we apply the split optimization
        self.variable = variable

    def there_are_restrictions(self, set_restrictions):
        for restriction in set_restrictions :
            if isinstance(restriction, SplitRestriction):
                if (restriction.func == self.func) & (restriction.variable == self.variable):
                    return restriction
        return None


    def __str__(self):
        if self.split_factor > 1:
            if self.variable.type_of_var() == 'Var':
                return '\n {}.split({}, {} , {} ,{});'.format(self.func, self.variable.name_var,\
                                                              self.variable.name_var+'o',\
                                                              self.variable.name_var+'i',\
                                                              self.split_factor)
            else :
                ## If it's a RVar variable we may have '.' in the variable name
                splitted_var = self.variable.name_var
                for char in splitted_var :
                    if char == '.':
                        index_char = splitted_var.index(char)
                        if len(splitted_var[index_char+1:]) > 1 :
                           # So delete the '.' if the variable is not defined by the user
                           # but it's created due to the split optimization
                           splitted_var = splitted_var.replace(char, '')
                           break

                splitted_var_out = self.variable.name_var+'o'
                if '.' in splitted_var_out :
                    index_char = splitted_var_out.index('.')
                    if len(splitted_var_out[index_char+1:]) > 1 :
                           splitted_var_out = splitted_var_out.replace('.', '')

                splitted_var_in = splitted_var_out[:len(splitted_var_out)-1]+'i'

                return '\n {}.split({}, {} , {} ,{});'.format(self.func, splitted_var,\
                                                              splitted_var_out,\
                                                              splitted_var_in, \
                                                              self.split_factor)
        else :
            return ''


    @staticmethod
    def append_optimizations(schedule, program, restrictions):
        new_schedule = schedule.copy_schedule()
        for func in program.functions :
          if func.is_consumer():
              for variable in func.list_variables :
                    # Create a split a optimization with factor = 1
                 nesting = SplitOptimization.nesting_split_of_var(restrictions, variable, func)
                 if SplitOptimization.split_again(variable.name_var, nesting) :
                    splitOptimization = SplitOptimization(func, 1, variable)
                    # Append the split optimization
                    new_schedule.optimizations.append(splitOptimization)
        return new_schedule


    @staticmethod
    def split_again(var_splitted, nesting):
      '''
      :param var_splitted: the splitted variable
      :param nesting: the authorized nesting level of splitting for the variable varSplitted.
      :return: True if we can split varSplitted again, False otherwise.
      '''
      var_splitted = var_splitted[1:]                                           ## We delete the first variable
      if var_splitted == '':
          return True
      else:
          index = 0
          length = 0
          while index < len(var_splitted):
              if ((var_splitted[index] == 'o') | (var_splitted[index] == 'i')):
                  length = length+1
              else :
                  lenght = 0
              index = index +1
          if length >= nesting:
              return False
          else:
              return True


    @staticmethod
    def nesting_split_of_var(setRestrictions, func, var):
      '''
    :param setRestrictions: restrictions related to generated schedules
    :param func: function concerned by the split restriction
    :param var: var concerned by the split restriction
    :return: maximum nesting of split fixed of the variable var in function func
      '''
      return 1


    def dimx(self):
        '''

        :return: the extent of self.variable
        '''
        return self.variable.extent_var

    def name_var(self):
        """

        :return: name of self.variable
        """
        return self.variable.name_var

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



#We can have a parallel optimization
class ParallelOptimization(Optimization):
    def __init__(self, func, variable, enable):
        super(ParallelOptimization, self).__init__(func)
        self.variable = variable
        self.enable = enable


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


#Wa can have a fuse optimization
class FuseOptimization(Optimization):
    def __init__(self, func, variable1, variable2, fused_var, enable):
        super(FuseOptimization, self).__init__(func)
        self.variable1 = variable1
        self.variable2 = variable2
        self.fused_var = fused_var
        self.enable = enable


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
                    for var in optim.variables :
                        list_of_vars.append(var)
        return list_of_vars


       new_schedule = schedule.copy_schedule()
       for func in program.functions :
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


#We can have a reorder optimization
class ReorderOptimization(Optimization):
    def __init__(self, func, variables):
        super(ReorderOptimization, self).__init__(func)
        self.variables = variables

    def __str__(self):
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

    @staticmethod
    def append_optimizations(schedule, program):
      first = False
      # unchoosen : represents the list of variables of the first func consumer
      unchoosen = list()
      # new_schedule : is a copy of schedule
      new_schedule = schedule.copy_schedule()
      for func in program.functions:
         if func.is_consumer():
               print func
               #if func.permit_optimization(setRestrictions, ReorderRestriction):
               reorderOptim = ReorderOptimization(func, list())
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



# We can have a reorder storage optimization
class ReorderStorageOptimization(Optimization):
    def __init__(self, func, variables):
        super(ReorderStorageOptimization, self).__init__(func)
        # List of variables concerned by the reorder_storage optimization
        self.variables = variables

    def __str__(self):
        str_to_return = '\n'+str(self.func)
        str_to_return = str_to_return+'.reorder_storage('
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



# We can have a compute_at optimization
class ComputeAtOptimization(Optimization):
    def __init__(self, func, variable, consumer):
        super(ComputeAtOptimization, self).__init__(func)
        if consumer == None :
            self.variable = 'root'
        else :
            # The consumer function
            self.consumer = consumer
            # The variable concerned by compute_at optimization
            self.variable = variable

    def __str__(self):
        consumer_name = self.consumer.name_function
        producer_name = self.func.name_function
        if 'update' in producer_name :
            producer_name = producer_name.split(".")[0]
        if 'update' in consumer_name :
            consumer_name = consumer_name.split(".")[0]
        if self.variable.name_var == 'root':
            return '{}.compute_root();'.format(producer_name)
        name_var = self.variable.name_var
        return '{}.compute_at({},{});'.format(producer_name, consumer_name, name_var)


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
                                                                            ,func))
        return new_schedule


# We can have a store_at optimization
class StoreAtOptimization(Optimization):
    def __init__(self, func, variable, consumer):
        super(StoreAtOptimization, self).__init__(func)
        if consumer == None :
            self.variable = 'root'
        else :
            self.consumer = consumer
            self.variable = variable
    def __str__(self):
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

    @staticmethod
    def append_optimizations(schedule, program):
        new_schedule = schedule.copy_schedule()
        for optim in new_schedule.optimizations :
            if isinstance(optim, ComputeAtOptimization):
                new_schedule.optimizations.append(StoreAtOptimization(optim.func, optim.variable, optim.consumer))
        return new_schedule








