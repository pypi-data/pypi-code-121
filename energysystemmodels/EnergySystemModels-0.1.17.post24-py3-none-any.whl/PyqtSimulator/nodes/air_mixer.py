from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#############les modèles d'un groupe frigorifique#################



@register_node(OP_NODE_AIRMIX)
class CalcNode_AIRMIX(CalcNode):
    icon = "icons/mixer.png"
    op_code = OP_NODE_AIRMIX
    op_title = "Mélangeur d'air"
    content_label = "+"
    content_label_objname = "calc_node_bg"
    
 

    def evalOperation(self, input1, input2):
        self.value=[]
        
        m_as1=input1[1]/(1+(input1[0]/1000)) #kg/s
        m_as2=input2[1]/(1+(input2[0]/1000)) #kg/s
       
        self.value.append((m_as1*input1[0]+m_as2*input2[0])/(m_as1+m_as2)) #Humidité absolue
        self.value.append(input1[1]+input2[1]) #débit kg/s OK
        self.value.append(min(input1[2],input2[2])) #pression min - OK
        self.value.append((m_as1*input1[3]+m_as2*input2[3])/(m_as1+m_as2)) #Enthalpie kJ/kas
            
        return self.value
    
