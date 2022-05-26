import copy
import pandas as pd

from loguru import logger
from time import sleep
from datetime import timedelta

from .utils.ut_fileimport import FileUtils
from .utils.ut import Utils


class FileImport():

    def __init__(self, core):
        global client
        client = core
        self.raiseException = client.raiseException
  
    def importNewInventory(self, filePath:str, delimiter:str):
        """
        Creates a new inventory from a CSV file
        
        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str
            The CSV delimiter. Choose ',', ';', or 'tab'.

        Example:
        --------
        >>> createInventoryFromCsv(filePath='C:\\temp\\CreateMeterData.csv', delimiter=';')          
        """

        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return
        for file in files:
            content = FileUtils._readCsvFile(file, delimiter)

            ## CHECK FILE
            if content[0][0] != 'name':
                Utils._error(self, f"Wrong format. Expected header 'name' (for inventory) at position (0, 0).")
                return
    
            if content[2][0] != 'name':
                Utils._error(self, f"Wrong format. Expected header 'name' (for property) at position (2, 0).")
                return

            inventoryName = content[1][0]

            if not inventoryName:
                Utils._error(self, f"Inventory name missing")
                return 
    
            ## PREPARE IMPORT
            propertyList =[]   
            boolKeys = ['nullable', 'isArray', 'isReference'] 
            keys = [item for item in content[2]]
            columns = len(keys)

            for i, row in enumerate(content):
                if i >= 3:
                    propertyDict = {}
                    for column in range(columns):
                        if content[2][column] in boolKeys:
                            if row[column] == 'false': value = False
                            if row[column] == 'true': value = True
                        elif not row[column]: continue
                        else: value = row[column]
                        propertyDict.setdefault(content[2][column], value)
                    propertyList.append(propertyDict)

            ## IMPORT
            logger.debug(propertyList)
            result = client.createInventory(inventoryName, propertyList)
            if result == {'createInventory': {'errors': None}}: 
                logger.info(f"Inventory {inventoryName} created.")

        return

    def importItems(
            self, 
            filePath:str, 
            inventoryName:str, 
            delimiter:str=',',
            chunkSize:int = 5000, 
            pause:int = 1
            ) -> None:
        """
        Imports  items from a CSV file. The CSV file only needs a header of
        property definitions. Each line below the header represents a new item.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        inventoryName : str
            The field name of the inventory.
        delimiter : str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.
        chunkSize : int = 5000
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 500 items per chunk.
        pause : int = 1
            Between each chunk upload a pause is inserted in order to avoid overloading.

        Example:
        --------
        >>> importItems(filePath='C:\\temp\\Items.csv', delimiter=';'
            inventoryName='meterData')          
        """
        ## TIMEZONE
        #timeZone = FileUtils._timeZone(timeZone)
               
        ## READ FILE
        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return
        for file in files:
            content = FileUtils._readCsvFile(file, delimiter)

            ## PREPARE IMPORT   
            properties = client.inventoryProperties(inventoryName)
            logger.debug(f'Property names: {list(properties["name"])}')

            diff = FileUtils._comparePropertiesBasic(properties, content[0])
            if len(diff) > 0:
                Utils._error(self, f"Unknown properties: {list(diff)}")
                return 

            dataType, isArray, nullable = FileUtils._analyzeProperties(inventoryName, properties)
            logger.debug(f'Data types: {dataType}')
            logger.debug(f'Array properties: {isArray}')
            logger.debug(f'Nullable properties: {nullable}')
            logger.info(f"File '{filePath}' read and properties analyzed")

            items = FileUtils._createItems(content, dataType, isArray, nullable)
            logger.debug(f'Basic items: {items}' )


            # ## IMPORT
            if len(items) > chunkSize:
                lenResult = 0
                for i in range(0, len(items), chunkSize):
                    result = client.addItems(inventoryName, items[i : i + chunkSize])
                    logger.info(f"{len(result)+lenResult} items of {len(items)} imported.")
                    sleep(pause)
            else:
                result = client.addItems(inventoryName, items)
                logger.info(f"{len(result)} items of file '{filePath}' imported.")

        return

    def importTimeSeriesItems(
        self, 
        filePath:str,  
        inventoryName:str, 
        delimiter:str=',',
        chunkSize:int = 500, 
        pause:int = 1
        ) -> None:
        """
        Imports time series inventory items from a CSV file. The CSV file only needs a header of
        property definitions. Each line below the header represents a new time series.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        inventoryName : str
            The field name of the inventory.
        delimiter : str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.
        chunkSize : int = 500
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 50 items per chunk.
        pause : int = 1
            Between each chunk upload a pause is inserted in order to avoid overloading.
                 
        """

        # if timeZone == None:
        #     timeZone = core._getDefaults()['timeZone']
               
        ## READ FILE
        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return
        for file in files:
            content = FileUtils._readCsvFile(file, delimiter)

            ## PREPARE IMPORT
            tsProperties = ['unit', 'timeUnit', 'factor']
            for header in tsProperties:
                if not header in content[0]:
                    Utils._error(self, f"Header {header} not found. Import aborted.")
                    return 
            
            properties = client.inventoryProperties(inventoryName)
            logger.debug(f'Property names: {list(properties["name"])}')

            diff = FileUtils._comparePropertiesTimeSeries(properties, content[0])
            if len(diff) > 0:
                Utils._error(self, f"Unknown properties: {list(diff)}")
                return 

            dataType, isArray, nullable = FileUtils._analyzeProperties(inventoryName, properties)
            logger.debug(f'Data types: {dataType}')
            logger.debug(f'Array properties: {isArray}')
            logger.debug(f'Nullable properties: {nullable}')
            logger.info(f"File '{filePath}' read and properties analyzed")

            timeSeriesItems = FileUtils._createTimeSeriesItems(content, dataType, isArray, nullable)
            logger.debug(f'Time series items: {timeSeriesItems}' )


            # ## IMPORT
            if len(timeSeriesItems) > chunkSize:
                lenResult = 0
                for i in range(0, len(timeSeriesItems), chunkSize):
                    result = client.TimeSeries.addTimeSeriesItems(inventoryName, timeSeriesItems[i : i + chunkSize])
                    logger.info(f"{len(result)+lenResult} items of {len(timeSeriesItems)} imported. Waiting {pause} second(s) before continuing...")
                    sleep(pause)
            else:
                result = client.TimeSeries.addTimeSeriesItems(inventoryName, timeSeriesItems)
                logger.info(f"{len(result)} items of {len(timeSeriesItems)} imported.") 
        return

    def importTimeSeriesData(
        self, 
        filePath:str, 
        inventoryName:str, 
        importKeyProperty:str=None, 
        delimiter:str=',', 
        timeZone:str=None, 
        dateTimeFormat:str=None, 
        fromTimepoint:str=None, 
        toTimepoint:str=None, 
        timeDelta:timedelta=None, 
        chunkSize:int=20000
        ) -> None: 
        """
        Imports time series data from a specific CSV file or a folder with multiple
        CSV files. The first column is the timestamp index, whereas the first row
        consists of inventory item ids or an import key from the time series property
        definitions. Time series values are spanned as matrix between first column and
        first row. 

        Parameters:
        -----------
        filePath: str
            A path to a folder or a specific CSV file
        inventoryName: str
            The field name of the inventory, if not provided in the import file. 
            In the import file the inventory nameis located at position (0,0).
        importKeyProperty: str = None
            By default the inventory item id is used to find map columns with 
            values with time series. As an alternative, the content of a specific
            property can be used as header which will be mapped with the time series.
            This property should be unique.
        delimiter: str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone.
        dateTimeFormat: str = None
            Several date-time formats are supported, however, a custom format according to
            datetime.strftime() and strptime() format codes can be passed to convert the
            timestamp.
        fromTimepoint: str = None
            Specify a timestamp in isoformat from which data should be imported.
        toTimepoint: str = None
            Specify a timestamp in isoformat until which data should be imported.
        timeDelta: datetime.timedelta = None
            Define a time delta to add or substract to the original timestamp.
        chunkSize: int = 20000
            Determines the number of time series datapoints which are written per chunk. Using chunks
            can be necessary to avoid overloading.

        Example:
        --------
        >>> client.FileImport.importTimeSeriesData(
            filePath=file,
            inventoryName='meterData'
            importKeyProperty='name'
            delimiter=';', 
            timeZone='CET', 
            dateTimeFormat='%Y-%b-%d %H:%M:%S'
            fromTimePoint='2023-01-01'
            toTimepoint='2023-03-05'
            timeDelta=-timedelta(hours=1))
            chunkSize=20000
        """

        ## TIMEZONE
        timeZone = FileUtils._timeZone(timeZone)

        ## CHECK FILE PATH
        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return

        output = {}
        
        for file in files:

            fileName = file.name
        
            output.setdefault(fileName, 
                {'Time series': 0,
                'Time series errors': 0,
                'Values written': 0,
                'Value errors': 0,
                'Errors': None})

            ## READ FILE
            content = FileUtils._readCsvFile(file, delimiter)

            tsLength = len(content) - 1

            # CONVERT DATETIME COLUMN
            if dateTimeFormat == None:
                dateTimeFormat = FileUtils._dateFormat(content[1][0])

            for i, row in enumerate(content):
                try:
                    if content[i][0] == '': continue
                    content[i][0] = FileUtils._convertTimestamp(content[i][0], timeZone, dateTimeFormat, timeDelta)
                except Exception as err: 
                    if i >= 1:
                        Utils._error(self, f"Timestamp {row[0]} could not be converted. {err}")
                        return 
                    pass

            ## GET ITEM ID FROM IMPORT KEY
            if importKeyProperty != None:
                try:
                    items = client.items(inventoryName, fields=['unit', 'resolution', 'sys_inventoryItemId', importKeyProperty])
                except Exception as err:
                    Utils._error(self, err)
                    return 
                names = content[0].copy()
                del names[0]
                items = items[items[importKeyProperty].isin(names)]
                idMapping = {}
                for item in items.iterrows():
                    idMapping.setdefault(item[1][importKeyProperty],item[1]['sys_inventoryItemId'])

                if len(idMapping) == 0:
                    Utils._error(self, err)
                    return 

                logger.debug(f"Id Mapping: {idMapping}")
            else:
                try:
                    items = client.items(inventoryName, fields=['unit', 'resolution', 'sys_inventoryItemId'])
                    logger.debug("Inventory read for default option (import with ivnentory item ids).")
                except Exception as err:
                    Utils._error(self, err)
                    return 

            # Get the Inventory Id
            try:                      
                inv = client.inventories(where=f'name eq "{inventoryName}"')
                inventoryId = inv.loc[0, 'inventoryId']
                logger.debug(f"Found inventoryId {inventoryId} for inventory {inventoryName}.")
            except:
                Utils._error(self, err)
                return 

            ## VERIFY IDS, CREATE DATA_DICTS, IMPORT
            errorDict = {}
            inv = None
            tsItems = [] # only used in bulk operation

            for column in range(1, len(content[0])):
                if importKeyProperty != None:
                    try:
                        inventoryItemId = idMapping[content[0][column]]
                    except:
                        logger.warning(f"ImportKeyProperty '{content[0][column]}' not found.")
                        output[fileName]['Time series errors'] += 1
                        errorDict.setdefault(content[0][column], 'Not found')
                        continue
                else:
                    try:
                        inventoryItemId = content[0][column]
                    except:
                        logger.warning(f"Inventory item id {inventoryItemId} not found.")
                        errorDict.setdefault(content[0][column], 'Not found')
                        continue                

                try:
                    properties = items[items['sys_inventoryItemId'] == inventoryItemId]
                    if properties.empty:
                        logger.warning(f"Inventory item id {inventoryItemId} not found.")
                        output[fileName]['Time series errors'] += 1
                        errorDict.setdefault(content[0][column], 'Not found')
                        continue
                except:
                    logger.warning(f"Inventory item id {inventoryItemId} not found.")
                    continue

                properties = properties.to_dict('records')[0]
                timeUnit = properties['resolution'].split(' ')[-1]
                factor = properties['resolution'].split(' ')[0]

                tsDict = {
                        'sys_inventoryId': inventoryId,
                        'sys_inventoryItemId': None,
                        'data': {
                            'resolution': {
                                'timeUnit': None,
                                'factor': None
                            },
                            'unit': None,
                            'dataPoints': None
                        }
                    }

                valueList = []
                for i, row in enumerate(content):
                    if i >= 1:     
               
                        try:
                            if row[0] == '': continue
                            if fromTimepoint:
                                if row[0] < fromTimepoint: continue
                            if toTimepoint:
                                if row[0] > toTimepoint: continue
                            float(row[column])              
                            valueList.append({'timestamp': row[0], 'value': row[column]})
                        except:
                            errorDict.setdefault(content[0][column], {})
                            errorDict[content[0][column]].setdefault(row[0], row[column])
                            output[fileName]['Value errors'] += 1     

                logger.debug(f"Value list first 5 items: {valueList[:5]}")

                tsDict['sys_inventoryItemId'] = inventoryItemId
                tsDict['data']['unit'] = properties['unit']
                tsDict['data']['resolution']['timeUnit'] = timeUnit
                tsDict['data']['resolution']['factor'] = factor  
                tsDict['data']['dataPoints'] = valueList

                tsItems.append(tsDict)
                output[fileName]['Values written'] += len(valueList)

            logger.debug("Time series collection created")
            output[fileName]['Time series'] = len(tsItems)

            tsItemsEmpty = copy.deepcopy(tsItems)
            for item in tsItemsEmpty:
                del item['data']['dataPoints']
            
            for i in range(0, tsLength, chunkSize):
                tsChunk = copy.deepcopy(tsItemsEmpty)
                for j, ts in enumerate(tsChunk):
                    tsChunk[j]['data'].setdefault('dataPoints', tsItems[j]['data']['dataPoints'][i : i + chunkSize])
                    
                client.TimeSeries.setTimeSeriesDataCollection(timeSeriesData=tsChunk)    
                logger.info(f"({int(i/chunkSize+1)}/{tsLength//chunkSize+1}) chunks imported.")            

        logger.info(f"Import finished")

        return 

    def importGroupInstanceItems(
            self, 
            filePath:str, 
            groupInventoryName:str,
            instanceInventoryName, 
            importKeyProperty, 
            delimiter:str=None, 
            chunkSize:int = 500,
            pause:int = 1
            ) -> None:
        """
        Imports  group instance items from a CSV file. The CSV file only needs a header
        of property definitions. The first column is reserved for the groupInventoryItemId.
        Each line below the header represents a new item.

        Parameters:
        -----------
        filePath: str
            The file path of the csv file that should be imported.
        groupInventoryName: str
            The field name of the group inventory.
        instanceInventoryName: str
            The field name of the time series instance inventory belonging to the group.
        importKeyProperty: str
            Provide a property of the parent group time series that is unique.
            (The first column 'groupName' used in the CSV file.)
        delimiter: str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.
        chunkSize: int = 500
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading.
        pause: int = 1
            Between each chunk upload a pause is inserted in order to avoid overloading.

        """
              
        ## READ FILE
        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return

        for file in files:
            content = FileUtils._readCsvFile(file, delimiter)

            ## PREPARE IMPORT
            properties = client.inventoryProperties(instanceInventoryName)
            logger.debug(f'Property names: {list(properties["name"])}')

            diff = FileUtils._comparePropertiesBasic(properties, content[0][1:-1])
            if len(diff) > 0:
                Utils._error(self, f"Unknown properties: {list(diff)}")
                return 

            if importKeyProperty != None:
                try:
                    items = client.items(groupInventoryName, fields=['sys_inventoryItemId', importKeyProperty])
                except Exception as err:
                    Utils._error(self, err)
                    return
            
                names = [row[0] for row in content]
                del names[0]

                items = items[items[importKeyProperty].isin(names)]

                idMapping = {}
                for item in items.iterrows():
                    idMapping.setdefault(item[1][importKeyProperty],item[1]['sys_inventoryItemId'])
                logger.debug(f"Id mapping: {idMapping}")
                if len(idMapping) == 0:
                    Utils._error(self, f"No item ids for importKeyProperty '{importKeyProperty}' found.")
                    return 

            dataType, isArray, nullable = FileUtils._analyzeProperties(instanceInventoryName, properties)
            logger.debug(f'Data types: {dataType}')
            logger.debug(f'Array properties: {isArray}')
            logger.debug(f'Nullable properties: {nullable}')
            logger.info(f"File '{filePath}' read and properties analyzed")

            items = FileUtils._createInstanceItems(content, dataType, isArray, nullable, idMapping)
            logger.debug(f'Instance items: {items}' )

            # ## IMPORT
            if len(items) > chunkSize:
                lenResult = 0
                for i in range(0, len(items), chunkSize):
                    result = client.TimeSeries.addTimeSeriesItemsToGroups(groupInventoryName, items[i : i + chunkSize])
                    logger.info(f"{len(result)+lenResult} items of {len(items)} imported.")
                    sleep(pause)
            else:
                result = client.TimeSeries.addTimeSeriesItemsToGroups(groupInventoryName, items)
                logger.info(f"{len(items)} items of file '{filePath}' imported.")

        return

    def importGroupInstanceItemsWithData(
            self, 
            filePath:str, 
            groupInventoryName:str,
            instanceInventoryName:str, 
            groupKeyProperty:str=None, 
            instanceKeyProperties:list=None,
            delimiter:str=',', 
            timeZone:str=None, 
            dateTimeFormat:str=None, 
            fromTimepoint:str=None, 
            toTimepoint:str=None, 
            timeDelta:timedelta=None, 
            chunkSize=20000, 
            pause:int = 1
            ) -> None:
        """
        Imports  group instance items from a CSV file. The CSV file only needs a header
        of property definitions. The first column is reserved for the groupInventoryItemId.
        Each line below the header represents a new item.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        groupInventoryName : str
            The field name of the group inventory.
        instanceInventoryName : str
            The field name of the time series instance inventory belonging to the group.
        groupKeyProperty : str
            Is a property of the group item to identify it, which have to be placed 
            in the first line of the file. If None, the group item id is expected. 
        instanceKeyProperties:
            One or two key properties of the instance item to identiy it uniquely. The order must be
            the same as in the import file.
        delimiter : str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone.
        dateTimeFormat: str = None
            Several date-time formats are supported, however, a custom format according to
            datetime.strftime() and strptime() format codes can be passed to convert the
            timestamp.
        fromTimepoint : str = None
            Specify a timestamp in isoformat from which data should be imported.
        toTimepoint : str = None
            Specify a timestamp in isoformat until which data should be imported.
        timeDelta: datetime.timedelta = None
            Define a time delta to add or substract to the original timestamp.
        chunkSize: int = 20000
            Determines the number of time series datapoints which are written per chunk. Using chunks
            can be necessary to avoid overloading.
        pause: int = 1
            Between each chunk upload a pause is inserted in order to avoid overloading.
        """

        ## TIMEZONE
        timeZone = FileUtils._timeZone(timeZone)

        ## CHECK FILE PATH
        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return
    
        output = {}
        
        for file in files:

            fileName = file.name
        
            output.setdefault(fileName, 
                {'Time series instances': 0,
                'Time series instance errors': 0,
                'Values written': 0,
                'Value errors': 0,
                'Errors': None})

            ## READ FILE
            content = FileUtils._readCsvFile(file, delimiter)

            ## PREPARE IMPORT: Get Instance properties
            instanceProperties = []
            for i, row in enumerate(content):
                if i == 0: continue
                if row[0] in ['unit', 'timeUnit', 'factor']: 
                    pass
                elif row[0] == 'data':
                    dataBegin = i + 1
                    break
                elif row[0] == 'values':
                    dataBegin = i + 1
                    break
                else:
                    instanceProperties.append(row[0])
                if i > 100: 
                    Utils._error(self, f"No keyword 'data' or 'values' found")
                    return

            tsLength = len(content) - dataBegin

            # CONVERT DATETIME COLUMN
            if dateTimeFormat == None:
                dateTimeFormat = FileUtils._dateFormat(content[dataBegin][0])

            for i, row in enumerate(content[dataBegin:]):
                try:
                    if row[0] == '': continue
                    content[dataBegin+i][0] = FileUtils._convertTimestamp(content[dataBegin+i][0], timeZone, dateTimeFormat, timeDelta)
                except Exception as err: 
                    if i >= 1:
                        Utils._error(self, f"Timestamp {row[0]} could not be converted. {err}")
                        return 
                    pass

            ## PREPARE IMPORT: Compare Instance properties
            properties = client.inventoryProperties(instanceInventoryName)
            logger.debug(f'Property names: {list(properties["name"])}')

            diff = FileUtils._comparePropertiesBasic(properties, instanceProperties)
            if len(diff) > 0:
                Utils._error(self, f"Unknown properties: {list(diff)}")
                return 

            ## PREPARE IMPORT: Get Mapping of Import Key
            if groupKeyProperty != None:
                try:
                    items = client.items(groupInventoryName, fields=['sys_inventoryItemId', groupKeyProperty])
                except Exception as err:
                    Utils._error(self, err)
                    return 
            
                names = [column for column in content[0]]
                del names[0]

                items = items[items[groupKeyProperty].isin(names)]

                idMapping = {}
                for item in items.iterrows():
                    idMapping.setdefault(item[1][groupKeyProperty],item[1]['sys_inventoryItemId'])
                logger.debug(f"Id mapping: {idMapping}")
                if len(idMapping) == 0:
                    Utils._error(self, f"No item ids for groupKeyProperty '{groupKeyProperty}' found.")
                    return 

            ## PREPARE IMPORT: Check dataType, Array and nullable properties
            dataType, isArray, nullable = FileUtils._analyzeProperties(instanceInventoryName, properties)
            logger.info(f"File '{filePath}' read and properties analyzed")

            itemContent = FileUtils._createInstanceItemContent(content[:dataBegin])
            tsItemContent = content[:dataBegin]
            items = FileUtils._createInstanceItems(itemContent, dataType, isArray, nullable, idMapping, transpose=True)
            tsItems = FileUtils._createInstanceItems(tsItemContent, dataType, isArray, nullable, idMapping, transpose=True)

            logger.debug(f'Instance items: {items}' )

            # Find position of instance key properties
            if instanceKeyProperties == None:
                Utils._error(self, f"No instanceKeyProperties provided.")
                return 

            instancePropPos = []
            for i, row in enumerate(content[:dataBegin]):
                for property in instanceKeyProperties:
                    if property == row[0]:
                        instancePropPos.append(i)

            try:                      
                inv = client.inventories(where=f'name eq "{instanceInventoryName}"')
                inventoryId = inv.loc[0, 'inventoryId']
                logger.debug(f"Found inventoryId {inventoryId} for inventory {instanceInventoryName}.")
            except:
                Utils._error(self, f"No inventory with name '{instanceInventoryName}'.")
                return 

            ## IMPORT: create group instance items
            errorDict = {}

            for i in range(0, len(items)):
                try:
                    client.TimeSeries.addTimeSeriesItemsToGroups(groupInventoryName, [items[i]])
                    sleep(pause)
                except:
                    logger.warning(f"Instance item in column {i+1} could not be created")
                    errorDict.setdefault(i+1, "Instance could not be created")
                try:
                    if len(instanceKeyProperties) == 1:
                        x0 = content[instancePropPos[0]][i+1]
                        instanceTs = client.items(instanceInventoryName, 
                            where=f'{instanceKeyProperties[0]} eq "{x0}"')
                    if len(instanceKeyProperties) >= 2:
                        x0 = content[instancePropPos[0]][i+1]
                        x1 = content[instancePropPos[1]][i+1]
                        instanceTs = client.items(instanceInventoryName, 
                            where=f'{instanceKeyProperties[0]} eq "{x0}" and {instanceKeyProperties[1]} eq "{x1}"')
                    inventoryItemId = instanceTs.loc[0, 'sys_inventoryItemId']
                except:
                    logger.warning(f"Instance item in column {i+1} not found")
                    output[fileName]['Time series instance errors'] += 1
                    continue
                sleep(pause)

                tsDict = {
                    'sys_inventoryId': inventoryId,
                    'sys_inventoryItemId': inventoryItemId ,
                    'data': {
                        'resolution': {
                            'timeUnit': tsItems[i]['timeUnit'],
                            'factor': tsItems[i]['factor']
                        },
                        'unit': tsItems[i]['unit'],
                        'dataPoints': None
                    }
                }

                valueList = []
                for row in content[dataBegin:]:
                    try:
                        if fromTimepoint:
                            if row[0] < fromTimepoint: continue
                        if toTimepoint:
                            if row[0] > toTimepoint: continue
                        float(row[i+1])   
                        valueList.append({'timestamp': row[0], 'value': row[i+1]})
                    except:
                        pass
                        errorDict[i+1] = {}
                        errorDict[i+1].setdefault(row[0], row[i+1])
                        output[fileName]['Value errors'] += 1
               
                for k in range(0, tsLength, chunkSize):     
                    tsDict['data']['dataPoints'] = valueList[k : k + chunkSize]
                    try:
                        client.TimeSeries.setTimeSeriesDataCollection(timeSeriesData=[tsDict])
                    except Exception as err:
                        logger.error(f"Time series values could not be written. Cause: {err}")
                        errorDict[i+1] = err
                        break

                output[fileName]['Values written'] += len(valueList)
            if len(errorDict) > 0:
                output[fileName]['Errors'] = errorDict
                        
        return output

    def importReferences(
        self, 
        filePath:str, 
        delimiter:str=','
        ) -> dict:
        """
        Connects reference fields of existing items of two inventories. 
        Connect array-type [n:1] and non array references [1:1].
        Use FileImport.ImportReferences() to generate a csv template.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str = ','
            The CSV delimiter. Choose ',', ';', or 'tab'.

        Example:
        --------
        >>> filePath = r'C:\temp\importReferences.csv'
        >>> client.FileImport.importReferences(filePath, delimiter=';')
        """

        def _readInventory(
                inventoryName:str, 
                property:str,
                items:list) -> pd.DataFrame:

            filterList = '['
            for item in items:
                filterList += f'"{item}",' 
            filterList += ']' 
            
            df = client.items(inventoryName, fields=[property,'sys_inventoryItemId'], 
                where=f'{property} in {filterList}')
            df.set_index(property, inplace=True)
            logger.debug(f"Items to reference (first 5):\n {df.iloc[:5]}")
            return df

        def _mapItems(
                content:list, 
                refItems:pd.DataFrame, 
                array:bool=True) -> dict:

            data = {}
            for i, row in enumerate(content):
                if i <= 1: continue
                if row[0] == '':
                    msg = f"No value in line {i}"
                    logger.warning(msg)
                    errors.setdefault(f'Row {i}', 'No value')
                    continue
                try:
                    if array == True:
                        data.setdefault(row[0], [])
                        data[row[0]].append(refItems['sys_inventoryItemId'][row[1]])
                    else:
                        data.setdefault(row[0], refItems['sys_inventoryItemId'][row[1]])
                except KeyError as err:
                    msg = f"Row {i}: unknown item {row[0]}"
                    logger.warning(msg)
                    errors.setdefault(f'Row {i}', f'unknown reference item {row[1]}')
                    continue
                except Exception as err:
                    msg = f"Row {i}: unknown error: {row[1]}"
                    logger.warning(msg)
                    errors.setdefault(f'Row {i}', f'unknown error: {row[1]}')
                    continue
            return data

        files = FileUtils._checkFilePath(filePath, self.raiseException)
        if files == None: return

        inventories = client.inventories(fields=['name', 'inventoryId'])

        output = {}
        
        for file in files:

            fileName = file.name
            errors = {}

            output.setdefault(fileName, 
                {'Items updated': 0,
                'Errors': None})
            content = FileUtils._readCsvFile(file, delimiter)
            
            # Read reference field
            try:
                inventory = content[0][0].split('.')[0]
                referenceField = content[0][0].split('.')[1]
            except:
                msg = f"'{content[0][0]}' is not a valid 'inventory.property' format."
                logger.error(f"{fileName}: {msg}")
                output[fileName]['Errors'] = msg
                continue

            # Arrange data
            fields = [column for column in content[1]]
            logger.debug(f"Fields: {fields}")
            invFields = {}
            inventoryList = []
            for item in fields:
                try:
                    splitItem = item.split('.')
                    invFields.setdefault(splitItem[0], splitItem[1])
                    inventoryList.append(splitItem[0])
                except:
                    msg = f"'{item}' is not a valid 'inventory.property' format."
                    logger.error(f"{fileName}: {msg}")
                    output[fileName]['Errors'] = msg
                    continue

            # Check if inventory is in inventories
            inventoryFieldsCorrect = True
            for key in invFields.keys():
                if key not in list(inventories['name']):
                    inventoryFieldsCorrect = False
                    msg = f"'{key}' is not a known inventory"
                    logger.error(f"{fileName}: {msg}")
                    output[fileName]['Errors'] = msg
                    continue                 
            if inventoryFieldsCorrect == False: return
            logger.debug(f"Inventories: {inventoryList}")

            # Check type of first field
            properties = client.inventoryProperties(inventory)
            properties.set_index('name', inplace=True)
            if properties['type'][referenceField] != 'reference':
                msg = f"'{property}' is not a reference field"
                logger.error(f"{fileName}: {msg}")
                output[fileName]['Errors'] = msg
                continue       

            if properties['isArray'][referenceField] == True:

                referenceValues = [row[1] for i, row in enumerate(content) if i > 1]
                logger.debug(f"Reference Values (first 5): {referenceValues[:5]}")

                # Read inventory items to reference    
                dfReferenceItems = _readInventory(inventoryList[1], invFields[inventoryList[1]], referenceValues)

                # Create Data Dict
                mappedItems = _mapItems(content, dfReferenceItems, array=True)
                   
                # Read inventory items to update
                dfUpdateItems = _readInventory(inventory, invFields[inventory], mappedItems.keys())

                # Create connections
                itemsUpdated = 0
                itemsReferred = 0
                for key, value in mappedItems.items():
                    try:
                        client.updateArrayProperty(inventory, dfUpdateItems['sys_inventoryItemId'][key], referenceField, 'insert', value)
                        if len(value) != 0:
                            itemsUpdated += 1
                        itemsReferred += len(value)
                    except Exception as err:
                        msg = f"Item: {dfUpdateItems['sys_inventoryItemId'][key]}, Value: {value}, Problem: {err}"
                        logger.warning(err)
                        errors.setdefault({dfUpdateItems['sys_inventoryItemId'][key]}, [f'Value: {value}', f'Problem: {err}'])

                output[fileName]['Items updated'] = itemsUpdated
                output[fileName].setdefault('Items referred', itemsReferred)
                if len(errors) != 0:
                    output[fileName]['Errors'] = errors

                return output

            else: #If it is not an array (1:1 reference)
                referenceValues = [row[1] for i, row in enumerate(content) if i > 1]
                logger.debug(f"Reference Values (first 5): {referenceValues[:5]}")

                dfReferenceItems = _readInventory(inventoryList[1], invFields[inventoryList[1]], referenceValues)

                # Create Data Dict
                mappedItems = _mapItems(content, dfReferenceItems, array=False)
                    
                # Read inventory items to update
                dfUpdateItems = _readInventory(inventory, invFields[inventory], mappedItems.keys())

                # Create connections
                updateItems = []
                for key, value in mappedItems.items():
                    item = {
                        'sys_inventoryItemId': dfUpdateItems['sys_inventoryItemId'][key],
                        referenceField: value
                    }
                    updateItems.append(item)
                client.updateItems(inventory, updateItems)

                output[fileName]['Items updated'] = len(updateItems)
                if len(errors) != 0:
                    output[fileName]['Errors'] = errors

                return output

    def templateImportReferences(
        self, 
        filePath:str=None
        ) -> pd.DataFrame:
        """Provides a template to import item references."""
        content = [
            ['updateInventory.propertyToBeUpdated', '', '// Enter inventory and property to be updated, like "marketData.qualityCriteria"'],
            ['updateInventory.uniqueProperty', 'referenceInventory.uniquePropertyOfReference', '// Enter inventory name to be updated and a unique property like "marketData.name" and a referring inventory with another unique property like "qualityCriteria.name"'],
            ['Swissgrid AE CH long', 'Swissgrid AE CH long', '// Example data, repeat entries and use same item in first column to import array items'],
            ['Swissgrid AE CH short', 'Swissgrid AE CH short','// Example data, repeat entries and use same item in first column to import array items']
        ]
        header = ['column 1', 'column 2', 'Remarks']

        df = pd.DataFrame(content, columns=header)
        if filePath != None:
            df.to_csv(filePath, index=False, header=False)
        return df
       

            