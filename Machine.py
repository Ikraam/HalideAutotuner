import cpuinfo
import platform
import subprocess

# to get information about the hardware characteristics
class Machine():

    def __init__(self):
        self.L2_cache = None
        self.L1d_cache = None
        self.L1i_cache = None
        self.nb_CPU = None
        self.L3_cache = None
        self.set_machine_information()

    def __str__(self):
        returnStr = 'nbCPU : ' + str(self.nb_CPU) + '\n'
        returnStr = returnStr +'L1iCache : ' + self.L1i_cache + '\n'
        returnStr = returnStr +'L1dCache : ' + self.L1d_cache + '\n'
        returnStr = returnStr +'L2Cache : ' + self.L2_cache + '\n'
        returnStr = returnStr +'L3Cache : ' + self.L3_cache + '\n'
        return returnStr



    def set_machine_information(self):
        # get machine's information
        info = cpuinfo.get_cpu_info()
        ## info is json file that contains information about my machine CPU
        ## number of CPUs
        self.nb_CPU = info.get('count')
        ## L2 cache size
        self.L2_cache = info.get('l2_cache_size')
        if platform.system() == 'Linux':
            # information_CPU is a list of caracteres
            information_CPU = subprocess.check_output(['lscpu'])
            self.L1i_cache = search_for_field('L1i', information_CPU)
            self.L2_cache = search_for_field('L2', information_CPU)
            self.L3_cache = search_for_field('L3', information_CPU)
            self.L1d_cache = search_for_field('L1d', information_CPU)
            # Let's transform information_CPU from list of caracters to a dictionary of {field : value}


# A function that extracts informations from the result of the command : lscpu
def search_for_field(field, information_CPU):
    find_field = False
    value = ''
    index = 0
    index_on_information_CPU = 0
    for caractere in information_CPU :
        if find_field == False :
            index = 0
            if caractere == field[0]:
                find_field = True
        else :
            if information_CPU[index_on_information_CPU:index_on_information_CPU + len(field)] == field :
                # We did find the field
                break
        index_on_information_CPU+= 1

    if find_field :
         # search for the next ':'
         for index in xrange(index_on_information_CPU+len(field), len(information_CPU)):
             if information_CPU[index] == ':':
                break

         # search for the value
         find_value = False
         for i in xrange(index+1, len(information_CPU)):
             if find_value == False :
                if information_CPU[i] != ' ':
                  find_value = True

             if find_value == True :
                 carac = information_CPU[i]
                 indexo = i
                 while (information_CPU[indexo] != ' ') & (information_CPU[indexo] != '\n'):
                     value= value + information_CPU[indexo]
                     indexo+=1
                 break

    return value










