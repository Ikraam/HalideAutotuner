import abc
class Optimization():
  __metaclass__ = abc.ABCMeta
  def __init__(self, func):
      ## An optimization is applied on a function
      self.func = func
