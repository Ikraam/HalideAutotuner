#-*- coding: utf-8 -*-
import time
import abc
import Restriction_
from Restriction_ import Restriction
import GenerationOfOptimizations.ComputeAtOptimizationGenerator
from GenerationOfOptimizations.ComputeAtOptimizationGenerator import *
ai = u"é"
aie = u"è"
a = u"à"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'





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
                  time.sleep(5)
                  settings.indexes_to_color([index])
                  print '--------------------------------------------------------------'
                  print 'Schedule m'+ai+'dian:'
                  time_ = schedule.test_schedule(program.args, id_program, program)
                  print '--------------------------------------------------------------'
                  if len(schedule.vars_of_func(consumer)) > 2 :
                    schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index+1]
                    time.sleep(9)
                    print 'Schedule droit :'
                    time_right = schedule.test_schedule(program.args, id_program, program)
                    schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index-1]
                    time.sleep(5)
                    print 'Schedule gauche :'
                    time_left = schedule.test_schedule(program.args, id_program, program)
                    print '--------------------------------------------------------------'
                  else :
                    if len(schedule.vars_of_func(consumer)) == 2 :
                      schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[0]
                      time_left = schedule.test_schedule(program.args,id_program, program)
                      schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[1]
                      time_right = schedule.test_schedule(program.args, id_program, program)

                  schedule.optimizations[index].variable = Variable("root",0,"Var")
                  print 'Schedule Root : '
                  time_root = schedule.test_schedule(program.args, id_program, program)
                  print '--------------------------------------------------------------'
                  #print '\n (Time medium : {}), (Time right : {}), (Time left : {})\n '.format(time_, time_right, time_left)
                  time_direction = float('inf')
                  if (( time_ != float('inf')) & (time_ <= time_left)) & (time_ <= time_right):
                      go = "Medium"
                      print color.GREEN+'(Temps m'+ai+'dian : '+str(time_)+')'+color.END+', (Temps droit : {}), (Temps gauche : {})'.format(time_right, time_left)
                      time.sleep(5)
                      time_direction = time_
                  if ((time_ == float('inf')) | (time_left < time_)) | (time_right < time_):
                     #print '\n (Time root : {}), (Time right : {}), (Time left : {})\n'.format(time_root, time_right, time_left)
                     if (time_root < time_right) & (time_root < time_left) :
                            print color.GREEN+'(Temps root : '+str(time_root)+')'+color.END+', (Temps droit : {}), (Temps gauche : {})'.format(time_right, time_left)
                            time.sleep(5)
                            go = "Root"
                            time_direction = time_root
                     else :
                          if time_right > time_left : ## go left
                             if time_left < time_root :
                                 print '(Temps m'+ai+'dian : '+str(time_)+'), (Temps droit : '+str(time_right)+'), '+color.GREEN+'(Temps gauche : '+str(time_left)+')'+color.END
                                 time.sleep(5)
                                 go = "Left"
                                 time_direction = time_left
                             else :
                                 go = "Root"
                                 time_direction = time_root
                          else : ## go right
                            if time_right < time_root :
                                print '(Temps m'+ai+'dian : '+str(time_)+'), '+color.GREEN+'(Temps droit : '+str(time_right)+')'+color.END+', (Temps gauche : '+str(time_left)+')'
                                time.sleep(5)
                                go = "Right"
                                time_direction = time_right
                            else :
                                go = "Root"
                                time_direction = time_root
                  settings.indexes_to_color(None)
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
           time = schedule.test_schedule(program.args, id_program, program)
           print 'Se diriger vers la gauche : '
           settings.indexes_to_color([index])
           print schedule.str_colors(settings.get_indexes())
           settings.indexes_to_color(None)
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
           time = schedule.test_schedule(program.args, id_program, program)
           print 'Se diriger vers la droite : '
           settings.indexes_to_color([index])
           print schedule.str_colors(settings.get_indexes())
           settings.indexes_to_color(None)
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
          print 'Aller vers le root :'
          settings.indexes_to_color([index])
          print schedule.str_colors(settings.get_indexes())
          settings.indexes_to_color(None)
          schedule.optimizations[index].variable = Variable("root",0,None)
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)

       if go == "Medium":
          print 'Rester sur la m'+ai+'diane : '
          settings.indexes_to_color([index])
          print schedule.str_colors(settings.get_indexes())
          settings.indexes_to_color(None)
          schedule.optimizations[index].variable = schedule.vars_of_func(consumer)[medium_variable_index]
          ComputeAtOptimizationGenerator.explore_possibilities(schedule, index + 1, program, \
                                                                      list(), set_restrictions, id_program, \
                                                                      index_order_optimization, \
                                                                      order_optimization)


