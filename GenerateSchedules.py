import hashlib
import Machine
from GenerationOfOptimizations.settings import *




COMPILE_CMD = (
  '{args.cxx} "{cpp}" -o "{bin}" -I "{args.halide_dir}/include" '
  '"{args.halide_dir}/lib/libHalide.a" -ldl -lcurses -lpthread {args.cxxflags} '
  '-DAUTOTUNE_N="{args.output_size}" -DAUTOTUNE_TRIALS={args.trials} '
  '-DAUTOTUNE_LIMIT={limit} -fno-rtti -DTYPE_N="{args.output_type}"')


log = logging.getLogger('halide')

parser = argparse.ArgumentParser()
parser.add_argument('source', help='Halide source file annotated with '
                                   'AUTOTUNE_HOOK')
parser.add_argument('--halide-dir', default=os.path.expanduser('/home/pfetuning/Halide'),
                    help='Installation directory for Halide')
parser.add_argument('--output-size',
                    help='Output size to test with')
parser.add_argument('--output-type',
                    help='Output type to test with')
parser.add_argument('--trials', default=3, type=int,
                    help='Number of times to test each schedule')
parser.add_argument('--nesting', default=1, type=int,
                    help='Maximum depth for generated loops')
parser.add_argument('--max-split-factor', default=8, type=int,
                    help='The largest value a single split() can add')
parser.add_argument('--compile-command', default=COMPILE_CMD,
                    help='How to compile generated C++ code')
parser.add_argument('--cxx', default='g++',
                    help='C++ compiler to use (e.g., g++ or clang++)')
parser.add_argument('--cxxflags', default='',
                    help='Extra flags to the C++ compiler')
parser.add_argument('--tmp-dir',
                    default=('/run/shm' if os.access('/run/shm', os.W_OK)
                             else '/tmp'),
                    help='Where to store generated tests')
parser.add_argument('--settings-file',
                    help='Override location of json encoded settings')
parser.add_argument('--debug-error',
                    help='Stop on errors matching a given string')
parser.add_argument('--limit', type=float, default=5.5,
                    help='Kill compile + runs taking too long (seconds)')
parser.add_argument('--memory-limit', type=int, default=1024 ** 3,
                    help='Set memory ulimit on unix based systems')
parser.add_argument('--enable-unroll', action='store_true',
                    help='Enable .unroll(...) generation')
parser.add_argument('--enable-store-at', action='store_true',
                    help='Never generate .store_at(...)')
parser.add_argument('--gated-store-reorder', action='store_true',
                    help='Only reorder storage if a special parameter is given')
group = parser.add_mutually_exclusive_group()
group.add_argument('--random-test', action='store_true',
                   help='Generate a random configuration and run it')
group.add_argument('--random-source', action='store_true',
                   help='Generate a random configuration and print source ')
group.add_argument('--make-settings-file', action='store_true',
                   help='Create a skeleton settings file from call graph')


def order_generation_optimizations():
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
    return order_optimizations

def generate_exhaustive_schedules(program, args, order_optimizations):
    schedule = Schedule(list(), args)
    id_program = hashlib.md5(str(program)).hexdigest()
    append_and_explore_optim(schedule, program, id_program, list(), 0, order_optimizations)


def main(args):

    ''' read program's characteristics'''
    [program, settings] = Program.init_program(args.settings_file, args)
    id_program = hashlib.md5(str(program)).hexdigest()
    ''' init a connexion to the database '''
    storage = StorageManager.StorageManager()
    ''' extract machine s characteristics'''
    machine = Machine.Machine()
    ''' store machine caracteristics'''
    idOfMachine = storage.store_machine(machine)
    ''' store program's characteristics'''
    storage.store_program(id_program, settings, idOfMachine)
    ''' get the order in which th optimizations are generated '''
    order_optimizations = order_generation_optimizations()
    ''' lunch the exhaustive search algorithm '''
    generate_exhaustive_schedules(program, args, order_optimizations)




if __name__ == '__main__':
    main(parser.parse_args())
