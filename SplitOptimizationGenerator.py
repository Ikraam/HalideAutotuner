import OptimizationGenerator
from OptimizationGenerator import OptimizationGenerator
import settings
from settings import *
import Schedule
from Schedule import *
import math
import Program
from Program import *

class SplitOptimizationGenerator(OptimizationGenerator):



  @staticmethod
  def update_optim__after_split(optimizations, func, var, split_factor, index, elemSupp, program, setRestrictions):
      '''
      :param optimizations: the current list of optimizations
      :param func: function of the splitted variable
      :param var: splitted variable
      :param split_factor:
      :param index: the index of the current optimization in optimizations
      :param elemSupp: the deleted elements from optimizations
      :param program: an object describing functions and their variables in the source
      :param setRestrictions : restrictions related to generated schedules
      :return: returns optimizations without optimizations on x, but with optimizations on xo and xi
      '''
      for function in program.functions :
          if function == func :
              for variable in function.list_variables :
                  if variable.name_var == var.name_var+'o':
                      varOuter = variable
                  if variable.name_var == var.name_var+'i':
                      varInner = variable

      newList = list()
      for pointToIndex in xrange(0, len(optimizations)):
        if pointToIndex == index :                                      ## Instead of split_x, 1 we put split_x_xo_xi, split_factor
           newList.append(SplitOptimization(func, split_factor, var))
           splittedVar = var.name_var+'o'                                ## if the variable has a combinaison of o,i, with length bigger that nesting
           levelSplitOfVar = SplitOptimizationGenerator.nesting_split_of_var(setRestrictions, func, var)
           if SplitOptimizationGenerator.split_again(splittedVar, levelSplitOfVar):
             splitOptimization = SplitOptimization(func, 1, varOuter)
             newList.append(splitOptimization)
             splitOptimization = SplitOptimization(func, 1, varInner)
             newList.append(splitOptimization)
        else :
            if isinstance(optimizations[pointToIndex], SplitOptimization) == False :
                newList.append(optimizations[pointToIndex])
            else :
                if (optimizations[pointToIndex].variable != var) | (optimizations[pointToIndex].func != func) :
                    newList.append(optimizations[pointToIndex])               ## add the other optimization of optimizations to newList
                else :
                    elemSupp.append(optimizations[pointToIndex])
      return newList


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
  def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram,\
                                                           index_order_optimization, order_optimization):
    '''

    :param listCfg: the current list of optimizations
    :param index: the index of the current optimization in listCfg
    :param program: an object discribing the functions and their variables
    :param elemSupp: the optimizations deleted once split = True
    :param setRestrictions: restrictions applied on schedule optimizations
    :param idProgram: the id of the current program
    :return: a valid configuration which contains only split optimizations
    '''

    # If we have a valid schedule which contains only split optimizations
    if len(schedule.optimizations) == index:
      settings.append_and_explore(schedule, program, idProgram, setRestrictions,index_order_optimization,\
                                  order_optimization)
      return schedule

    else:
        # If we are on a split optimization
        if isinstance(schedule.optimizations[index],SplitOptimization) :
            func = schedule.optimizations[index].func
            var = schedule.optimizations[index].variable
            dim = schedule.optimizations[index].dimx()
            max_split_fct = var.extent_var // 2
            # if dim is bigger than 4, and the split optimization so we can split the variable var

            if (dim >= 4) & (SplitOptimizationGenerator.nesting_split_of_var(setRestrictions, func, var) > 0) :
              for split_factor in map(lambda v : pow(2,v), reversed(range(0,int(math.log(max_split_fct, 2)+1)))):
                func = schedule.optimizations[index].func
                var = schedule.optimizations[index].variable
                dim = schedule.optimizations[index].dimx()
                SplitOptimizationGenerator.replace_var_split(program, func, var, split_factor)
                elemSupp = list()
                schedule.optimizations = SplitOptimizationGenerator.update_optim__after_split(schedule.optimizations, func ,var ,split_factor,index, elemSupp, program, setRestrictions)
                toRemember = [dim, elemSupp]
                SplitOptimizationGenerator.explore_possibilities(schedule, index+1, program, toRemember, \
                                                                 setRestrictions, idProgram\
                                                                 , index_order_optimization, \
                                                                 order_optimization)
                func = schedule.optimizations[index].func
                var = schedule.optimizations[index].variable
                SplitOptimizationGenerator.update_cfg_undo_split(schedule.optimizations, func, var, index, toRemember[1], setRestrictions)
                SplitOptimizationGenerator.replace_var_un_split(program, func, var, toRemember[0])
            else :
              SplitOptimizationGenerator.explore_possibilities(schedule,index+1, program, None, setRestrictions, \
                                                                            idProgram,index_order_optimization, \
                                                                            order_optimization)
        else :
            # if the current optimization is not a split optimization, just move to the next optimization
            SplitOptimizationGenerator.explore_possibilities(schedule,index+1, program, None, setRestrictions, \
                                                                            idProgram, index_order_optimization, \
                                                                            order_optimization)




  @staticmethod
  def replace_var_un_split(program, func, var, dimx):
     '''
      :param program: information about program functions
      :param func: the function concerned by the split optimization
      :param var: the splitted variable
      :param dimx: dimension of the splitted variable
      :return: unset xi and xo from variables of function func and reset the x variable
     '''
     for function in program.functions:
        if function == func :
          vars_dict = func.vars_of_func_dict()
          if var.name_var not in vars_dict.keys():
            for variable in function.list_variables :
                if variable.name_var == var.name_var+'i':
                    index = function.list_variables.index(variable)
                    function.list_variables[index] = var
                if variable.name_var == var.name_var+'o':
                    function.list_variables.remove(variable)




  @staticmethod
  def replace_var_split(program, func, var, split_factor):
     '''

      :param func: the function concerned by the split optimization
      :param var: the splitted variable
      :param split_factor: the factor of split
      :param program: information about functions of the program
      :return: update on list variables of function func in program
     '''
     if split_factor > 1 :
       for function in program.functions:
        if function == func :
            new_list_var = list()
            for variable in func.list_variables:
                if variable == var :
                    dimVar = variable.extent_var
                    variable = Variable(var.name_var +'i', split_factor, var.type)
                    new_list_var.append(variable)
                    variable = Variable(var.name_var +'o', dimVar // split_factor, var.type)
                    new_list_var.append(variable)
                else :
                    new_list_var.append(variable)
            func.list_variables = new_list_var


  @staticmethod
  def splitAgain(var_splitted, nesting):
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
  def update_cfg_undo_split(optimizations, func, var, index, elemSupp, setRestrictions):

     '''
      :param optimizations: the current list of optimizations
      :param func: function of the splitted variable
      :param var: the splitted variable
      :param index: the index of the current optimization in listCfg
      :param elemSupp: the elements that must be appended to listCfg that were deleted when Split enabled
      :param program: information about program functions
      :return: listCfg + elemSupp and we delete the appended elements when split was enabled
      '''

     ## Remove split(x,xo,x1, sf) , put no split instead.
     optimizations[index] = SplitOptimization(func, 1, var)
     ## retrieve all the deleted optimizations from schedule.optimizations
     for optim in elemSupp:
        optimizations.append(optim)
     levelOfNesting = SplitOptimizationGenerator.nesting_split_of_var(setRestrictions, var, func)
     for optim in optimizations :
       if isinstance(optim, SplitOptimization):
        if SplitOptimizationGenerator.split_again(var.name_var, levelOfNesting):
            if (optim.func == func) & (optim.variable.name_var== var.name_var+'o'):
                optimizations.remove(optim)
            if (optim.func == func) & (optim.variable.name_var== var.name_var+'i'):
                optimizations.remove(optim)


  @staticmethod
  def nesting_split_of_var(setRestrictions, func, var):
      '''
    :param setRestrictions: restrictions related to generated schedules
    :param func: function concerned by the split restriction
    :param var: var concerned by the split restriction
    :return: maximum nesting of split fixed of the variable var in function func
      '''
      return 1
      '''for restriction in setRestrictions :
        if isinstance(restriction, SplitRestriction):
            if (restriction.func == func) & (restriction.variable == var) :
                if restriction.maxNestingOfSplit == None :
                    return 0
                else :
                    return restriction.maxNestingOfSplit'''
