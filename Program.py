import json
import re
import Schedule
import hashlib


class Variable():
    def __init__(self, name_var, extent_var, type):
        self.name_var = name_var
        self.extent_var = extent_var
        self.type = type

    @property
    def name_var(self):
        return self.name_var

    @name_var.setter
    def name_var(self, name_var):
        self.name_var = name_var

    def __str__(self):
        return self.name_var

    def type_of_var(self):
        '''

        :return: type of variable object
        '''
        return self.type


# A Function has a name and a set of variable objects and a set of producers function, an instruction and
# reuses loop nest level.

class Function():

    def __init__(self, name_function, list_variables, list_producers, legal_vectorize, instruction, \
                 reuses, tile_level):
        self.name_function = name_function
        self.list_variables = list_variables
        self.list_producers = list_producers
        self.legal_vectorize = legal_vectorize
        self.instruction = instruction
        self.reuses = reuses
        self.tile_level = tile_level

    def __str__(self):
        return self.name_function

    def is_consumer(self):
        '''

        :return: True if the function is a consumer for other stages, False otherwise.
        '''
        if len(self.list_producers) == 0 :
            return False
        else :
            return True



    def vars_of_func_dict_schedule(self, schedule):
        '''
        :return: a dictionary : {name_var1 : object_var1, name_var2 : object_var2} so we can access the variables object
                 using their names
        '''
        dictio = dict()
        for var in schedule.vars_of_func(self) :
            dictio[var.name_var] = var
        return dictio

    def vars_of_func_dict(self):
        '''
        :return: a dictionary : {name_var1 : object_var1, name_var2 : object_var2} so we can access the variables object
                 using their names
        '''
        dictio = dict()
        for var in self.list_variables :
            dictio[var.name_var] = var
        return dictio


    def outermost_variable(self, schedule):
        '''

        :param schedule:
        :return: the index (the variable) of the outermost loop of func 'self'
        '''
        list_vars = schedule.vars_of_func(self)
        return list_vars[len(list_vars)-1]


    def search_for_vectorize(self, legal_vectorize, schedule):
        '''

        :param legal_vectorize: index name of the legal vectorized loop.
        :return: the innermost legal vectorized loop index
        '''
        vars_dict = self.vars_of_func_dict_schedule(schedule)
        legal_vectorize_searched = legal_vectorize
        if legal_vectorize in vars_dict.keys() :
            return vars_dict[legal_vectorize]
        else :
         found = False
         while found == False :
          legal_vectorize_searched = legal_vectorize_searched+'i'
          for var in vars_dict.keys():
            if var == legal_vectorize_searched :
                return vars_dict[var]
        return None


    def two_innermost_variable_for_unroll(self, schedule):
        '''

        :param func:
        :param schedule: the schedule may change the order of variables in function func. So we need to check it
        :return: two innermost variables of function
        '''
        list_variables = schedule.vars_of_func(self)
        inner1 = None
        inner2 = None
        if re.match(self.legal_vectorize+"(i)*",list_variables[0].name_var):
            vectorized = False
            inner1 = list_variables[0]
            for optim in schedule.optimizations :
                if isinstance(optim, Schedule.VectorizeOptimization) :
                  if (optim.func == self) & (optim.enable == True) :
                    if inner1 == optim.variable :
                        vectorized = True
                        break
            if vectorized == True  :
             if len(list_variables) > 1 :
               inner1 = list_variables[1]
               if len(list_variables) > 2 :
                   inner2 = list_variables[2]


        else :
            inner1 = list_variables[0]
            if len(list_variables) > 1 :
                if re.match(self.legal_vectorize+"(i)*",list_variables[1].name_var):
                    inner2 = None
                else :
                    if len(list_variables) > 1 :
                        inner2 = list_variables[1]
        return [inner1, inner2]




class Program():

    @staticmethod
    def init_program(settingsFileName, args):
        '''

     :param settingsFileName: name of input settings file
     :param args: arguments passed from the input command line
     :return: program object and its settings
     '''
        ## As .settings file is a json file, let's load it
        with open(settingsFileName) as fd:
            settings = json.load(fd)
        list_of_functions = list()
        # Let's init program variables
        output_size = settings['output_size']
        args.output_size = settings['output_size']
        output_type = settings['output_type']
        nameProgram = settings['name_program']
        args.nameProgram = settings['name_program']
        args.output_type = settings['output_type']
        args.limit = 6.0
        if 'RVars' in settings :
            RVars = settings['RVars']
        else :
            RVars = None
        if 'constantes' in settings :
            constantes = settings['constantes']
        else :
            constantes = None
        for func in settings['functions']:
            if 'tile_level' in func :
                tile_level = func['tile_level']
            else :
                tile_level = 1
            if 'instruction' in func :
                instruction=func['instruction']
            else :
                instruction=None
            if 'legal_vectorize' in func :
                legal_vectorize=func['legal_vectorize']
            else :
                legal_vectorize = None
            list_variables = list()
            for estime in func['estime']:
                for var in estime.keys():
                   if RVars != None :
                    if var in RVars :
                        type_var = 'RVar'
                    else :
                        type_var = 'Var'
                   new_var = Variable(var, estime[var], type_var)
                   list_variables.append(new_var)
            list_producers = list()
            for producer in func['calls']:
                list_producers.append(producer)
            list_reuses = list()
            if 'reuse' in func :
                for reuse in func['reuse']:
                    list_reuses.append(reuse)
            new_func = Function(func['name'], list_variables, list_producers, legal_vectorize, instruction, list_reuses, tile_level)
            list_of_functions.append(new_func)
        # Create the object program

        program1 = Program(output_size, output_type, list_of_functions, nameProgram, RVars, constantes, \
                           args, None)
        id_program = hashlib.md5(str(program1)).hexdigest()
        program1.id = id_program
        return [program1, settings]


    def reorder_functions_program(self):
        '''

        :return: function list of program in order : starting the pipeline from the last stage to the first stage.
        '''
        new_list_functions = list()

        while True :
          for func in self.functions :
            if func not in new_list_functions :
                consumers_in_list=func.consumer_of_func(new_list_functions)
                all_consumers = func.consumer_of_func(self.functions)
                if len(consumers_in_list) == len(all_consumers):
                      new_list_functions.append(func)
          if len(self.functions) == len(new_list_functions):
              break
        ## if a function has an update, its update must appear before the non updated function
        for func in self.functions :
            if '.update' in func.nameFunction :
                index_update = new_list_functions.index(func)
                no_updated_name_func = func.nameFunction.split(".")[0]
                no_updated_func=self.functions_of_program()[no_updated_name_func]
                index_no_update = new_list_functions.index(no_updated_func)
                if (index_no_update < index_update) :
                    new_list_functions[index_no_update] = func
                    new_list_functions[index_update] = no_updated_func
        return new_list_functions



    def __init__(self, output_size, output_type, functions, name_program, RVars, constantes, args, id):
        # outputSize represents the size of the output buffer
        self.output_size = output_size
        # outputType represents the type of the output buffer
        self.output_type = output_type
        # functions represents the present functions in the program
        self.functions = functions
        # the routine's name
        self.name_program = name_program
        # RVars variables
        self.RVars = RVars
        # if there are constants
        self.constantes = constantes
        self.args = args
        self.id = id


    def __str__(self):
        return_str = 'Output Size : '+self.output_size+'\n'
        return_str = return_str+'Output Type : '+self.output_type+'\n'
        for func in self.functions :
            return_str = return_str + '\n'+str(func)
            for var in func.list_variables :
                return_str = return_str+' '+var.name_var+' '+str(var.extent_var)+','
        return return_str


    def functions_of_program(self):
        '''

        :return: a dictionary : {func_name1 : func_obj1, func_name2 : func_obj2} so we can access the functions object
                                using their names
        '''
        dictio = dict()
        for func in self.functions :
            dictio[func.name_function] = func
        return dictio


    # Create a new instance of program which has the same properties of the current program
    def copy_program(self):
        '''

        :return: new instance of program which has the same attributes as the 'self' program
        '''
        list_func = list()
        for func in self.functions :
            list_func.append(func)
        program = Program(self.output_size, self.output_type, list_func, \
                          self.name_program, self.RVars, self.constantes, self.args, self.id)
        return program
