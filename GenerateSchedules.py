import hashlib
import Machine
from GenerationOfOptimizations.settings import *
import Heuristics.HalideAutotuner
import Heuristics.Exhaustive_search
import Heuristics.Reorder_analytique
import Heuristics.Reorder_explore
import Save_excel
from Save_excel import ExcelWriter

COMPILE_CMD = (
  '{args.cxx} "{cpp}" -o "{bin}" -I "{args.halide_dir}/include" '
  '"{args.halide_dir}/lib/libHalide.a" -ldl -lcurses -lpthread {args.cxxflags} '
  '-DAUTOTUNE_N="{args.output_size}" -DAUTOTUNE_TRIALS={args.trials} '
  '-DAUTOTUNE_LIMIT={args.time_limit} -fno-rtti -DTYPE_N="{args.output_type}"')


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
parser.add_argument('--time-limit', default=99999, type=int,
                    help='Number of seconds to wait for a schedule to be tested')
parser.add_argument('--heuristic-limit', default=None, type=int,
                    help='Number of seconds to wait for a schedule to be tested')
parser.add_argument('--trials', default=3, type=int,
                    help='Number of times to test each schedule')
parser.add_argument('--schedule-limit', default=None, type=int,
                    help='Number of tested schedules')
parser.add_argument('--heuristic', default=None, type=str,
                    help='Name of the heuristic to launch')
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
#parser.add_argument('--limit', type=float, default=5.5,
#                    help='Kill compile + runs taking too long (seconds)')

parser.add_argument('--memory-limit', type=int, default=1024 ** 3,
                    help='Set memory ulimit on unix based systems')
parser.add_argument('--enable-unroll', action='store_true',
                    help='Enable .unroll(...) generation')
parser.add_argument('--enable-store-at', action='store_true',
                    help='Never generate .store_at(...)')
parser.add_argument('--gated-store-reorder', action='store_true',
                    help='Only reorder storage if a special parameter is given')
group = parser.add_mutually_exclusive_group()
#group.add_argument('--random-test', action='store_true',
#                   help='Generate a random configuration and run it')
#group.add_argument('--random-source', action='store_true',
#                   help='Generate a random configuration and print source ')
#group.add_argument('--make-settings-file', action='store_true',
#                   help='Create a skeleton settings file from call graph')


def switch_heuristic_launch(heuristic, program, args, cache_line_size):
    if (heuristic == "HalideAutotuner") | (heuristic == None):
        Heuristics.HalideAutotuner.generate_schedules_heuristic(program, cache_line_size)
    else :
        if heuristic == "Reorder_explore" :
           Heuristics.Reorder_explore.generate_schedules_heuristic(program, args)
        else :
            if heuristic == "Reorder_analytique":
                Heuristics.Reorder_analytique.generate_schedules_heuristic(program, args, cache_line_size)
            else :
                Heuristics.Exhaustive_search.generate_exhaustive_schedules(program, args)



def main(args):
    ''' read program's characteristics'''
    [program, settings_] = Program.init_program(args.settings_file, args)
    id_program = hashlib.md5(str(program)).hexdigest()
    ''' init a connexion to the database '''
    storage = StorageManager.StorageManager()
    ''' extract machine s characteristics'''
    machine = Machine.Machine()
    ''' store machine caracteristics'''
    idOfMachine = storage.store_machine(machine)
    ''' store program's characteristics'''
    storage.store_program(id_program, settings_, idOfMachine)
    ''' No schedule explored '''
    settings.set_total_nb_schedule(0)
    ''' start the timer '''
    settings.start_timer()
    ''' launch the heuristic'''
    #
    schedules_id = storage.find_schedules_by_program(id_program)
    settings.set_schedules_id(schedules_id)
    switch_heuristic_launch(args.heuristic, program, args, cache_line_size=4)
    settings.finish()



if __name__ == '__main__':
   try :
    main(parser.parse_args())
   except IndexError :
       print color.RED+"Peu d'arguments en entr"+ai+"e"+color.END
       exit(0)

