# Engine class can be used to fill all web pages, as long as the import model matches our model prototype, and already contains value. 
# Every page has to make its own page data tree model , and assembly values together.  So, the only import data is assemblied model and data sets. 
# The class takes charge of identifing element type and do related action (click, select, and finally fill text fields...)
from operator import contains
from models.definition import Action
from models.element import (RadioYesNoElement,RadioYesNoNullElement,ButtonElement,
                            CheckboxElement,SelectElement, InputElement,AreatextElement,
                            TurnPage,DependantSelectElement)

class Engine():
    def __init__(self):
        self.output = [] # js app handleable objects list
    
    # recurssion for manupilating all elements. It's common for all pages, so put these functions into the Page prototype
    def treeForeach(self,model):
        for node in model:
            self.handleNode(node)
            children = self.getChildren(node)
            children and self.treeForeach(children) # 遍历子树

    # This function focuses on processing node founded by getChildren
    def handleNode(self,node):
        match node.get("action_type"):
            case Action.Radio_Yes_No.value:
                # 根据模型和数据，生成puppeteer能处理的对象
                radio_yn=RadioYesNoElement(**node)
                self.output.append(radio_yn.make())
                
            case Action.Radio_Yes_No_Null.value:
                radio_ynn=RadioYesNoNullElement(**node)
                self.output.append(radio_ynn.make())
                    
            case Action.Checkbox.value:
                cbk=CheckboxElement(**node)
                self.output.append(cbk.make())
            
            case Action.Select.value:
                select=SelectElement(**node)
                self.output.append(select.make())
            
            case Action.SelectPopup.value: 
                select=SelectElement(**node)
                self.output.append(select.make())
                
            case Action.Input.value:
                input=InputElement(**node)
                self.output.append(input.make())  
                
            case Action.Areatext.value:
                areatext=AreatextElement(**node)
                self.output.append(areatext.make())  
            
            case Action.Button.value:
                button=ButtonElement(**node)
                self.output.append(button.make()) 
                
            case Action.Turnpage.value:
                turnpage=TurnPage(**node)
                self.output.append(turnpage.make())  
                
            case Action.RepeatSection.value:
                self.repeatSection(node)
            
            case Action.DependantSelect.value:
                ds=DependantSelectElement(**node)
                self.output.append(ds.make()) 
            
            case Action.SelectPopup2.value: # dependanat select and followed by children
                #1 get dependant select element
                dse={
                    "action_type":"DependantSelectElement",
                    "select1":node.get('select1'),
                    "select2":node.get('select2')
                }
                select2=DependantSelectElement(**dse)
                self.output.append(select2.make())  

            case _:
                pass

    # This funciton only takes charge of finding nodes, not processing it.
    def getChildren(self,node):
        match node.get("action_type"):
            case Action.Radio_Yes_No.value:
                return node.get("yes_children") if node.get("value") else node.get("no_children")
            case Action.Radio_Yes_No_Null.value:
                if node.get("value") != None:
                    return node.get("yes_children") if node.get("value") else node.get("no_children")
                return node.get("null_children")
            case Action.SelectPopup.value:
                #according to the selection, choose  children
                childName = '_'.join(node.get("nameValue").split('-')).lower() + "_children" if "-" in node.get("nameValue")  else "_".join(node.get('nameValue').split(' ')).lower() + "_children"
                return node[childName]
            case Action.SelectPopup2.value:
                #according to the selection, choose  children
                return node[node.get('generated_children_name')]
            case _:
                return node.get("children")
    
    # handle repeat sections
    # 限制：repeat内部的元素，必须是最底层element,不能再有下级元素。
    # valueObjects是客户数据，targetElements是网页元素，本程序匹配他们生成最终填表列表数据
    def repeatSection(self,node):
        # loop the valueObjects, and create new keys based on targetElements, then meke new list of objects by assigning value to new keys
        for index, value_object in enumerate(node.get("valueObjects")):
            for target_element in node.get("targetElements"):
                # 从target emement的value处，获得value object的key
                key=target_element['value']
                #element.value is the key of value object, so get the final value for web element
                value=value_object[key]  
                # targetElements中, ???是通配符，需要用index来替代。
                newElementId = target_element['id'].replace("???",str(index))
                # 将获得了新ID和value的元素替代老的
                newElement = {**target_element, **{ "id": newElementId, "value": value } }
                self.handleNode(newElement);


    