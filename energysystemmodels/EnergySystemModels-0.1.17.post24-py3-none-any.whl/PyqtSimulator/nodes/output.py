from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

from CoolProp.CoolProp import PropsSI


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        
        
        self.fluid_lbl = QLabel("", self)
        
        
        self.F_kgs_lbl = QLabel("", self)
        self.NV_flow_lbl = QLabel("", self)
        self.V_flow_lbl = QLabel("", self)
        
       
        self.P_lbl = QLabel("", self)
        
        
        self.lbl = QLabel("", self)

        self.T_lbl = QLabel("", self)
        
        
        
         
        self.layout=QVBoxLayout()

        
        self.layout.addWidget(self.fluid_lbl)  
        
        
        self.layout.addWidget(self.F_kgs_lbl) 
        self.layout.addWidget(self.NV_flow_lbl) 
        self.layout.addWidget(self.V_flow_lbl)
      
        
        self.layout.addWidget(self.P_lbl)
        
  
        self.layout.addWidget(self.lbl)
        
      
        self.layout.addWidget(self.T_lbl)
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)


@register_node(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    icon = "icons/out.png"
    op_code = OP_NODE_OUTPUT
    op_title = "Output"
    content_label_objname = "calc_node_output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.height=250
      

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()
       # print("les données d'entrée de output sont : ",val)

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return
        try:
            self.T=PropsSI("T", "P", 100000*val[2], "H", val[3]*1000, val[0])-273.15
        except:
           self.T=0-273.15
        
        if (100000*val[2])<PropsSI("Pcrit",val[0]): #comparer à la pression critique
            Hv=PropsSI("H", "P", 100000*val[2], "Q", 1, val[0])
           # print("Hv=",Hv)
            Hl=PropsSI("H", "P", 100000*val[2], "Q", 0, val[0])
          #  print("Hl=",Hl)
            self.Q=1-((Hv-val[3]*1000)/(Hv-Hl))
            
            if self.Q>=1:
                self.content.fluid_lbl.setText(val[0]+" vapeur"+"%.2f" % self.Q) #"%d" % 
            elif (self.Q<1 and self.Q>0):
                self.content.fluid_lbl.setText(val[0]+" diphasique"+"%.2f" % self.Q) #"%d" % 
            else:
                self.content.fluid_lbl.setText(val[0]+" liquide"+"%.2f" % self.Q) #"%d" % 
           # print("Qualité=",self.Q)
            
        else:
            self.content.fluid_lbl.setText(val[0]+" supercritique") #"%d" % 
            
         
        if (100000*val[2])<PropsSI("Pcrit",val[0]): #comparer à la pression critique
            if self.Q>1:
                V_flow=val[1]/PropsSI("D", "P", 100000*val[2], "T", (self.T+273.15), val[0])
            elif (self.Q<=1 and self.Q>=0):
                V_flow=self.Q*val[1]/PropsSI("D", "P", 100000*val[2], "Q", 1, val[0])+(1-self.Q)*val[1]/PropsSI("D", "P", 100000*val[2], "Q", 0, val[0])
            else:
               V_flow=val[1]/PropsSI("D", "P", 100000*val[2], "T", (self.T+273.15), val[0])        
        else:    
            V_flow=val[1]/PropsSI("D", "P", 100000*val[2], "T", (self.T+273.15), val[0])
        
        NV_flow=val[1]/PropsSI("D", "P", 100000*1.01325, "T", (15+273.15), val[0])
        
    
        
        
        self.content.NV_flow_lbl.setText("%.3f" % (NV_flow*3600)+" Nm3/h")
        self.content.V_flow_lbl.setText("%.3f" % (V_flow*3600)+" m3/h")
        
        self.content.F_kgs_lbl.setText("%.3f" % (val[1]*3600)+" kg/h")
        self.content.P_lbl.setText("%.3f" % val[2]+" bar")
        self.content.lbl.setText("%.3f" % val[3]+" kJ/kg-K")
        self.content.T_lbl.setText("%.1f" % self.T+ " °C")
        
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return val
