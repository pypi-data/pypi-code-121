from typing import Dict
from localstack.services.cloudformation.deployment_utils import(generate_default_name_without_stack,params_list_to_dict)
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.collections import select_attributes
from localstack.utils.objects import not_none_or
class QLDBLedger(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::QLDB::Ledger"
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("Name")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("qldb")
  ledger_name=self.resolve_refs_recursively(stack_name,self.props.get("Name"),resources)
  result=client.describe_ledger(Name=ledger_name)
  return result
 @staticmethod
 def add_defaults(resource:Dict,stack_name:str):
  props=resource["Properties"]
  if not props.get("Name"):
   props["Name"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 @staticmethod
 def get_deploy_templates():
  def _delete_ledger(resource_id,resources,*args,**kwargs):
   qldb=aws_stack.connect_to_service("qldb")
   props=resources[resource_id]["Properties"]
   ledger_name=props.get("Name")
   qldb.update_ledger(Name=ledger_name,DeletionProtection=False)
   qldb.delete_ledger(Name=ledger_name)
  def _create_params(params,*args,**kwargs):
   result=select_attributes(params,["DeletionProtection","KmsKey","Name","PermissionsMode"])
   if params.get("Tags"):
    tags=params_list_to_dict("Tags")(params)
    result["Tags"]={k:str(not_none_or(v,""))for k,v in tags.items()}
   return result
  return{"create":{"function":"create_ledger","parameters":_create_params},"delete":{"function":_delete_ledger}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
