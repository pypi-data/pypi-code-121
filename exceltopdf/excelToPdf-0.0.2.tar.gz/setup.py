import setuptools 


setuptools.setup(
    name="excelToPdf", 
    version="0.0.2", 
    author="Suraj Kumar", 
    description="A Package To Convert Excels to pdf. ", 
    packages=["excelToPdf"],
    package_data={'excelToPdf': ['app.jar','unoconv']},
    include_package_data=True 
)