import json
import os
import pytest
from docparser.doc_parser_factory import DocParserFactory
from tests.excel_config import ExcelConfig as Config

doc1_config = {}
test_config = {
    "id": "ZIM",
    "name": "ZIM config",
    "kv": {
        "Vessel/Voyage": {
            "position_pattern": [
                "^Vessel/Voyage:"
            ],
            "value_pattern": [
                "(?P<Vessel>([a-zA-Z]*\\s*)*[\\w\\W]*?(?:\\r\\n|\\n|$))",
                "\\s*(?P<Vessel>.*?)(?:\\n|\\r\\n)(?P<ETA>\\d{1,}/\\d{1,}/\\d{2,})",

            ],
            "repeat_count": 1,
            "find_mode": "h",
            "separator_mode": "regex",
            "is_split_cell": 0,
            "split_pattern": [
                ""
            ],
            "action": [
                {
                    "keyword": "VesselName",
                    "key": "Vessel",
                    "pattern_list": [
                        "(?P<value>[\\w\\W]*)\\s+?(.{7,})$"
                    ]
                },
                {
                    "keyword": "VoyageNo",
                    "key": "Vessel",
                    "pattern_list": [
                        "([\\w\\W]*)\\s+?(?P<value>.{7,})$"
                    ]
                },
                {
                    "keyword": "EstimatedArrivalDate",
                    "key": "ETA"
                }
            ]
        },
        "Bill of Lading": {
            "position_pattern": [
                "^Exchange Method", "Bill of Lading"
            ],
            "value_pattern": [
                "\\s*(([\\w\\s]*[\\r\\n])|())(?P<billoflading>.*)(?:\\s|$)",
                "(?P<billoflading>[a-zA-Z]{4,}\\d{4,})"
            ],
            "repeat_count": 1,
            "find_mode": "h",
            "separator_mode": "regex",
            "is_split_cell": 0,
            "split_pattern": [
                ""
            ],
            "action": [
                {
                    "keyword": "BillOfLadingsId",
                    "key": "billoflading"
                }
            ]
        },
        "Destination": {
            "position_pattern": [
                "^Port of Loading"
            ],
            "value_pattern": [
                "[\\w\\W]*?Port of Destination\\s*:\\s*(?P<PortofDestination>[^\\n]*?)(?:\\r\\n|\\n|$)Manifest\\s*Destination\\s*:\\s*(?P<ManifestDestination>[^\\n]*?)(?:\\r\\n|\\n|$)"
            ],
            "repeat_count": 1,
            "find_mode": "default",
            "separator_mode": "regex",
            "is_split_cell": 0,
            "split_pattern": [
                ""
            ],
            "action": [
                {
                    "keyword": "DestinationPortName",
                    "key": "PortofDestination"
                },
                {
                    "keyword": "DeliveryPlaceName",
                    "key": "ManifestDestination"
                }
            ]
        },
        "ETA": {
            "position_pattern": [
                "^ETA:"
            ],
            "value_pattern": [
                "(?P<ETA>\\d{1,}/\\d{1,}/\\d{2,})"
            ],
            "repeat_count": 1,
            "find_mode": "h",
            "separator_mode": "regex",
            "is_split_cell": 0,
            "split_pattern": [
                ""
            ],
            "action": [
                {
                    "keyword": "EstimatedArrivalDate",
                    "key": "ETA",
                    "action_type": "append"
                }
            ]
        }
    },
    "table": {
        "containers": {
            "position_pattern": [
                "^Port of Loading",
                "^Container"
            ],
            "separator": "     ",
            "find_mode": "h",
            "separator_mode": "regex",
            "column": [
                "ContainerNo",
                "ContainerSize"
            ],
            "behaviors": [
                {
                    "over_action": "row",
                    "value_pattern": [
                        "\\s*(?P<col_1>[a-zA-Z]{4,}\\d{7,})\\s{4,}(?P<col_2>[a-zA-Z]{2,}\\d{2,})\\s{4,}[\\w\\W]*?$"
                    ],
                    "action": []
                }
            ]
        }
    },
    "data_type_format": {
        "VoyageNo": {
            "data_type": "str",
            "filter": "([/\\s])"
        },
        "EstimatedArrivalDate": {
            "data_type": "time",
            "format": "%m/%d/%Y",
            "filter": ""
        }
    },
    "address_repair": {
        "db": {
            "pub": {
                "user": "co",
                "pwd": "Co&23@2332$22",
                "server": "db.dev.com:1433",
                "database": "CO_PUB"
            }
        },
        "repairs": [
            {
                "key": "DestinationPortName",
                "db_key": "pub",
                "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                "column": [
                    0,
                    1,
                    2,
                    3
                ],
                "value": 4,
                "mapping": "DestinationPortId",
                "old_val_handle": "empty"
            },
            {
                "key": "DeliveryPlaceName",
                "db_key": "pub",
                "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                "column": [
                    0,
                    1,
                    2,
                    3
                ],
                "value": 4,
                "mapping": "DeliveryPlaceId",
                "old_val_handle": "empty"
            }
        ]
    }
}


class TestExcelDocumentParser:

    def test_excel_file_parse(self):
        """
        单文件测试
        :return:
        """
        name = "cma".upper()

        doc1_config["id"] = f"AN_{name}_"

        test_config["id"] = name
        test_config["name"] = f"{name} config"
        doc1_config["parse"] = test_config
        # print(test_config)
        print(json.dumps(test_config))
        factory = DocParserFactory.create("excel2",
                                          r"C:\Users\APing\Desktop\temp\c244c6c2-3670-6559-e7bd-3a031a9477f5.xlsx",
                                          test_config)
        result, errors = factory.parse()

        print(result, errors)

    # def test_excel_dir_parse(self):
    #     """
    #     测试文件夹下的拥有对应名称配置的excel文件
    #     :return:
    #     """
    #     path = os.getcwd() + "\\files"
    #     dirs = os.listdir(path)
    #     for file in dirs:
    #         name = file.split(".")[0]
    #         if ".xlsx" in file:
    #             _config = Config.get_config(name.lower())
    #             if _config is None:
    #                 continue
    #             factory = DocParserFactory.create("excel2", "%s\\%s.xlsx" % (path, name.lower()), _config)
    #             result, errors = factory.parse()
    #             print("=========================", file, "========================")
    #             print(_config)
    #             print(path + file)
    #             print(result)
    #             print(errors)
    #             print("------------------------------------------------------------")
    #             print("\r\n\r\n")


if __name__ == '__main__':
    pytest.main("-q --html=report.html")
