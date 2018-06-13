import hashlib
import Schedule
import GenerationOfOptimizations.settings
from GenerationOfOptimizations.settings import *




def generate_exhaustive_schedules(program, args):
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
    append_and_explore_optim(schedule, program, id_program, list(), 0, order_optimizations)
