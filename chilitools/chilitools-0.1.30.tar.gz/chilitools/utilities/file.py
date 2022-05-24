from __future__ import annotations
import requests
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chilitools.api.connector import ChiliConnector

from os.path import isfile, dirname, realpath
from os import makedirs
from chilitools.utilities.errors import ErrorHandler
from chilitools.utilities.xml import getTaskResultURL
from chilitools.utilities.defaults import DEFAULT_TASKPRIORITY

def currentPath() -> str:
  return dirname(realpath(__file__))

def readFile(fileName: str, isJSON: bool = False, encoding: str = None) -> dict:
  if checkForFile(fileName=fileName):
    with open(fileName, 'r', encoding=encoding) as file:
      if isJSON:
        return json.loads(file.read())
      else:
        return file.read()
  else:
    return ErrorHandler().getError(errorName="FILENOTFOUND")

def writeFile(fileName: str, data, isJSON: bool = False, encoding: str = None) -> None:
  makedirs(dirname(fileName), exist_ok=True)
  with open(fileName, 'w', encoding=encoding) as file:
    if isJSON:
      file.write(json.dumps(data))
    else:
      file.write(data)

def checkForFile(fileName: str) -> bool:
  if isfile(fileName):
    return True
  return False

def downloadFile(url: str, fullFileName: str, queryParams: dict = None) -> bool:
  if queryParams is None: queryParams = {}
  try:
    download = requests.get(url=url, allow_redirects=True, params=queryParams)
    open(fullFileName, 'wb').write(download.content)
    return True
  except Exception as e:
    print(e)
    return False

def generateAndDownloadPDF(connector: ChiliConnector, fullFileName: str, documentID: str = None, documentXML: str = None, settingsXML: str = None, settingsID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY, verbose: bool = False) -> str:
  if documentID is None and documentXML is None:
    return 'You need to provide a document ID or document XML parameter'
  if settingsID is None and settingsXML is None:
    return "You need to provide a PDF Export Settings Item ID or PDF Export Settings XML"
  if settingsID is not None:
    print(f"Getting PDF Export Settings XML for {settingsID}")
    settingsXML = connector.resources.getPDFSettingsXML(settingsID=settingsID).text
  if documentID is not None:
    resp = connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/representations/pdf",
      queryParams={'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )
  elif documentXML is not None:
    resp = connector.documents.createTempPDF(documentXML=documentXML, settingsXML=settingsXML)
  if verbose: print(resp.text)
  if resp.didSucceed():
    taskID = resp.contentAsDict()['task']['@id']
    task = connector.system.waitForTask(taskID=taskID, debug=verbose)
    if task == ErrorHandler().getError("TASKNOTSUCCEEDED"):
      return ErrorHandler().getError("TASKNOTSUCCEEDED")
    success = downloadFile(url=getTaskResultURL(task=task), fullFileName=fullFileName)
    print(f"URL: {getTaskResultURL(task=task)}")
    if success:
      return (f"The file successfully downloaded to {fullFileName}")
    return "The file download process failed."

def createAndDownloadImages(connector: ChiliConnector, documentID: str, imageConversionProfileID: str, settingsXML: str, taskPriority: int = DEFAULT_TASKPRIORITY):
  resp = connector.makeRequest(
    method='post',
    endpoint=f"resources/documents/{documentID}/representations/images",
    queryParams={'imageConversionProfileID':imageConversionProfileID, 'taskPriority':taskPriority},
    json={'settingsXML':settingsXML}
  )
  if resp.didSucceed():
    taskID = resp.contentAsDict()['task']['@id']
    task = connector.system.waitForTask(taskID=taskID)
    return task
  return f"Request to make images failed: {resp.text}"