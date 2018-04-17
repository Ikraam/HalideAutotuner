import StorageManager
import re
import Schedule
from Schedule import *
import argparse
import multiprocessing
import threading
import subprocess
from multiprocessing.pool import ThreadPool
import tempfile
import math
import logging
from logging import log as log
import os
import errno
import time
import signal

try:
  import resource
except ImportError:
  resource = None



class ScheduleExecution():

  def __init__(self, args, limit):
        # to compute schedule's timing
        timing_prefix = open(os.path.join(os.path.dirname(__file__),'timing_prefix.h')).read()
        # Additional information for exemple : time limit for a schedule, number of tests for one schedule.
        self.args = args
        # The output program template
        self.template = timing_prefix + open(args.source).read()
        # Disable parallelism
        self.args.parallelism = 1
        # Processes that are launched
        self.pids = []
        self.pid_lock = threading.Lock()
        # minimum time returned among all the tested schedules
        self.min_collection_cost = 30
        self.limit = limit



  def test_schedule(self, schedule, idProgram):
      storage = StorageManager.StorageManager()
      time = storage.find_schedule(schedule, idProgram)
      if time == None :
        time_and_error = self.run_schedule(schedule, self.limit)
        time = time_and_error[0]
        if time == None :
           time = float('inf')
        error = time_and_error[1]
        storage.store_schedule(schedule, error, idProgram, time)
      return time



  def run_source(self, source, limit, extra_args=''):
    cmd = ''
    ch = logging.StreamHandler()
    file = open('test.cpp','w')
    file.write(source)
    file.close()
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger().setLevel(logging.WARN)
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.DEBUG)
    with tempfile.NamedTemporaryFile(suffix='.cpp', prefix='halide',
                                     dir=self.args.tmp_dir) as cppfile:
      cppfile.write(source)
      cppfile.flush()
      binfile = ''
      with tempfile.NamedTemporaryFile(suffix='.bin', prefix='halide',
                                               dir=self.args.tmp_dir, delete=False) \
                                               as binfiletmp:

        binfile = binfiletmp.name     # temp file to contain the executable
      assert(binfile)
      cmd = self.args.compile_command.format(
        cpp=cppfile.name, bin=binfile, args=self.args,
        limit=math.ceil(limit) if limit < float('inf') else 0)  # fill the command arguments
      cmd += ' ' + extra_args
      print '\n'+cmd+'\n'
      # compile the code and get the result in compile_result
      compile_result = self.call_program(cmd, limit,
                                         memory_limit=self.args.memory_limit)

      # If there was a compile error
      if compile_result['returncode'] != 0:
        logging.error('compile failed: %s', compile_result)
        typeError = 'compile failed'
        return [None, typeError]

    try:
      # Execute the binfile
      result = self.call_program(binfile,
                                 limit,
                                 memory_limit=self.args.memory_limit)
      stdout = result['stdout']
      stderr = result['stderr']
      returncode = result['returncode']

      # If we had an error or result timeout
      if result['timeout']:
        logging.info('compiler timeout %d (%.2f+%.0f cost)', limit,
                 compile_result['time'], limit)
        typeError = 'compile failed'
        return [float('inf'), typeError]
      elif returncode == 142 or returncode == -14:
        logging.info('program timeout %d (%.2f+%.2f cost)', math.ceil(limit),
                 compile_result['time'], result['time'])
        typeError = 'program timeout'
        return [None, typeError]

      # If we had an invalid schedule
      elif returncode != 0:
        logging.error('invalid schedule (returncode=%d): %s', returncode,
                  stderr.strip())
        typeError = 'invalid schedule'
        with tempfile.NamedTemporaryFile(suffix='.cpp', prefix='halide-error',
                                         dir=self.args.tmp_dir, delete=False) as errfile:
          errfile.write(source)
          logging.error('failed schedule logged to %s.\ncompile as `%s`.', errfile.name, cmd)
          typeError = 'failed schedule'
        if self.args.debug_error is not None and (
            self.args.debug_error in stderr
        or self.args.debug_error == ""):
          self.args.debug_schedule('/tmp/halideerror.cpp', source)
        return [None, typeError]
      else:

        # Try to get the time of schedule if everything goes well
        try:
          time = json.loads(stdout)['time']
        except:
          logging.exception('error parsing output: %s', result)
          typeError = 'Error parsing'
          return [None, typeError]

        # Print the execution time
        logging.info('success: %.4f (collection cost %.2f + %.2f)',
                 time, compile_result['time'], result['time'])
        self.min_collection_cost = min(
          self.min_collection_cost, result['time'])
        typeError = None
        # Return the execution time and error if we had
        return [time, typeError]
    finally:
      os.unlink(binfile)




  def run_schedule(self, schedule, limit):
       """
       Generate a temporary Halide cpp file with schedule inserted and run it
       with our timing harness found in timing_prefix.h.
       """
       return self.run_source(self.schedule_to_source(\
           ScheduleExecution.schedule_to_sourceSchedule(schedule)), limit)



  #Generate a temporary Halide cpp file with schedule inserted
  def schedule_to_source(self, schedule):

    def repl_autotune_hook(match):
      tmpl = '''
    {
        std::map<std::string, Halide::Internal::Function> funcs = Halide::Internal::find_transitive_calls((%(func)s).function());
        outputBufNaive=_autotune_timing_stub(%(func)s, true);
    }
    {
        std::map<std::string, Halide::Internal::Function> funcs = Halide::Internal::find_transitive_calls((%(func)s).function());
        %(sched)s        
        outputBuf=_autotune_timing_stub(%(func)s, false);
    } 
    '''
      return tmpl % {"sched": schedule.replace('\n', '\n        '), "func": match.group(1)}

    source = re.sub(r'\n\s*AUTOTUNE_HOOK\(\s*([a-zA-Z0-9_]+)\s*\)',
                    repl_autotune_hook, self.template)
    return source



  @staticmethod
  def schedule_to_sourceSchedule(schedule):
      '''

      :return: schedule that can be inserted to the input program
      '''
      declared_vars_to_schedule = ''
      declared_var = list()
      declared_r_var = list()

      # If we have Split or fuse optimizations in schedule, we need to define new variables and add them to
      # the source
      for optim in schedule.optimizations :
          if isinstance(optim, SplitOptimization):
              if optim.split_factor != 1 :
                  # If splitFactor is bigger than 1 : so we have a split
                  # If variable is of type RVar
                  if optim.variable.type_of_var() == 'RVar':
                      # We need to define two new RVar
                      splitted_var = optim.variable.name_var
                      for char in splitted_var :                             ## We delete '.' from the name of the variable so
                         if char == '.' :                                   ## that we can declare it
                            splitted_var = splitted_var.replace(char, '')
                      if splitted_var+'i' not in declared_r_var :              ## If RVars are not declared yet
                        declared_r_var.append(splitted_var+'i')                ## Let's declare them
                        declared_r_var.append(splitted_var+'o')
                        ## Append them to the schedule string
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(splitted_var+'i',splitted_var+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(splitted_var+'o',splitted_var+'o')
                  else :
                      # We need to define the two Var
                      splitted_var = optim.variable.name_var
                      if splitted_var+'i' not in declared_var :              ## If Vars are not declared yet
                        declared_var.append(splitted_var+'i')
                        declared_var.append(splitted_var+'o')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(splitted_var+'i',splitted_var+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(splitted_var+'o',splitted_var+'o')

          if isinstance(optim, TileOptimization):
            if (optim.tile_factor_in > 1) | (optim.tile_factor_out > 1) :
                  # If tile_factor_in is bigger than 1 : so we have a tile
                  # If variable is of type RVar
                  if optim.variable_in.type_of_var() == 'RVar':
                      # We need to define two new RVar
                      tiled_var_in = optim.variable_in.name_var
                      for char in tiled_var_in :                             ## We delete '.' from the name of the variable so
                         if char == '.' :                                   ## that we can declare it
                            tiled_var_in = tiled_var_in.replace(char, '')
                      if tiled_var_in+'i' not in declared_r_var :              ## If RVars are not declared yet
                        declared_r_var.append(tiled_var_in+'i')                ## Let's declare them
                        declared_r_var.append(tiled_var_in+'o')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(tiled_var_in+'i',tiled_var_in+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(tiled_var_in+'o',tiled_var_in+'o')
                  else :
                      # We need to define the two Var
                      tiled_var_in = optim.variable_in.name_var
                      if tiled_var_in+'i' not in declared_var :              ## If Vars are not declared yet
                        declared_var.append(tiled_var_in+'i')
                        declared_var.append(tiled_var_in+'o')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(tiled_var_in+'i',tiled_var_in+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(tiled_var_in+'o',tiled_var_in+'o')


                  # If tile_factor_out is bigger than 1 : so we have a tiling
                  # If variable is of type RVar
                  if optim.variable_out.type_of_var() == 'RVar':
                      # We need to define two new RVar
                      tiled_var_out = optim.variable_out.name_var
                      for char in tiled_var_out :                             ## We delete '.' from the name of the variable so
                         if char == '.' :                                   ## that we can declare it
                            tiled_var_out = tiled_var_out.replace(char, '')
                      if tiled_var_out+'i' not in declared_r_var :              ## If RVars are not declared yet
                        declared_r_var.append(tiled_var_out+'i')                ## Let's declare them
                        declared_r_var.append(tiled_var_out+'o')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(tiled_var_out+'i',tiled_var_out+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(tiled_var_out+'o',tiled_var_out+'o')
                  else :
                      # We need to define the two Var
                      tiled_var_out = optim.variable_out.name_var
                      if tiled_var_out+'i' not in declared_var :              ## If Vars are not declared yet
                        declared_var.append(tiled_var_out+'i')
                        declared_var.append(tiled_var_out+'o')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(tiled_var_out+'i',tiled_var_out+'i')
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(tiled_var_out+'o',tiled_var_out+'o')

          # if we have a fusion, we must add the new variable
          if isinstance(optim, FuseOptimization):
              if optim.enable == True :
                  # if one of the variables is of type RVar
                  if optim.variable1.type_of_var() == 'RVar':
                      nameFusedVar = optim.fused_var.name_var
                      for char in nameFusedVar :
                          if char == '.' :
                              nameFusedVar = nameFusedVar.replace(char,'')
                      if nameFusedVar not in declared_r_var :
                        declared_r_var.append(nameFusedVar)
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n RVar {}(\"{}\");".format(nameFusedVar,nameFusedVar)
                  else :
                      nameFusedVar = optim.fused_var.name_var
                      if nameFusedVar not in declared_var :
                        declared_var.append(nameFusedVar)
                        declared_vars_to_schedule = declared_vars_to_schedule +"\n Var {}(\"{}\");".format(nameFusedVar,nameFusedVar)
      declared_vars_to_schedule=declared_vars_to_schedule+str(schedule)
      return declared_vars_to_schedule






  ## We use this function from OpenTuner [https://github.com/jansel/opentuner]

  def call_program(self, cmd, limit=None, memory_limit=None, **kwargs):
    """
    call cmd and kill it if it runs for longer than limit

    returns dictionary like
      {'returncode': 0,
       'stdout': '', 'stderr': '',
       'timeout': False, 'time': 1.89}
    """
    the_io_thread_pool_init(self.args.parallelism)
    if limit is float('inf'):
      limit = None
    if type(cmd) in (str, unicode):
      kwargs['shell'] = True
    killed = False
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         preexec_fn=preexec_setpgid_setrlimit(memory_limit),
                         **kwargs)
    # Add p.pid to list of processes to kill in case of keyboardinterrupt
    self.pid_lock.acquire()
    self.pids.append(p.pid)
    self.pid_lock.release()

    try:
      stdout_result = the_io_thread_pool.apply_async(p.stdout.read)
      stderr_result = the_io_thread_pool.apply_async(p.stderr.read)
      while p.returncode is None:
        if limit is None:
          goodwait(p)
        elif limit and time.time() > t0 + limit:
          killed = True
          goodkillpg(p.pid)
          goodwait(p)
        else:
          # still waiting...
          sleep_for = limit - (time.time() - t0)
          if not stdout_result.ready():
            stdout_result.wait(sleep_for)
          elif not stderr_result.ready():
            stderr_result.wait(sleep_for)
          else:
            #TODO(jansel): replace this with a portable waitpid
            time.sleep(0.001)
        p.poll()
    except:
      if p.returncode is None:
        goodkillpg(p.pid)
      raise
    finally:
      # No longer need to kill p
      self.pid_lock.acquire()
      if p.pid in self.pids:
        self.pids.remove(p.pid)
      self.pid_lock.release()

    t1 = time.time()
    return {'time': float('inf') if killed else (t1 - t0),
            'timeout': killed,
            'returncode': p.returncode,
            'stdout': stdout_result.get(),
            'stderr': stderr_result.get()}






### Additional function to execute programs
def goodkillpg(pid):
  """
  wrapper around kill to catch errors
  """
  #log.debug("killing pid %d", pid)
  try:
    if hasattr(os, 'killpg'):
      os.killpg(pid, signal.SIGKILL)
    else:
      os.kill(pid, signal.SIGKILL)
  except:
    log.error('error killing process %s', pid, exc_info=True)


def goodwait(p):
  """
  python doesn't check if its system calls return EINTR, retry if it does
  """
  while True:
    try:
      rv = p.wait()
      return rv
    except OSError, e:
      if e.errno != errno.EINTR:
        raise

the_io_thread_pool = None

def preexec_setpgid_setrlimit(memory_limit):
  if resource is not None:
    def _preexec():
      os.setpgid(0, 0)
      try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
      except ValueError:
        pass  # No permission
      if memory_limit:
        try:
          (soft, hard) = resource.getrlimit(resource.RLIMIT_AS)
          resource.setrlimit(resource.RLIMIT_AS, (min(soft, memory_limit),
                                                  min(hard, memory_limit)))
        except ValueError:
          pass  # No permission
    return _preexec



def the_io_thread_pool_init(parallelism=1):
    global the_io_thread_pool
    if the_io_thread_pool is None:
        the_io_thread_pool = ThreadPool(2 * parallelism)
        # make sure the threads are started up
        the_io_thread_pool.map(int, range(2 * parallelism))
