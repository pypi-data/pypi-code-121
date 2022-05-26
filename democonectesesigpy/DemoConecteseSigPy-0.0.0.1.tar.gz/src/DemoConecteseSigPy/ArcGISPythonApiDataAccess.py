from arcgis.gis import GIS
from arcgis import features
from arcgis import geometry
from arcgis.features import _version

from DemoConecteseSigPy.DataAccess import DataAccess
from DemoConecteseSigPy.Utiles import ToolboxLogger

DEFAULT_FILTER_STRING = "1=1"

class ArcGISPythonApiDataAccess(DataAccess) :

    @staticmethod
    def getGIS(url_portal = None, username = None, password = None) :
        gis = None
        try :
            if url_portal == None and username == None and password == None :
                gis = GIS("home")    
            elif username == None and password == None :
                gis = GIS(url_portal)
            else :
                gis = GIS(url_portal, username, password)
        except Exception as e:
            ToolboxLogger.info("ERROR: ---->'{}'".format(e))

        return gis

    def __init__(self, gis):
        super().__init__()
        self.__gis = gis
        self.__version = None
        self.__version_manager = None
        self.__feature_service = None 
        self.outSpatialReference = None
        self.hasZ = False
        self.returnZ = False

    def __find_table(self, table_name) : 
        if self.__feature_service == None:
            raise Exception("Capa o tabla '{}' no disponible.".format(table_name))
        elif self.__feature_service.layers == None:
            raise Exception("Capa o tabla '{}' no disponible.".format(table_name))

        table = [x for x in self.__feature_service.layers if x.properties["name"].lower() == table_name.lower()]

        if len(table) == 0 :
            table = [x for x in self.__feature_service.tables if x.properties["name"].lower() == table_name.lower()]

        if len(table) == 0:
            return None

        return table[0]

    def getTable(self, table_name) :
        return self.__find_table(table_name)

    def _search_da(self, table, fields, filter = None, return_geometry = True, spatial_reference = None) :
        features = []

        ToolboxLogger.debug("nombre : {}".format(table.properties.name))
        ToolboxLogger.debug("filtro : {}".format(filter))
        ToolboxLogger.debug("campos : {}".format(fields))

        if filter != "" :

            if filter == None  :
                filter = DEFAULT_FILTER_STRING

            if isinstance(fields, list) :
                outFields = str.join(",", fields)
            else :
                outFields = fields

            if not spatial_reference:
                spatial_reference = self.outSpatialReference

            if self.__version != None :
                gdb_version = self.__version.properties.versionName
                query = table.query(
                    where= filter, 
                    outFields = outFields, 
                    return_z = self.returnZ,
                    return_geometry = return_geometry, 
                    out_sr = spatial_reference,
                    gdb_version = gdb_version)
            else :
                query = table.query(
                    where = filter, 
                    outFields = outFields, 
                    return_z = self.returnZ,
                    return_geometry = return_geometry, 
                    out_sr = spatial_reference)

            features = []
            for feature in query.features :
                f = feature.attributes
                if return_geometry and table.properties.type != "Table":
                    f["geometry"] = feature.geometry
                    if feature.geometry and not "spatial_reference" in feature.geometry :
                        f["geometry"]["spatial_reference"] = query.spatial_reference
                features.append(f)

        ToolboxLogger.debug("registros : {}".format(len(features)))
        return features

    def getSpatialReference(self) :
        if self.__feature_service and self.__feature_service.layers:
            sr = self.__feature_service.spatialReference
            ToolboxLogger.info("Referencia Espacial --> {}".format(sr))
            return self.__feature_service.layers[0].properties.extent.spatialReference
        return None

    def __getHasZ(self) :
        if self.__feature_service and self.__feature_service.layers:
            featLayers = [x for x in self.__feature_service.layers if x.properties.type == "Feature Layer"]
            if featLayers:
                return featLayers[0].properties.hasZ
        return False

    def _getFeature(self, record, spatialReference = None) :
        _attributes = record.copy()

        f = features.Feature()

        if "geometry" in _attributes and _attributes["geometry"] != {}:
            geo_key = _attributes["geometry"]
            del _attributes["geometry"]

            if geo_key :
                if not "spatialReference" in geo_key and spatialReference:
                    geo_key["spatialReference"] = spatialReference
                if not "hasZ" in geo_key:
                    geo_key["hasZ"] = self.hasZ
                if self.hasZ:
                    if "rings" in geo_key:
                        for ring in geo_key["rings"]:
                            if len(ring[0]) < 3:
                                for xy in ring:
                                    xy.append(0)
                f.geometry = geometry.Geometry(geo_key)
               
        f.attributes = _attributes
        return f

    @ToolboxLogger.log_method
    def add(self, table, record, spatialReference = None) :
        if isinstance(table, str):
            table = self.__find_table(table)

        features = []
        if isinstance(record, list):
            for r in record:
                f = self._getFeature(r, spatialReference)
                features.append(f)
        else:
            f = self._getFeature(record, spatialReference)
            features.append(f)

        if self.__version != None :
            r = self.__version.edit(layer=table, adds=features)
        else :
            r = table.edit_features(adds=features)

        if isinstance(record, list):
            return r["addResults"] if r["addResults"] else None
        else: 
            return r["addResults"][0] if r["addResults"] else None

    @ToolboxLogger.log_method
    def update(self, table, record) :
        
        if isinstance(table, str):
            table = self.__find_table(table)
        
        features = []
        if isinstance(record, list):
            for r in record:
                f = self._getFeature(r)
                features.append(f)
        else:
            f = self._getFeature(record)
            features.append(f)

        if self.__version != None :
            r = self.__version.edit(layer=table, updates=features)
        else :
            r = table.edit_features(updates=features)

        if isinstance(record, list):
            return r["updateResults"] if r["updateResults"] else None
        else:
            return r["updateResults"][0] if r["updateResults"] else None 

    @ToolboxLogger.log_method
    def delete(self, table, record) :         
        if isinstance(table, str):
            table = self.__find_table(table)

        oid_field = table.properties.objectIdField
        ids = []

        if isinstance(record, list) :
            for r in record:
                ids.append(r[oid_field])
        else :
            ids.append(record[oid_field])     

        if ids != [] :
            if self.__version != None :
                r = self.__version.edit(layer=table, deletes=ids)
            else :
                r = table.edit_features(deletes=ids)

            if isinstance(record, list) :
                return r["deleteResults"] if r["deleteResults"] else None
            else :
                return r["deleteResults"][0] if r["deleteResults"] else None
        else :
            return []

    @ToolboxLogger.log_method
    def query(self, table, fields, filter = None, return_geometry = True, spatial_reference = None) :
        if isinstance(table, str) :
            table = self.__find_table(table)

        return self._search_da(table, fields, filter, return_geometry, spatial_reference)

    @ToolboxLogger.log_method
    def getServiceTables(self) :
        tables = [x for x in self.__feature_service.tables]

        return tables

    @ToolboxLogger.log_method
    def getServiceLayers(self) :
        tables = [x for x in self.__feature_service.layers]
        return tables

    @ToolboxLogger.log_method
    def queryRelatedRecords(self, table, record, relationshipId, fields = '*', expression = None) :
        if isinstance(table, str) :
            table = self.__find_table(table)

        oid_field = table.properties.objectIdField
        ids = []
        
        if isinstance(record, list) :
            for r in record:
                ids.append("{}".format(r[oid_field]))
        else :
            ids.append("{}".format(record[oid_field]))    

        if isinstance(fields, list):
            fields = ",".join(fields)

        ids = ",".join(ids)

        if self.__version != None :
            gdb_version = self.__version.properties.versionName
            r = table.query_related_records(ids, relationshipId, definition_expression=expression, out_fields=fields, gdb_version = gdb_version)
        else :
            r = table.query_related_records(ids, relationshipId, definition_expression=expression, out_fields=fields)

        result = []
        for r in r["relatedRecordGroups"]:
            item = {}
            item["objectid"] = r["objectId"]

            records = []
            for rr in r["relatedRecords"]: 
                f = rr["attributes"]
                if "geometry" in rr:
                    f["geometry"] = rr["geometry"]
                    
                records.append(f)
                    
            item["records"] = records
            result.append(item)

        return result

    @ToolboxLogger.log_method
    def setFeatureService(self, feature_service_name) :
        query = "title: '{}' AND type: 'Feature Service'".format(feature_service_name)
        search_results = self.__gis.content.search(query = query, max_items = 10)
        self.__feature_service = [x for x in search_results if x["title"] == feature_service_name][0] if search_results else None
        self.hasZ = self.__getHasZ()
        self.returnZ = self.hasZ

        return self.__feature_service

    @ToolboxLogger.log_method
    def copyFeatureService(self, new_service_name) :
        if(self.__feature_service != None) :
            return self.__feature_service.copy(title = new_service_name)
        else:
            return None

    @ToolboxLogger.log_method
    def setVersionManager(self) :

        if(self.__feature_service != None) :
            feature_service_url = self.__feature_service.url
            if feature_service_url != None :
                version_manager_service_url = feature_service_url.replace("FeatureServer", "VersionManagementServer")
                self.__version_manager = _version.VersionManager(version_manager_service_url, self.__gis, self.__feature_service)
        return self.__version_manager

    @ToolboxLogger.log_method
    def isVersionLocked(self, versionName) :
        try:
            if self.__version_manager :
                versions = [x for x in self.__version_manager.locks if x.properties.versionName.lower() == versionName.lower()]
                if(len(versions)) > 0:
                    version = versions[0]
                    ToolboxLogger.debug("version.properties.isBeingEdited: {}".format(version.properties.isBeingEdited))
                    ToolboxLogger.debug("version.properties.isBeingRead: {}".format(version.properties.isBeingRead))
                    ToolboxLogger.debug("version.properties.isLocked: {}".format(version.properties.isLocked))
                    ToolboxLogger.debug("version.mode: {}".format(version.mode))
                    if version.properties.isBeingEdited or version.properties.isBeingRead :
                        ToolboxLogger.info("{}".format(version.properties))
                        result = self.__version_manager.purge(version.properties.versionName)
                    return version.properties.isBeingEdited or version.properties.isBeingRead, result
                else :
                    return False, False
            else :
                raise Exception("VersionManager Nulo")
        except Exception as e:
            ToolboxLogger.info("ERROR: ---->'{}'".format(e))

    @ToolboxLogger.log_method
    def setVersion(self, versionName) :
        try:
            all_versions = [x for x in self.__version_manager.all if x.properties.versionName.lower() == versionName.lower()]
            if (len(all_versions) > 0) :
                self.__version = all_versions[0]
                self.__version.save_edits = True
            else:
                raise Exception("Versión No Existe!")

            return self.__version
        except Exception as e:
            ToolboxLogger.info("ERROR: ---->'{}'".format(e))

        return None 

    @ToolboxLogger.log_method
    def purgeVersion(self, versionName) :
        versionsToPurge = [x for x in self.__version_manager.all if x.properties.versionName.lower() == versionName.lower()]
        versionToPurge = versionsToPurge[0] if len(versionsToPurge) > 0 else None
        if versionToPurge:
            ToolboxLogger.debug("version.properties.isBeingEdited: {}".format(versionToPurge.properties.isBeingEdited))
            ToolboxLogger.debug("version.properties.isBeingRead: {}".format(versionToPurge.properties.isBeingRead))
            ToolboxLogger.debug("version.properties.isLocked: {}".format(versionToPurge.properties.isLocked))
            ToolboxLogger.debug("version.mode: {}".format(versionToPurge.mode))
            
            result = self.__version_manager.purge(versionToPurge.properties.versionName) if versionToPurge.mode == None and versionToPurge.properties.isLocked else True
        return result
        
    @ToolboxLogger.log_method
    def createVersion (self, versionName, permission="public", description ="") :
        result = self.__version_manager.create(versionName, permission, description)

        if result : 
            new_versions = [x for x in self.__version_manager.all if x.properties.versionName.__contains__(versionName)]
            return new_versions[0].properties.versionName if new_versions != None else None 
        else:
            return None

    @ToolboxLogger.log_method
    def deleteVersions(self, propietario, encuesta) :
        versions = [x for x in self.__version_manager.all if x.properties.versionName.__contains__(propietario + ".") and x.properties.versionName.__contains__(encuesta)]

        for version in versions:
            ToolboxLogger.debug("eliminando '{}'".format(version.properties.versionName))
            if version.properties.isLocked == True :
                self.__version_manager.purge(version.properties.versionName, propietario)
            version.delete()

    @ToolboxLogger.log_method
    def setMode(self, modo) :
        if self.__version :
            self.__version.mode = modo

    @ToolboxLogger.log_method
    def startEditing(self):
        if self.__version :
            try:
                result = False
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                result = self.__version.start_editing()
            except Exception as ex:
                ToolboxLogger.info(ex)
            finally :
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                return result

    @ToolboxLogger.log_method
    def stopEditing(self, save_edits):
        if self.__version :
            try:
                result = False
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                result = self.__version.stop_editing(save_edits)
            except Exception as ex:
                ToolboxLogger.info(ex)
            finally :
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                return result

    @ToolboxLogger.log_method
    def startReading(self):
        if self.__version :
            try:
                result = False
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                result = self.__version.start_reading()
            except Exception as ex:
                ToolboxLogger.info(ex)
            finally :
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                return result 

    @ToolboxLogger.log_method
    def stopReading(self):
        if self.__version :
            try:
                result = False
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                result = self.__version.stop_reading()
            except Exception as ex:
                ToolboxLogger.info(ex)
            finally :
                ToolboxLogger.debug("version.mode: {}".format(self.__version.mode))
                return result

    @ToolboxLogger.log_method
    def describeRelation(self, table_name, idRelacion) :
        relacion = None
        if idRelacion :
            table = self.__find_table(table_name)
            relaciones = [x for x in table.properties.relationships if x.id == idRelacion] 
            if len(relaciones) > 0 :
                for relacion in relaciones :
                    ToolboxLogger.debug("relacion id: {} - nombre: '{}'".format(relacion.id, relacion.name))
        return relacion

    def getElementsInFolder(self, folder_name) :   
        list_elements = self.__gis.content.items(folder=folder_name, max_items=10)
        return list_elements
    
    @ToolboxLogger.log_method
    def searchElement(self, element_name, element_type) :
        query = "title: '{}' AND type: '{}'".format(element_name, element_type)
        search_results = self.__gis.content.search(query=query, max_items=10)
        
        return search_results

    @ToolboxLogger.log_method
    def copyElement(self, element, new_element_name) :
        if(element != None) :
            return element.copy(title=new_element_name)
        else:
            return None
    
