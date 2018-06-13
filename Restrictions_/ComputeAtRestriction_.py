import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.ComputeAtOptimizationGenerator
from GenerationOfOptimizations.ComputeAtOptimizationGenerator import *


# Compute_at Restriction is a restriction on compute_at optimization for function func
class ComputeAtRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, consumer, enable):
        super(ComputeAtRestriction, self).__init__(func, enable)
        # the consumer concerned by the optimization
        self.consumer = consumer


class ComputeAtFixValue(ComputeAtRestriction):
    def __init__(self, func, consumer, fix_value, enable):
        super(ComputeAtFixValue, self).__init__(func, consumer, enable)
        # the consumer concerned by the optimization
        self.fix_value = fix_value

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
          if self.fix_value != None :
              schedule.optimizations[index].variable = self.fix_value
              ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)
              return False
          else :
              return True




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
                  nb_variables = len(schedule.vars_of_func(consumer))
                  medium_variable_index = nb_variables // 2
                  schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index]
                  print schedule
                  time = schedule.test_schedule(program.args, id_program)
                  print 'medium schedule :',schedule, producer.name_function
                  if len(schedule.vars_of_func(consumer)) > 2 :
                    schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index+1]
                    print schedule
                    time_right = schedule.test_schedule(program.args, id_program)
                    print 'schedule right',schedule, time_right, producer.name_function
                    schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index-1]
                    time_left = schedule.test_schedule(program.args, id_program)
                  else :
                    if len(schedule.vars_of_func(consumer)) == 2 :
                      schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[0]
                      time_left = schedule.test_schedule(program.args,id_program)
                      schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[1]
                      time_right = schedule.test_schedule(program.args, id_program)

                  schedule.optimizations[index].variable = Variable("root",0,"Var")
                  print schedule
                  time_root = schedule.test_schedule(program.args, id_program)
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
       nb_variables = len(schedule.vars_of_func(consumer))
       medium_variable_index = nb_variables // 2
       left_side_variables = schedule.vars_of_func(consumer)[:medium_variable_index]
       right_side_variables = schedule.vars_of_func(consumer)[medium_variable_index+1:]
       [go, time_direction] = ComputeAtHillClimbing.go_left_right_compute_at_hill(schedule, program, \
                                                                                  index, consumer, \
                                                                                  id_program, producer)

       if go == "Left":
          var_best_index = medium_variable_index-1
          for var in reversed(left_side_variables):
           schedule.optimizations[index].variable = var
           print schedule
           time = schedule.test_schedule(program.args, id_program)
           print 'go left : ',schedule, producer.name_function
           if time > time_direction :
               schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[var_best_index]
               break
           else :
               time_direction = time
               var_best_index = schedule.vars_of_func(consumer).index(var)

           ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)

       if go == "Right":
          var_best_index = medium_variable_index+1
          for var in right_side_variables:
           schedule.optimizations[index].variable = var
           print schedule
           time = schedule.test_schedule(program.args, id_program)
           print 'go right : ',schedule, producer.name_function
           if time > time_direction :
              schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[var_best_index]
              break
           else :
               time_direction = time
               var_best_index = schedule.vars_of_func(consumer).index(var)
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
          schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index]
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)


