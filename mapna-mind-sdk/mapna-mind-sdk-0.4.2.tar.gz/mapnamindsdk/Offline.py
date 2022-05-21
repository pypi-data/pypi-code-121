from requests import session
from mapnamindsdk.Mapper import Mapper as mapper
import mapnamindsdk.Constants as Constants
# from http.client import IncompleteRead
import pandas as pd
from mapnamindsdk.Rest import Rest as Rest
from mapnamindsdk.Mind import Mind
import datetime


def switch_plant(argument):
    switcher = {
        Constants.FARS_PLANT: 3,
        Constants.PARESAR_PLANT: 4
    }
    return switcher.get(argument, "Invalid Plant")


class Offline(Mind):

    @staticmethod
    def getUdsValue(signalNames, startDate, endDate, userId):

        Offline._validate(startDate)
        Offline._validate(endDate)

        try:
            body = {"signalNames": signalNames,
                    "startDate": startDate,
                    "endDate": endDate,
                    "userId": userId
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/offline/getUsd', params=body)
            listResult = post_req.post()

            print(listResult)

            return listResult

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def getValue(plantName, signalNames,signalClass, startDate, endDate, aggregation, interval, pageNumber=1, pageSize=100000000):
        jsonResult = None

        try:
            Offline._validate_signalName(signalNames)
            Offline._plant_validate(plantName)
            Offline._validate(startDate,endDate,interval)
            # Offline._validate(endDate)
            signalNames.sort()
            print(len(signalNames))
            units = list(map(lambda x: int(x[0:2]), signalNames))
            unit = set(units)
            if len(unit) != 1:
                raise Exception("INPUT ERROR: All Signals Must Belong to One Unit")

            plant = switch_plant(plantName)
            f = mapper.getInstance(plant)

            # Get signalId for given signalName from the Mapper
            signalIDs = list(map(lambda x: int(f.SignalMapper[x]), signalNames))

            t1 = datetime.datetime.now()
            print(t1)

            # Request Body
            signal_str = ', '.join(f"'{w}'" for w in signalNames)
            units_str = ', '.join(f"{w}" for w in units)

            body = {
                "plant": plantName, "from_date": startDate, "to_date": endDate, "agg": aggregation,
                "interval": interval, "page_size": pageSize, "page_number": pageNumber, "userId": "1",
                # "signalClass": signalClass,
                "signalClass": signalClass,"signalNames": signal_str, "units": units_str
            }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/data/getData', params=body,
                            header={'Content-Type': 'application/json; charset=utf-8'})
            print(body)
            jsonResult = post_req.post()
            print("jsonResulttttttttt\n")
            t2 = datetime.datetime.now()
            print(t2)
        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))

        if (isinstance(jsonResult, list) and len(jsonResult)):
            print(len(jsonResult))
            df_result = Offline._convertJsonToDataFrame(jsonResult, signalNames)
            if (df_result is not None):
                print("df_resulttttttt\n")
                print(df_result.count())
                print(df_result.head(5))
                t3 = datetime.datetime.now()
                print(t3)
                return df_result
        else:
            print(jsonResult)
        return None

    @staticmethod
    def getValue2(signalNames, timeRanges: list, aggregation, interval, pageNumber=1, pageSize=1000) -> pd.DataFrame:
        final_result = pd.DataFrame([])
        # final_result_list=[]
        for range in timeRanges:
            startDate = range[0]
            endDate = range[1]
            df = Offline.getValue(signalNames, startDate=startDate, endDate=endDate, aggregation=aggregation,
                                  interval=interval, pageNumber=pageNumber, pageSize=pageSize)
            final_result = pd.concat([final_result, df])
            # final_result_list.append(df)

        return final_result

    @staticmethod
    def getLastValue(signalNames):
        return super(Offline, Offline).getValue(signalNames)

    @staticmethod
    def getVibValue(plant, signalName, startDate, endDate, pageNumber=1, pageSize=1000):
        jsonResult = {}
        try:
            print(session)
            print(datetime.datetime.now())
            Offline._date_validate(startDate)
            Offline._date_validate(endDate)
            # Offline._signal_type_validate(input_signal_type)
            Offline._signal_name_validate(signalName)
            table_name = Offline._find_signal_input_table(signalName)
            print(table_name)
            # Request Body
            # print(switch_plant(plant))
            # table_name = input_signal_type
            body = {"kks": signalName,
                    "fromDate": startDate,
                    "toDate": endDate,
                    "plantId": switch_plant(plant),
                    "table": table_name,
                    # "interval": interval,
                    # "page_size": pageSize,
                    # "page_number": pageNumber
                    }
            post_req = Rest(f'http://{Constants.VIB_SERVICE_IP}:{Constants.VIB_SERVICE_PORT}',
                            path=f'/steady', params=body)
            jsonResult = post_req.post()
        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        if (isinstance(jsonResult, list) and len(jsonResult)):
            # print(len(jsonResult))
            df_result = Mind._convertJsonVibToDataFrame(jsonResult, table_name)
            # return jsonResult
            if (df_result is not None):
                print("df_resulttttttt\n")
                print(df_result.count())
                print(df_result.head(5))
            return df_result
        print(jsonResult)
        return None

    @staticmethod
    def get_signal_name():
        plantName = {'fars'}
        plant = switch_plant(plantName)

        f = mapper.getInstance(plant)
        return f.getMapper()

        # Get signalId for given signalName from the Mapper
        # signalIDs = list(map(lambda x: int(f.SignalMapper[x]), signalNames))
