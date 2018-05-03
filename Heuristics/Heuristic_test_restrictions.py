import hashlib
import GenerationOfOptimizations.settings
from GenerationOfOptimizations.settings import *
import Restrictions_
from Restrictions_ import *
import Schedule
from Schedule import *

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
                                                    None, None, True, False)
               restrictions.append(split_restriction)
               unroll_restriction = UnrollRestriction(function,False,False)
               restrictions.append(unroll_restriction)
               vectorize_restriction = VectorizeRestriction(function, "x" ,True, True, False)
               restrictions.append(vectorize_restriction)


               #parallel_res = ParallelRestriction(function, True, False, True)

        for consumer in program.functions :
           if function.name_function in consumer.list_producers :
              store_atres = StoreAtRestriction(function, consumer, False)
              restrictions.append(store_atres)
              compute_atRes = ComputeAtHillClimbing(function, consumer, True, True)
              restrictions.append(compute_atRes)
    return restrictions

