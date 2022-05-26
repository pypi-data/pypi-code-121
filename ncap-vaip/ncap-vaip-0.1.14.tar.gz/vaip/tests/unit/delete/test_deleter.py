import json
import os
import unittest
from copy import deepcopy

import boto3
import pytest
from moto import mock_s3
from vaip.delete.deleter import *

os.environ['AIP_BUCKET'] = 'test-vaip-bucket'
os.environ['ARCHIVE_BUCKET'] = 'test-archive-bucket'


@pytest.mark.usefixtures("fixtures")
class Handlertest(unittest.TestCase):

    @mock_s3
    def setUp(self):
        self.client = boto3.client('s3', region_name='us-east-1')

        # We expect an AIC to be present for these granule-level updates
        fixture_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "fixtures"
        )
        with open(os.path.join(fixture_path, "C00844.json"), 'rb') as f:
            self.collection_vaip = json.loads(f.read())
        with open(os.path.join(
                fixture_path, "oisst-avhrr-v02r01.20200725.json"), 'rb') as f:
            self.granule_vaip = json.loads(f.read())

        # Get the dataset configuration file, too
        with open(os.path.join(
                fixture_path, "metadata_model.json"), 'rb') as f:
            self.metadata_model = json.loads(f.read())

        self.data_key = "arbitrary/prefix/oisst-avhrr-v02r01.20200422.nc"
        self.aip_full_key = self.data_key.replace('.nc', '.json')

        self.event = {
            "key": self.data_key,
            "s3_event": {
                "time": "2021-04-01T00:00:00",
                "detail": {
                    "responseElements": {
                        "x-amz-delete-marker": "true",
                        "x-amz-version-id": "59rlU2EB8h3gHRCNxA3sYJ.laWrdyeac"
                    }
                }
            },
            "granule": {
                "vaip": {
                    "algorithm": "MD5",
                    "retention": 1337,
                    "poc": "test"
                },
                "size": 1337,
                "checksum": "test23a6498ef444dcde36efb400a3a1",
                "uuid": "test0b4-06f1-4bb9-b7e5-99266f33d639",
                "shortname": "gov.noaa.ncdc:C00844",
                "poc": {
                    "email": "test@noaa.gov"
                }
            },
            "archive_result": {
                "ResponseMetadata": {
                    "HTTPHeaders": {
                        "x-amz-version-id": "561VLdshfnvo9tui4amhzhlPHGz3s5dj"
                    },
                    "RetryAttempts": 0
                },
                "CopyObjectResult": {
                    "LastModified": "2021-03-01"
                },
                "VersionId": "LHEnMpUI1rRPVuAC9RxmHCIbyhTDD_ut"
            }
        }

        # Hard delete is distinguished by an absence of `x-amz-delete-marker`
        self.hard_event = deepcopy(self.event)
        self.hard_event['s3_event']['detail']['responseElements'].pop(
            'x-amz-delete-marker')

    def test_get_shortname_from_config(self):
        this_shortname = get_shortname_from_config(
            self.metadata_model, self.data_key)
        assert this_shortname == "gov.noaa.ncdc:C00844"

    @mock_s3
    def test_remove_entry_from_collection_vaip(self):
        # We assume the AIC was instantiated in the collection state machine
        self.client.create_bucket(Bucket=os.environ['AIP_BUCKET'])
        self.client.put_object(
            Bucket=os.environ['AIP_BUCKET'],
            Key="collections/C00844.json",
            Body=json.dumps(self.collection_vaip)
        )
        uuid = self.granule_vaip['content_information']['content_data_object'][
            'data_object'][0]['UUID']

        latest_aic = remove_entry_from_collection_vaip(
            self.metadata_model,
            self.event,
            self.client,
            uuid
        )
        assert len(latest_aic['preservation_description_information'][
                       'provenance'][
                       'granules']) == 0

    @mock_s3
    def test_add_delete_version_to_gvaip(self):
        # Set up the bucket
        self.client.create_bucket(Bucket=os.environ['AIP_BUCKET'])
        self.client.put_object(
            Bucket=os.environ['AIP_BUCKET'],
            Key=self.aip_full_key,
            Body=json.dumps(self.granule_vaip)
        )
        # Show the soft delete
        new_aiu = add_delete_version_to_gvaip(self.event, self.granule_vaip)
        versions = new_aiu['preservation_description_information'][
            'provenance']['versions']
        assert len(versions) == 2
        assert versions[-1]['action'] == "DELETED (CAN BE RESTORED)"

        # Show the hard delete
        new_aiu = add_delete_version_to_gvaip(
            self.hard_event, self.granule_vaip)
        versions = new_aiu['preservation_description_information'][
            'provenance']['versions']
        assert len(versions) == 3
        assert versions[-1]['action'] == "DELETED (CANNOT BE RESTORED)"

    @mock_s3
    def test_handle_granule_vaip(self):
        # Set up the bucket
        self.client.create_bucket(Bucket=os.environ['AIP_BUCKET'])
        self.client.put_object(
            Bucket=os.environ['AIP_BUCKET'],
            Key=self.aip_full_key,
            Body=json.dumps(self.granule_vaip)
        )

        # Show the soft delete
        new_aiu = handle_granule_vaip(
            self.event, self.client, self.aip_full_key)
        versions = new_aiu['preservation_description_information'][
            'provenance']['versions']
        assert len(versions) == 2
        assert versions[-1]['action'] == "DELETED (CAN BE RESTORED)"

        # Show the hard delete
        new_aiu = handle_granule_vaip(
            self.hard_event, self.client, self.aip_full_key)
        versions = new_aiu['preservation_description_information'][
            'provenance']['versions']
        assert len(versions) == 3
        assert versions[-1]['action'] == "DELETED (CANNOT BE RESTORED)"
