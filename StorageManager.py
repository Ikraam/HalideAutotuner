import json
import datetime
import collections
import json
from pymongo import MongoClient
import Schedule
from Schedule import *
import hashlib
import Schedule

## Set a connection to the database 'opentuner'
class StorageManager():
    client=MongoClient()
    db = client['opentuner']


    # Return 'time' of a schedule if it exists on the database
    def find_schedule(self, schedule, idProgram):
        '''
        :param schedule: the wanted schedule.
        :param idProgram: id of program for which the schedule was designed.
        :return: None if schedule unfound Time of the schedule if it has been found.
        '''
        idOfSchedule = hashlib.md5(str(schedule)+idProgram).hexdigest()
        # If I can't find my schedule in the DB, return None
        if self.db.schedule.find({"_id": idOfSchedule}).count() == 0 :
            return None
        else :
            doc = self.db.schedule.find_one({"_id": idOfSchedule})
            # Return time of the schedule
            time = doc.get('time')
            return time




    # Store program settings into the database
    def store_program(self, idProgram, settings, idOfMachine):
        '''
        :param program: the program that we want to store in the database
        :param settings: the information of the program
        '''
        settings['_id'] = idProgram
        settings['id_machine'] = idOfMachine
        # Insert my program if it is not already inserted
        if self.db.program.find({"_id": idProgram}).count() != 0 :
         if self.db.program.find_one({"_id": idProgram}).get('id_machine') == None :
            self.db.program.update({"_id": idProgram},{'id_machine':idOfMachine}, upsert= True)
        if self.db.program.find({"_id": idProgram}).count() == 0 :
            self.db.program.insert(settings,check_keys = False)


    # Store machine caracteristiques on the database
    def store_machine(self, machine):
        # set the tuple
        data_machine = {}
        data_machine["L1i_Cache_Size"] = machine.L1i_cache
        data_machine["L1d_Cache_Size"] = machine.L1d_cache
        data_machine["L2_Cache_Size"] = machine.L2_cache
        data_machine["L3_Cache_Size"] = machine.L3_cache
        data_machine["nbCPU"] = machine.nb_CPU
        # generate the id = hash(str(machine))
        idOfMachine = hashlib.md5(str(machine)).hexdigest()
        data_machine["_id"] = idOfMachine
        # If machine is not already stored
        if self.db.machine.find({"_id": idOfMachine}).count() == 0 :
            # Store machine caracteristiques
            self.db.machine.insert(data_machine,check_keys = False)
        return idOfMachine






    # Store schedule into the database
    def store_schedule(self, schedule, error, idProgram, time_of_schedule):
        '''
        :param schedule: the schedule that we want to store
        :param error: the error that we get once we execute the schedule
        :param idProgram:
        :param time_of_schedule:
        :return: idSchedule
        '''
        insert = False
        modify = False

        # Set time_of_schedule to Infinity
        if time_of_schedule == None :
            time_of_schedule = float('inf')

        # Set the id of schedule to hash(schedule)
        idOfSchedule = hashlib.md5(str(schedule)+idProgram).hexdigest()

        # Check if we don't have 1000000 schedules for out program already inserted into the DB
        if self.db.schedule.find({"id_program":idProgram}).count() < 1000000 :
            # Check if schedule is not inserted into the DB
            if self.db.schedule.find({"_id": idOfSchedule}).count() == 0 :
                # Initialize a document to store our schedule
                result2=self.db.schedule.insert_one({"_id": idOfSchedule,"id_program":idProgram, "split":[], "vectorize":[], "unroll":[], "parallel":[]
                                         , "reorder":[], "reorder_storage":[], "fuse":[], "compute_at":[], "store_at":[], "compute_root":[]
                                         ,"store_root":[], "time": time_of_schedule, "error":error})
                # resultn contains the idOfSchedule
                resultn = result2.inserted_id
                insert = True
            else :
                # If the schedule exists in the DB, don't store this new schedule
                doc = self.db.schedule.find_one({"_id": idOfSchedule})
                resultn = doc.get('_id')
                modify = False
                insert = False
        else :
            # If we have already 1 million schedule in the database, we must replace the worstSchedule with the current schedule
            worst_case = list(self.db.schedule.find().sort([('time',-1)]).limit(1))
            for elem in worst_case :
                for key in elem.keys():
                    if key == "time":
                        worst_time = elem[key]
            # Check if the Worst Schedule is worst than the current one
            if worst_time > time_of_schedule :
                for elem in worst_case :
                    for key in elem.keys():
                        if key == "_id":
                            resultn = elem[key]
                modify = True

        # Store the current Schedule
        if (modify) | (insert):
            # Let's store every single optimization of schedule
            for optim in schedule.optimizations:
                # If we are on SplitOptimization
                if isinstance(optim, Schedule.TileOptimization):
                    # Extract all the relevant information of the current optimization
                    if (optim.tile_factor_in > 1) | (optim.tile_factor_out > 1) :
                        # name = name of the current function
                        name = optim.func.name_function
                        var_outer_in = optim.variable_in.name_var+'o'
                        var_outer_out = optim.variable_out.name_var+'o'
                        var_inner_in = optim.variable_in.name_var+'i'
                        var_inner_out = optim.variable_out.name_var+'i'
                        factor_in = optim.tile_factor_in
                        factor_out = optim.tile_factor_out
                        self.db.schedule.update({"_id":resultn}, {"$push": { "tile" :{"func":name, "var_tiled_in": optim.variable_in.name_var, \
                                                                                    "var_tiled_out": optim.variable_out.name_var,
                                                                                    "var_inner_in": var_inner_in, \
                                                                                    "var_inner_out":var_inner_out, \
                                                                                    "var_outer_in": var_outer_in, \
                                                                                    "var_outer_out":var_outer_out, \
                                                                                    "factor_in":factor_in, \
                                                                                    "factor_out":factor_out
                                                                                              }}})
                if isinstance(optim, Schedule.SplitOptimization):
                    # Extract all the relevant information of the current optimization
                    if optim.split_factor > 1 :
                        # name = name of the current function
                        name = optim.func.name_function
                        var_splitted = optim.variable.name_var
                        var_outer = optim.variable.name_var+'o'
                        var_inner = optim.variable.name_var+'i'
                        factor = optim.split_factor
                        self.db.schedule.update({"_id":resultn}, {"$push": { "split" :{"func":name, "var_splitted": var_splitted,
                                                                                           "var_inner": var_inner, "var_outer":var_outer, "factor":factor}}})
                # If we are on FuseOptimization
                if isinstance(optim, Schedule.FuseOptimization):
                    if optim.enable  :
                        name = optim.func.name_function
                        var1 = optim.variable1.name_var
                        var2 = optim.variable2.name_var
                        fusedVar = optim.fused_var.name_var
                        self.db.schedule.update({"_id":resultn}, {"$push": { "fuse" :{"func":name, "var1": var1,
                                                                                           "var2": var2, "fused_var":fusedVar}}})


                # If we are on ReorderOptimization
                if isinstance(optim, Schedule.ReorderOptimization):
                    if len(optim.variables) != 0 :
                        name = optim.func.name_function
                        var_of_reorder = list()
                        for var in optim.variables :
                            var_of_reorder.append(var.name_var)
                        self.db.schedule.update({"_id":resultn}, {"$push": { "reorder" :{"func":name, "reorder":var_of_reorder}}})

                # If we are on ComputeAtOptimization
                if isinstance(optim, Schedule.ComputeAtOptimization) :
                    producer = optim.func.name_function
                    consumer = optim.consumer.name_function
                    # If the variable is 'root' so store in compute_root instead of compute_at
                    if optim.variable.name_var != 'root':
                        self.db.schedule.update({"_id":resultn}, {"$push": { "compute_at" :{"producer":producer, "consumer":consumer,
                                                                                              "var":optim.variable.name_var}}})
                    else :
                        self.db.schedule.update({"_id":resultn}, {"$push": { "compute_root" :{"producer":producer}}})


                # If we are on StoreAtOptimization
                if isinstance(optim, Schedule.StoreAtOptimization):
                    producer = optim.func.name_function
                    consumer = optim.consumer.name_function
                    # If the variable is 'root' so store in store_root instead of store_at
                    if optim.variable.name_var != 'root' :
                        self.db.schedule.update({"_id":resultn}, {"$push": { "store_at" :{"producer":producer, "consumer":consumer,
                                                                                              "var":optim.variable.name_var}}})
                    else :
                        self.db.schedule.update({"_id":resultn}, {"$push": { "store_root" :{"producer":producer}}})

                # If we are on VectorizeOptimization
                if isinstance(optim, Schedule.VectorizeOptimization):
                    if optim.enable :
                        name = optim.func.name_function
                        var = optim.variable.name_var
                        self.db.schedule.update({"_id":resultn}, {"$push": { "vectorize" :{"func":name, "var": var}}})


                # If we are on UnrollOptimization
                if isinstance(optim, Schedule.UnrollOptimization):
                    if optim.enable :
                        name = optim.func.name_function
                        var = optim.variable.name_var
                        self.db.schedule.update({"_id":resultn}, {"$push": { "unroll" :{"func":name, "var": var}}})


                # If we are on ParallelOptimization
                if isinstance(optim, Schedule.ParallelOptimization):
                    if optim.enable :
                        name = optim.func.name_function
                        var = optim.variable.name_var
                        self.db.schedule.update({"_id":resultn}, {"$push": { "parallel" :{"func":name, "var": var}}})


        return resultn



    # Find the best schedule for the program with the id : idProgram
    def find_best_schedule(self, idProgram):
        best_case = list(self.db.schedule.find({"id_program":idProgram, "error":None}).sort([('time',1)]).limit(1))
        print json.dumps(best_case[0], indent=4, sort_keys=True)


