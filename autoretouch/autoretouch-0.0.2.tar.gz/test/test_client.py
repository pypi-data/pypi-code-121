import time
from typing import Tuple, Dict
from unittest import TestCase
from uuid import UUID
from assertpy import assert_that

from autoretouch.api_client.client import (
    AutoRetouchAPIClient,
)
from autoretouch.api_client.model import Organization, Workflow, WorkflowExecution
from test.api_config_dev import CONFIG_DEV

CREDENTIALS_PATH = "../tmp/credentials.json"
USER_AGENT = "Python-Unit-Test-0.0.1"


class HealthApiIntegrationTest(TestCase):
    def setUp(self) -> None:
        self.client = AutoRetouchAPIClient(api_config=CONFIG_DEV, user_agent="Python-Unit-Test-0.0.1")

    def test_health(self):
        assert_that(self.client.get_api_status()).is_equal_to(200)


class APIClientIntegrationTest(TestCase):
    # Warning! This integration test runs real workflow executions
    # in your autoretouch account which will cost money.

    def setUp(self) -> None:
        self.client = AutoRetouchAPIClient(api_config=CONFIG_DEV, credentials_path=CREDENTIALS_PATH,
                                           user_agent=USER_AGENT)

    def test_upload_image_then_start_workflow_execution(self):
        organization, workflow = self.__get_organization_and_workflow()

        input_image_content_hash = self.client.upload_image("../assets/input_image.jpeg", organization.id)
        self.assertIsNotNone(input_image_content_hash)
        self.assertEqual(
            input_image_content_hash,
            "8bcac2125bd98cd96ba75667b9a8832024970ac05bf4123f864bb63bcfefbcf7",
        )

        workflow_execution_id = (
            self.client.create_workflow_execution_for_image_reference(workflow.id, input_image_content_hash,
                                                                      "input_image.jpeg", "image/jpeg",
                                                                      {"myLabel": "myValue"}, workflow.version,
                                                                      organization.id)
        )
        self.assertIsNotNone(workflow_execution_id)

        self.__assert_execution_has_started(
            organization,
            workflow,
            workflow_execution_id,
            input_image_content_hash,
            "input_image.jpeg",
            {"myLabel": "myValue"},
        )
        self.__assert_workflow_executions_contain_execution(
            organization, workflow, workflow_execution_id
        )

        self.__wait_for_execution_to_complete(organization, workflow_execution_id)
        workflow_execution_completed = self.__get_completed_execution_and_assert_fields(
            organization,
            workflow,
            workflow_execution_id,
            input_image_content_hash,
            "input_image.jpeg",
            {"myLabel": "myValue"},
        )

        self.__download_result_and_assert_equal(
            organization, workflow_execution_completed
        )

    def test_upload_image_from_memory(self):
        organization, _ = self.__get_organization_and_workflow()
        with open("../assets/input_image.jpeg", "rb") as file:
            file_content = file.read()
        input_image_content_hash = self.client.upload_image_from_bytes(image_content=file_content,
                                                                       image_name="input_image.jpeg",
                                                                       mimetype="image/jpeg",
                                                                       organization_id=organization.id)
        self.assertIsNotNone(input_image_content_hash)
        self.assertEqual(
            input_image_content_hash,
            "8bcac2125bd98cd96ba75667b9a8832024970ac05bf4123f864bb63bcfefbcf7",
        )

    def test_upload_image_from_disk(self):
        organization, _ = self.__get_organization_and_workflow()

        input_image_content_hash = self.client.upload_image("../assets/input_image.jpeg", organization.id)
        self.assertIsNotNone(input_image_content_hash)
        self.assertEqual(
            input_image_content_hash,
            "8bcac2125bd98cd96ba75667b9a8832024970ac05bf4123f864bb63bcfefbcf7",
        )

    def test_start_workflow_execution_immediately_and_wait(self):
        organization, workflow = self.__get_organization_and_workflow()

        workflow_execution_id = self.client.create_workflow_execution_for_image_file(workflow.id,
                                                                                     "../assets/input_image.jpeg",
                                                                                     {"myLabel": "myValue"},
                                                                                     workflow.version, organization.id)
        self.assertIsNotNone(workflow_execution_id)

        input_image_content_hash = (
            "8bcac2125bd98cd96ba75667b9a8832024970ac05bf4123f864bb63bcfefbcf7"
        )
        self.__assert_execution_has_started(
            organization,
            workflow,
            workflow_execution_id,
            input_image_content_hash,
            "input_image.jpeg",
            {"myLabel": "myValue"},
        )
        self.__assert_workflow_executions_contain_execution(
            organization, workflow, workflow_execution_id
        )

        result_bytes = self.client.download_result_blocking(workflow_execution_id, organization.id)
        assert_that(len(result_bytes)).is_greater_than(0)
        workflow_execution_completed = self.__get_completed_execution_and_assert_fields(
            organization,
            workflow,
            workflow_execution_id,
            input_image_content_hash,
            "input_image.jpeg",
            {"myLabel": "myValue"},
        )

        self.__download_result_and_assert_equal(
            organization, workflow_execution_completed
        )

    def __get_organization_and_workflow(self) -> Tuple[Organization, Workflow]:
        organizations = self.client.get_organizations()
        organization = organizations[0]
        self.assertIsNotNone(organization)
        workflows = self.client.get_workflows(organization.id)
        workflow = workflows[0]
        self.assertIsNotNone(workflow)
        return organization, workflow

    def __assert_execution_has_started(
            self,
            organization: Organization,
            workflow: Workflow,
            workflow_execution_id: UUID,
            input_image_content_hash: str,
            input_image_name: str,
            labels: Dict[str, str],
    ):
        execution_details = self.client.get_workflow_execution_details(workflow_execution_id, organization.id)
        assert_that(execution_details.workflow).is_equal_to(workflow.id)
        assert_that(execution_details.workflowVersion).is_equal_to(workflow.version)
        assert_that(execution_details.organizationId).is_equal_to(organization.id)
        assert_that(execution_details.inputContentHash).is_equal_to(
            input_image_content_hash
        )
        assert_that(execution_details.inputFileName).is_equal_to(input_image_name)
        assert_that(execution_details.labels).is_equal_to(labels)
        assert_that(["CREATED", "ACTIVE"]).contains(execution_details.status)

    def __assert_workflow_executions_contain_execution(
            self,
            organization: Organization,
            workflow: Workflow,
            workflow_execution_id: UUID,
    ):
        workflow_executions = self.client.get_workflow_executions(workflow.id, organization.id)
        assert_that(len(workflow_executions.entries)).is_greater_than(0)
        assert_that(workflow_executions.total).is_greater_than(0)
        assert_that([entry.id for entry in workflow_executions.entries]).contains(
            workflow_execution_id
        )

    def __wait_for_execution_to_complete(
            self, organization: Organization, workflow_execution_id: UUID
    ):
        timeout = 10
        interval = 1
        seconds_waited = 0
        while seconds_waited < timeout:
            execution_details = self.client.get_workflow_execution_details(workflow_execution_id, organization.id)
            if execution_details.status == "COMPLETED":
                return
            elif (
                    execution_details.status == "FAILED"
                    or execution_details.status == "PAYMENT_REQUIRED"
            ):
                raise RuntimeError(
                    f"Workflow Execution ended in error state {execution_details.status}"
                )
            seconds_waited += interval
            time.sleep(1)
        raise RuntimeError(f"Workflow Execution did not complete in {timeout} seconds")

    def __get_completed_execution_and_assert_fields(
            self,
            organization: Organization,
            workflow: Workflow,
            workflow_execution_id: UUID,
            input_image_content_hash: str,
            input_image_name: str,
            labels: Dict[str, str],
    ) -> WorkflowExecution:
        execution_details_completed = self.client.get_workflow_execution_details(workflow_execution_id, organization.id)
        assert_that(execution_details_completed.workflow).is_equal_to(workflow.id)
        assert_that(execution_details_completed.workflowVersion).is_equal_to(
            workflow.version
        )
        assert_that(execution_details_completed.organizationId).is_equal_to(
            organization.id
        )
        assert_that(execution_details_completed.inputContentHash).is_equal_to(
            input_image_content_hash
        )
        assert_that(execution_details_completed.inputFileName).is_equal_to(
            input_image_name
        )
        assert_that(execution_details_completed.labels).is_equal_to(labels)
        assert_that(execution_details_completed.status).is_equal_to("COMPLETED")
        assert_that(
            execution_details_completed.chargedCredits
        ).is_greater_than_or_equal_to(10)
        assert_that(execution_details_completed.resultContentHash).is_not_empty()
        assert_that(execution_details_completed.resultContentType).is_not_empty()
        assert_that(execution_details_completed.resultFileName).is_not_empty()
        assert_that(execution_details_completed.resultPath).starts_with("/image/")
        return execution_details_completed

    def __download_result_and_assert_equal(
            self, organization: Organization, workflow_execution: WorkflowExecution
    ):
        result_bytes = self.client.download_result_blocking(workflow_execution.id, organization.id)
        assert_that(len(result_bytes)).is_greater_than(0)

        result_bytes_2 = self.client.download_result(workflow_execution.resultPath, organization.id)
        assert_that(len(result_bytes_2)).is_greater_than(0)
        assert_that(result_bytes_2).is_equal_to(result_bytes)

        result_bytes_3 = self.client.download_image(workflow_execution.resultContentHash,
                                                    workflow_execution.resultFileName, organization.id)
        assert_that(len(result_bytes_3)).is_greater_than(0)
        assert_that(result_bytes_3).is_equal_to(result_bytes)
