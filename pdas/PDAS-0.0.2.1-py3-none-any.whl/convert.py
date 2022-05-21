class PDAS_Conversion:
  def convert(arg):
      if type(arg) == str:
       if arg in ["true", "True", "1", "Y"]:
         return True
       if arg in ["false", "False", "0", "N"]:
         return False
      if type(arg) == int:
        if arg in [0o1, 1]:
          return True
        if arg in [0o0, 0]:
          return False
        