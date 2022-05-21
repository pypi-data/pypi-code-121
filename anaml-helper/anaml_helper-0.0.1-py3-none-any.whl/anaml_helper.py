from anaml_client import Anaml
from anaml_client.models.ref import BranchRef
from anaml_client.models.table import RootTable, ViewTable, TableId, TableName
from anaml_client.models.feature import Feature, RowFeature, EventFeature, FeatureId, FeatureName, FeatureVersionId
from anaml_client.models.feature_set import FeatureSet, FeatureSetName, FeatureSetId, FeatureSetVersionId
from anaml_client.models.entity import Entity, EntityId, EntityName, EntityVersionId
from anaml_client.models.event_window import RowWindow, OpenWindow, DayWindow, EventWindow
from anaml_client.models.select_expression import SelectExpression
from anaml_client.models.filter_expression import FilterExpression
from anaml_client.models.post_aggregate_expression import PostAggregateExpression
from anaml_client.models.aggregate import AggregateExpression
from anaml_client.models.schedule import DailySchedule, CronSchedule
from anaml_client.models.attribute import Attribute
from anaml_client.models.label import Label
from anaml_client.models.feature_store import FeatureStore, FeatureStoreId, FeatureStoreName
from anaml_client.models.feature_creation_request import FeatureCreationRequest, EventFeatureCreationRequest, RowFeatureCreationRequest
from anaml_client.models.feature_set_creation_request import FeatureSetCreationRequest
import uuid
import requests
from abc import ABC, abstractmethod
import os,io,json
from datetime import date, datetime, timezone, timedelta
from requests.auth import HTTPBasicAuth
from functools import partial
from dataclasses import dataclass, replace
from typing import Optional, List, Dict, Set, Callable

###Usage
#from anaml_client import Anaml
#from anaml_helper import AnamlHelper

#anaml_client = Anaml(url=,apikey=,secret=,ref=)
#anaml_helper = AnamlHelper(anaml_client)

###Aims 
#Provide access to lower level methods i.e update_feature_name() opposed to update_feature()
#Allows easier usage of sdk with features and feature sets
#as simplifies parameters by omitting the need to construct 
#complete Anaml objects to pass as parameter for updating certain attributes.

#Also aims to simplify feature creation process by
#providing method with params to create feature
#instead of expecting constructed EventFeatureCreationRequest to
#be passed to anaml.create_feature()

class AnamlHelper:
    __slots__ = ("_anaml")
    
    def __init__(self, anaml: Anaml) -> None:
        self._anaml = anaml
        
    @property
    def url(self) -> str:
        return self._anaml._url
    
    @property
    def branch(self) -> str:
        return self._anaml._ref.get("branch")
    
    #private method for handling aggregate type
    def __get_aggregate_type(self, aggregate: str) -> AggregateExpression:
        aggregations = {
            "count": AggregateExpression.Count,
            "countdistinct": AggregateExpression.CountDistinct,
            "last": AggregateExpression.Last,
            "first": AggregateExpression.First,
            "max": AggregateExpression.Max,
            "min": AggregateExpression.Min,
            "sum": AggregateExpression.Sum,
            "avg": AggregateExpression.Avg
        }
        return aggregations.get(aggregate.lower())
    
    ###Creating Features
    def create_feature(self,
                       name: str,
                       attributes: List[dict[str,str]],
                       labels: List[str],
                       select: str,
                       description: str,
                       template: Optional[str],
                       table: int,
                       filter: str,
                       aggregate: str,
                       post_aggregate: str,
                       entity_ids: List[int]
                       ):
        creation_request = EventFeatureCreationRequest(
            attributes=[Attribute.from_json(attr) for attr in attributes],
            labels=[Label(label) for label in labels],
            name=FeatureName(value=name),
            description=description,
            select=SelectExpression(sql=select),
            template=template,
            table=TableId(value=table),
            window=OpenWindow(),
            filter=FilterExpression(sql=filter),
            aggregate=self.__get_aggregate_type(aggregate),
            postAggregateExpr=PostAggregateExpression(sql=post_aggregate),
            entityRestrictions=[EntityId(entity) for entity in entity_ids]
        )
        return self._anaml.create_feature(creation_request)

    ###Updating Features
    def update_feature_name(self, feature_id: int, name: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, name=FeatureName(name), version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_attributes(self, feature_id: int, attributes: Dict[str,str]):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        new_attributes = [Attribute(key=k, value=v) for k,v in attributes.items()]
        updated_feature = replace(current_feature, attributes=new_attributes, version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_description(self, feature_id: int, description: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, description=description, version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_labels(self, feature_id: int, labels: List[str]):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        new_labels = [Label(value=label) for label in labels]
        updated_feature = replace(current_feature, labels=new_labels, version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_table(self, feature_id: int, table_id: int):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, table=TableId(value=table_id), version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_select(self, feature_id: int, select_expression: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, select=SelectExpression(sql=select_expression), version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_filter(self, feature_id: int, filter_expression: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, filter=FilterExpression(sql=filter_expression), version=FeatureVersionId(uuid.uuid4()))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_aggregate(self, feature_id: int, aggregate: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, aggregate=self.__get_aggregate_type(aggregate))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_to_RowWindow(self, feature_id: int, rows: int):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, window=RowWindow(rows=rows))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_to_DayWindow(self, feature_id: int, days: int):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, window=DayWindow(days=days))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_to_OpenWindow(self, feature_id: int):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, window=OpenWindow())
        return self._anaml.update_feature(updated_feature)
    
    def update_feature_postAggregateExpr(self, feature_id: int, post_agg_expression: str):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, postAggregateExpr=PostAggregateExpression(sql=post_agg_expression))
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_entityRestrictions(self, feature_id: int, entity_ids: List[int]):
        current_feature = self._anaml.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, entityRestrictions=[EntityId(entity) for entity in entity_ids])
        return self._anaml.update_feature(updated_feature)
        
    def update_feature_template(self, feature_id: int, template: str):
        current_feature = self._anam.get_feature_by_id(feature_id)
        updated_feature = replace(current_feature, template=template)
        return self._anaml.update_feature(updated_feature)
        
    ###Creating Feature Sets
    def create_featureset(self,
                          name: str,
                          entity: int,
                          description: str,
                          labels: List[str],
                          attributes: List[dict[str,str]],
                          features: List[int]):
        creation_request = FeatureSetCreationRequest(
                    name=FeatureSetName(value=name),
                    entity=EntityId(entity),
                    description=description,
                    labels=[Label(label) for label in labels],
                    attributes=[Attribute.from_json(attr) for attr in attributes],
                    features=[FeatureId(feature_id) for feature_id in features]
        )
        return self._anaml.create_feature_set(creation_request)
    
    ###Updating Feature Sets
    def update_featureset_name(self, featureset_id: int, name: str):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        updated_featureset = replace(current_featureset, name=FeatureSetName(value=name))
        return self._anaml.update_feature_set(updated_featureset)
        
    def update_featureset_entity(self, featureset_id: int, entity_id: int):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        updated_featureset = replace(current_featureset, entity=EntityId(value=entity_id))
        return self._anaml.update_feature_set(updated_feature)
        
    def update_featureset_description(self, featureset_id: int, description: str):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        updated_featureset = replace(current_featureset, description=description)
        return self._anaml.update_feature_set(updated_featureset)
        
    def update_featureset_labels(self, featureset_id: int, labels: List[str]):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        new_labels = [Label(label) for label in labels]
        updated_featureset = replace(current_featureset, labels=new_labels)
        return self._anaml.update_feature_set(updated_featureset)
    
    def update_featureset_attributes(self, featureset_id: int, attributes: dict[str,str]):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        new_attributes = [Attribute(key=k,value=v) for k,v in attributes.items()]
        updated_featureset = replace(current_featureset, attributes=new_attributes)
        return self._anaml.update_feature_set(updated_featureset)
        
    def update_featureset_features(self, featureset_id: int, features: List[int]):
        current_featureset = self._anaml.get_feature_set_by_id(featureset_id)
        new_features = [FeatureId(value=feature_id) for feature_id in features]
        updated_featureset = replace(current_featureset, labels=new_labels)
        return self._anaml.update_feature_set(updated_featureset)