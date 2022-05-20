'''
  /¯¯¯¯¯¯¯¯¯\
 /           \
|   |   __    |  *********************************************
|   |  |  \   |  Code writen by Ignacio and Martin.
|   |  |  |   |
|   |__|_ |   |  La Data Web 
|      |__/   |  *********************************************
 \            /
  \__________/
  
'''

import json
import requests
from simplepbi import utils
import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder

class Imports():
    """Simple library to use the Power BI api and obtain imports from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request imports API
        Args:
            token: String
                Bearer Token to use the Power Bi Rest API
        """
        self.token = token
    
    def get_import(self, import_id):
        """Returns the specified import from My workspace.
        ### Parameters
        ----
        import_id: str uuid
            The Power Bi import id. 
        ### Returns
        ----
        Dict:
            A dictionary containing a import in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports/{}".format(import_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_import_in_group(self, workspace_id, import_id):
        """Returns the specified import from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        import_id: str uuid
            The Power Bi import id.
        ### Returns
        ----
        Dict:
            A dictionary containing a import in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports/{}".format(workspace_id, import_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_imports(self):
        """Returns a list of imports from My workspace.
        ### Parameters
        ----
        None
        ### Returns
        ----
        Dict:
            A dictionary containing all the imports in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_imports_in_group(self, workspace_id):
        """Returns a list of imports from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the imports in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def simple_import_pbix(self, filePath, datasetDisplayName, nameConflict=None, overrideModelLabel=None, overrideReportLabel=None):
        """Creates new content in My Workspace. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        datasetDisplayName: str 
            The display name of the dataset should include file extension
        filePath: str
            Full local path like "C:/Users/SimplePBI/Documents/Filename.pbix"
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath
            The path of the OneDrive for Business Excel (.xlsx) file to import, which can be absolute or relative. Power BI .pbix files aren't supported.
        fileUrl
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/imports?datasetDisplayName={}".format(workspace_id, datasetDisplayName)
            if nameConflict != None:
                url = url + "&nameConflict={}".format(str(nameConflict))
            if overrideModelLabel != None:
                url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
            if overrideReportLabel != None:
                url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
            # you need this dictionary to convert a binary file into form-data format
            # None here means we skip the filename and file content is important 
            files = {'value': (None, open(filePath, 'rb'), 'multipart/form-data')}
            # The MultipartEncoder is posted as data, don't use files=...!
            mp_encoder = MultipartEncoder(fields=files)
            # The MultipartEncoder provides the content-type header with the boundary:
            headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = mp_encoder, headers=headers)
            res.raise_for_status()
            
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def simple_import_pbix_in_group(self, workspace_id, filePath, datasetDisplayName, nameConflict=None, overrideModelLabel=None, overrideReportLabel=None):
        """Creates new content in the specified workspace. Pbix with size lower than 1gb or with temporal blog storage url created
        Note: supported content for now Power BI .pbix files. Soon JSON files (.json), Excel files (.xlsx), SQL Server Report Definition Language files (.rdl)        
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        datasetDisplayName: str 
            The display name of the dataset should include file extension
        filePath: str
            Full local path like "C:/Users/SimplePBI/Documents/Filename.pbix"
        nameConflict: str
            Specifies what to do if a dataset with the same name already exists. The default value is Ignore. You can also use CreateOrOverwrite,GenerateUniqueName or Overwrite
        overrideModelLabel: str
            Determines whether to override the existing label on a model when republishing a Power BI .pbix file. The service default value is true.
        overrideReportLabel: str
            Whether to override the existing label on a report when republishing a Power BI .pbix file. The service default value is true.
        ### Request Body
        ----
        filePath
            The path of the OneDrive for Business Excel (.xlsx) file to import, which can be absolute or relative. Power BI .pbix files aren't supported.
        fileUrl
            SOON The shared access signature URL of the temporary blob storage used to import large Power BI .pbix files between 1 GB and 10 GB in size.
            
        ### Returns
        ----
        Dict:
            Response 202. A dict with a new report id.
        ### Limitations
        ----
        Importing a Power BI .pbix file from OneDrive isn't supported.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}".format(workspace_id, datasetDisplayName)
            if nameConflict != None:
                url = url + "&nameConflict={}".format(str(nameConflict))
            if overrideModelLabel != None:
                url = url + "&overrideModelLabel={}".format(str(overrideModelLabel))
            if overrideReportLabel != None:
                url = url + "&overrideReportLabel={}".format(str(overrideReportLabel))                        
            # you need this dictionary to convert a binary file into form-data format
            # None here means we skip the filename and file content is important 
            files = {'value': (None, open(filePath, 'rb'), 'multipart/form-data')}
            # The MultipartEncoder is posted as data, don't use files=...!
            mp_encoder = MultipartEncoder(fields=files)
            # The MultipartEncoder provides the content-type header with the boundary:
            headers = {'Content-Type': 'multipart/form-data', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = mp_encoder, headers=headers)
            res.raise_for_status()
            
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

