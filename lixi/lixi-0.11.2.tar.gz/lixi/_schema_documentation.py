import os, pkg_resources, zipfile, shutil
from io import BytesIO
from lxml import etree


def create_schema_documentation(xml_schema_string , json_schema_string, output_folder, output_name, glossary_string=None):
    """
    Generates documentation for the provided LIXI schema. Documentation is based on a custom version of readthedocs [https://docs.readthedocs.io/en/rel/theme.html] theme.

    Args:
        xml_schema_string (:obj:`str`, required): LIXI XML schema provided as string.
        json_schema_string (:obj:`str`, required): LIXI XML schema provided as string.
        output_folder (:obj:`str`, required): Path to write the produced lixi schema documentation to.
        outputname (:obj:`str`, required): Custom schema name used in namespace.
        glossary_string (:obj:`str`, optional): LIXI Glossary update provided as a string. Defaults to None.
            
    Returns:
        Outputs the custom documentation for a schema to the specified folder. 
    """   
    
    if output_folder!=None:
        

        def copytree(src, dst, symlinks=False, ignore=None):
            
            if os.path.exists(dst):
                shutil.rmtree(dst)
                os.mkdir(dst)
            else:    
                os.mkdir(dst)
            
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    if item not in ['README.md', 'create_documentation.py', '.gitlab-ci.yml', '.gitignore']:
                        shutil.copy2(s, d)    
        
        # First create the directory
        output_path = os.path.join(output_folder, output_name) 
        
        # Copy all documentation files from lib to provided path
        docs_location = pkg_resources.resource_filename(__name__, "documentation")
        copytree(docs_location, output_path)
        
        # Write data to file to display correct info
        data = "var schemaString = `" + xml_schema_string + "`"
        writepath = os.path.join(output_path, 'js', 'LIXI-Master-Schema.js')
        with open(writepath, 'w+') as file:
            data = file.write(data)
            
        if glossary_string !=None:
            data = "var glossaryString = `" + glossary_string + "`"
            writepath = os.path.join(output_path, 'js', 'LIXI_Glossary.js')
            with open(writepath, 'w+') as file:
                data = file.write(data)
            
        return True        
        
    else:
        inMemoryOutputFile = BytesIO()
        zipFile = zipfile.ZipFile(inMemoryOutputFile, 'w', zipfile.ZIP_DEFLATED) 
        path = pkg_resources.resource_filename(__name__, "documentation")
    
        for root, dirs, files in os.walk(path):
            for file in files:
                if file not in ['README.md', 'create_documentation.py', '.gitlab-ci.yml', '.gitignore']: 
                    path_after_doc = output_name + root.split('documentation')[1]
                    zipFile.write(os.path.join(root, file), os.path.join(path_after_doc, file))
    
        text = "var schemaString = vkbeautify.xml(`" + xml_schema_string + "`)"
        zipFile.writestr(os.path.join(output_name,'js','LIXI-Master-Schema.js'), text)
        
        if glossary_string !=None:
            text = "var glossaryString = vkbeautify.xml(`" + glossary_string + "`)"
            zipFile.writestr(os.path.join(output_name,'js','LIXI_Glossary.js'), text)        
    
        if json_schema_string:
            zipFile.writestr(os.path.join(output_name + '.json'), json_schema_string)
        else:
            zipFile.writestr(os.path.join(output_name + '.xsd'), xml_schema_string)
        
        zipFile.close()
    
        return inMemoryOutputFile.getvalue()


        
        