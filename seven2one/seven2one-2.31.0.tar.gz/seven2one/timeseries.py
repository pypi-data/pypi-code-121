from codecs import ignore_errors
import pandas as pd
import pytz
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger
from numpy import nan

from seven2one.utils.ut_time import TimeUtils

from .utils.ut import Utils
from .utils.ut_timeseries import UtilsTimeSeries
from time import time
import sys

class TimeSeries():

    def __init__(
            self, 
            accessToken:str, 
            endpoint:str, 
            client:object
        ) -> None:

        global core
        core = client
            
        header = {
            'authorization': 'Bearer ' + accessToken
        }
        
        transport =  RequestsHTTPTransport(url=endpoint, headers=header, verify=True, proxies=core.proxies)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

        self.raiseException = core.raiseException
        self.defaults = core.defaults
        self.structure = core.structure
        self.scheme = core.scheme
        return

    def addTimeSeriesItems(
            self, 
            inventoryName:str, 
            timeSeriesItems:list
            ) -> list:
        """
        Adds new time series and time series group items from a list of 
        dictionaires and returns a list of the created inventoryItemIds.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series item and the properties
            of the time series feature (unit, timeUnit and factor)

        Example:
        >>> timeSeriesItems = [
                {
                'meterId': 'XYZ123',
                'orderNr': 300,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:56Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh'
                },
                {
                'meterId': 'XYZ123',
                'orderNr': 301,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:55Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh',
                },
            ]
        >>> client.TimeSeries.addTimeSeriesItems('meterData', timeSeriesItems)
        """
        
        properties = Utils._tsPropertiesToString(timeSeriesItems)
        if properties == None: return

        key = f'create{inventoryName}'
        graphQLString = f'''mutation addTimeSeriesItems {{
            {key} (input: 
                {properties}
            )
            {{
                inventoryItems {{
                    sys_inventoryItemId
                }}
                {Utils.errors}
            }}
        }} 
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)

        ids = result[key]['inventoryItems']
        idList = [item['sys_inventoryItemId'] for item in ids]
        logger.info(f"Created {len(idList)} time series items.")

        return idList

    def addTimeSeriesItemsToGroups(
            self, 
            inventoryName:str, 
            timeSeriesItems:list
            ):
        """
        Adds new time series items to existing time series groups.
        
        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series items together 
            with the sys_inventoryItemId of the related group time series.

        Example:
        --------
        >>> items = [
                {
                    'issueDate':'2020-11-01T00:00+0200',
                    'name': 'forecast_wind_pro_de',
                    'sys_groupInventoryItemId': 'Sdin6tNl8S'
                }
            ]
        >>> client.TimeSeries.addTimeSeriesItemsToGroups('GroupInventory', instanceItems)
        """

        properties = Utils._propertiesToString(timeSeriesItems)
        if properties == None: return

        key = f'addTimeSeriesTo{inventoryName}'

        graphQLString = f'''mutation addTimeSeriesItemstoGroup {{
           {key} (input: 
                {properties}
            )
            {{
                inventoryItems {{
                    sys_inventoryItemId
                }}
                {Utils.errors}
            }}
        }}
        ''' 
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)

        try:
            ids = result[key]['inventoryItems']
            idList = [item['sys_inventoryItemId'] for item in ids]
            logger.info(f"Group instance(s) created.")
            return idList
        except:
            pass
            return   

    def setTimeSeriesData(
            self, 
            inventoryName:str, 
            inventoryItemId:str, 
            timeUnit:str, factor:int, 
            unit:str, 
            dataPoints:dict, 
            chunkSize:int=10000
            ) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryItemId of the time series is used. As 
        timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or DateTimeOffset 
        (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ---------
        inventoryName: str
            The name of the inventory to which the time series belong.
        inventoryItemId: str
            The inventoryItemId to which data is to be written.
        timeUnit: str
            Is the time unit of the time series item
        factor: int
            Is the factor of the time unit
        unit: str
            The unit of the values to be written. 
        dataPoints: dict
            Provide a dictionary with timestamps as keys.
        chunkSize:int = 10000
            Specifies the chunk size of time series values that are written in 
            a single transaction
        
        Example: 
        --------
        >>> inventory = 'meterData'
            inventoryItemId = 'TzdG1Gj2GW'
            tsData = {
                '2020-01-01T00:01:00Z': 99.91,
                '2020-01-01T00:02:00Z': 95.93,
            }
            
        >>> client.TimeSeries.setTimeSeriesData(inventory, inventoryItemId,
                'MINUTE', 1, 'W', tsData)
        """

        inventoryId = core.structure[inventoryName]['inventoryId']
        logger.debug(f"Found inventoryId {inventoryId} for {inventoryName}.")

        key = f'setTimeSeriesData'

        def _setTimeSeriesData(_dataPoints):
           
            graphQLString = f'''
                mutation setTimeSeriesData {{
                setTimeSeriesData(input: {{
                    sys_inventoryId: "{inventoryId}"
                    sys_inventoryItemId: "{inventoryItemId}",
                    data: {{
                        resolution: {{
                            timeUnit: {timeUnit}
                            factor: {factor}
                            }}
                        unit: "{unit}"
                        dataPoints: [
                            {_dataPoints}
                        ]
                    }}
                }})
                    {{
                        {Utils.errors}
                    }}
                }}
            '''
            result = Utils._executeGraphQL(self, graphQLString)
            return result

        if len(dataPoints) < chunkSize:
            _dataPoints = UtilsTimeSeries._dataPointsToString(dataPoints)
            result = _setTimeSeriesData(_dataPoints)
            
            if result[key]['errors']:
                Utils._listGraphQlErrors(result, key)
            else:
                logger.info(f"{len(dataPoints)} data points set for time series {inventoryItemId}.")
            if result == None: return
            return

        else:
            dataPointsCount = 0
            for i in range(0, len(dataPoints), chunkSize):
                sliceDataPoints = UtilsTimeSeries._sliceDataPoints(dataPoints.items(), i, i + chunkSize)
                _sliceDataPoints = UtilsTimeSeries._dataPointsToString(sliceDataPoints)
                result = _setTimeSeriesData(_sliceDataPoints)
                if result == None: continue
                if result[key]['errors']:
                    Utils._listGraphQlErrors(result, key)
                
                dataPointsCount += len(sliceDataPoints)

            logger.info(f"{dataPointsCount} data points set for time series {inventoryItemId}.")

        return

    def setTimeSeriesDataCollection(
            self, 
            timeSeriesData:list, 
            chunkSize:int=10000
            ) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryId and sys_inventoryItemId of the 
        time series is used. The dictionary represents the GraphQL format.
        As timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or 
        DateTimeOffset (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ----------
        data: list
            A list of dictionaries defining inventory, inventoryItemId, resolution, 
            unit and time series values. Is used to write time series values for
            many time series in one single transaction.
        chunkSize: int = 10000
            Determines the packageSize of time series values that are written in 
            a single transaction

        Example: 
        --------
        >>> tsItems = [
                {
                    'sys_inventoryId': 'A6RGwtDbbk', 
                    'sys_inventoryItemId': 'TzdG1Gj2GW', 
                    'data': 
                        {
                            'resolution': {'timeUnit': 'MINUTE', 'factor': 15}, 
                            'unit': 'kW', 
                            'dataPoints': [
                                {
                                    'timestamp': '2021-12-10T07:40:00Z', 
                                    'value': 879.2
                                }
                            ]
                        }
                    },
                ] 
        >>> client.TimeSeries.setTimeSeriesDataCollection(tsItems)
        """
        try:
            _timeSeriesData = UtilsTimeSeries._tsCollectionToString(timeSeriesData)
        except Exception as err:
            Utils._error(self, f"GraphQL string could not be created out of dictionary. Cause: {err}")
            return

        key = f'setTimeSeriesData'        
        graphQLString = f'''
            mutation {key} {{
            {key} (input: {_timeSeriesData})
                {{
                    {Utils.errors}
                }}
            }}
        '''

        result = Utils._executeGraphQL(self, graphQLString)
           
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.debug(f"time series data points set.")
        if result == None: return
        return
   
    def timeSeriesData(
            self, 
            inventoryName:str, 
            fromTimepoint:str, 
            toTimepoint:str, 
            fields:list=['sys_displayValue'], 
            where:str=None,
            unit:str=None,
            timeUnit:str=None, 
            factor:int=1, 
            aggregationRule:str='AVG', 
            timeZone:str=None, 
            includeMissing:bool=False,
            displayMode:str='pivot'
            ) -> pd.DataFrame:
        """
        Queries time series data and returns its values and properties 
        in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        includeMissing: bool = False
            If True, timestamps without values will be loaded and lead to a larger DataFrame. 
        displayMode: str = pivot
            pivot: pivot display of columns and timestamps, columns without values are dropped
            rows: row display

        Examples:
        ---------
        >>> timeSeriesData('meterData', '2020-10-01', '2020-10-01T:05:30:00Z')
        >>> timeSeriesData('meterData', fromTimepoint='2020-06-01', 
                toTimepoint='2020-06-15', fields=['meterId', 'phase'] 
                where='measure eq "voltage"')    
        """

        if timeZone == None:
            timeZone = self.defaults.timeZone 
        logger.debug(f"Timezone: {timeZone}")

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

        # where
        topLevelWhere, resolvedFilterDict = Utils._handleWhere(core, where, inventoryName)

        # fields
        deleteIdAfterwards = False
        if fields != None:
            propertyDict = Utils._properties(self.scheme, inventoryName, recursive=True, 
                sysProperties=self.defaults.includeSystemProperties)   
            if type(fields) != list:
                fields = [fields]
            if 'sys_inventoryItemId' not in fields:
                fields += ['sys_inventoryItemId']
                deleteIdAfterwards = True
            _fields = Utils._queryFields(fields, propertyDict['arrayTypeFields'], 50, 
                filter=resolvedFilterDict, recursive=True)
            if 'pageSize' in _fields:
                Utils._error(self, f"Array type fields are not supported in 'fields'-argument ({_fields})")
                return
        else:
            fields = ['sys_displayValue', 'sys_inventoryItemId']
            _fields = ''
            for field in fields:
                _fields += field + '\n'

        unit = Utils._argNone('unit', unit)

        if timeUnit != None:
            aggregation = f'''
                aggregation: {aggregationRule}
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        if includeMissing == True:
            allowedFlags = f'allowedFlags: [MISSING, VALID, NO_VALUE, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'
        else:
            allowedFlags= f'allowedFlags: [VALID, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'

        result = []
        count = 0
        countDp = 0
        lastId = ''
        pageSize = 1 # Initial page size
        maxTimePoints = 40000

        key = inventoryName
        while True:         
            start = time()
            graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: {pageSize}
                {topLevelWhere}
                {lastId}
                )
                {{
                    {_fields}
                    _dataPoints (input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {unit}                        
                        {aggregation}
                        {allowedFlags}
                        }})
                    {{
                        timestamp
                        value
                        flag
                    }}
                }}
            }}'''

            if count == 0:
                Utils._copyGraphQLString(graphQLString)

            _result = Utils._executeGraphQL(self, graphQLString)
           
            ## Automatic paging
            countDp = 0
            countTs = len(_result[key])
            if countTs == 0: break
            for i in _result[key]:
                if i['_dataPoints'] == None:
                    continue
                else:
                    countDp += len(i['_dataPoints'])
            end = round(time()-start, 2)
            logger.debug(f"Iteration: {count}, timeSeries: {countTs}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
            try:
                pageSize = maxTimePoints * pageSize // countDp
                if pageSize > 2000: pageSize = 2000
            except ZeroDivisionError:
                pageSize = 10**(count + 1)
                if pageSize > 2000: pageSize = 2000
            pageSize = 1 if pageSize == 0 else pageSize
  
            if _result[inventoryName]:
                result += _result[inventoryName]
                count += 1
            try:
                cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                lastId = f'lastId: "{cursor}"'
            except Exception as err:
                Utils._error(self, f"Problem with pagination: {err}")
                return
        
        if deleteIdAfterwards == True:
            fields.remove('sys_inventoryItemId')

        meta = []
        for i in result:
            for k, v in i.items():
                if v == None:
                    i[k] = {'code1':'NONE'}

        for field in fields:
            if field.count('.') == 1:
                compoundField = field.split('.')
                meta.append([compoundField[0], compoundField[1]])
            else:
                meta.append(field)

        try:
            df = pd.json_normalize(result, record_path = ['_dataPoints'],
                meta=meta)
        except KeyError:
            Utils._error(self, f"There is a problem with the provided fields. Probably one or more fields have no values. ")
            return

        if df.empty:
            logger.info('The query did not produce results.')
            return df

        df = UtilsTimeSeries._processDataFrame(core, result, df, fields, timeZone, displayMode, includeMissing)
        return df     

    def timeSeriesGroupData(
            self, 
            inventoryName:str, 
            fromTimepoint:str, 
            toTimepoint:str, 
            fields:list=['sys_displayValue'], 
            instanceFields:list=['sys_displayValue'], 
            instancePrefix:str='instance.', 
            where:str=None, 
            whereInstance:str=None,
            unit:str=None, 
            timeUnit:str=None, 
            factor:int=1, 
            aggregationRule:str='AVG', 
            timeZone:str=None, 
            includeMissing:bool=False,
            displayMode:str='pivot'
            ) -> pd.DataFrame:
        """
        Queries time series data from time series groups and returns its values and properties 
        for each time series instance in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        instanceFields: list|str = None
            Properties of the time series instance to be used as header. Uses the displayValue as default. 
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        unit: str = None
            Use a string to convert time series values into another unit.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
v

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instanceFields='issueDate',
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        if timeZone == None:
            timeZone = self.defaults.timeZone 
        logger.debug(f"Timezone: {timeZone}")        

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

        deleteIdAfterwards = False
        if fields != None:
            if type(fields) != list:
                fields = [fields]
            if 'sys_inventoryItemId' not in fields:
                fields += ['sys_inventoryItemId']
                deleteIdAfterwards = True
        else:
            fields = ['sys_displayValue', 'sys_inventoryItemId']
            deleteIdAfterwards = True

        _groupFields = ''
        for field in fields:
            _groupFields += field + '\n'

        if type(instanceFields) != list:
            instanceFields = [instanceFields]

        _instanceFields = ''
        for field in instanceFields:
            _instanceFields += field + '\n'

        # resolvedFilter = ''
        # if where != None: 
        #     resolvedFilter = Utils._resolveWhereString(self, where)
        topLevelWhere, _ = Utils._handleWhere(self, where, inventoryName)

        # resolvedInstanceFilter = ''
        # if whereInstance != None: 
        #     resolvedInstanceFilter = Utils._resolveWhereString(self, whereInstance)

        instanceWhere, _ = Utils._handleWhere(self, whereInstance, inventoryName)

        unit = Utils._argNone('unit', unit)

        if timeUnit != None:
            aggregation = f'''
                aggregation: {aggregationRule}
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        if includeMissing == True:
            allowedFlags = f'allowedFlags: [MISSING, VALID, NO_VALUE, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'
        else:
            allowedFlags= f'allowedFlags: [VALID, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'
           
        instanceDataPoints = f'''_dataPoints (input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {unit}
                        {aggregation}
                        {allowedFlags}
                        }})
                    {{
                        timestamp
                        value
                        flag
                    }}
        '''
        
        key = inventoryName

        result = []
        count = 0
        countDp = 0
        lastId = ''
        pageSize = 1 # Initial page size
        maxTimePoints = 40000

        while True:
            
            start = time()
            graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: {pageSize}
                {topLevelWhere}
                {lastId}
                )
                {{
                    {_groupFields}
                    timeSeriesInstances (
                    pageSize: 5000
                    {instanceWhere}
                    ) {{
                        {_instanceFields}
                        {instanceDataPoints}
                    }}
                }}
            }}'''

            if count == 0:
                Utils._copyGraphQLString(graphQLString)

            _result = Utils._executeGraphQL(self, graphQLString)
            
            # Automatic paging
            try:
                countDp = 0
                countInst = 0
                countGroupTs = len(_result[key])
                if countGroupTs == 0: break
                for i in _result[key]:
                    countInst += len(i['timeSeriesInstances'])
                    for j in i['timeSeriesInstances']:
                        countDp += len(j['_dataPoints'])
                end = round(time()-start, 2)
                logger.debug(f"Iteration: {count}, groupTimeSeries: {countGroupTs}, instances: {countInst}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
                try:
                    pageSize = maxTimePoints * pageSize // countDp
                    if pageSize > 10000: pageSize = 10000
                except ZeroDivisionError:
                    pageSize = 10**(count + 1)
                    if pageSize > 10000: pageSize = 10000
                pageSize = 1 if pageSize == 0 else pageSize
            except Exception as err:
                Utils._error(self, f"Problem with pagination: {err}")
                return

            if _result[inventoryName]:
                result += _result[inventoryName]
                count += 1
            try:
                cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                lastId = f'lastId: "{cursor}"'
            except Exception as err: 
                Utils._error(self, f"Problem with pagination: {err}")
                return

        if deleteIdAfterwards == True:
            fields.remove('sys_inventoryItemId')
        meta = []
        if type(fields) != list:
            meta.append(fields)
        else:
            for field in fields:
                meta.append(field)

        if type(instanceFields) != list:
            meta.append(['timeSeriesInstances', instanceFields])
        else:
            for field in instanceFields:
                meta.append(['timeSeriesInstance', field])

        try:
            df = pd.json_normalize(result, record_path = ['timeSeriesInstances', '_dataPoints'],
                meta=meta)
        except KeyError:
            Utils._error(self, f"There is a problem with the provided fields. Probably one or more fields have no values. ")
            return

        # rename columns
        reColumns = []
        for col in df.columns:
            if col.startswith('timeSeriesInstance'):
                col = col.replace('timeSeriesInstance.', instancePrefix)
            reColumns.append(col)
        df.columns = reColumns  

        pivotColumns = list(df.columns)[3:]

        df = UtilsTimeSeries._processDataFrame(core, result, df, pivotColumns, timeZone, displayMode, includeMissing)
        return df       
        
    def timeSeriesGroupDataReduced(
            self, 
            inventoryName:str, 
            fromTimepoint:str, 
            toTimepoint:str, 
            reduceFunction:str='LAST', 
            fields:list=['sys_displayValue'], 
            instanceFields:list=['sys_displayValue'], 
            where:str=None, 
            whereInstance:str=None, 
            unit:str=None,
            timeUnit:str=None, 
            factor:int=1,
            timeZone:str=None,
            includeMissing:bool=False,
            displayMode:str='pivot'
            ) -> pd.DataFrame:
        """
        Queries time series group data, reduces time series instances to a single array
        for each time series group and returns its values and properties 
        in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        reduceFunction: str = 'LAST'
            The function that determines how values from multiple time series instances should be reduced 
            to a single array.
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        instanceFields: list|str = None
            Properties of the time series instance to be used as header. Uses the displayValue as default. 
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        displayMode: str = pivot
            pivot: pivot display of columns and timestamps, columns without values are dropped
            rows: row display

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instanceFields='issueDate',
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        if timeZone == None:
            timeZone = self.defaults.timeZone 
        logger.debug(f"Timezone: {timeZone}")            

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

        if type(fields) != list:
            _groupFields = fields
            if 'sys_inventoryItemId' not in _groupFields:
                _groupFields += ['sys_inventoryItemId']
        else:
            _groupFields = ''
            for field in fields:
                _groupFields += field + '\n'
            _groupFields += 'sys_inventoryItemId\n'
        if type(instanceFields) != list:
            _instanceFields = instanceFields
        else:
            _instanceFields = ''
            for field in instanceFields:
                _instanceFields += field + '\n'

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(self, where)

        resolvedInstanceFilter = ''
        if whereInstance != None: 
            resolvedInstanceFilter = Utils._resolveWhereString(self, whereInstance)

        unit = Utils._argNone('unit', unit)

        if timeUnit != None:
            aggregation = f'''
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        if resolvedInstanceFilter == '':
            instanceInput = ''
        else:
            instanceInput = f'''({resolvedInstanceFilter})'''
           
        groupInput = f'''input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {unit}
                        {aggregation}
                        reducer: {reduceFunction}
                        showMissing: true
                        }}
        '''
        
        key = inventoryName
        graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: 500 
                {resolvedFilter}
                {groupInput}
                )
                {{
                    {_groupFields}
                    _dataPoints {{
                        timestamp
                        value
                        flag
                        }}
                    timeSeriesInstances {instanceInput} {{
                        sys_inventoryItemId
                    }}
                }}
            }}'''

        result = []
        count = 0
        countDp = 0
        lastId = ''
        pageSize = 1 # Initial page size
        maxTimePoints = 40000

        while True:
            
            start = time()
            graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: {pageSize}
                {resolvedFilter}
                {lastId}
                {groupInput}
                )
                {{
                    {_groupFields}
                    _dataPoints {{
                        timestamp
                        value
                        flag
                        }}
                    timeSeriesInstances {instanceInput} {{
                        sys_inventoryItemId
                    }}
                }}
            }}'''

            if count == 0:
                Utils._copyGraphQLString(graphQLString)

            _result = Utils._executeGraphQL(self, graphQLString)
            
            # Automatic paging
            countDp = 0
            countTs = len(_result[key])
            if countTs == 0: break
            for i in _result[key]:
                countDp += len(i['_dataPoints'])
            end = round(time()-start, 2)
            logger.debug(f"Iteration: {count}, groupTimeSeries: {countTs}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
            try:
                pageSize = maxTimePoints * pageSize // countDp
            except ZeroDivisionError:
                pageSize = 10**(count + 1)
                if count == 5: count = 1 # To prevent too large pageSize
            pageSize = 1 if pageSize == 0 else pageSize

            if _result[inventoryName]:
                result += _result[inventoryName]
                count += 1
            try:
                cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                lastId = f'lastId: "{cursor}"'
            except Exception as err: 
                Utils._error(self, f"Problem with pagination: {err}")
                return

        try:
            df = pd.json_normalize(result, ['_dataPoints'], fields)
        except KeyError:
            Utils._error(self, f"There is a problem with the provided fields. Probably one or more fields have no values. ")
            return
            
        pivotColumns = list(df.columns)[3:]

        df = UtilsTimeSeries._processDataFrame(core, result, df, pivotColumns, timeZone, displayMode, includeMissing)
        return df  
       
    def deleteTimeSeriesData(
            self,
            inventoryName:str, 
            fromTimepoint:str,
            toTimepoint:str, 
            inventoryItemIds:list=None, 
            where:str=None,
            timeZone:str=None,
            force:bool=False
            ) -> None:

        """
        Deletes time series data for a specified time range for multiple time series within an inventory.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be deleted. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The end of the time range up until time series values will be deleted.
        inventoryItemIds: list = None
            A list of inventoryItemIds that should be deleted.
        where: str = None
            Filter criteria to select items that should be deleted.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        force: bool = False
            Use True to ignore confirmation.
        """

        def createDataPoints(fromTimepoint, toTimepoint, timeUnit, factor) -> list:
            unitMapping = {
                'MILLISECOND':'ms',
                'SECOND':'S',
                'MINUTE':'min',
                'HOUR':'H',
                'DAY':'D',
                'WEEK':'W',
                'MONTH':'M',
                'YEAR':'YS'
            }
            freq = f'{factor}{unitMapping[timeUnit]}'
            index = pd.date_range(fromTimepoint, toTimepoint, freq=freq)
            logger.debug(f"DateTimeIndex: {index}")

            dataPoints = []
            for timepoint in index:
                data = {
                    'timestamp': timepoint,
                    'value': 0,
                    'flag':'MISSING'
                }
                dataPoints.append(data)
            
            return dataPoints

        if timeZone != None:
            tz = timeZone
        else:
            tz = self.defaults.timeZone          

        fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, tz)
        toTimepoint = TimeUtils._inputTimestamp(toTimepoint, tz)

        inventory = core.inventories(where=f'name eq "{inventoryName}"')
        sys_inventoryId = inventory.loc[0, 'inventoryId']

        if inventoryItemIds == None and where == None:
            Utils._error(self, f"No id list of items and no where-criteria were provided.")
            return

        if inventoryItemIds != None and where != None:
            logger.warning(f"List of items and where-criteria has been provided. Item list is used.")

        if where != None:
            df = core.items(inventoryName, fields=['sys_inventoryItemId','resolution'], where=where)
            if df.empty:
                logger.info(f"The where criteria '{where}' led to no results.")
                return
            
        if inventoryItemIds != None:
            idList = '['
            for item in inventoryItemIds:
                idList += f'"{item}", '
            idList += ']'
            df = core.items(inventoryName, fields=['sys_inventoryItemId','resolution'], where=f'sys_inventoryItemId in {idList}')

        if force == True:
            confirm = 'y'
        else:
            confirm = input(f"Press 'y' to delete values for {len(df)} time series items: ")
        if confirm != 'y':
            return

        for ts in df.iterrows():

            sys_inventoryItemId = ts[1]['sys_inventoryItemId']
            timeUnit = ts[1]['resolution'].split(' ')[1]
            factor = ts[1]['resolution'].split(' ')[0]
            dataPoints = createDataPoints(fromTimepoint, toTimepoint, timeUnit, factor)
            resolution = {'timeUnit':timeUnit, 'factor':factor}

            timeSeries = [{
                'sys_inventoryId': sys_inventoryId,
                'sys_inventoryItemId': sys_inventoryItemId,
                'data':
                    {
                    'resolution': resolution,
                    'dataPoints': dataPoints
                    }
                }]

            self.setTimeSeriesDataCollection(timeSeries)
        logger.info(f"Deleted values for {len(df)} time series items")

        return

    def timeSeriesItems(self, inventoryName:str, references:bool=False, fields:list=None, where:str=None, 
        orderBy:str=None, asc:bool=True, pageSize:int=5000, 
        arrayPropertiesToPage:list=None, arrayPageSize:int=50) -> pd.DataFrame:
        """
        Returns items of an inventory in a DataFrame.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        references: bool = False
            If True, items of referenced inventories will be added to the DataFrame. If
            the fields-parameter is used, this parameter is ignored.
        fields: list | str = None
            A list of all properties to be queried. If None, all properties will be queried.
            For referenced items use a '.' between inventory name and property.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'.
            Referenced items are not supported.
        orderBy: str = None
            Select a field to sort by.
        asc: bool = True
            Determines the sort order of items. If set to False, a descending order 
            is applied.
        pageSize: int = 5000
            The page size of items that is used to retrieve a large number of items.
        arrayPropertiesToPage:list = None
            Array (list) properties that should be paged. Real paging for array properties is 
            not yet supported. The properties listed here will just make use of of the arrayPageSize.
        arrayPageSize: int = 50
            The page size of list items that is used to page list items in an inventory item.

        Example:
        --------
        >>> items('meterData', references=True)
        """

        deleteId = False
        if fields != None:
            if type(fields) != list:
                fields = [fields]
            if 'sys_inventoryItemId' not in fields:
                deleteId = True
                fields += ['sys_inventoryItemId']
            _fields = Utils._queryFields(fields, recursive=True)
        else:
            properties = Utils._properties(self, inventoryName, recursive=True)
            properties = Utils._propertyList(properties, recursive=references)
            
            _fields = Utils._queryFields(properties, recursive=references)

        if len(_fields) == 0:
            Utils._error(self, f"Inventory '{inventoryName}' not found.")
            return

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(self, where)
        
        if orderBy != None:
            if asc != True:
                _orderBy = f'order: {{ {orderBy}: DESC }}'
            else:
                _orderBy = f'order: {{ {orderBy}: ASC }}'
        else: _orderBy = ''

        if arrayPropertiesToPage != None:
            listPagination = 'listPagination: [\n'
            for arrayProperty in arrayPropertiesToPage:
                listPagination += f'{{ from: 0, size: {arrayPageSize}, propertyPath: "{arrayProperty}" }}\n'
            listPagination += ']\n'
        else:
            listPagination = ''

        result = []
        count = 0
        lastId = ''

        while True:
            graphQLString= f''' query getItems {{
                    {inventoryName} (
                            pageSize: {pageSize} 
                            {listPagination}
                            {lastId}
                            {resolvedFilter}
                            {_orderBy}
                            ) {{
                        {_fields}
                    }}
                }}
                '''
            if count == 0:
                Utils._copyGraphQLString(graphQLString)

            _result = Utils._executeGraphQL(self, graphQLString)   
            
            if _result[inventoryName]:
                result += _result[inventoryName]
                count += 1
            try:
                cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                lastId = f'lastId: "{cursor}"'
            except: 
                break

        df = pd.json_normalize(result)
        
        if fields != None: #sorts dataframe according to given fields
            try: # for array field this does not work
                df = df[fields]
            except:
                pass 
        if deleteId: del df['sys_inventoryItemId']

        return df   

    def units(self) -> pd.DataFrame:
        """
        Returns a DataFrame of existing units.

        Examples:
        >>> units()
        """

        graphQLString = f'''query getUnits {{
        units
            {{
            name
            baseUnit
            factor
            isBaseUnit
            aggregation
            }}
        }}
        '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        return pd.json_normalize(result['units'])

    def createUnit(self, unit:str, baseUnit:str, factor:int, aggregation:str) -> None:
        """
        Creates a unit on basis of a base unit.

        Parameters:
        ----------
        unit : str
            The name of the unit to be created.
        baseUnit : str
            The name of an existing base unit.
        factor : float
            The factor related to the base unit.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG' This 
            kind of aggregation is used for integral units (kW -> kWh), which are not supported 
            yet.

        Example:
        >>> createUnit('kW', 'W', 1000, 'AVG')
        """

        graphQLString = f'''
            mutation createUnit {{
                createUnit(input: {{
                    name: "{unit}"
                    baseUnit: "{baseUnit}"
                    factor: {factor}
                    aggregation: {aggregation}}})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        key = f'createUnit'
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Unit {unit} created.")
        return

    def createBaseUnit(self, baseUnit:str, aggregation:str) -> None:
        """
        Creates a base unit.

        Parameters:
        ----------
        baseUnit : str
            The name of the base unit to be created.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG'.

        Example:
        >>> createBaseUnit('W', 'AVG')
        """

        graphQLString = f'''
            mutation createBaseUnit {{
                createBaseUnit(input: {{
                    name: "{baseUnit}"
                    aggregation: {aggregation}}})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        key = f'createBaseUnit'
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Unit {baseUnit} created.")

        return

    def updateUnit(self, unit:str, baseUnit:str=None, factor:int=None, aggregation:str=None) -> None:
        """
        Updates a unit.

        Parameters:
        ----------
        unit : str
            The name of the unit to be updated.
        baseUnit : str
            The name of an existing base unit.
        factor : float
            The factor related to the base unit.
        aggregation : str
            The enum value for default aggregation. Possible enums are 'SUM' and 'AVG' 

        Example:
        >>> updateUnit('kW', 'W', 1000, 'AVG')
        """

        baseUnit = Utils._argNone('baseUnit', baseUnit)
        factor = Utils._argNone('factor', factor)
        aggregation = Utils._argNone('aggregation', aggregation, enum=True)

        graphQLString = f'''
            mutation updateUnit {{
                updateUnit(input: {{
                    name: "{unit}"
                    {baseUnit}
                    {factor}
                    {aggregation}
                    }})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        key = f'updateUnit'
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Unit {unit} updated.")
        return


    def deleteUnit(self, unit:str, force=False) -> None:
        """
        Deletes a unit. Units can only be deleted if there are no Time Series that use this unit. 
        Base units can only be deleted, if no derived units exist.

        Parameters:
        ----------
        unit : str
            Name of the unit to be deleted.
        force : bool
            Optional, use True to ignore confirmation.
        
        Example:
        >>> deleteUnit('kW', force=True)
        """

        if force == False:
            confirm = input(f"Press 'y' to delete unit '{unit}'")
        else: confirm = 'y'

        graphQLString = f'''
        mutation deleteUnit{{
            deleteUnit (input: {{
                name: "{unit}"
                }})
                    {{
                    {Utils.errors}
                }}
            }}
            '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        logger.info(f"Unit {unit} deleted.")

        return

