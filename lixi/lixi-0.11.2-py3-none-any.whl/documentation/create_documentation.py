import os
import time

start = time.time()

currentDirectory = os.getcwd()

print("working directory: " + currentDirectory)		
readpath = os.path.join(currentDirectory,'TransactionMaster','LIXI-Master-Schema.xsd')
print("read path: " + readpath)
with open(readpath, 'r') as file:
    data = file.read()
data = "var schemaString = `" + data + "`"
writepath = os.path.join(currentDirectory, 'js', 'LIXI-Master-Schema.js')
print("write path: " + writepath)
with open(writepath, 'w') as file:
    data = file.write(data)

    
readpath = os.path.join(currentDirectory,'TransactionMaster','LIXI_Glossary.xml')
print("read path: " + readpath)
with open(readpath, 'r') as file:
    data = file.read()
data = "var glossaryString = `" + data + "`"
writepath = os.path.join(currentDirectory, 'js', 'LIXI_Glossary.js')
print("write path: " + writepath)
with open(writepath, 'w') as file:
    data = file.write(data)


end = time.time()
print("\nComplete.")
print("   - Total Time:                      " + str(end - start))   
