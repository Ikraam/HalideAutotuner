import hashlib
import GenerationOfOptimizations.settings
from GenerationOfOptimizations.settings import *
import Restrictions
from Restrictions import SplitRestriction

def generate_schedules_heuristic_test(program, args):
    order_optimizations = list()
    order_optimizations.append("Tile")
    order_optimizations.append("Split")
    order_optimizations.append("Reorder")
    order_optimizations.append("Fuse")
    order_optimizations.append("Parallel")
    order_optimizations.append("Vectorize")
    order_optimizations.append("Unroll")
    order_optimizations.append("Compute_At")
    order_optimizations.append("Store_At")
    schedule = Schedule(list(), args)
    id_program = hashlib.md5(str(program)).hexdigest()
    # define my restrictions
    restrictions = define_restrictions(program)
    append_and_explore_optim(schedule, program, id_program, restrictions, 0, order_optimizations)


def define_restrictions(program):
    restrictions = list()
    for function in program.functions :
        if function.is_consumer():
           for variable in function.list_variables :
               split_restriction = SplitRestriction(function, None, variable, 2, \
                                                    None, None, True, True)
               restrictions.append(split_restriction)
    return restrictions

