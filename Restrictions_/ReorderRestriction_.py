import Restriction_
from Restriction_ import Restriction
import abc

import GenerationOfOptimizations.ReorderOptimizationGenerator
from GenerationOfOptimizations.ReorderOptimizationGenerator import *



class ReorderRestriction(Restriction):
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
        super(ReorderRestriction, self).__init__(func, enable)


# Reorder Restriction is a restriction on reorder optimization for function func
class ReorderFixRestriction(ReorderRestriction):
    def __init__(self, func, fix_reorder, enable):
        super(ReorderFixRestriction, self).__init__(func, enable)
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

