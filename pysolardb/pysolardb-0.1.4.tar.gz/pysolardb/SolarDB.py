import requests
import json
import os
import logging
import outdated
import pandas as pd
from io import StringIO
from __init__ import __version__

class SolarDB():

    def __init__(self):
        self.checkIfOutdated()
        self.__baseURL = "https://solardb.univ-reunion.fr/api/v1/"
        self.__cookies = None
        self.logger = logging.getLogger(__name__)
        self.setloggerLevel(logging.INFO)
        ## Automatically logs in SolarDB if the token is saved in the '~/.bashrc' file
        token = os.environ.get('SolarDBToken')
        if token is not None:
            self.login(token)
        else:
            self.logger.warning("You will need to use your token to log in SolarDB")    


    ## Methods to log in SolarDB----------------------------------------------------------

    def login(self, token:str):
        """
        Gives access of SolarDB

        Parameters
        ----------
        token : str
            This string is used as a key to log in SolarDB.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem 
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        try:
            res = requests.get(self.__baseURL + "login?token=" + token)
            res.raise_for_status()
            self.__cookies = res.cookies
            self.logger.debug(json.loads(res.content)["message"])
        except requests.exceptions.HTTPError:
            self.logger.warning(
                                "login -> HTTP Error: ",
                                json.loads(res.content)["message"]
                                )
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("login -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("login -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("login -> Request Error: ",err)

    def register(self, email:str):
        """
        Sends a token via email.

        Parameters
        ----------
        email : str
            This string represents the user's mail address.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem 
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        try:
            res = requests.get(self.__baseURL + "register?email=" + email)
            res.raise_for_status()
            self.logger.debug(json.loads(res.content)["message"])
        except requests.exceptions.HTTPError:
            self.logger.warning("register -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("register -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("register -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("register -> Request Error: ",err)

    def status(self):
        """
        This method is used to verify if you are still logged in. It becomes obsolete if
        the logging level is higher than INFO.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        try:
            res = requests.get(self.__baseURL + "status", cookies = self.__cookies)
            self.logger.info(json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("status -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("status -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("status -> Request Error: ",err)

    def logout(self):
        """
        Logs out of SolarDB.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        try:
            res = requests.get(self.__baseURL + "logout", cookies = self.__cookies)
            res.raise_for_status()
            self.logger.debug(json.loads(res.content)["message"])
            self.__cookies = None
        except requests.exceptions.HTTPError:
            self.logger.warning("logout -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("logout -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("logout -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("logout -> Request Error: ",err)


    ## Methods to recover the data -------------------------------------------------------

    def getAllSites(self):
        """
        Returns all the alias sites accessible through SolarDB.

        Returns
        -------
            A list every alias site present in SolarDB.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        sites = []
        try:
            res = requests.get(self.__baseURL + "data/sites", cookies=self.__cookies)
            res.raise_for_status()
            for i in range(len(json.loads(res.content)["data"])):
                sites.append(json.loads(res.content)["data"][i])
            self.logger.debug("All data sites successfully extracted from SolarDB")
            return sites
        except requests.exceptions.HTTPError:
            self.logger.warning("getAllSites -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getAllSites -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getAllSites -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getAllSites -> Request Error: ",err)

    def getAllTypes(self):
        """
        Returns all the data types accessible through SolarDB.

        Returns
        -------
            A list every data type present in SolarDB.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        types = []
        try:
            res = requests.get(self.__baseURL + "data/types", cookies=self.__cookies)
            res.raise_for_status()
            for i in range(len(json.loads(res.content)["data"])):
                types.append(json.loads(res.content)["data"][i])
            self.logger.debug("All data types successfully extracted from SolarDB")
            return types
        except requests.exceptions.HTTPError:
            self.logger.warning("getAllTypes -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getAllTypes -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getAllTypes -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getAllTypes -> Request Error: ",err)

    def getSensors(self, sites:list[str] = None, types:list[str] = None):
        """
        Returns sensors present in SolarDB by sites and/or types.
        If no sites or types are given, returns all sensors present in SolarDB

        Parameters
        ----------
        sites : list[str] (OPTIONAL)
            This list is used to specify the sites in which we will search the sensors.
        types : list[str] (OPTIONAL)
            This list is used to specify sensor types to recover.

        Returns
        -------
        A list containing the sensors extracted from SolarDB

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """
        sensors = []
        query = self.__baseURL + "data/sensors"
        args = ""
        if sites is not None:
            args += "&site=" + ','.join(sites)
        if types is not None:
            args += "&type=" + ','.join(types)
        if args != "":
            query += "?" + args
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            sensors = json.loads(res.content)["data"]
            self.logger.debug("All sensors successfully extracted from SolarDB")
            return sensors
        except requests.exceptions.HTTPError:
            self.logger.warning("getSensors -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getSensors -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getSensors -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getSensors -> Request Error: ",err)

    def getData(
                self,
                sites:list[str] = None,
                types:list[str] = None,
                sensors:list[str] = None,
                start:str = None,
                stop:str = None,
                aggrFn:str = None,
                aggrEvery:str = None
                ):
        """
        Extracts data associated to at least one site, sensor and/or type. The user can
        choose the time period on which the extraction is set (set on the last 24h by
        default) and define an aggregation for a better analysis.

        Parameters
        ----------
        sites : list[str]
            This list is used to specify the sites for which we will search the data.
        types : list[str]
            This list is used to specify sensor types used to recover the data.
        sensors : list[str]
            This list is used to specify the sensors used to recover the data.
        start : str (OPTIONAL)
            This string specifies the starting date for the data recovery. It either follows
            a date format, an RFC3339 date format, or a duration unit respecting the '[N][T]'
            format, where [N] is an integer and [T] is one of the following strings:
            * 'y'   : year
            * 'mo'  : month
            * 'w'   : week
            * 'd'   : day
            * 'h'   : hour
            * 'm'   : minute
            Example: '-24d' == 24 days ago
        stop : str (OPTIONAL)
            This string specifies the ending date for the data recovery. It follows the same
            format as "start".
        aggrFn : str (OPTIONAL)
            This string represents the function to apply for the aggregation, such as:
            * 'mean'    : the average value
            * 'min'     : the minimum value
            * 'max'     : the maximum value
            * 'count'   : the number of non-null value
        aggrEvery : str (OPTIONAL)
            This string represents the period for the aggregation. It follows the duration
            unit format defined previously.

        Returns
        -------
            A dictionary containing the data per site and sensor. It is structured as 
            follows:
            data{
                site{
                    sensor{
                        dates:  [...]
                        values: [...]
                    }
                }
            }

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """
        query = self.__baseURL + "data/json"
        args = ""
        if sites is not None:
            args += "&site=" + ','.join(sites)
        if types is not None:
            args += "&type=" + ','.join(types)
        if sensors is not None:
            args += "&sensorid=" + ','.join(sensors)
        if start is not None:
            args += "&start=" + start
        if stop is not None:
            args += "&stop=" + stop
        if aggrFn is not None:
            args += "&aggrFn=" + aggrFn
        if aggrEvery is not None:
            args += "&aggrEvery=" + aggrEvery
        if args != "":
            query += "?" + args

        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            data = json.loads(res.content)["data"]
            if data:
                self.logger.debug("Data successfully recovered")
            else:
                self.logger.info("There is no data for this particular request")
            return data
        except requests.exceptions.HTTPError:
            self.logger.warning("getData -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getData -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getData -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getData -> Request Error: ",err)

    def getBounds(
                  self,
                  sites:list[str] = None,
                  types:list[str] = None,
                  sensors:list[str] = None
                  ):
        """
        Extracts the temporal bounds of each sensor associated to at least one site, sensor
        and/or type.

        Parameters
        ----------
        sites : list[str]
            This list is used to specify the sites for which we will search the bounds.
        types : list[str]
            This list is used to specify sensor types used to recover the bounds.
        sensors : list[str]
            This list is used to specify the sensors used to recover the bounds.

        Returns
        -------
            A dictionary containing the bounds per site and sensor structured as follows:
            data{
                site{
                    sensor{
                        start:  "..."
                        stop:   "..."
                    }
                }
            }

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        bounds = None
        query = self.__baseURL + "data/json/bounds"
        args = ""
        if sites is not None:
            args += "&site=" + ','.join(sites)
        if types is not None:
            args += "&type=" + ','.join(types)
        if sensors is not None:
            args += "&sensorid=" + ','.join(sensors)
        if args != "":
            query += "?" + args
        
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            bounds = json.loads(res.content)["data"]
            if bounds:
                self.logger.debug("Bounds successfully recovered")
            else:
                self.logger.info("The bounds defined by this request are null")
            return bounds
        except requests.exceptions.HTTPError:
            self.logger.warning("getBounds -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getBounds -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getBounds -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getBounds -> Request Error: ",err)


    ## Methods to recover the metadata ----------------------------------------------------
    
    def getCampaigns(
                     self,
                     ids:str = None,
                     name:str = None,
                     territory:str = None,
                     alias:str = None
                     ):
        """
        Extracts the different campaigns that took place during the IOS-Net project.
        Specifying the campaign id, name, territory and/or alias will narrow down the
        campaigns recovered.

        Parameters
        ----------
        ids : str (OPTIONAL)
            This string is the identity key. It corresponds to the '_id' field in the Mongo
            'campaigns' collection.
        name : str (OPTIONAL)
            This corresponds to the station official name and is associated to the 'name'
            field in the Mongo 'campaigns' collection.
        territory : str (OPTIONAL)
            This string represents the territory name and is associated to the 'territory'
            field in the Mongo 'campaigns' collection.
        alias : str (OPTIONAL)
            This string is the site practical name (which is used for data extraction) and
            is associated to the 'alias' field in the Mongo 'campaigns' collection.

        Returns
        -------
            A dictionary containing the campaigns' metadata.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        campaigns = None
        query = self.__baseURL + "metadata/campaigns"
        args = ""
        if ids is not None:
            args += "&id=" + ids
        if name is not None:
            args += "&name=" + name
        if territory is not None:
            args += "&territory=" + territory
        if alias is not None:
            args += "&alias=" + alias
        if args != "":
            query += "?" + args

        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            campaigns = json.loads(res.content)["data"]
            if campaigns:
                self.logger.debug("Campaign metadata successfully recovered")
            else:
                self.logger.info("The campaigns defined by this request do not exist")
            return campaigns
        except requests.exceptions.HTTPError:
            self.logger.warning("getCampaigns -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getCampaigns -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getCampaigns -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getCampaigns -> Request Error: ",err)

    def getInstruments(
                       self,
                       ids:str = None,
                       name:str = None,
                       label:str = None,
                       serial:str = None
                       ):
        """
        Returns the different instruments used in the IOS-Net project. Specifying the id,
        name, label and/or serial number will narrow down the instruments recovered.

        Parameters
        ----------
        ids : str (OPTIONAL)
            This string is the identity key. It corresponds to the '_id' field in the Mongo
            'instruments' collection.
        name : str (OPTIONAL)
            This corresponds to the station official name and is associated to the 'name'
            field in the Mongo 'instruments' collection.
        label : str (OPTIONAL)
            This string represents the instrument's label and is associated to the 'label'
            field in the Mongo 'instruments' collection.
        serial : str (OPTIONAL)
            This string is the instrument's serial number and is associated to the 'serial'
            field in the Mongo 'instruments' collection.

        Returns
        -------
            A dictionary containing the instruments' metadata.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        instruments = None
        query = self.__baseURL + "metadata/instruments"
        args = ""
        if ids is not None:
            args += "&id=" + ids
        if name is not None:
            args += "&name=" + name
        if label is not None:
            args += "&label=" + label
        if serial is not None:
            args += "&serial=" + serial
        if args != "":
            query += "?" + args
        
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            instruments = json.loads(res.content)["data"]
            if instruments:
                self.logger.debug("Instrument metadata successfully recovered")
            else:
                self.logger.info("The intstruments defined by this request do not exist")
            return instruments
        except requests.exceptions.HTTPError:
            self.logger.warning("getInstruments -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getInstruments -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getInstruments -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getInstruments -> Request Error: ",err)

    def getMeasures(
                    self,
                    ids:str = None,
                    names:list[str] = None,
                    dtype:str = None,
                    nested:bool = None
                    ):
        """
        Extracts the different measure types used in the IOS-Net project. Specifying the id,
        name and/or data type will narrow down the measures recovered.

        Parameters
        ----------
        ids : str (OPTIONAL)
            This string is the identity key. It corresponds to the '_id' field in the Mongo
            'measures' collection.
        names : list[str] (OPTIONAL)
            This corresponds to the sensor/s name/s and is associated to the 'name' field
            in the Mongo 'measures' collection.
        dtype : list[str] (OPTIONAL)
            This string represents the data type and is associated to the 'type' field in the
            Mongo 'measures' collection.
        nested : bool (OPTIONAL)
            This boolean, which is false by default, indicates whether the user wants to recieve
            all the metadata or only key metadata information associated to the measures.

        Returns
        -------
            A dictionary containing the measures' metadata

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        measures = None
        query = self.__baseURL + "metadata/measures"
        args = ""
        if ids is not None:
            args += "&id=" + ids
        if names is not None:
            args += "&name=" + ','.join(names)
        if dtype is not None:
            args += "&type=" + dtype
        if nested is not None:
            args += "&nested=" + str(nested)
        if args != "":
            query += "?" + args
        
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            measures = json.loads(res.content)["data"]
            if measures:
                self.logger.debug("Measure metadata successfully recovered")
            else:
                self.logger.info("The measures defined by this request do not exist")
            return measures
        except requests.exceptions.HTTPError:
            self.logger.warning("getMeasures -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getMeasures -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getMeasures -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getMeasures -> Request Error: ",err)

    def getModels(
                  self,
                  ids:str = None,
                  name:str = None,
                  dtype:str = None
                  ):
        """
        Returns the models used in the IOS-Net project. Specifying the id, name and/or data
        type will narrow down the models recovered.

        Parameters
        ----------
        ids : str (OPTIONAL)
            This string is the identity key. It corresponds to the '_id' field in the Mongo
            'models' collection.
        name : str (OPTIONAL)
            This corresponds to the station official name and is associated to the 'name'
            field in the Mongo 'models' collection.
        dtype : str (OPTIONAL)
            This string represents the data type and is associated to the 'type' field in
            the Mongo 'models' collection.

        Returns
        -------
            A dictionary containing the models' metadata.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """

        models = None
        query = self.__baseURL + "metadata/models"
        args = ""
        if ids is not None:
            args += "&id=" + ids
        if name is not None:
            args += "&name=" + name
        if dtype is not None:
            args += "&type=" + dtype
        if args != "":
            query += "?" + args
        
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            models = json.loads(res.content)["data"]
            if models:
                self.logger.debug("Models metadata successfully recovered")
            else:
                self.logger.info("The measures defined by this request do not exist")
            return models
        except requests.exceptions.HTTPError:
            self.logger.warning("getModels -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getModels -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getModels -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getModels -> Request Error: ",err)


    ## Utils

    def getSiteDataframe(self, site:str, start:str = None, stop:str = None):
        """
        Extracts a CSV file containing the data associated to a site and converts it into
        a pandas dataframe object. The user can choose the time period on which the extraction
        is set (set on the last 24h by default).

        Parameters
        ----------
        site : str
            This string is used to specify the site chosen by the user.
        start : str (OPTIONAL)
            This string specifies the starting date for the data recovery. It either follows
            a date format, an RFC3339 date format, or a duration unit respecting the '[N][T]'
            format, where [N] is an integer and [T] is one of the following strings:
            * 'y'   : year
            * 'mo'  : month
            * 'w'   : week
            * 'd'   : day
            * 'h'   : hour
            * 'm'   : minute
            Example: '-24d' == 24 days ago
        stop : str (OPTIONAL)
            This string specifies the ending date for the data recovery. It follows the same
            format as "start".

        Returns
        -------
            A Pandas dataframe containing the data for each sensor of the site on the requested
            time period.

        Raises
        ------
        HTTPError
            If the responded HTTP Status is between 400 and 600 (i.e if there is a problem
            with the request or the server)
        ConnectionError
            If the program is unable to connect to SolarDB
        TimeOutError
            If the SolarDB response is too slow
        RequestException
            In case an error that is unaccounted for happens
        """
        query = self.__baseURL + "data/csv/" + site
        args = ""
        if start is not None:
            args += "&start=" + start
        if stop is not None:
            args += "&stop=" + stop
        if args != "":
            query += "?" + args
        try:
            res = requests.get(query, cookies=self.__cookies)
            res.raise_for_status()
            df = pd.read_csv(StringIO(res.text))
            return df
        except requests.exceptions.HTTPError:
            self.logger.warning("getData -> HTTP Error: ", json.loads(res.content)["message"])
        except requests.exceptions.ConnectionError as errc:
            self.logger.warning("getData -> Connection Error:",errc)
        except requests.exceptions.Timeout as errt:
            self.logger.warning("getData -> Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            self.logger.warning("getData -> Request Error: ",err)

    def setloggerLevel(self, val:int):
        """
        Changes the logging level. It is used to enable and/or disable the messages.
        
        Parameters
        ----------
        val : str
            This integer represents the logging level as follows:
            - 0  : NOTSET
            - 10 (or logging.DEBUG)     : DEBUG
            - 20 (or logging.INFO)      : INFO
            - 30 (or logging.WARN)      : WARNING
            - 40 (or logging.ERROR)     : ERROR
            - 50 (ot logging.CRITICAL)  : CRITICAL
            The levels allow all the logging levels with a higher severity to appear
            (e.g a logging.INFO level will disable all messages marked with logging.DEBUG).
            If val is set to 0/logging.NOTSET, the logging level will be set to the root level,
            which is WARNING.
        """
        # remove all handlers
        while self.logger.hasHandlers():
            self.logger.removeHandler(self.logger.handlers[0])
        self.logger.setLevel(val)
        __ch = logging.StreamHandler()
        __ch.setLevel(val)
        self.logger.addHandler(__ch)


    def checkIfOutdated(self):
        """
        Checks if the current version of this package is the latest.
        """
        is_outdated, latest_version = outdated.check_outdated("pysolardb", __version__)
        if is_outdated:
            print("A newer version of the pySolarDB package is currently available: pysolardb ", latest_version)
    