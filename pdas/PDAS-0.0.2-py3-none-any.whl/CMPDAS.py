from PDAS.PDAS import *
from PDAS.convert import PDAS_Conversion as PDASC
import json



with open("j.json", "r+") as jsonfile1:
    config = json.load(jsonfile1)
    lconfig = list(config)
    lattributes = list(lconfig)
    jsondump = []
class PDAS_Configuration:

  def __init__(self):
    with open("CPDAS.json","r") as jsonsunload:
      jsons = json.load(jsonsunload)
      if jsons['doPassword'] == True or "true" or "True":
        verif = PDAS.PDAS.System.Security.Lock()
        if verif == 1:
          PDAS_Configuration.menu()
          pass
        else:
          pass
  def menu(self):
    Options = ["View", "Change", "Exit"]
    print("------------PDAS------------")
    for x in range(len(Options)):
      print(f"{x} : {Options[x]}")
    print("------------PDAS------------")
    Action = input(f"Pick an option from 0 to {len(Options) - 1} \n")
    if Action == "0":
      PDAS_Configuration.view()
    if Action == "1":
      PDAS_Configuration.edit()
    if Action == "2":
        PDAS_Configuration.exit()
    


  def edit(self):
    for x in range(len(lconfig)):
      y = input(f"Enter New Value for {lconfig[x]} which is currently set to {config[lattributes[x]]} \n")
      jsondump.append(y)
    with open("j.json", "r+") as jsonfile1:
      json.dump({lconfig[0]: PDASC.convert(jsondump[0]),   lconfig[1] : PDASC.convert(jsondump[1]), lconfig[2]: PDASC.convert(jsondump[2]), lconfig[3]: jsondump[3], lconfig[4] : jsondump[4] , lconfig[5] : PDASC.convert(jsondump[5]) }, jsonfile1)
  
  
  def view(self):
    for x in range(len(config)):
      print(f"{lconfig[x]} which is currently set to {config[lattributes[x]]}")
  def exit(self):
    print("Exiting")
    pass
      
            
        
