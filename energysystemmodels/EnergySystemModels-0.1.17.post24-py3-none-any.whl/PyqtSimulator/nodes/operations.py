from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#############les modèles d'un groupe frigorifique#################
#from Modules_GroupeFrigorifique.Evaporator import Evaporator
from ThermodynamicCycles.Compressor import Compressor
#from Modules_GroupeFrigorifique.Desuperheater import Desuperheater
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort


@register_node(OP_NODE_MIX)
class CalcNode_Mix(CalcNode):
    icon = "icons/mixer.png"
    op_code = OP_NODE_MIX
    op_title = "Mélangeur"
    content_label = "+"
    content_label_objname = "calc_node_bg"
    
 

    def evalOperation(self, input1, input2):
        self.value=[]
        
       
        self.value.append(input1[0]) #fluide
        self.value.append(input1[1]+input2[1]) #débit
        self.value.append(min(input1[2],input2[2])) #pression min
        self.value.append((input1[1]*input1[3]+input2[1]*input2[3])/(input1[1]+input2[1])) #Enthalpie
            
        return self.value
    
@register_node(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = "icons/add.png"
    op_code = OP_NODE_ADD
    op_title = "Add"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        self.value=[]
        for i in range(min(len(input1),len(input2))):
            self.value.append(input1[i]+input2[i])
       # print("input1 = ",input1)
      #  print("input2 = ",input2)
      #  print("somme = ",self.value)
        return self.value
    
    

@register_node(OP_NODE_SUB)
class CalcNode_Sub(CalcNode):
    icon = "icons/sub.png"
    op_code = OP_NODE_SUB
    op_title = "Substract"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        self.value=[]
        
       
        self.value.append(input1[0]) #fluide
        self.value.append(input1[1]-input2[1]) #diff_débit
        self.value.append((input1[2]+input2[2])/2) #moy Pression
        self.value.append(input1[3]-input2[3]) #d_Enthalpie
            
        return self.value

@register_node(OP_NODE_MUL)
class CalcNode_Mul(CalcNode):
    icon = "icons/mul.png"
    op_code = OP_NODE_MUL
    op_title = "Multiply"
    content_label = "*"
    content_label_objname = "calc_node_mul"

    def evalOperation(self, input1, input2):
        print('foo')
        return input1 * input2

@register_node(OP_NODE_DIV)
class CalcNode_Div(CalcNode):
    icon = "icons/divide.png"
    op_code = OP_NODE_DIV
    op_title = "Divide"
    content_label = "/"
    content_label_objname = "calc_node_div"

    def evalOperation(self, input1, input2):
        return input1 / input2

# way how to register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)