from __future__ import annotations
from typing import TYPE_CHECKING, OrderedDict
if TYPE_CHECKING:
    from chilitools.api.connector import ChiliConnector

from time import sleep
from chilitools.api.mycp import generateLoginTokenForURL, getCredentials
from chilitools.utilities.errors import ErrorHandler
from chilitools.utilities.defaults import DEFAULT_TASKPRIORITY, DEFAULT_TASKUPDATETIME, STAFF_TYPE, USER_TYPE

class Resources:

  def __init__(self, connector: ChiliConnector):
    self.connector = connector
  def DownloadTempFile(self, assetType: str, path: str = '', data: str = '', dynamicAssetProviderID: str = '', noContentHeader: bool = None):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"resources/{assetType}/download/tempfile",
      queryParams={'path':path, 'data':data, 'dynamicAssetProviderID':dynamicAssetProviderID, 'noContentHeader':noContentHeader}
    )
  def ResourceItemMove(self, resourceType: str, itemID: str, newName: str, newFolderPath: str):
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/{resourceType}/items/{itemID}/move",
      queryParams={'newName':newName, 'newFolderPath':newFolderPath}
    )
  def ResourceItemCopy(self, resourceType: str, itemID: str, newName: str, folderPath: str = ''):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items/{itemID}/copy",
      queryParams={'newName':newName, 'folderPath':folderPath },
    )
  def ResourceItemDelete(self, resourceType: str, itemID: str):
    return self.connector.makeRequest(
      method='delete',
      endpoint=f"/resources/{resourceType}/items/{itemID}",
    )
  def ResourceItemSave(self, resourceType: str, itemID: str, xml: str):
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/{resourceType}/items/{itemID}/save",
      json={'xml':xml}
    )
  def ResourceItemGetXML(self, resourceType: str, itemID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/xml"
    )
  def ResourceItemGetURL(self, resourceType: str, itemID: str, URLtype: str, pageNum: int = 1):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/url",
      queryParams={'type':URLtype, 'pageNum':pageNum},
    )
  def ResourceItemAdd(self, resourceType: str, newName: str, folderPath: str, xml: str, fileData: str = ''):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items",
      queryParams={'newName':newName, 'folderPath':folderPath},
      json={'xml':xml, 'fileData':fileData}
    )
  def ResourceItemAddFromURL(self, resourceType: str, newName: str, folderPath: str, url: str, authUsername: str = None, authPassword: str = None, reuseExisting: bool = None, previewFileURL: str = None, previewExtension: str = None, isPermanentPreview: bool = None):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items/fromurl",
      queryParams={'newName':newName, 'folderPath':folderPath, 'url':url, 'login':authUsername, 'pw':authPassword, 'reuseExisting':reuseExisting, 'previewFileURL':previewFileURL, 'previewExtension':previewExtension, 'isPermanentPreview':isPermanentPreview },
    )
  def ResourceGetTreeLevel(self, resourceType: str, parentFolder: str = '', numLevels: int = 1, includeSubDirectories: bool = True, includeFiles: bool = True):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/treelevel",
      queryParams={'parentFolder':parentFolder, 'numLevels':numLevels, 'includeSubDirectories':includeSubDirectories, 'includeFiles':includeFiles}
    )
  def ResourceGetTree(self, resourceType: str, parentFolder: str = '', includeSubDirectories: bool = 'False', includeFiles: bool = True):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/tree",
      queryParams={'parentFolder':parentFolder, 'includeSubDirectories':includeSubDirectories, 'includeFiles':includeFiles}
    )
  def ResourceSearch(self, resourceType: str, name: str = ''):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}",
      queryParams={'name':name}
    )
  def ResourceItemGetDefinitionXML(self, resourceType: str, itemID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/definitionxml"
    )
  def DownloadAsset(self, resourceType: str, id: str, itemPath: str = None, name: str = None, assetType: str = None, page: int = None, docID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/download",
      queryParams={'id':id, 'path':itemPath, 'name':name, 'type':assetType, 'page':page, 'docId':docID, 'taskPriority':taskPriority}
    )
  def getPDFSettingsXML(self, settingsID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/PdfExportSettings/items/{settingsID}/xml"
    )
  def setNextResourceItemID(self, resourceType: str, itemID: str):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/nextitemid",
      queryParams={'itemID':itemID}
    )
  def getResourceList(self):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources"
    )
  def getDownloadURL(self, resourceType: str, itemID: str, pageNum: int = 1):
    return 'https://' + self.connector.baseURL + '/' + self.connector.enviroment + '/download.aspx?type=original&resourceName=' + resourceType + '&id=' + itemID + '&apiKey=' + self.connector.getAPIKey() + '&pageNum=' + pageNum

class Documents:
  def __init__(self, connector: ChiliConnector):
    self.connector = connector

  def setAssetDirectories(self, documentID: str, userAssetDirectory: str, userGroupAssetDirectory: str, documentAssetDirectory: str):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/assetdirectories",
      queryParams={'userAssetDirectory':userAssetDirectory, 'userGroupAssetDirectory':userGroupAssetDirectory, 'documentAssetDirectory':documentAssetDirectory },
    )
  def setDataSource(self, documentID: str, datasourceXML: str):
    return self.connector.makeRequest(
      method="post",
      endpoint=f"/resources/documents/{documentID}/datasource",
      json={'datasourceXML':datasourceXML}
    )
  def getInfo(self, documentID: str, extended: bool = False):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/info",
      queryParams={'extended':extended}
    )
  def delete(self, documentID: str):
    return self.connector.resources.ResourceItemDelete(resourceType='documents', itemID=documentID)
  def getPreviewURL(self, documentID: str, URLtype: str = 'full', pageNum: int = 1):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/items/{documentID}/url",
      queryParams={'type':URLtype, 'pageNum':pageNum},
    )
  def getEditorURL(self, documentID: str, workSpaceID: str = None, viewPrefsID: str = None, constraintsID: str = None, viewerOnly: bool = None, forAnonymousUser: bool = None):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"resources/documents/{documentID}/urls/editor",
      queryParams={'workSpaceID':workSpaceID, 'viewPrefsID':viewPrefsID, 'constraintsID':constraintsID, 'viewerOnly':viewerOnly, 'forAnonymousUser':forAnonymousUser}
    )
  def getXML(self, documentID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/items/{documentID}/xml"
    )
  def setXML(self, documentID: str, docXML: str):
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/documents/items/{documentID}/save",
      json={'xml':docXML}
    )
  def getVariableValues(self, documentID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/variablevalues"
    )
  def setVariableValues(self, documentID: str, varXML: str):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/variablevalues",
      json={'varXML':varXML}
    )
  def createPDF(self, documentID: str, settingsXML: str, taskPriority: int = DEFAULT_TASKPRIORITY):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/representations/pdf",
      queryParams={'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )
  def createTempPDF(self, documentXML: str, settingsXML: str = None, settingsID: str = None, itemID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY):
    if settingsID is None and settingsXML is None:
      return
    if settingsID is not None:
      settingsXML = self.resources.getPDFSettingsXML(settingsID=settingsID).text
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/tempxml/pdf",
      queryParams={'itemID':itemID, 'taskPriority':taskPriority},
      json={'settingsXML':settingsXML, 'docXML':documentXML}
    )
  def processServerSide(self, documentID: str):
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/documents/documentprocessor",
      json={'itemID':documentID, 'resourceXML':''}
    )

  def createImages(self, documentID: str, imageConversionProfileID: str, settingsXML: str, taskPriority: int = DEFAULT_TASKPRIORITY):
    return self.connector.makeRequest(
      method='post',
      endpoint=f"resources/documents/{documentID}/representations/images",
      queryParams={'imageConversionProfileID':imageConversionProfileID, 'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )

class System:
  def __init__(self, connector: ChiliConnector):
    self.connector = connector

  def getTaskStatus(self, taskID: str):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/system/tasks/{taskID}/status"
    )
  def waitForTask(self, taskID: str, taskUpdateTime: int = DEFAULT_TASKUPDATETIME, debug: bool = False) -> OrderedDict:
    while True:
      resp = self.getTaskStatus(taskID=taskID).contentAsDict()
      if debug: print(resp)
      if resp['task']['@finished'] == "True":
        return resp
      sleep(taskUpdateTime)

  def GenerateApiKey(self):
    login = getCredentials()
    if login['type'] == STAFF_TYPE:
      requestJSON = {'userName':'ChiliAdmin', 'password': generateLoginTokenForURL(backofficeURL=self.connector.backofficeURL)}
    elif login['type'] == USER_TYPE:
      requestJSON = login['credentials']
    response = self.connector.makeRequest(
        method='post',
        endpoint='system/apikey',
        queryParams={'environmentNameOrURL': self.connector.getEnvironment()},
        json=requestJSON,
        authRequired=False
    )
    if 'apiKey' in response.contentAsDict().keys():
        return response.contentAsDict()['apiKey']
    else:
      print(response)
      return ErrorHandler().getError('GENAPIKEY')
  def SetAutomaticPreviewGeneration(self, createPreviews: bool):
    return self.connector.makeRequest(
      method='put',
      endpoint='system/apikey/autopreviewgeneration',
      queryParams={'createPreviews':createPreviews}
    )

