import abc

# Restriction is applied to a function to not let an optimization takes all the possible combination
class Restriction:
    __metaclass__ = abc.ABCMeta
    def __init__(self, func, enable):
      self.func = func
      # enable to indicate the enability of the optimization
      self.enable = enable
