import Optimization
from Optimization import Optimization
# We can have a reorder storage optimization
class ReorderStorageOptimization(Optimization):
    def __init__(self, func, variables):
        super(ReorderStorageOptimization, self).__init__(func)
        # List of variables concerned by the reorder_storage optimization
        self.variables = variables

    def __str__(self):
        str_to_return = '\n'+str(self.func)
        str_to_return = str_to_return+'.reorder_storage('
        for var in self.variables :
            if var.name_var.count('.') == 1 :
                # I need to count the number of letters after this point
                length = 0
                for index in xrange(0, len(var.name_var)):
                    if var.name_var[index] == '.' :
                        length = len(var.name_var[index+1:])
                variable_without_dot = var.name_var
                if length > 1 :
                    ## I need to delete the . from var
                    for char in variable_without_dot :
                        if char == '.':
                            variable_without_dot = variable_without_dot.replace(char, '')
                str_to_return=str_to_return+variable_without_dot+','

            else :
              if var.name_var.count('.') > 1 :
                for char in variable_without_dot :
                        if char == '.':
                            variable_without_dot = variable_without_dot.replace(char, '')
                str_to_return=str_to_return+variable_without_dot+','
              else :
                str_to_return=str_to_return+str(var)+','
        str_to_return = str_to_return[0:len(str_to_return)-1]
        str_to_return = str_to_return+');'
        return str_to_return
