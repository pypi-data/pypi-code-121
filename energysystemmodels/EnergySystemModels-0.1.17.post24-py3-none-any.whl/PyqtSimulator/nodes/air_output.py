from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#from AHU.air_humide import air_humide
from AHU.air_humide import air_humide
#from CoolProp.CoolProp import PropsSI


class CalcAirOutputContent(QDMNodeContentWidget):
    def initUI(self):
        
        
        self.HA_lbl = QLabel("", self)
        
        
        self.F_kgs_lbl = QLabel("", self)
        
       
        self.P_lbl = QLabel("", self)
        
        
        self.lbl = QLabel("", self)

        self.T_lbl = QLabel("", self)
        self.HR_lbl = QLabel("", self)
        
        
        
         
        self.layout=QVBoxLayout()

        
        self.layout.addWidget(self.HA_lbl)  
        
        
        self.layout.addWidget(self.F_kgs_lbl) 
      
        
        self.layout.addWidget(self.P_lbl)
        
  
        self.layout.addWidget(self.lbl)
        
      
        self.layout.addWidget(self.T_lbl)
        self.layout.addWidget(self.HR_lbl)
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)


@register_node(OP_NODE_AIR_OUTPUT)
class CalcNode_AirOutput(CalcNode):
    icon = "icons/out.png"
    op_code = OP_NODE_AIR_OUTPUT
    op_title = "AirOutput"
    content_label_objname = "calc_node_air_output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcAirOutputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.height=200
      

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()
        print("les données d'entrée de output sont : ",val)

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return
        # try:
        #     self.T=PropsSI("T", "P", 100000*val[2], "H", val[3]*1000, val[0])-273.15
        # except:
        self.T=air_humide.Temperature(val[3],val[0])
        self.HR=air_humide.HR(air_humide.Pvs(self.T),val[0],val[2]*100000)
        

        self.content.HA_lbl.setText("%.2f" % val[0]+"g/kg-as") #"%d" % 
        #     elif (self.Q<1 and self.Q>0):
        #         self.content.HA_lbl.setText(val[0]+" diphasique"+"%.2f" % self.Q) #"%d" % 
        #     else:
        #         self.content.HA_lbl.setText(val[0]+" liquide"+"%.2f" % self.Q) #"%d" % 
        #     print("Qualité=",self.Q)
            
        # else:
        #     self.content.HA_lbl.setText(val[0]+" supercritique") #"%d" % 
        
        
    
        
        
        self.content.F_kgs_lbl.setText("%.1f" % (val[1]*3600)+" kg/h")
        self.content.P_lbl.setText("%.3f" % val[2]+" bar")
        self.content.lbl.setText("%.3f" % val[3]+" kJ/kg-as")
        self.content.T_lbl.setText("%.1f" % self.T+ " °C")
        self.content.HR_lbl.setText("%.1f" % self.HR+ " %")
        
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return val
