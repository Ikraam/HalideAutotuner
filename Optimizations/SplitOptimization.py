import Optimization
from Optimization import Optimization
import Restrictions_.SplitRestriction_
from Restrictions_.SplitRestriction_ import *


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
                 nesting = 1
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
