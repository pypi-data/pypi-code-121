import os

path = os.path.join( os.path.dirname(__file__), "tutorial" )
execute  = "cp -r " + path + " "
execute += "vem_tutorial"
status = os.system(execute)
if status != 0: raise RuntimeError(status)

print("#################################################################")
print("## An example script is now located in the 'vem_tutorial' folder.")
print("#################################################################")
