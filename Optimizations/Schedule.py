import ScheduleExecution
import Optimizations.SplitOptimization
from Optimizations.SplitOptimization import SplitOptimization
import Optimizations.ReorderOptimization
from Optimizations.ReorderOptimization import ReorderOptimization
import Optimizations.ReorderStorageOptimization
from Optimizations.ReorderStorageOptimization import ReorderStorageOptimization
import Optimizations.TileOptimization
from Optimizations.TileOptimization import TileOptimization
import Optimizations.FuseOptimization
from Optimizations.FuseOptimization import FuseOptimization
import Optimizations.ComputeAtOptimization
from Optimizations.ComputeAtOptimization import ComputeAtOptimization
import Optimizations.StoreAtOptimization
from Optimizations.StoreAtOptimization import StoreAtOptimization
import Optimizations.ParallelOptimization
from Optimizations.ParallelOptimization import ParallelOptimization
import Optimizations.VectorizeOptimization
from Optimizations.VectorizeOptimization import VectorizeOptimization
import Optimizations.UnrollOptimization
from Optimizations.UnrollOptimization import UnrollOptimization
import Program
from Program import Variable



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

    def test_schedule(self, program, id_program):
        sched_exec = ScheduleExecution.ScheduleExecution(program.args, 1000)
        time = sched_exec.test_schedule(self, id_program)
        return time



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
            new_optim = ReorderOptimization(optim.func, optim.variables[:], optim.enable)
        if isinstance(optim, UnrollOptimization):
            new_optim = UnrollOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, ParallelOptimization):
            new_optim = ParallelOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, VectorizeOptimization):
            new_optim = VectorizeOptimization(optim.func, optim.variable, optim.enable)
        if isinstance(optim, ReorderStorageOptimization):
            new_optim = ReorderStorageOptimization(optim.func, optim.variables)
        if isinstance(optim, FuseOptimization):
            new_optim = FuseOptimization(optim.func, optim.variable1, optim.variable2, optim.fused_var,\
                                         optim.enable)
        if isinstance(optim, ComputeAtOptimization):
            new_optim = ComputeAtOptimization(optim.func, optim.variable, optim.consumer, optim.enable)
        if isinstance(optim, StoreAtOptimization):
            new_optim = StoreAtOptimization(optim.func, optim.variable, optim.consumer, optim.enable)
        list_of_optim.append(new_optim)
      new_schedule = Schedule(list_of_optim, self.args)
      return new_schedule

