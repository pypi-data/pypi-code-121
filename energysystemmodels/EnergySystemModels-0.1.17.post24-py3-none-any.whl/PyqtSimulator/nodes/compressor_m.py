# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 19:39:26 2020

@author: zohei
"""

from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#############les modèles d'un groupe frigorifique#################
#from Modules_GroupeFrigorifique.Evaporator import Evaporator
from ThermodynamicCycles.Compressor import Compressor_m
#from Modules_GroupeFrigorifique.Desuperheater import Desuperheater
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcCompContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.HP_lbl=QLabel("pression de ref (bar)", self) 
        self.HP_edit=QLineEdit("15.0", self)
        
        self.IsenEff_lbl=QLabel("Rendement isentropique:", self) 
        self.K1_lbl=QLabel("K1:", self) 
        self.K1_edit=QLineEdit("0.8", self)
        self.K2_lbl=QLabel("K2:", self) 
        self.K2_edit=QLineEdit("0.0037", self)
        self.K3_lbl=QLabel("K3:", self) 
        self.K3_edit=QLineEdit("-0.16", self)
        self.R1_lbl=QLabel("R1:", self) 
        self.R1_edit=QLineEdit("7.0", self)
        self.R2_lbl=QLabel("R1:", self) 
        self.R2_edit=QLineEdit("1.2", self)
        
       
        
        self.VolEff_lbl=QLabel("Rendement volumétrique:", self) 
        self.a0_lbl=QLabel("a0:", self) 
        self.a0_edit=QLineEdit("0.9", self)
        self.a1_lbl=QLabel("a1:", self) 
        self.a1_edit=QLineEdit("0.038", self)
        
       
        
        
        self.MecEff_lbl=QLabel("Rendement mécanique:", self) 
        self.MecEff_edit=QLineEdit("0.7", self)
        
        self.cyl_lbl=QLabel("cylindrée (m3)", self) 
        self.cyl_edit=QLineEdit("0.0200", self)
        
        
        
        self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        self.Tref_edit=QLineEdit("80", self)
        
        self.Pu_lbl_title = QLabel("Puissance utile (kW)", self)
        self.Pu_lbl = QLabel("", self)
        
        self.Pel_lbl_title = QLabel("Puissance électrique (kW)", self)
        self.Pel_lbl = QLabel("", self)
        
        
        self.Qlosses_lbl_title = QLabel("refroidissement (kW):", self)
        self.Qlosses_lbl = QLabel("", self)
        
        self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        self.Tis_lbl = QLabel("", self)
        
        
        
        
         
       # self.layout=QVBoxLayout()
        self.layout = QGridLayout()

        self.layout.addWidget(self.HP_lbl, 0, 0,1,2)
        self.layout.addWidget(self.HP_edit, 0, 2,1,2)
        self.layout.addWidget(self.Tref_lbl, 1, 0,1,2)
        self.layout.addWidget(self.Tref_edit, 1, 2,1,2)

        
        self.layout.addWidget(self.IsenEff_lbl, 2, 1,1,4)
        self.layout.addWidget(self.K1_lbl, 3, 0)
        self.layout.addWidget(self.K1_edit, 3, 1)
        self.layout.addWidget(self.K2_lbl, 3, 2)
        self.layout.addWidget(self.K2_edit, 3, 3)
        
        self.layout.addWidget(self.K3_lbl, 4, 0,1,2)
        self.layout.addWidget(self.K3_edit, 4, 2,1,2)
        
        self.layout.addWidget(self.R1_lbl, 5, 0)
        self.layout.addWidget(self.R1_edit, 5, 1)
        self.layout.addWidget(self.R2_lbl, 5, 2)
        self.layout.addWidget(self.R2_edit, 5, 3)
        
        
        
        self.layout.addWidget(self.VolEff_lbl, 6, 1,1,4)
        self.layout.addWidget(self.a0_lbl, 7, 0)
        self.layout.addWidget(self.a0_edit, 7, 1)
        self.layout.addWidget(self.a1_lbl, 7, 2)
        self.layout.addWidget(self.a1_edit, 7, 3)
        
        self.layout.addWidget(self.MecEff_lbl, 8, 0,1,2)
        self.layout.addWidget(self.MecEff_edit, 8, 2,1,2)
        
        self.layout.addWidget(self.cyl_lbl, 9, 0,1,2)
        self.layout.addWidget(self.cyl_edit, 9, 2,1,2)
        
        
        
        self.layout.addWidget(self.Pu_lbl_title, 10, 0,1,2)
        self.layout.addWidget(self.Pu_lbl, 10, 2,1,2)
        
        self.layout.addWidget(self.Pel_lbl_title, 11, 0,1,2)
        self.layout.addWidget(self.Pel_lbl, 11, 2,1,2)
        
        self.layout.addWidget(self.Qlosses_lbl_title, 12, 0,1,2)
        self.layout.addWidget(self.Qlosses_lbl, 12, 2,1,2)
      
        self.layout.addWidget(self.Tis_lbl_title, 13, 0,1,2)
        self.layout.addWidget(self.Tis_lbl, 13, 2,1,2)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setObjectName(self.node.content_label_objname)
        
    def serialize(self):
        res = super().serialize()
        res['HP'] = self.HP_edit.text()
        res2 = super().serialize()
        res2['K1'] = self.K1_edit.text()
        
        res3 = super().serialize()
        res3['K2'] = self.K2_edit.text()
        
        res4 = super().serialize()
        res4['K3'] = self.K3_edit.text()
        
        res5 = super().serialize()
        res5['R1'] = self.R1_edit.text()
        
        res6 = super().serialize()
        res6['R2'] = self.R2_edit.text()
        
        res7 = super().serialize()
        res7['Tref'] = self.Tref_edit.text()
        
        res8 = super().serialize()
        res8['a0'] = self.a0_edit.text()
        
        res9 = super().serialize()
        res9['a1'] = self.a1_edit.text()
        
        res10 = super().serialize()
        res10['MecEff'] = self.MecEff_edit.text()
        
        res11= super().serialize()
        res11['cyl'] = self.cyl_edit.text()
        
      
        
        return res,res2,res3 ,res4, res5, res6, res7, res8, res9, res10, res11

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
        res3 = super().deserialize(data, hashmap)
        res4 = super().deserialize(data, hashmap)
        res5 = super().deserialize(data, hashmap)
        res6 = super().deserialize(data, hashmap)
        res7 = super().deserialize(data, hashmap)
        res8 = super().deserialize(data, hashmap)
        res9 = super().deserialize(data, hashmap)
        res10 = super().deserialize(data, hashmap)
        res11= super().deserialize(data, hashmap)
        try:
            
            HP = data[0]["HP"]
            K1 = data[1]['K1']
            K2 = data[2]['K2']
            K3 = data[3]['K3']
            R1 = data[4]['R1']
            R2 = data[5]['R2']
            Tref = data[6]['Tref']
            a0 = data[7]['a0']
            a1 = data[8]['a1']           
            MecEff = data[9]['MecEff']
            cyl = data[10]['cyl']
            
            # print("values=",value,value2,value3,value4)
            
            self.HP_edit.setText(HP)
            self.K1_edit.setText(K1)
            self.K2_edit.setText(K2)
            self.K3_edit.setText(K3)
            self.R1_edit.setText(R1)
            self.R2_edit.setText(R2)
            
            self.Tref_edit.setText(Tref)
            self.a0_edit.setText(a0)
            self.a1_edit.setText(a1)
            self.MecEff_edit.setText(MecEff)
            self.cyl_edit.setText(cyl)
            # self.F_kgs_edit.setText(value4)
            
            return True & res  & res2 & res3 & res4 & res5 & res6 & res7 & res8 & res9 & res10 & res11
        except Exception as e:
            dumpException(e)
        return res,res2,res3 ,res4, res5, res6, res7, res8, res9, res10, res11

@register_node(OP_NODE_COMP_M)
class CalcNode_Comp(CalcNode):
    icon = "icons/compressor.png"
    op_code = OP_NODE_COMP_M
    op_title = "Compresseur m"
    content_label = "/"
    content_label_objname = "calc_node_comp_m"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcCompContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=500
        self.grNode.width=350
        
        self.content.HP_edit.textChanged.connect(self.onInputChanged)
        self.content.Tref_edit.textChanged.connect(self.onInputChanged)
        self.content.K1_edit.textChanged.connect(self.onInputChanged)
        self.content.K2_edit.textChanged.connect(self.onInputChanged)
        self.content.K3_edit.textChanged.connect(self.onInputChanged)
        self.content.R1_edit.textChanged.connect(self.onInputChanged)
        self.content.R2_edit.textChanged.connect(self.onInputChanged)
        self.content.a0_edit.textChanged.connect(self.onInputChanged)
        self.content.a1_edit.textChanged.connect(self.onInputChanged)
        self.content.MecEff_edit.textChanged.connect(self.onInputChanged)
        self.content.cyl_edit.textChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       
        COMP=Compressor_m.Object()
        Fluid_connect(COMP.Inlet,a)
        ################""""
        u_HP = self.content.HP_edit.text()
        s_HP = float(u_HP)
        ####################
        COMP.HP=1e5*s_HP
        COMP.K1=float(self.content.K1_edit.text()) 
        COMP.K2=float(self.content.K2_edit.text()) 
        COMP.K3=float(self.content.K3_edit.text()) 
        COMP.R1=float(self.content.R1_edit.text()) 
        COMP.R2=float(self.content.R2_edit.text()) 
        
        COMP.a0=float(self.content.a0_edit.text()) 
        COMP.a1=float(self.content.a1_edit.text())
        COMP.MecEff=float(self.content.MecEff_edit.text()) 
        COMP.cyl=float(self.content.cyl_edit.text()) 
        
        COMP.Tdischarge_target=float(self.content.Tref_edit.text())
        COMP.calculate()
        
       
        self.value.append(COMP.Outlet.fluid) #fluide
        self.value.append(COMP.Outlet.F_kgs) #débit
        self.value.append(COMP.Outlet.P/1e5) #pression min
        self.value.append(COMP.Outlet.h/1000) #Enthalpie
        
        self.content.Pu_lbl.setText("%.2f" % (COMP.Pu/1000)) #"%d" % 
        self.content.Pel_lbl.setText("%.2f" % (COMP.Pel/1000)) #"%d" % 
        
        self.content.Qlosses_lbl.setText("%.2f" % (COMP.Qlosses/1000))
        self.content.Tis_lbl.setText("%.2f" % (COMP.T3is-273.15))
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value
    
    
    
    
 