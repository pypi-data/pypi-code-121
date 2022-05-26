from itertools import islice
import pandas as pd
from numpy import nan
import pytz
from loguru import logger
from .ut import Utils

class UtilsTimeSeries():

    def _tsCollectionToString(collection:list) -> str:
        """Converts a list of dicts with time series data into graphQL string"""

        tsData = '[\n'
        for item in collection:
            tsData += '{\n'
            for key, value in item.items():
                if key in ['sys_inventoryId', 'sys_inventoryItemId']:
                    tsData += f'  {key}: "{value}"\n'
                elif key == 'data':
                    tsData += '  data: {\n'
                    for dkey, dvalue in value.items():
                        if dkey == 'resolution':
                            tsData += f'''  resolution: {{timeUnit: {dvalue['timeUnit']}, factor: {dvalue['factor']}}}\n'''
                        elif dkey == 'unit':
                            tsData += f'''  unit: "{dvalue}"\n'''
                        elif dkey == 'dataPoints':
                            tsData += '    dataPoints: [\n'
                            for dp_key in dvalue:
                                if 'flag' not in dp_key:
                                    tsData += f'''     {{timestamp: "{dp_key['timestamp']}", value: {dp_key['value']}}}\n'''
                                else:    
                                    tsData += f'''     {{timestamp: "{dp_key['timestamp']}", value: {dp_key['value']}, flag: {dp_key['flag']}}}\n'''
                            tsData += '    ]\n'
                        else: pass
                    tsData += '  }\n'
                else:pass
            tsData += '}\n'
        tsData += ']\n'
        return tsData

    def _dataPointsToString(dataPoints:dict) -> str:
        """Converts a dictionary of datapoints to graphQL string"""

        _dataPoints = ''
        for timestamp, value in dataPoints.items():
            if value == None:
                _dataPoints += f'''{{
                    timestamp: "{timestamp}"
                    value: 0
                    flag: MISSING
                    }}\n'''
            else: 
                _dataPoints += f'''{{
                        timestamp: "{timestamp}"
                        value: {value}
                        }}\n'''

        return _dataPoints

    def _sliceDataPoints(dataPoints:dict, start:int, stop:int):
        """Return a slice of the dataPoints dictionary"""

        return dict(islice(dataPoints, start, stop))

    def _processDataFrame(
        self,
        result:dict,
        dataFrame:pd.DataFrame,
        fields:list,
        timeZone:pytz.timezone,
        displayMode:str, 
        includeMissing:bool
        ) -> pd.DataFrame:
        """
        Creates a time Series DataFrame for different time series data methods
        """
        df = dataFrame
        if df.empty:
            logger.info('The query did not produce results.')
            return df
        df.loc[(df.flag == 'MISSING'), 'value'] = nan

        if displayMode == 'pivot':
            if includeMissing == False:
                df = df.pivot_table(index='timestamp', columns=fields, values='value', dropna=True)
            else:
                df = df.pivot_table(index='timestamp', columns=fields, values='value', dropna=False)

            if len(df.columns) == 0:
                logger.warning(f"No display value found. Provide at least 1 property for argument 'fields'.")
                return
            df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S').tz_convert(pytz.timezone(timeZone))
            if self.defaults.useDateTimeOffset == False:
                df.index = df.index.tz_localize(tz=None)

            columnNumber = len(result)
            dfColumnNumber = len(df.columns)
            if len(df.columns) < len(result):
                logger.info(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers or NaN-columns.")
            return df

        elif displayMode == 'rows':
            df.set_index('timestamp', inplace=True)
            df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S').tz_convert(pytz.timezone(timeZone))
            if self.defaults.useDateTimeOffset == False:
                df.index = df.index.tz_localize(tz=None)
            return df

        else:
            Utils._error(self, msg=f"Unknown displayMode '{displayMode}'. Use 'pivot' or 'rows'.")
            return

 