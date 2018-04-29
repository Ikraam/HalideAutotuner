from settings import *



class StoreAtOptimizationGenerator(OptimizationGenerator):

    @staticmethod
    def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                                                  index_order_optimization, order_optimization):
        if index == len(schedule.optimizations):
            settings.append_and_explore_optim(schedule, program, idProgram, setRestrictions, index_order_optimization \
                                              , order_optimization)
        else :
            if isinstance(schedule.optimizations[index], StoreAtOptimization):
                optim = schedule.optimizations[index]
                var = optim.variable
                consumer = optim.consumer
                # search variables of consumer
                list_vars_func = schedule.vars_of_func(consumer)
                if var in list_vars_func :
                    index_var = list_vars_func.index(var)
                    for i in range(index_var, len(list_vars_func)):
                        var_store_at = list_vars_func[i]
                        optim.variable = var_store_at
                        StoreAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                           elemSupp, setRestrictions, \
                                                                           idProgram, \
                                                                           index_order_optimization, \
                                                                           order_optimization)
                    var_store_at = Variable('root',0,"Var")
                    optim.variable = var_store_at
                    StoreAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                           elemSupp, setRestrictions, \
                                                                           idProgram, \
                                                                           index_order_optimization, \
                                                                           order_optimization)
                else :
                    StoreAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                           elemSupp, setRestrictions, \
                                                                           idProgram, \
                                                                           index_order_optimization, \
                                                                           order_optimization)
            else :
                StoreAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                           elemSupp, setRestrictions, \
                                                                           idProgram, \
                                                                           index_order_optimization, \
                                                                           order_optimization)





class ComputeAtOptimizationGenerator(OptimizationGenerator):
    @staticmethod
    def explore_possibilities(schedule, index, program, elemSupp, setRestrictions, idProgram, \
                              index_order_optimization, order_optimization):
        if index == len(schedule.optimizations):
            settings.append_and_explore_optim(schedule, program, idProgram, setRestrictions, index_order_optimization,
                                              order_optimization)
            return schedule
        else :
            if isinstance(schedule.optimizations[index],ComputeAtOptimization):
              producer = schedule.optimizations[index].func
              consumer =  schedule.optimizations[index].consumer
              for var in consumer.list_variables:
                    schedule.optimizations[index].variable = var
                    ComputeAtOptimizationGenerator.explore_possibilities(schedule, index+1, \
                                                                         program, elemSupp, \
                                                                         setRestrictions, idProgram, \
                                                                         index_order_optimization, \
                                                                         order_optimization)

              schedule.optimizations[index].variable = Variable('root',0,"Var")
              ComputeAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                   elemSupp, setRestrictions, idProgram, \
                                                                   index_order_optimization,\
                                                                   order_optimization)
            else :
              ComputeAtOptimizationGenerator.explore_possibilities(schedule, index+1, program, \
                                                                   elemSupp, setRestrictions, idProgram, \
                                                                   index_order_optimization, \
                                                                   order_optimization)


