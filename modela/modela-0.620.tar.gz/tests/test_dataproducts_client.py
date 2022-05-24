import time
import unittest

from modela import *
from modela.ModelaException import *
from modela.common import PriorityLevel
from modela.data.DataProduct import DataProduct
from modela.data.common import DataType
from modela.data.models import DataProductSpec
from modela.server import Modela
from modela.training.common import Imputation, TaskType


class Test_Modela_dataproduct(unittest.TestCase):
    """Tests for `modela.data.DataProduct`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_0_create(self):
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test",
                                              serving_site="serving-site",
                                              lab="lab",
                                              public=True,
                                              task_type=TaskType.Regression,
                                              default_training_workload=Workload("general-small"),
                                              default_serving_workload=Workload("general-small"),
                                              default_bucket="test",
                                              notification_settings=NotificationSettings(NotifierName="test"))
        dataproduct.submit(replace=True)
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test")
        assert dataproduct.spec.ServingSiteName == "serving-site"
        assert dataproduct.spec.LabName == "lab"
        assert dataproduct.spec.Public
        assert dataproduct.spec.TrainingResources == Workload("general-small")
        assert dataproduct.spec.ServingResources == Workload("general-small")
        assert dataproduct.spec.DataLocation.BucketName == "test"
        assert dataproduct.spec.Notification == NotificationSettings(NotifierName="test")
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test",
                                              serving_site=self.modela.ServingSite("default-tenant",
                                                                                   "default-serving-site"),
                                              lab=self.modela.Lab("default-tenant", "default-lab"))
        dataproduct.update()
        dataproduct.sync()
        assert dataproduct.spec.ServingSiteName == "default-serving-site"
        assert dataproduct.spec.LabName == "default-lab"
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test",
                                              permissions=Permissions.create({
                                                  self.modela.Account("default-tenant", "administrator"):
                                                      self.modela.UserRoleClass("default-tenant", "administrator")
                                              }))
        dataproduct.update()
        dataproduct.sync()
        assert dataproduct.spec.Permissions == \
               Permissions(Stakeholders=[Stakeholder(Account='administrator', Roles=[
                   ObjectReference(Namespace='default-tenant', Name='administrator')])])

        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test",
                                              permissions=Permissions.create({
                                                  self.modela.Account("default-tenant", "administrator"): [
                                                      'administrator', 'business']
                                              }))
        dataproduct.update()
        dataproduct.sync()
        assert dataproduct.spec.Permissions == \
               Permissions(Stakeholders=[Stakeholder(Account='administrator', Roles=[
                   ObjectReference(Namespace='default-tenant', Name='administrator'),
                   ObjectReference(Namespace='default-tenant', Name='business')])])

    def test_1_list(self):
        assert len(self.modela.DataProducts.list("default-tenant")) == 2

    def test_2_update(self):
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test")
        assert dataproduct.spec.Priority == PriorityLevel.Medium
        dataproduct.spec.Priority = PriorityLevel.High
        dataproduct.update()
        newdp = self.modela.DataProduct(namespace="default-tenant", name="test")
        assert newdp._object.spec.priority == "high"

    def test_3_get(self):
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test")
        assert type(dataproduct.spec) == DataProductSpec

    def test_4_delete(self):
        dataproduct = self.modela.DataProduct(namespace="default-tenant", name="test")
        dataproduct.delete()
        self.assertRaises(ResourceNotFoundException, self.modela.DataProducts.get, "default-tenant", "test")
