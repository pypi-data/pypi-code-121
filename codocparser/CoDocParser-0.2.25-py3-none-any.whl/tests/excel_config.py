class ExcelConfig:
    one_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Arrival Vessel ": {
                "position_pattern": [r"^Arrival Vessel :"],
                "value_pattern": [
                    r"Arrival\s*Vessel\s*:\s*(?P<Arrival>[^\n]*?)\nB/L\s*No\s*:\s*(?P<BLNO>[\w]*)(?:\s*|)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Arrival Vessel", "key": 0, "action_type": "add", "default_value": ""},
                    {"keyword": "B/L No", "key": 1, "action_type": "add", "default_value": ""}
                ]
            },
            "Port of Discharging": {
                "position_pattern": [r"^Port of Discharging"],
                "value_pattern": [
                    r"[\w\W]*?(?:\w|\n)(?P<ETA>\d{2}\s*[a-zA-Z]{3,}\s*\d{2}\s*\d{2}\:\d{2}\([a-zA-Z]{2,}\))(?:\s*|\w|\n).*(?P<Available>\d{2}\s*[a-zA-Z]{3,}\s*\d{2}\s*\d{2}\:\d{2})"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ETA", "key": "ETA", "action_type": "add", "default_value": ""},
                    {"keyword": "Available Date", "key": "Available", "action_type": "add", "default_value": ""}
                ]
            },
            "Est. General Order": {
                "position_pattern": [r"^Est. General Order"],
                "value_pattern": [
                    r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Est. General Order"}
                ]
            },
            "CONTAINER#": {
                "position_pattern": [r"^CONTAINER#"],
                "value_pattern": [
                    r"([a-zA-Z]{4,}\d{7,})"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "CONTAINER#"}
                ]
            },
        }
    }

    hpl_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Ocean Vessel": {
                "position_pattern": [r"^Ocean Vessel:"],
                "value_pattern": [
                    r"(.*)"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Ocean Vessel"}
                ]
            },
            "Voyage No.": {
                "position_pattern": [r"^Voyage No"],
                "value_pattern": [
                    r"^Voyage No\.\s*:\s*(.*)(?:\s*|)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Voyage No"}
                ]
            },
            "Due to arrive at Terminal:": {
                "position_pattern": [r"^Due\s*to\s*arrive\s*at\s*Terminal\s*"],
                "value_pattern": [
                    r"^Due\s*to\s*arrive\s*at\s*Terminal\s*:\s*\n(.*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Due to arrive at Terminal"}
                ]
            },
            "HBL NO": {
                "position_pattern": [r"[\w\W]*?HBL\s*NO\s*:\s*"],
                "value_pattern": [
                    r"[\w\W]*?HBL\s*NO\s*:\s*(\w*)(?:\n|)"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "HBL NO"}
                ]
            },
        }
    }

    zim_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Vessel/Voyage": {
                "position_pattern": [r"^Vessel/Voyage:"],
                "value_pattern": [
                    r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Vessel/Voyage"}
                ]
            },
            "ETA": {
                "position_pattern": [r"^ETA:"],
                "value_pattern": [
                    r"\n"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "split",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ETA"}
                ]
            },
            "Date of Loading at": {
                "position_pattern": [r"^Date of Loading at"],
                "value_pattern": [
                    r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Date of Loading at Original Port of Loading"}
                ]
            },
            "Bill of Lading": {
                "position_pattern": [r"^Bill of Lading"],
                "value_pattern": [
                    r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Bill of Lading"}
                ]
            },
            "Container": {
                "position_pattern": [r"^Container"],
                "value_pattern": [
                    r"(.*)\n"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Container"}
                ]
            },
        }
    }

    cmacgm_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "VESSEL": {
                "position_pattern": [r"^VESSEL:"],
                "value_pattern": [
                    r"\n"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "split",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "VESSEL"}
                ]
            },
            "VOYAGE": {
                "position_pattern": [r"^\s*VOYAGE\s*:"],
                "value_pattern": [r"^VOYAGE\s*:\s*(?P<VOYAGE>[\w\W]*)$"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "VOYAGE", "key": "VOYAGE", "action_type": "add", "default_value": ""}
                ]
            },
            "LOAD PICKUP POOL ADDRESS": {
                "position_pattern": [r"^LOAD PICKUP POOL ADDRESS:"],
                "value_pattern": [r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "LOAD PICKUP POOL ADDRESS"}
                ]
            },
            "EMPTY RETURN DEPOT": {
                "position_pattern": [r"^EMPTY RETURN DEPOT:"],
                "value_pattern": [r"(.*)"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "EMPTY RETURN DEPOT"}
                ]
            },
            "B/L": {
                "position_pattern": [r"^SCAC     B/L #"],
                "value_pattern": [r".*\s+(\w+)"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "B/L"}
                ]
            },
            "CONTAINER  #": {
                "position_pattern": [r"^CONTAINER  #"],
                "value_pattern": [r"^([a-zA-Z]{4,}\d{4,})"],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "CONTAINER"}
                ]
            },
        }
    }

    matson_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Vessel/Voyage": {
                "position_pattern": [r"^Vessel/Voyage:"],
                "value_pattern": [
                    r"\n"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "split",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Vessel/Voyage"}
                ]
            },
            "ETA into: LONG BEACH": {
                "position_pattern": [r"^ETA into: LONG BEACH"],
                "value_pattern": [r"\n"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "split",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ETA into: LONG BEACH"}
                ]
            },
            "Bill of Lading Number": {
                "position_pattern": [r"^Bill of Lading Number:"],
                "value_pattern": [r"^Bill\s*of\s*Lading\s*Number:\s*([a-zA-Z]{4,}\d{4,})\s*Service"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Bill of Lading Number"}
                ]
            }
        },
        "table": {
            "bill": {
                "position_pattern": [r"^Container#"],
                "separator": "\n",
                "find_mode": "v",
                "separator_mode": "regex",
                "column": ["CONTAINER  #"],
                "behaviors": [
                    {
                        "over_action": "row",
                        "value_pattern": [
                            r"(?P<col_1>[a-zA-Z]{4,}\d{4,}\s*\d+)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(Total Piece Count)"]
                    }
                ]
            }
        }
    }

    cosco_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "B/L Number": {
                "position_pattern": [r"^Type of B/L"],
                "value_pattern": [
                    r"[\w\W]*B/L Number\s*:\s*(?P<Number>(\w+)|())(?:\n|)B/L Vessel/Voyage:(?:\n|)(?P<Vessel>[^\n]*)(?:\n|)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "B/L Number"},
                    {"keyword": "B/L Vessel/Voyage"}
                ]
            },
            "ESTIMATE ARRIVAL AT POD": {
                "position_pattern": [r"[\w\W]*ESTIMATE ARRIVAL AT POD:", r"[\w\W]*?EST CARGO AVAILABLE AT\s*:"],
                "value_pattern": [r"[\w\W]*ESTIMATE ARRIVAL AT POD\s*:\s*(?P<pod_country>\w+)",
                                  r"(?P<POD_time>([\w\W]*?)|(\s|\n|))EST CARGO AVAILABLE AT\s*:\s*(?P<AT_country>[^\n]*?)\n(?P<AT_time>[\w\W]*)(?:\n||$)"],
                "repeat_count": 2,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ESTIMATE ARRIVAL AT POD Country", "key": "pod_country"},
                    {"keyword": "ESTIMATE ARRIVAL AT POD Time", "key": "POD_time"},
                    {"keyword": "ESTIMATE ARRIVAL AT Country", "key": "AT_country"},
                    {"keyword": "ESTIMATE ARRIVAL AT Time", "key": "AT_time"},
                ]
            }
        },
        "table": {
            "bill": {
                "position_pattern": [r"^CONTAINER NO\.\n\/ SEAL NO\."],
                "separator": "\n",
                "repl_separator": " ",
                "find_mode": "v",
                "separator_mode": "regex",
                "column": ["CONTAINER NO./ SEAL NO."],
                "behaviors": [
                    {
                        "over_action": "row",
                        "value_format": r"([a-zA-Z]{4,}\d{7,}\s*\d{8,})",
                        "value_pattern": [
                            r"(?P<col_1>^[a-zA-Z]{4,}\d{7,}[\w\W]*?\d{7,}$)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(Remarks)"]
                    }
                ]
            }
        },
        "data_type_format": {
                     "ESTIMATE ARRIVAL AT POD Country": {"table": "", "data_type": "time", "format": "%A, %d %b, %Y %I:%M %p", "filter": "(\\n)"},
                     "ESTIMATE ARRIVAL AT POD Time": {"table": "", "data_type": "time", "format": "%A, %d %b, %Y %I:%M %p", "filter": "(\\n)"},
        }
    }

    evergreen_config = {
        "id": "group_A",
        "name": "多页模板",
        "multi_page": 1,
        "page_pattern": [r"^(ITY OCEAN INTERNATIONAL INC\.,[\w\W]*?CARGO PICK UP LOCATION)(?:\n|$|)"],
        "kv": {
            "ARRIVING VESSEL": {
                "position_pattern": [r"^ARRIVING VESSEL"],
                "value_pattern": [
                    r"ARRIVING VESSEL / VOYAGE NO\.\s*([\w\W]*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ARRIVING VESSEL / VOYAGE NO."},
                ]
            },
            "VESSEL ETA": {
                "position_pattern": [r"^VESSEL ETA"],
                "value_pattern": [r"^VESSEL ETA\.\s*([\w\W]*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "VESSEL ETA"}
                ]
            },
            "CONTAINER NUMBER": {
                "position_pattern": [r"^CONTAINER NUMBER"],
                "value_pattern": [r"CONTAINER NUMBER / CARGO DESCRIPTION\s*([a-zA-Z]{4,}\d{7,}\s*[a-zA-Z]{4,}\d{4,})\s{1,}"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "CONTAINER NUMBER / CARGO DESCRIPTION"}
                ]
            },
            "MASTER’s House B/L No.": {
                "position_pattern": [r"^MASTER’s House B/L No"],
                "value_pattern": [r"MASTER’s House B/L No\.\s*:(?P<no>[\w\W]*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "MASTER’s House B/L No"}
                ]
            }
        }

    }

    smline_config1 = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Arrival Vessel": {
                "position_pattern": [r"^Arrival Vessel"],
                "value_pattern": [
                    r"Arrival Vessel\s*:\s*(\w*\s*\w*\s*\d+\s+\w+)\s{4,}[\w\W]*?\nB/L No\s*:\s*([\w]*?)\s{1,}"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Arrival Vessel"},
                    {"keyword": "B/L No"}
                ]
            },
            "ETA": {
                "position_pattern": [r"^ETA/ETB"],
                "value_pattern": [
                    r"[\w\W]*?(\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,}\([a-zA-Z]{2}\))[\w\W]*?(\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,})[\w\W]*?([a-zA-Z]{3,}\s*\d+\s*[a-zA-Z]{3,})"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ETA"},
                    {"keyword": "vailable Date"},
                    {"keyword": "Port Free Time"},
                ]
            }
        },
        "table": {
            "bill": {
                "position_pattern": [r"^CONTAINER#"],
                "separator": "\n",
                "find_mode": "h",
                "separator_mode": "regex",
                "column": ["CHG", "RATED AS", "RATE", "PE", "COLLECT"],
                "behaviors": [
                    {
                        "over_action": "row",
                        "loop": 1,
                        "value_pattern": [
                            r"(?P<col_1>[a-zA-Z]*\s{1,}[a-zA-Z]*)\s{1,}(?P<col_2>\d{1,}\.\d{1,})\s{1,}(?P<col_3>\d{1,}\.\d{1,})\s*(?P<col_4>\w{1,})\s{1,}(?P<col_5>\d{1,}\.\d{1,})(?:\n|$)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(DESTINATION)"]
                    }
                ]
            }
        }
    }

    oocl_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "B/L Number": {
                "position_pattern": [r"^Type of B/L"],
                "value_pattern": [
                    r"[\w\W]*B/L Number:\s*([a-zA-Z]+\d+)\s*B/L Vessel/Voyage\s*:\s*(\w+\s+\w+\s+\w+)(?:\n|\s|)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Vessel/Voyage"},
                    {"keyword": "B/L Number"}

                ]
            },
            "ESTIMATE ARRIVAL AT POD": {
                "position_pattern": [r"^ESTIMATE ARRIVAL AT POD"],
                "value_pattern": [r"ESTIMATE ARRIVAL AT POD:\s*([^\n]*？)\n([\w\W]*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ESTIMATE ARRIVAL AT POD1"},
                    {"keyword": "ESTIMATE ARRIVAL AT POD2", "key": 1},
                ]
            },
            "EST CARGO AVAILABLE AT": {
                "position_pattern": [r"^EST CARGO AVAILABLE AT"],
                "value_pattern": [r"^EST CARGO AVAILABLE AT:\s*([^\n]*？)\n([\w\W]*)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "EST CARGO AVAILABLE AT1"},
                    {"keyword": "EST CARGO AVAILABLE AT2", "key": 1}
                ]
            }
        },
        "table": {
            "bill": {
                "position_pattern": [r"^CONTAINER NO\.\n\/ SEAL NO\."],
                "separator": "\n",
                "repl_separator": " ",
                "find_mode": "v",
                "separator_mode": "regex",
                "column": ["CONTAINER NO./ SEAL NO."],
                "behaviors": [
                    {
                        "over_action": "row",
                        "value_format": r"([a-zA-Z]{4,}\d{7,}\s*\d{8,})",
                        "value_pattern": [
                            r"(?P<col_1>^[a-zA-Z]{4,}\d{7,}[\w\W]*?\d{7,}$)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(Remarks)"]
                    }
                ]
            }
        }
    }

    smline_config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Arrival Vessel": {
                "position_pattern": [r"^Arrival Vessel"],
                "value_pattern": [
                    r"Arrival Vessel\s*:\s*(?P<Vessel>\w*\s*\w*\s*\d+\s+\w+)\s{4,}[\w\W]*?\nB/L No\s*:\s*(?P<BillOfLadingsId>[\w]*?)\s{1,}"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "VesselName", "key": "Vessel", "pattern_list": [r"(?P<value>[\w\W]*)\s+?(.{4,})$"]},
                    {"keyword": "VoyageNo", "key": "Vessel", "pattern_list": [r"([\w\W]*)\s+?(?P<value>.{4,})$"]},
                    {"keyword": "BillOfLadingsId", "key": "BillOfLadingsId"}
                ]
            },
            "Port of Discharging": {
                "position_pattern": [r"^Port of Discharging"],
                "value_pattern": [
                    r"\s*Port\s*of\s*Discharging\s(?:\:|\s*)(.*?)(?:\(|$)"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "DestinationPortName"}
                ]
            },
            "ETA": {
                "position_pattern": [r"^ETA/ETB"],
                "value_pattern": [
                    r"\s*(?P<EstimatedArrivalDate>\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,})\s*/\s*\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,}\s*(?P<DeliveryPlaceName>[a-zA-Z0-9, ]*)(?:\r\n|\n)(?P<DeliveryEstimatedArrivalDate>\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,})"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "EstimatedArrivalDate", "key": "EstimatedArrivalDate"},
                    {"keyword": "DeliveryPlaceName", "key": "DeliveryPlaceName"},
                    {"keyword": "DeliveryEstimatedArrivalDate", "key": "DeliveryEstimatedArrivalDate"},
                ]
            }
        },
        "table": {
            "containers": {
                "position_pattern": [r"^CONTAINER#"],
                "separator": "\n",
                "find_mode": "h",
                "separator_mode": "regex",
                "column": ["ContainerNo"],
                "behaviors": [
                    {
                        "over_action": "row",
                        "loop": 1,
                        "value_pattern": [
                            r"(?P<col_1>[a-zA-Z]{4,}\d{7,})\s*.*?(?:\r\n|\n|$)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(DESTINATION)"]
                    }
                ]
            }
        },
        "data_type_format": {
            "EstimatedArrivalDate": {"data_type": "time", "format": "%d %b %y %H:%M", "filter": "(\\(CY\\))"},
            "VoyageNo": {"data_type": "str", "filter": " "},
            "DeliveryEstimatedArrivalDate": {"data_type": "time", "format": "%d %b %y %H:%M", "filter": "(\\n)"}
        },
        "address_repair": {
            "db": {
                "pub": {"user": "co", "pwd": "Co&23@2332$22", "server": "db.dev.com:1433",
                        "database": "CO_PUB"}
            },
            "repairs": [
                {"key": "DestinationPortName", "db_key": "pub",
                 "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                 "column": [0, 1, 2, 3], "value": 4, "mapping": "DestinationPortId",
                 "old_val_handle": "empty"},
                {"key": "DeliveryPlaceName", "db_key": "pub",
                 "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                 "column": [0, 1, 2, 3], "value": 4, "mapping": "DeliveryPlaceId",
                 "old_val_handle": "empty"}
            ]

        }
    }

    @staticmethod
    def get_config(name):
        try:
            print("%s_config" % name)
            return getattr(ExcelConfig, "%s_config" % name)
        except:
            return None
