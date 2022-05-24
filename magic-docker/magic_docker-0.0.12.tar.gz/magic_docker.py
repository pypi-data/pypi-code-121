#########################

"""

Author : Babak.EA 
Date   : 2020-05-04 v.01
update : 2022-05-24 v.0.12
App    : Magic_Docker # an automated python tools to speed up the containerizing process


"""




a=" Hi  "
b= """ You are using the Magic-Docker Tools. It is an automated python application to create an error-free Docker Image. 
"""+ """ The current version has been programmed for Linux and MAC Os if you are a Linux or MAC user, good news! 
this magical tool will take care of all the steps. """ + """ If you are a windows user, the program still would help you. 
It will create the Dockerfile, requirements, and the shell script to build and save the created docker image. "
c=" You need to run the shell command manually.""" 

d=" Please feel free to contact me if you needed any further assistance. "

e="Thank you. "

f=" Babak EA"

   
from stdlib_list import stdlib_list
from ipywidgets import FileUpload   
import ipywidgets
from ipywidgets import widgets
import os,sys
import re
import pkg_resources
import datetime
import subprocess
#import platform
from sys import platform
import numpy as np
#from gtts import gTTS




"""

%%html
<style>
.output_wrapper, .output {
    height:auto !important;
    max-height: none;
}
.output_scroll {
    box-shadow:none !important;
    webkit-box-shadow:none !important;
}

.package_header {
    width: 100%;
    background-color: #0e2b59;
    color: #ffffff;
    font-size: 14px;
    text-align: center;
    padding-top: 8px;
    padding-right: 8px;
    padding-bottom: 8px;
    padding-left: 8px;
}

.placeholder {
    width: 100%;
    background-color: gray;
    height: 100px;
}

.passed_test_table {
  display: table;         
  width: 100%;         

  background-color: #ebffd3;                
  border-spacing: 5px;
}

# (...) rest of css classes omitted 
</style>
"""
display(a,
       b,
       c,
       d,
       e,
       f)
#del(a,b,c,d,e,f)







#############################
class Magic:
    def __init__(self,manual_reject=0):
        #print(Greeting_Message)
        self.lib=[]
        if manual_reject==0 :
            self.manual_reject=["pkg_resources"]
        else:
            self.manual_reject=["pkg_resources"]+manual_reject
        self.python_ver=sys.version[0:3]
        self.embeded_lib = stdlib_list(self.python_ver)#python version detection
        self.Tag=datetime.date.today().strftime("%m%d%Y")#Docker Tag declaration
        self.OS_name=platform
        #base line for Dockerfile  
        self.DOC_TEXT="FROM ubuntu:latest \n"+\
        "RUN apt-get update && apt-get -y update \n"+\
        "RUN apt-get install -y build-essential python{} python3-pip python3-dev \n".format(self.python_ver)+\
        "RUN pip3 -q install pip --upgrade \n"+\
        "RUN mkdir src \n"+\
        "WORKDIR src/ \n"+\
        "COPY . . \n"+\
        "RUN pip3 install -r requirements.txt \n" +\
        "RUN pip3 install jupyter \n"+\
        "WORKDIR /src/ \n"+\
        "RUN chmod +x /usr/bin/ \n"+\
        "COPY . . \n"+\
        "EXPOSE 8888 \n"+\
        'CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]'
                          

        self.File_reader()    
    def File_reader(self):
        upload=widgets.FileUpload()

        output_class = widgets.Output()
        
        display("please select the python model :",upload)
        self.model=upload
        self.model.observe(self.upload_class_eventhandler, names='value')

    def upload_class_eventhandler(self,names):
        self.Docker_name="docker_"+self.model.metadata[0]['name'].split(".")[0].lower()

        self.Lib_add()

        
    def lib_f(text):
        out=[]
        
        if re.match(r'^import', text):

            if " as " in text:
                text=text.replace("import ","").replace("\n","")
                text=text.split(" ")[0]
                text=text.split(".")[0]
                out+=[text]
            else:
                text=text.replace("import ","").replace(" ","").replace("\n","")
                text=text.split(",")

                if type(text)==str:
                    out+=[text]

                else:
                    #text=[x.split(".")[0] for x in text]
                    #print(text)
                    out+=text

            return list(set(out))
        elif re.match(r'from',text):
            text=text.replace("from ","")
            text=text.split(" ")[0]
            text=text.split(".")[0]
            #text=[x.split(".")[0] for x in text]
            out+=[text]
            
            
            return list(set(out))
        else:
            return np.NAN    
        
    def Lib_add(self):
        Lines=str(self.model.data[0]).split("\\n")
        #print(Lines)
        #self.lib=["numpy","pandas"]
        for line in Lines:
            if re.findall(r"import",line):

                line=line.replace("\\r","").replace('"','').replace("\\","")

                tem=Magic.lib_f(str(line).strip())

                if tem==tem:

                    self.lib+=tem
        self.lib=list(set(self.lib))
        self.lib=[x for x in self.lib if x not in self.embeded_lib+self.manual_reject]
        
        display("The following Libraries have been detected : ")
        display(self.lib)
        display("Please kindly add more file if there is any; otherwise press continue ... ")
        self.reset_btn(0)
        
            
    def reset_btn(self,flag):
        Continue_BTN = widgets.Button(description='Continue..')
        display(Continue_BTN)
        if flag==0:
            Continue_BTN.on_click(self.Continue_BTN_eventhandler)
        elif flag==1:
            Continue_BTN.on_click(self.Continue_BTN_eventhandler_W_DOCKER)
            
            
            
    def Continue_BTN_eventhandler(self,a):

        self.Lib_Version()
        
    def Continue_BTN_eventhandler_W_DOCKER(self,a):
        self.Write_Requirments(0) #### write requirments
        self.Write_Requirments(1) #### write Dockerfile
        display("Docker is creating the environment, it may take 5 to 10 minutes ")
        
        
        if "win" in self.OS_name.lower():
            self.Write_Windows()
        elif "lin" in self.OS_name.lower():
            self.Write_Linux()
        else :
            self.Write_MAC()
        
        


    def Lib_Version(self):
        #self.Requirment_dic=dict()
        self.STR=""

        for i in self.lib:
            try:
                self.STR+= i + "=="+ pkg_resources.get_distribution(i).version +"\n"
            except:
                self.STR+= i+"\n"   
            """
            try:
                self.Requirment_dic[i]=pkg_resources.get_distribution(i).version
            except:
                self.Requirment_dic[i]=np.nan
            """
            
        display("The following Text boxes are your Docker baselines:")
        display("**************************************************** ")
        display("Requirements : is including all the required libraries, You can add if you need more ...")
        display("**************************************************** ")
        
        
        
        self.text = widgets.Textarea(
        value=self.STR,
        placeholder='Paste ticket description here!',
        description='Requirements:',
        rows=5,  
        layout=widgets.Layout(width="70%",height="auto" ),
        )
        #disabled=False)

        #text.value="wfr3gt4h234"
        #text.add_class("placeholder")

            
        

        display(self.text)
            
        self.STR=self.text.value
        self.STR=self.STR.replace("sklearn","scikit-learn")
        
            
        
        
        display("****************************************************")
        display("Docker File : is including all the requirments such as OS, python, and the model requirments. you can install more tools if you want ...")
        display("**************************************************** ")
              
        self.DOCKER_text = widgets.Textarea(
        value=self.DOC_TEXT,
        placeholder='Paste ticket description here!',
        description='Dockerfile:',
        rows=15,  
        layout=widgets.Layout(width="70%",height="auto"),
            
        )
        #disabled=False)


        #DOCKER_text.add_class("placeholder")
        #DOCKER_text.width ='600px'
        #DOCKER_text.height='350px'
        display(self.DOCKER_text)
        #self.DOC_TEXT=DOCKER_text.value
        
        display("****************************************************")
        

        display("Please kindly edit the text boxes and press the conticue key to complete the process ...")
        self.reset_btn(1)  
        
  
    def Write_Requirments(self,flag):
        if flag==0:
            filehandle = open("./requirements.txt", "w")
            STR=self.text.value
            
            #print(self.text.value)
            #print(self.STR)

        elif flag==1:
            filehandle = open("./Dockerfile", "w")
            #STR=self.DOC_TEXT
            STR=self.DOCKER_text.value
        #filebuffer = ["hi","welcome","yes yes welcome"]
        filehandle.writelines(STR)
        filehandle.close()
        #self.reset_btn(1)
        
    def Write_Linux(self):
        shel_file = open('./Permission_set.sh', 'w')
        Shel_TEXT=["echo 'please type your password to complete the process:' \n",
                  "sudo chmod 777 /var/run/docker.sock"+"\n",
                  "\n",
                  "docker build -t {}/{} .".format(self.Docker_name,self.Tag)+" \n",
                  "docker save {}/{} > {}_{}".format(self.Docker_name,self.Tag,self.Docker_name,self.Tag+".tar")+" \n",
                  "echo 'Thnak you' \n"]

        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        subprocess.call(["sh","Permission_set.sh"])
        
        shel_file = open('./Run_docker.sh', 'w')
        Shel_TEXT=["docker run -p 8888:8888 {}/{}".format(self.Docker_name,self.Tag) ]

        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        
        
    
    def Write_Windows(self):
        display("****************************************************")
       
        shel_file = open('./Permission_set.bat', 'w')
        Shel_TEXT=["\n",
                  "docker build -t {}/{} .".format(self.Docker_name,self.Tag)+" \n",
                  "docker save {}/{} > {}_{}".format(self.Docker_name,self.Tag,self.Docker_name,self.Tag+".tar")+" \n",
                  "echo 'Thnak you' \n"]


        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        
        
        #subprocess.call(["powershell","Permission_set.bat"])
        display(" the process has been completed")
        display(" please run the 'Permission_set.ssh' using shell command and the Docker image will be created automatically")
        #subprocess.call(["sh","Permission_set.bat"])
        
        shel_file = open('./Run_docker.bat', 'w')
        Shel_TEXT=["docker run -p 8888:8888 {}/{}".format(self.Docker_name,self.Tag) ]

        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        
        
        
    def Write_MAC(self):
        display("**************************************************** ")
        shel_file = open('./Permission_set.sh', 'w')
        Shel_TEXT=[
                  "echo ' building process .... ' \n",
                  "\n",
                  "docker build -t {}/{} .".format(self.Docker_name,self.Tag)+" \n",
                  "docker save {}/{} > {}_{}".format(self.Docker_name,self.Tag,self.Docker_name,self.Tag+".tar")+" \n",
                  "echo 'Thnak you' \n"]

        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        subprocess.call(["sh","Permission_set.sh"])

        
        shel_file = open('./Run_docker.sh', 'w')
        Shel_TEXT=["docker run -p 8888:8888 {}/{}".format(self.Docker_name,self.Tag) ]

        shel_file.writelines(Shel_TEXT)
        shel_file.close()
        
    def version():
        return("Magic_docker: v0.0.11 , last update 2022-05-23")


     
####################

