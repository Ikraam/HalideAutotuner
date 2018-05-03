import abc
import math
import re
from abc import ABCMeta
import GenerationOfOptimizations.SplitOptimizationGenerator
import GenerationOfOptimizations.ParallelOptimizationGenerator
import GenerationOfOptimizations.TileOptimizationGenerator
import GenerationOfOptimizations.ComputeAtOptimizationGenerator
import GenerationOfOptimizations.FuseOptimizationGenerator
import GenerationOfOptimizations.ReorderOptimizationGenerator
from GenerationOfOptimizations.ReorderOptimizationGenerator import *
from GenerationOfOptimizations.FuseOptimizationGenerator import *
from GenerationOfOptimizations.ComputeAtOptimizationGenerator import *
from GenerationOfOptimizations.TileOptimizationGenerator import *
from GenerationOfOptimizations.ParallelOptimizationGenerator import *


# Restriction is applied to a function to not let an optimization takes all the possible combination
class Restriction:
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      self.func = func
      # enable to indicate the enability of the optimization
      self.enable = enable


# Split Restriction is a restriction on split optimization for function func over the variable variable
class SplitRestriction(Restriction):
    def __init__(self, func, fixe_split_factor, variable, max_nesting_of_split, max_split_factor, skip_one, pow_two_split, enable):
        super(SplitRestriction, self).__init__(func, enable)
        self.variable = variable
        # When variable must be splitted with one fixed split factor.
        self.fixe_split_factor = fixe_split_factor
        # When a variable can be splitted recursively.
        self.max_nesting_of_split=max_nesting_of_split
        # When a variable can be splitted from 1 to max_split_factor.
        self.max_split_factor = max_split_factor
        # When a variable is splitted from 2 to max.
        self.skip_one = skip_one
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split


    def __str__(self):
        string_to_return = '\n split over F : '+str(self.func)+' and V :'+str(self.variable)+' with fixe_split_factor : '+str(self.fixe_split_factor)
        string_to_return = string_to_return +' with maxNesting : ' + str(self.max_nesting_of_split) + ' with max_split_factor : ' + str(self.max_split_factor)
        return string_to_return


    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        func = self.func
        var = self.variable
        dim = self.variable.extent_var
        first_factor = 1
        last_factor = var.extent_var // 2
        nesting = 1
        if self.max_split_factor != None :
           last_factor = self.max_split_factor
        if self.skip_one == True :
           first_factor = 2
        if self.max_nesting_of_split != None :
            nesting = self.max_nesting_of_split


        if self.pow_two_split :
            list_values = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor, 2)),\
                                                                  int(math.log(last_factor, 2)+1))))
        else :
            list_values = [x for x in range(first_factor, last_factor) if x is not 0 and dim % x == 0 \
                                       and x <= last_factor//2]

        if ((dim >= 4) & (nesting > 0)) & (self.enable == True):
              for split_factor in list_values:
                func = self.func
                var = self.variable
                dim = self.variable.extent_var
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.replace_var_split(program, func, var, split_factor)
                elemSupp = list()
                schedule.optimizations = GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.update_optim__after_split(\
                    schedule.optimizations, func ,var ,split_factor,index, elemSupp, program, \
                    set_restrictions,nesting)
                toRemember = [dim, elemSupp]
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.explore_possibilities(schedule, index + 1, program, toRemember, \
                                                                 set_restrictions, id_program \
                                                                 , index_order_optimization, \
                                                                 order_optimization)
                func = schedule.optimizations[index].func
                var = schedule.optimizations[index].variable
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.update_cfg_undo_split(schedule.optimizations, func, var, \
                                                                 index, toRemember[1], set_restrictions,\
                                                                 nesting)
                GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.replace_var_un_split(program, func, var, toRemember[0])
        else :
              GenerationOfOptimizations.SplitOptimizationGenerator.SplitOptimizationGenerator.explore_possibilities(schedule, index + 1, program, None, \
                                                               set_restrictions, \
                                                               id_program, index_order_optimization, \
                                                               order_optimization)

        return False




# Unroll Restriction is a restriction on unroll optimization for function func
class UnrollRestriction(Restriction):
    def __init__(self, func, two_innermost, enable):
        super(UnrollRestriction, self).__init__(func, enable)
        self.two_innermost = two_innermost

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        if (self.two_innermost == True) & (self.enable == True) :
           return True
        else :
            var = schedule.optimizations[index].variable
            func = schedule.optimizations[index].func
            [inner1, inner2] = func.two_innermost_variable_for_unroll(schedule)
            if inner1 == var :
              if self.enable == True :
                schedule.optimizations[index].enable = True
                UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, list()\
                                                                       , set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
              schedule.optimizations[index].enable = False
              UnrollOptimizationGenerator.explore_possibilities(schedule, index+1, program, list(), \
                                                                  set_restrictions, id_program, \
                              index_order_optimization, order_optimization)
            return False






# Vectorize Restriction is a restriction on vectorize optimization for function func
class VectorizeRestriction(Restriction):
    def __init__(self, func, legal_innermost, fix, fixed_value, enable):
        super(VectorizeRestriction, self).__init__(func, enable)
        # Indicate the legal variable to be vectorized
        self.legal_innermost = legal_innermost
        self.fix = fix
        self.fixed_value = fixed_value

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
       if self.enable == True :
            optim = schedule.optimizations[index]
            if re.match(self.legal_innermost+"(i)*",optim.variable.name_var):
                if (self.fix == True) & (self.fixed_value != None) :
                    schedule.optimizations[index].enable = self.fixed_value
                    VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
                    return False
                else :
                    return True
            return True
       else :
           schedule.optimizations[index].enable = False
           VectorizeOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
           return False







class TileRestriction(Restriction):
    def __init__(self, func, fix_factor_in, fix_factor_out, variable_in, variable_out, max_factor_in, max_factor_out,
                 skip_one_in, skip_one_out, pow_two_split, nesting, enable):
        super(TileRestriction, self).__init__(func, enable)
        self.variable_in = variable_in
        self.variable_out = variable_out
        # When variable must be splitted with one fixed split factor.
        self.fix_factor_in = fix_factor_in
        self.fix_factor_out = fix_factor_out
        # When a variable can be splitted recursively.
        self.max_factor_in=max_factor_in
        self.max_factor_out=max_factor_out
        # When a variable is splitted from 2 to max.
        self.skip_one_in = skip_one_in
        self.skip_one_out = skip_one_out
        # When we want to split over power of 2 factors
        self.pow_two_split = pow_two_split
        self.nesting = nesting


    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
          if self.enable == True :
            func = schedule.optimizations[index].func
            var_in = schedule.optimizations[index].variable_in
            var_out = schedule.optimizations[index].variable_out
            dim_in = var_in.extent_var
            dim_out = var_out.extent_var
            max_factor_in = dim_in // 2
            max_factor_out = dim_out // 2
            first_factor_in = 1
            first_factor_out = 1
            nesting = 1
            if self.nesting != None :
               nesting = self.nesting
            if self.skip_one_out :
                first_factor_out = 2
            if self.skip_one_in :
                first_factor_in = 2
            if self.max_factor_in != None :
                max_factor_in = self.max_factor_in
            if self.max_factor_out != None :
                max_factor_out = self.max_factor_out

            if self.fix_factor_out :
               first_factor_out = self.fix_factor_out
               max_factor_out = first_factor_out
            if self.fix_factor_in :
                first_factor_in = self.fix_factor_in
                max_factor_in = first_factor_in


            if self.pow_two_split :
                list_values_in = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_in, 2)),\
                                                                  int(math.log(max_factor_in, 2)+1))))
                list_values_out = map(lambda v : pow(2,v), reversed(range(int(math.log(first_factor_out, 2)),\
                                                                  int(math.log(max_factor_out, 2)+1))))

            else :
                list_values_in = [x for x in range(first_factor_in, max_factor_in) if x is not 0 and dim_in % x == 0 \
                                       and x <= max_factor_in//2]
                list_values_out = [x for x in range(first_factor_out, max_factor_out) \
                                   if x is not 0 and dim_out % x == 0 \
                                       and x <= max_factor_out//2]


            if (dim_in >= 4) & (nesting > 0)  :
             if (dim_out >= 4) & (nesting > 0) :
              for tile_factor_in in list_values_in:
               for tile_factor_out in list_values_out:
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                dim_in = var_in.extent_var
                dim_out = var_out.extent_var
                TileOptimizationGenerator.replace_var_split(program, func, var_in, tile_factor_in)
                TileOptimizationGenerator.replace_var_split(program, func, var_out, tile_factor_out)

                elem_supp = list()
                schedule.optimizations = TileOptimizationGenerator.update_optim__after_tile(\
                                                                            schedule.optimizations,\
                                                                            func ,var_in, var_out ,\
                                                                            tile_factor_in,tile_factor_out,\
                                                                            index, elem_supp, program, \
                                                                            set_restrictions)
                to_remember = [dim_in, dim_out, elem_supp]
                TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, to_remember, \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, order_optimization)
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                TileOptimizationGenerator.update_cfg_undo_tile(schedule.optimizations, func, var_in, var_out, index, to_remember[2], set_restrictions)
                TileOptimizationGenerator.replace_var_un_split(program, func, var_in, to_remember[0])
                TileOptimizationGenerator.replace_var_un_split(program, func, var_out, to_remember[1])
            return False

          else :
              TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, order_optimization)
              return False


    def __str__(self):
        return 'tile restriction on in : {} and out : {}, with max_in : {} , and max_out {}, with fix_in {} and fix_out {} with skip_in {}' \
               'and skip_out {}'.format(self.variable_in, self.variable_out, self.max_factor_in, self.max_factor_out \
                                        , self.fix_factor_in, self.fix_factor_out, self.skip_one_in, self.skip_one_out)

# Parallel Restriction is a restriction on parallel optimization for function func
class ParallelRestriction(Restriction):
    def __init__(self, func, fix, fixed_value, enable):
        super(ParallelRestriction, self).__init__(func, enable)
        # Indicate if the optimization Parallel must be setted at fix value and not varying
        self.fix = fix
        self.fixed_value = fixed_value

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
       if self.enable == True :
            optim = schedule.optimizations[index]
            if (self.fix == True) & (self.fixed_value != None) :
                    optim.enable = self.fixed_value
                    ParallelOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
                    return False
            else :
                    return True
       else :
           schedule.optimizations[index].enable = False
           ParallelOptimizationGenerator.explore_possibilities(schedule, index+1,program,\
                                                                 list(),set_restrictions, id_program,\
                                                                 index_order_optimization, \
                                                                 order_optimization)
           return False

# Fuse Restriction is a restriction on fuse optimization for function func
class FuseRestriction(Restriction):
    def __init__(self, func, two_innermost, two_outermost, enable):
        super(FuseRestriction, self).__init__(func, enable)
        # Indicate if we can fuse the two innermost variables of func
        self.two_innermost = two_innermost
        # Indicate if we can fuse the two outermost variables of func
        self.two_outermost = two_outermost

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
        if self.enable == False :
            schedule.optimizations[index].enable = False
            FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
        else :
            if (self.two_outermost) & (self.two_innermost == False) :
                return True
            else:
                if (self.two_outermost == False) & (self.two_innermost == False) :
                    FuseOptimizationGenerator.explore_possibilities(schedule, index + 1, program, list(), set_restrictions, id_program, \
                                                            index_order_optimization, order_optimization)
                    return False
                else :
                   if (self.two_outermost == True) & (self.two_innermost == True):
                    return True
                   else :
                      return True
                      # only innermost is True







# Reorder Restriction is a restriction on reorder optimization for function func
class ReorderRestriction(Restriction):
    def __init__(self, func, fix_reorder, enable):
        super(ReorderRestriction, self).__init__(func, enable)
        # fix_reorder is a list of variables, for example : fix_reorder = [[xi,yo], [r.x, r.y]] to say that all the reorder
        # for function func must respect that yo must appear after xi and r.y must appear after r.x
        self.fix_reorder = fix_reorder

    def __str__(self):
        return 'reorder fix :'+str(self.fix_reorder)

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization, info):

      def index_out(index_choosed, list_of_index):
           '''

             :param index:
             :param list_of_index:
             :return: True if max(listOfIndex) is bigger than index_choosed, otherwise False
            '''
           for elem in list_of_index:
               if elem > index_choosed :
                  return True
           return False

      if self.enable :
          unchoosen  = info['unchoosen']
          choosen = info['choosen']
          for i in xrange(0, len(unchoosen)):
              var = unchoosen[i]                      ## choose the variable to add in list of Reorder
              choosen.append(var)                     ## delete it from unchoosen
              elem_supp = list()
              found = False
              if len(self.fix_reorder) != 0 :
                 for list_vars in self.fix_reorder:
                     if len(list_vars) >= 2 :
                        list_of_index = list()
                        for variable in choosen :
                            try :
                               index_choosed = list_vars.index(variable.name_var)
                               if (index_out(index_choosed, list_of_index)==True):
                                   elem_supp.append(variable)
                                   found = True
                                   break
                               else :
                                   list_of_index.append(index_choosed)
                            except :
                               continue
                        if found == True :
                           found = False
                           break
              if len(elem_supp) == 0 :
                 ReorderOptimizationGenerator.explore_possibilities(schedule, index, choosen, \
                                                                 unchoosen[:i] +unchoosen[i+1:], \
                                                                 program, set_restrictions, id_program, \
                                                                 index_order_optimization, \
                                                                 order_optimization)
                 choosen.remove(var)
              else :
                 choosen.remove(var)
                 return False

      else :
          optim = schedule.optimizations[index]
          optim.enable = False
          optim.variables = optim.func.list_variables
          unchoosen = list()
          if (index+1 != len(schedule.optimizations)):
                for var in schedule.optimizations[index+1].func.list_variables :
                    unchoosen.append(var)
          choosen = list()
          ReorderOptimizationGenerator.explore_possibilities(schedule, index + 1, choosen, unchoosen, \
                                                                program, set_restrictions, id_program,
                                                                index_order_optimization, order_optimization)
          return False




# Reorder Storage Restriction is a restriction on reorder_storage optimization for function func
class ReorderStorageRestriction(Restriction):
    def __init__(self, func, fix_reorder_storage, enable):
        super(ReorderStorageRestriction, self).__init__(func, enable)
        # Same as fix_reorder of Reorder Restriction
        self.fix_reorder_storage = fix_reorder_storage



# Compute_at Restriction is a restriction on compute_at optimization for function func
class ComputeAtRestriction(Restriction):
    def __init__(self, func, consumer, enable):
        super(ComputeAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer


class ComputeAtHillClimbing(ComputeAtRestriction):
    def __init__(self, func, consumer, hill, enable):
        super(ComputeAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        self.hill = hill
        self.enable = enable



    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):
      if self.enable == False :
        schedule.optimizations[index].enable = False
        ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)
        return False
      else :
        if self.hill :
            ComputeAtHillClimbing.hill_climbing_compute_at(schedule, index, id_program, program, \
                                                       self.consumer, self.func, set_restrictions,\
                                                       index_order_optimization, \
                                                       order_optimization)
            return False
        else :
            return True

    @staticmethod
    def go_left_right_compute_at_hill(schedule, program,  index, consumer, id_program, producer):
                  nb_variables = len(consumer.list_variables)
                  medium_variable_index = nb_variables // 2
                  schedule.optimizations[index].variable = consumer.list_variables[medium_variable_index]
                  time = schedule.test_schedule(program, id_program)
                  print 'medium schedule :',schedule, producer.name_function
                  if len(consumer.list_variables) > 2 :
                    schedule.optimizations[index].variable = consumer.list_variables[medium_variable_index+1]
                    time_right = schedule.test_schedule(program, id_program)
                    print 'schedule right',schedule, time_right, producer.name_function
                    schedule.optimizations[index].variable = consumer.list_variables[medium_variable_index-1]
                    time_left = schedule.test_schedule(program, id_program)
                  else :
                    if len(consumer.list_variables) == 2 :
                      schedule.optimizations[index].variable = consumer.list_variables[0]
                      time_left = schedule.test_schedule(program,id_program)
                      schedule.optimizations[index].variable = consumer.list_variables[1]
                      time_right = schedule.test_schedule(program, id_program)

                  schedule.optimizations[index].variable = Variable("root",0,"Var")
                  time_root = schedule.test_schedule(program, id_program)
                  print 'test_root :',schedule, producer.name_function
                  print '\n \n \n time_medium {} time_right {} time_left {}\n \n \n'.format(time, time_right, time_left)
                  time_direction = float('inf')
                  if (( time != float('inf')) & (time <= time_left)) & (time <= time_right):
                      go = "Medium"
                      time_direction = time
                  if ((time == float('inf')) | (time_left < time)) | (time_right < time):
                     print '\n \n \n time_root {} time_right {} time_left {}\n \n \n'.format(time_root, time_right, time_left)
                     if (time_root < time_right) & (time_root < time_left) :
                            go = "Root"
                            time_direction = time_root
                     else :
                          if time_right > time_left : ## go left
                             if time_left < time_root :
                                 go = "Left"
                                 time_direction = time_left
                             else :
                                 go = "Root"
                                 time_direction = time_root
                          else : ## go right
                            if time_right < time_root :
                                go = "Right"
                                time_direction = time_right
                            else :
                                go = "Root"
                                time_direction = time_root

                  return [go, time_direction]


    @staticmethod
    def hill_climbing_compute_at(schedule, index, id_program, program, consumer, producer, \
                                 set_restrictions, index_order_optimization, order_optimization):
       nb_variables = len(consumer.list_variables)
       medium_variable_index = nb_variables // 2
       left_side_variables = consumer.list_variables[:medium_variable_index]
       right_side_variables = consumer.list_variables[medium_variable_index+1:]
       [go, time_direction] = ComputeAtHillClimbing.go_left_right_compute_at_hill(schedule, program, \
                                                                                  index, consumer, \
                                                                                  id_program, producer)

       if go == "Left":
          var_best_index = medium_variable_index-1
          for var in reversed(left_side_variables):
           schedule.optimizations[index].variable = var
           time = schedule.test_schedule(program, id_program)
           print 'go left : ',schedule, producer.name_function
           if time > time_direction :
               schedule.optimizations[index].variable = consumer.list_variables[var_best_index]
               break
           else :
               time_direction = time
               var_best_index = consumer.list_variables.index(var)

           ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)



       if go == "Right":
          var_best_index = medium_variable_index+1
          for var in right_side_variables:
           schedule.optimizations[index].variable = var
           time = schedule.test_schedule(program, id_program)
           print 'go right : ',schedule, producer.name_function
           if time > time_direction :
              schedule.optimizations[index].variable = consumer.list_variables[var_best_index]
              break
           else :
               time_direction = time
               var_best_index = consumer.list_variables.index(var)
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)

       if go == "Root":
          schedule.optimizations[index].variable = Variable("root",0,None)
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)

       if go == "Medium":
          schedule.optimizations[index].variable = consumer.list_variables[medium_variable_index]
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)







# Compute_at Restriction is a restriction on compute_at optimization for function func
class StoreAtRestriction(Restriction):
    def __init__(self, func, consumer, enable):
        super(StoreAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer
        # fix_compute_at is a variable which means that if this variable is set, store_at for func will be setted
        # by defaut to store_at(consumer, fix_compute_at)

    def restrict(self, schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization):

             schedule.optimizations[index].enable = self.enable
             StoreAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                       list(), set_restrictions, \
                                                                       id_program, \
                                                                       index_order_optimization, \
                                                                       order_optimization)
             return False



