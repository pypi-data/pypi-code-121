import argparse
import os.path

from numpy import void
from functionblock import ASLibraryDataType, ASLibraryFunction, ASLibrary, BlockSection
from jinja2 import Environment, FileSystemLoader

def BuildFunctionBlockPage(funct : ASLibraryFunction) -> None:
    if(os.path.exists('./Output/{0}.html'.format(funct._name))):
        os.remove('./Output/{0}.html'.format(funct._name))

    with open('./Output/{0}.html'.format(funct._name),"w") as f:
        file_loader = FileSystemLoader("./src/Templates/")
        env = Environment(loader = file_loader)

        template = env.get_template("functionBlockPage.html")
        output = template.render(functionBlock = funct)
        f.write(output)

# Output all of the datatype files from the library's typ file(s)
def BuildTypePage(typ : ASLibraryDataType) -> None:
    if(os.path.exists('./Output/DataTypes/{0}.html'.format(typ._name))):
        os.remove('./Output/DataTypes/{0}.html'.format(typ._name))
    
    with open('./Output/DataTypes/{0}.html'.format(typ._name),"w") as f:
        file_loader = FileSystemLoader("./src/Templates/")
        env = Environment(loader = file_loader)

        template = env.get_template("libDatatypePage.html")
        output = template.render(datatype = typ)
        f.write(output)

#Main classes if you're trying to call the script standalone
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fun', help='Function File Path', dest='funFilePath', required=True)
    parser.add_argument('-t', '--type', help='Type File Path', dest='typFilePath', required=True)
    args = parser.parse_args()
    funFileContents = ''
    typFileContents = ''
    with open(args.funFilePath) as file:
        funFileContents = file.read()
    with open(args.typFilePath) as file:
        typFileContents = file.read()
    lib = ASLibrary(funFileContents,typFileContents)
    for funct in lib._functions:
        BuildFunctionBlockPage(funct)
    for typ in lib._datatypes:
        BuildTypePage(typ)
                

if __name__ == '__main__':
    main()
