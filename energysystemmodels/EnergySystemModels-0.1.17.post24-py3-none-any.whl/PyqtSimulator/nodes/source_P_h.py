from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

from CoolProp.CoolProp import PropsSI

class CalcInputContent(QDMNodeContentWidget):
    def initUI(self):
        
        
        
        self.fluid_lbl = QLabel("Type de fluide", self)
        self.fluid=QComboBox(self)
        
        self.fluid.addItem("ammonia")
        self.fluid.addItem("water")
        listeDesFluides=Fluid().listeDesFluides()
        
        for i in listeDesFluides:
            self.fluid.addItem(i)        
        # self.fluid.setStyleSheet("QComboBox"
        #                              "{"
        #                               "background-color: lightgreen;"
        #                              "}") 
        self.fluid.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)                   
        
        self.F_kgs_lbl=QLabel("débit (kg/s)", self) 
        self.F_kgs_edit=QLineEdit("0.27777777", self)
        
        self.h_lbl = QLabel("enthalpie (kJ/kg-K)", self)              
        self.h_edit = QLineEdit("500", self)
        
        self.P_lbl = QLabel("Pression (bar)", self)                       
        self.P_edit = QLineEdit("1.01325", self)
        
        self.layout=QVBoxLayout()
        
        self.layout.addWidget(self.fluid_lbl)
        self.layout.addWidget(self.fluid)        
        self.layout.addWidget(self.F_kgs_lbl)
        self.layout.addWidget(self.F_kgs_edit)        
        self.layout.addWidget(self.h_lbl)
        self.layout.addWidget(self.h_edit)
        self.layout.addWidget(self.P_lbl)
        self.layout.addWidget(self.P_edit)
        
        
        
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        

    def serialize(self):
        res = super().serialize()
        res['h'] = self.h_edit.text()
        res2 = super().serialize()
        res2['P'] = self.P_edit.text()
        
        res3 = super().serialize()
        res3['fluid'] = self.fluid.currentText()
        
        res4 = super().serialize()
        res4['F_kgs'] = self.F_kgs_edit.text()
        
        return res,res2,res3,res4

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
        res3 = super().deserialize(data, hashmap)
        res4 = super().deserialize(data, hashmap)
       # print("res=",res,res2,res3,res4)
       # print("dataaaaaaaaaa=",data)
        try:
            
            h = data[0]["h"]
            P = data[1]['P']
            fluid = data[2]['fluid']
            F_kgs = data[3]['F_kgs']
            
           # print("values=",h,P,fluid,F_kgs)
            
            self.h_edit.setText(h)
            self.P_edit.setText(P)
            self.fluid.setCurrentText(fluid)
            self.F_kgs_edit.setText(F_kgs)
            
            return True & res & res2 & res3 & res4
        except Exception as e:
            dumpException(e)
        return res,res2,res3,res4


@register_node(OP_NODE_INPUT_P_h)
class CalcNode_Input(CalcNode):
    icon = "icons/in.png"
    op_code = OP_NODE_INPUT_P_h
    op_title = "Source_P_h"
    content_label_objname = "calc_node_input"
    

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.height=300
        self.grNode.width=200
        self.content.h_edit.textChanged.connect(self.onInputChanged)
        self.content.P_edit.textChanged.connect(self.onInputChanged)
        self.content.F_kgs_edit.textChanged.connect(self.onInputChanged)
        self.content.fluid.currentIndexChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_h = self.content.h_edit.text()
        s_h = float(u_h)
        
        u_P = self.content.P_edit.text()
        s_P = float(u_P)
        
        u_F_kgs = self.content.F_kgs_edit.text()
        s_F_kgs = float(u_F_kgs)
        
        u_fluid = self.content.fluid.currentText()
        s_fluid = u_fluid
        
        
        
        
        fluid=self.content.fluid.currentText()
        
        #self.h=PropsSI("H", "P", 100000*s_P, "H", s_h*1000, fluid)/1000
        self.h=s_h
        
        self.value = [s_fluid,s_F_kgs,s_P,self.h]
        
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()
      #  print("données entrée = ",self.value)
        return self.value
   
class Fluid:
    def __init__(self):
        self.fluid_list=["1-Butene","Acetone"	,"Air"	,"Ammonia","Argon"	,"Benzene"	,"CarbonDioxide"	,"CarbonMonoxide","CarbonylSulfide"	,
"CycloHexane"	,"CycloPropane"	,"Cyclopentane"	,"D4"	,"D5"	,"D6"	,"Deuterium"	,"Dichloroethane"	,"DiethylEther"	,
"DimethylCarbonate"	,
"DimethylEther"	,
"Ethane"	,
"Ethanol"	,
"EthylBenzene"	,
"Ethylene"	,
"EthyleneOxide"	,
"Fluorine"	,
"HFE143m"	,
"HeavyWater"	,
"Helium"	,
"Hydrogen"	,
"HydrogenChloride"	,
"HydrogenSulfide"	,
"IsoButane"	,
"IsoButene"	,
"Isohexane"	,
"Isopentane"	,
"Krypton"	,
"MD2M"	,
"MD3M"	,
"MD4M"	,
"MDM"	,
"MM"	,
"Methane"	,
"Methanol"	,
"MethylLinoleate"	,
"MethylLinolenate"	,
"MethylOleate"	,
"MethylPalmitate"	,
"MethylStearate"	,
"Neon"	,
"Neopentane"	,
"Nitrogen"	,
"NitrousOxide"	,
"Novec649"	,
"OrthoDeuterium"	,
"OrthoHydrogen"	,
"Oxygen"	,
"ParaDeuterium"	,
"ParaHydrogen"	,
"Propylene"	,
"Propyne"	,
"R11"	,
"R113"	,
"R114"	,
"R115"	,
"R116"	,
"R12"	,
"R123"	,
"R1233zd(E)"	,
"R1234yf"	,
"R1234ze(E)"	,
"R1234ze(Z)"	,
"R124"	,
"R125"	,
"R13"	,
"R134a"	,
"R13I1"	,
"R14"	,
"R141b"	,
"R142b"	,
"R143a"	,
"R152A"	,
"R161"	,
"R21"	,
"R218"	,
"R22"	,
"R227EA"	,
"R23"	,
"R236EA"	,
"R236FA"	,
"R245ca"	,
"R245fa"	,
"R32"	,
"R365MFC"	,
"R40"	,
"R404A"	,
"R407C"	,
"R41"	,
"R410A"	,
"R507A"	,
"RC318"	,
"SES36"	,
"SulfurDioxide"	,
"SulfurHexafluoride"	,
"Toluene"	,
"Water"	,
"Xenon"	,
"cis-2-Butene"	,
"m-Xylene"	,
"n-Butane"	,
"n-Decane"	,
"n-Dodecane"	,
"n-Heptane"	,
"n-Hexane"	,
"n-Nonane"	,
"n-Octane"	,
"n-Pentane"	,
"n-Propane"	,
"n-Undecane"	,
"o-Xylene"	,
"p-Xylene"	,
"trans-2-Butene"	]
    
    def listeDesFluides(self):
        return self.fluid_list
       
            


class FluidPort:
    def __init__(self):
        self.F_kgs=0
        self.P = 101325
        self.h = 10000
        self.fluid = "ammonia"
        
    def propriete(self,Pro,I1,ValI1,I2,ValI2):
        result=PropsSI(Pro, I1, ValI1, I2, ValI2, self.fluid)
        return result