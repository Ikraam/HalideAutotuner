from GenerationOfOptimizations.OptimizationGenerator import *
import Schedule
from Program import *
import math

import settings


class TileOptimizationGenerator(OptimizationGenerator):

    @staticmethod
    def explore_possibilities(schedule, index, program, elemSupp, set_restrictions, id_program, \
                              index_order_optimization, order_optimization):
     '''
          :param schedule: the current list of optimizations
          :param index: the index of the current optimization in listCfg
          :param program: an object discribing the functions and their variables
          :param elemSupp: the optimizations deleted once split = True
          :param set_restrictions: restrictions applied on schedule optimizations
          :param id_program: the id of the current program
          :return: a valid configuration which contains only split optimizations
           '''

     # If we have a valid schedule which contains only tile optimizations
     if len(schedule.optimizations) == index:
        # append next optimizations and explore them
        settings.append_and_explore_optim(schedule, program, id_program, set_restrictions, index_order_optimization, \
                                          order_optimization)

        return schedule

     else:
        # If we are on a tile optimization
        if isinstance(schedule.optimizations[index],Schedule.TileOptimization) :
          restriction = schedule.optimizations[index].there_are_restrictions(set_restrictions)
          back_execution = True
          if restriction != None :
            back_execution = restriction.restrict(schedule, program, index, set_restrictions, id_program, \
                                                                index_order_optimization, \
                                                                order_optimization)
          if back_execution == True :
            # get all the relevant information
            func = schedule.optimizations[index].func
            var_in = schedule.optimizations[index].variable_in
            var_out = schedule.optimizations[index].variable_out
            dim_in = var_in.extent_var
            dim_out = var_out.extent_var
            max_factor_in = dim_in // 2
            max_factor_out = dim_out // 2
            if (dim_in >= 4) & (TileOptimizationGenerator.nesting_split_of_var(set_restrictions, \
                                                                               func, var_in) > 0) :
             if (dim_out >= 4) & (TileOptimizationGenerator.nesting_split_of_var(set_restrictions, \
                                                                                 func, var_out) > 0) :

              for tile_factor_in in map(lambda v : pow(2,v), reversed(range(0,int(math.log(max_factor_in, 2)+1)))):
               for tile_factor_out in map(lambda v : pow(2,v), reversed(range(0,int(math.log(max_factor_out, 2)+1)))):
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                dim_in = var_in.extent_var
                dim_out = var_out.extent_var
                TileOptimizationGenerator.replace_var_split(program, func, var_in, tile_factor_in)
                TileOptimizationGenerator.replace_var_split(program, func, var_out, tile_factor_out)

                elemSupp = list()
                schedule.optimizations = TileOptimizationGenerator.update_optim__after_tile(\
                                                                            schedule.optimizations,\
                                                                            func ,var_in, var_out ,\
                                                                            tile_factor_in,tile_factor_out,\
                                                                            index, elemSupp, program, \
                                                                            set_restrictions)
                toRemember = [dim_in, dim_out, elemSupp]
                TileOptimizationGenerator.explore_possibilities(schedule, index + 1, program, toRemember, \
                                                                set_restrictions, id_program, \
                                                                index_order_optimization, order_optimization)
                func = schedule.optimizations[index].func
                var_in = schedule.optimizations[index].variable_in
                var_out = schedule.optimizations[index].variable_out
                TileOptimizationGenerator.update_cfg_undo_tile(schedule.optimizations, func, var_in, var_out, index, toRemember[2], set_restrictions)
                TileOptimizationGenerator.replace_var_un_split(program, func, var_in, toRemember[0])
                TileOptimizationGenerator.replace_var_un_split(program, func, var_out, toRemember[1])


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
                if restriction.max_nesting_of_split == None :
                    return 0
                else :
                    return restriction.max_nesting_of_split'''


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
    def update_optim__after_tile(optimizations, func, var_in, var_out, tile_factor_in, tile_factor_out, index, elem_supp, program, setRestrictions):

       new_list = list()
       for function in program.functions :
          if function == func :
              for variable in function.list_variables :
                  if variable.name_var == var_in.name_var+'o':
                      var_outer_in = variable
                  if variable.name_var == var_in.name_var+'i':
                      var_inner_in = variable
                  if variable.name_var == var_out.name_var+'o':
                      var_outer_out = variable
                  if variable.name_var == var_out.name_var+'i':
                      var_inner_out = variable


       for point_to_index in xrange(0, len(optimizations)):
        if point_to_index == index :                                      ## Instead of split_x, 1 we put split_x_xo_xi, split_factor
           new_list.append(Schedule.TileOptimization(func, tile_factor_in, tile_factor_out,var_in, \
                                                     var_out))
           splittedVar = var_in.name_var+'o'                                ## if the variable has a combinaison of o,i, with length bigger that nesting
           level_split_of_var = TileOptimizationGenerator.nesting_split_of_var(setRestrictions, func, var_in)
           if TileOptimizationGenerator.split_again(splittedVar, level_split_of_var):
             tile_optimization = Schedule.TileOptimization(func,1,1, var_outer_in, var_outer_out)
             new_list.append(tile_optimization)

        else :
            if isinstance(optimizations[point_to_index], Schedule.TileOptimization) == False :
                new_list.append(optimizations[point_to_index])
            else :
                if (optimizations[point_to_index].variable_in != var_in) | (optimizations[point_to_index].func != func) :
                    new_list.append(optimizations[point_to_index])               ## add the other optimization of optimizations to new_list
                else :
                    elem_supp.append(optimizations[point_to_index])

       return new_list



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
                    dim_var = variable.extent_var
                    variable = Variable(var.name_var +'i', split_factor, var.type)
                    new_list_var.append(variable)
                    variable = Variable(var.name_var +'o', dim_var // split_factor, var.type)
                    new_list_var.append(variable)
                else :
                    new_list_var.append(variable)
            func.list_variables = new_list_var




    @staticmethod
    def update_cfg_undo_tile(optimizations, func, var_in, var_out, index, deleted_optimizations, set_restrictions):

     '''
   :param optimizations: the current list of optimizations
   :param func: function of the splitted variable
   :param var: the splitted variable
   :param index: the index of the current optimization in optimizations
   :param deleted_optimizations: the elements that must be appended to optimizations that were deleted when Split enabled
   :param program: information about program functions
   :return: optimizations + elemSupp and we delete the appended elements when split was enabled
     '''

     ## Remove tile(x,y,xo,yo,xi,yi,f1,f2) , put no tile instead = tile(x,y,xo,yo,xi,yi,1,1).
     optimizations[index] = Schedule.TileOptimization(func, 1, 1, var_in, var_out)
     ## append all the deleted optimizations from schedule.optimizations
     for optim in deleted_optimizations:
        optimizations.append(optim)
     # level_of_nesting = 1 si we can split x only one time, 2 if we can split x, xi and xo also
     level_of_nesting = TileOptimizationGenerator.nesting_split_of_var(set_restrictions, var_in, func)
     # delete all the optimizations that are applied on func and either xo, xi, yo, yi
     for optim in optimizations :
      if (isinstance(optim, Schedule.SplitOptimization)) | \
              ((isinstance(optim, Schedule.UnrollOptimization)) | \
               (isinstance(optim, Schedule.VectorizeOptimization))):
        if TileOptimizationGenerator.split_again(var_in.name_var, level_of_nesting):
            if (optim.func == func) & (optim.variable.name_var == var_in.name_var+'o'):
                optimizations.remove(optim)
            if (optim.func == func) & (optim.variable.name_var == var_in.name_var+'i'):
                optimizations.remove(optim)

     level_of_nesting = TileOptimizationGenerator.nesting_split_of_var(set_restrictions, var_out, func)
     for optim in optimizations :
       if (isinstance(optim, Schedule.SplitOptimization)) |\
               ((isinstance(optim, Schedule.UnrollOptimization)) \
                | (isinstance(optim, Schedule.VectorizeOptimization))):
        if TileOptimizationGenerator.split_again(var_out.name_var, level_of_nesting):
            if (optim.func == func) & (optim.variable.name_var == var_out.name_var+'o'):
                optimizations.remove(optim)
            if (optim.func == func) & (optim.variable.name_var == var_out.name_var+'i'):
                optimizations.remove(optim)



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


