#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bson
import copy
from bson.codec_options import CodecOptions
from TDhelper.db.mongodb.dbhelper import dbhelper
from TDhelper.db.mongodb.setting import db_cfg
'''
class\r\n
    objectId
description\r\n
    mongodb's bson.objectid\r\n
'''
class objectId(dbhelper):
    model=None
    def __init__(self):
        super(objectId,self).__init__()
        self.setCollection(type(self).__name__)
        self.model={
            "_id":None
        }
    @property
    def oId(self):
        if self.model["_id"]:
            return self.model["_id"]
        else:
            self.model["_id"]=bson.objectid.ObjectId()
            return self.model["_id"]
    @oId.setter
    def oId(self,args):
        if args:
            self.model["_id"]=bson.objectid.ObjectId(args)
        else:
            self.model["_id"]=bson.objectid.ObjectId()

    def toSave(self):
        if self.model:
            if self.oId:  
                return self.save(self.model)
        else:
            return None

    def deleteById(self):
        if self.model:
            return self.remove({'_id':self.oId})

    def getbyId(self):
        if self.model:
            result=copy.deepcopy(self)
            if result:
                oResult=self.findOne({'_id':self.oId})
                if oResult:
                    result.model=oResult
                    return result
                return None
        return None

    def getByfield(self, field_name):
        if field_name:
            return self.findOne({field_name: self.model[field_name]})
        return None

    def UpdateById(self):
        if self.oId:
            self.update({'_id':self.oId}, self.model)

    def getOneByQuery(self, query):
        if self.model:
            result=copy.deepcopy(self)
            if result:
                oResult=self.findOne(query)
                if oResult:
                    result.model=oResult
                    return result
        return None