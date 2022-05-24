#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from enum import Enum

from psym.common.data_class import RecommendationSources, recommendations



class Entity(Enum):
    Location = "Location"
    LocationType = "LocationType"
    Equipment = "Equipment"
    EquipmentType = "EquipmentType"
    EquipmentPort = "EquipmentPort"
    EquipmentPortType = "EquipmentPortType"
    Link = "Link"
    Service = "Service"
    ServiceType = "ServiceType"
    ServiceEndpoint = "ServiceEndpoint"
    ServiceEndpointDefinition = "ServiceEndpointDefinition"
    SiteSurvey = "SiteSurvey"
    Customer = "Customer"
    Document = "Document"
    PropertyType = "PropertyType"
    Property = "Property"
    DocumentCategory = "DocumentCategory"
    User = "User"
    recommendations="recommendations"
    RecomendationSources="RecomendationSources"
    RecomendationsCategory="RecomendationsCategory"
    WorkOrder = "WorkOrder"
    WorkOrderType = "WorkOrderType"
    ProjectType = "ProjectType"
    Project = "Project"
    KqiCategory = "KqiCategory"
    KqiPerspective = "KqiPerspective"
    KqiTemporalFrecuency = "KqiTemporalFrecuency"
    KqiSource = "KqiSource"
    Kqi = "Kqi"
    KpiCategory = "KpiCategory"
    domain = "domain"
    tech = "tech"
    vendor = "vendor"
    NetworkType = "NetworkType"
    CounterFamiliy = "CounterFamiliy"
    Kpi = "Kpi"
    formula = "formula"
    counter = "counter"
    counterFormula = "counterFormula"
    ruleType= "ruleType"
    eventSeverity = "eventSeverity"
    comparator = "comparator"
    threshold = "threshold"
    rule= "rule"
    alarmStatus="alarmStatus"
    organization="organization"
    ruleLimit="ruleLimit"

