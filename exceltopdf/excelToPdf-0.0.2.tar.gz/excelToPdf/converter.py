from io import BufferedReader
from sre_compile import isstring
import subprocess
from urllib import parse
import json 
import os  
import uuid
import traceback


def convertToPdf(file,options):
    try: 

        if isstring(file): 
            if ( not  os.path.exists(file))  or  (not  os.path.isfile(file)):
                raise Exception("Invalid File Path / File Does Not Exist ")
        if isinstance(file, (BufferedReader)):
            bytesArray = file.read()
            fileName ="./{}.xlsx".format(uuid.uuid4())
            with open(fileName,"wb") as out:
                out.write(bytesArray)
                
                file = os.path.abspath(fileName )
    
        fileDetails = file.split('.')
        fileDetails.pop() 
        fileDetails.append("pdf")
        fileNameForPdf = ".".join(fileDetails)

        filePathForPdf = os.path.join(os.path.abspath("."),fileNameForPdf)
        commandStrings =["java","-jar",os.path.join(os.path.dirname(__file__),"app.jar"),file ,file ,parse.quote(json.dumps(options))]  
        command = " ".join(commandStrings) 
        res =subprocess.run(command) 
        
        pdfCommandString = ["python", os.path.join(os.path.dirname(__file__),"unoconv"),"-o",filePathForPdf , "-f","pdf",file ] 

        resPdf = subprocess.run(" ".join(pdfCommandString))
        return_data = open(filePathForPdf,"rb").read() 
        os.unlink(file)
        os.unlink(filePathForPdf)
        return return_data

    except Exception as e: 
        print(e)
        traceback.print_stack()





    pass 