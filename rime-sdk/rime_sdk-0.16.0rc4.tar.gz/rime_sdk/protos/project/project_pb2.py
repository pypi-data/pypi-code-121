# autogenerated
# mypy: ignore-errors
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/project/project.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from rime_sdk.protos.results_upload import results_upload_pb2 as protos_dot_results__upload_dot_results__upload__pb2
from rime_sdk.protos.google.api import annotations_pb2 as protos_dot_google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cprotos/project/project.proto\x12\x04rime\x1a\x1fgoogle/protobuf/timestamp.proto\x1a*protos/results_upload/results_upload.proto\x1a#protos/google/api/annotations.proto\"\x16\n\x07SafeURL\x12\x0b\n\x03url\x18\x01 \x01(\t\"9\n\x14\x43reateProjectRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"7\n\x15\x43reateProjectResponse\x12\x1e\n\x07project\x18\x01 \x01(\x0b\x32\r.rime.Project\"\'\n\x11GetProjectRequest\x12\x12\n\nproject_id\x18\x01 \x01(\t\"=\n\x12GetProjectResponse\x12\'\n\x07project\x18\x01 \x01(\x0b\x32\x16.rime.AnnotatedProject\"\\\n\x14UpdateProjectRequest\x12\x1e\n\x07project\x18\x01 \x01(\x0b\x32\r.rime.Project\x12$\n\x04mask\x18\x02 \x01(\x0b\x32\x16.rime.ProjectWriteMask\"7\n\x15UpdateProjectResponse\x12\x1e\n\x07project\x18\x01 \x01(\x0b\x32\r.rime.Project\"*\n\x14\x44\x65leteProjectRequest\x12\x12\n\nproject_id\x18\x01 \x01(\t\"\x17\n\x15\x44\x65leteProjectResponse\"<\n\x13ListProjectsRequest\x12\x12\n\npage_token\x18\x01 \x01(\t\x12\x11\n\tpage_size\x18\x02 \x01(\x03\"Y\n\x14ListProjectsResponse\x12(\n\x08projects\x18\x01 \x03(\x0b\x32\x16.rime.AnnotatedProject\x12\x17\n\x0fnext_page_token\x18\x02 \x01(\t\"<\n&ServeAvailableColumnsForProjectRequest\x12\x12\n\nproject_id\x18\x01 \x01(\t\"X\n\'ServeAvailableColumnsForProjectResponse\x12\x12\n\nproject_id\x18\x01 \x01(\t\x12\x19\n\x11\x61vailable_columns\x18\x02 \x03(\t\"\xb8\x01\n\x07Project\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x30\n\x0c\x63reated_time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\x10selected_columns\x18\x05 \x03(\x0b\x32\x14.rime.SelectedColumn\x12\x1c\n\x14\x66irewall_test_run_id\x18\x06 \x01(\t\"5\n\x0eSelectedColumn\x12\x13\n\x0b\x63olumn_name\x18\x01 \x01(\t\x12\x0e\n\x06pinned\x18\x02 \x01(\x08\"\xe1\x01\n\x10\x41nnotatedProject\x12\x1e\n\x07project\x18\x01 \x01(\x0b\x32\r.rime.Project\x12\x36\n\x12last_test_run_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x16\n\x0etest_run_count\x18\x03 \x01(\x04\x12\x39\n\x16test_run_count_mapping\x18\x04 \x03(\x0b\x32\x19.rime.TestRunCountMapping\x12\"\n\x0bweb_app_url\x18\x05 \x01(\x0b\x32\r.rime.SafeURL\"P\n\x13TestRunCountMapping\x12!\n\ttest_type\x18\x01 \x01(\x0e\x32\x0e.rime.TestType\x12\x16\n\x0etest_run_count\x18\x02 \x01(\x04\"m\n\x10ProjectWriteMask\x12\x0c\n\x04name\x18\x02 \x01(\x08\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\x08\x12\x18\n\x10selected_columns\x18\x05 \x01(\x08\x12\x1c\n\x14\x66irewall_test_run_id\x18\x06 \x01(\x08\x32\xc8\x04\n\x0eProjectManager\x12\x61\n\rCreateProject\x12\x1a.rime.CreateProjectRequest\x1a\x1b.rime.CreateProjectResponse\"\x17\x82\xd3\xe4\x93\x02\x11\"\x0c/v1/projects:\x01*\x12\x62\n\nGetProject\x12\x17.rime.GetProjectRequest\x1a\x18.rime.GetProjectResponse\"!\x82\xd3\xe4\x93\x02\x1b\x12\x19/v1/projects/{project_id}\x12H\n\rUpdateProject\x12\x1a.rime.UpdateProjectRequest\x1a\x1b.rime.UpdateProjectResponse\x12H\n\rDeleteProject\x12\x1a.rime.DeleteProjectRequest\x1a\x1b.rime.DeleteProjectResponse\x12[\n\x0cListProjects\x12\x19.rime.ListProjectsRequest\x1a\x1a.rime.ListProjectsResponse\"\x14\x82\xd3\xe4\x93\x02\x0e\x12\x0c/v1/projects\x12~\n\x1fServeAvailableColumnsForProject\x12,.rime.ServeAvailableColumnsForProjectRequest\x1a-.rime.ServeAvailableColumnsForProjectResponseB\x18Z\x16ri/_gen/protos/projectb\x06proto3')



_SAFEURL = DESCRIPTOR.message_types_by_name['SafeURL']
_CREATEPROJECTREQUEST = DESCRIPTOR.message_types_by_name['CreateProjectRequest']
_CREATEPROJECTRESPONSE = DESCRIPTOR.message_types_by_name['CreateProjectResponse']
_GETPROJECTREQUEST = DESCRIPTOR.message_types_by_name['GetProjectRequest']
_GETPROJECTRESPONSE = DESCRIPTOR.message_types_by_name['GetProjectResponse']
_UPDATEPROJECTREQUEST = DESCRIPTOR.message_types_by_name['UpdateProjectRequest']
_UPDATEPROJECTRESPONSE = DESCRIPTOR.message_types_by_name['UpdateProjectResponse']
_DELETEPROJECTREQUEST = DESCRIPTOR.message_types_by_name['DeleteProjectRequest']
_DELETEPROJECTRESPONSE = DESCRIPTOR.message_types_by_name['DeleteProjectResponse']
_LISTPROJECTSREQUEST = DESCRIPTOR.message_types_by_name['ListProjectsRequest']
_LISTPROJECTSRESPONSE = DESCRIPTOR.message_types_by_name['ListProjectsResponse']
_SERVEAVAILABLECOLUMNSFORPROJECTREQUEST = DESCRIPTOR.message_types_by_name['ServeAvailableColumnsForProjectRequest']
_SERVEAVAILABLECOLUMNSFORPROJECTRESPONSE = DESCRIPTOR.message_types_by_name['ServeAvailableColumnsForProjectResponse']
_PROJECT = DESCRIPTOR.message_types_by_name['Project']
_SELECTEDCOLUMN = DESCRIPTOR.message_types_by_name['SelectedColumn']
_ANNOTATEDPROJECT = DESCRIPTOR.message_types_by_name['AnnotatedProject']
_TESTRUNCOUNTMAPPING = DESCRIPTOR.message_types_by_name['TestRunCountMapping']
_PROJECTWRITEMASK = DESCRIPTOR.message_types_by_name['ProjectWriteMask']
SafeURL = _reflection.GeneratedProtocolMessageType('SafeURL', (_message.Message,), {
  'DESCRIPTOR' : _SAFEURL,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.SafeURL)
  })
_sym_db.RegisterMessage(SafeURL)

CreateProjectRequest = _reflection.GeneratedProtocolMessageType('CreateProjectRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEPROJECTREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.CreateProjectRequest)
  })
_sym_db.RegisterMessage(CreateProjectRequest)

CreateProjectResponse = _reflection.GeneratedProtocolMessageType('CreateProjectResponse', (_message.Message,), {
  'DESCRIPTOR' : _CREATEPROJECTRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.CreateProjectResponse)
  })
_sym_db.RegisterMessage(CreateProjectResponse)

GetProjectRequest = _reflection.GeneratedProtocolMessageType('GetProjectRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETPROJECTREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.GetProjectRequest)
  })
_sym_db.RegisterMessage(GetProjectRequest)

GetProjectResponse = _reflection.GeneratedProtocolMessageType('GetProjectResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETPROJECTRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.GetProjectResponse)
  })
_sym_db.RegisterMessage(GetProjectResponse)

UpdateProjectRequest = _reflection.GeneratedProtocolMessageType('UpdateProjectRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEPROJECTREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.UpdateProjectRequest)
  })
_sym_db.RegisterMessage(UpdateProjectRequest)

UpdateProjectResponse = _reflection.GeneratedProtocolMessageType('UpdateProjectResponse', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEPROJECTRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.UpdateProjectResponse)
  })
_sym_db.RegisterMessage(UpdateProjectResponse)

DeleteProjectRequest = _reflection.GeneratedProtocolMessageType('DeleteProjectRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELETEPROJECTREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.DeleteProjectRequest)
  })
_sym_db.RegisterMessage(DeleteProjectRequest)

DeleteProjectResponse = _reflection.GeneratedProtocolMessageType('DeleteProjectResponse', (_message.Message,), {
  'DESCRIPTOR' : _DELETEPROJECTRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.DeleteProjectResponse)
  })
_sym_db.RegisterMessage(DeleteProjectResponse)

ListProjectsRequest = _reflection.GeneratedProtocolMessageType('ListProjectsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTPROJECTSREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.ListProjectsRequest)
  })
_sym_db.RegisterMessage(ListProjectsRequest)

ListProjectsResponse = _reflection.GeneratedProtocolMessageType('ListProjectsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTPROJECTSRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.ListProjectsResponse)
  })
_sym_db.RegisterMessage(ListProjectsResponse)

ServeAvailableColumnsForProjectRequest = _reflection.GeneratedProtocolMessageType('ServeAvailableColumnsForProjectRequest', (_message.Message,), {
  'DESCRIPTOR' : _SERVEAVAILABLECOLUMNSFORPROJECTREQUEST,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.ServeAvailableColumnsForProjectRequest)
  })
_sym_db.RegisterMessage(ServeAvailableColumnsForProjectRequest)

ServeAvailableColumnsForProjectResponse = _reflection.GeneratedProtocolMessageType('ServeAvailableColumnsForProjectResponse', (_message.Message,), {
  'DESCRIPTOR' : _SERVEAVAILABLECOLUMNSFORPROJECTRESPONSE,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.ServeAvailableColumnsForProjectResponse)
  })
_sym_db.RegisterMessage(ServeAvailableColumnsForProjectResponse)

Project = _reflection.GeneratedProtocolMessageType('Project', (_message.Message,), {
  'DESCRIPTOR' : _PROJECT,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.Project)
  })
_sym_db.RegisterMessage(Project)

SelectedColumn = _reflection.GeneratedProtocolMessageType('SelectedColumn', (_message.Message,), {
  'DESCRIPTOR' : _SELECTEDCOLUMN,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.SelectedColumn)
  })
_sym_db.RegisterMessage(SelectedColumn)

AnnotatedProject = _reflection.GeneratedProtocolMessageType('AnnotatedProject', (_message.Message,), {
  'DESCRIPTOR' : _ANNOTATEDPROJECT,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.AnnotatedProject)
  })
_sym_db.RegisterMessage(AnnotatedProject)

TestRunCountMapping = _reflection.GeneratedProtocolMessageType('TestRunCountMapping', (_message.Message,), {
  'DESCRIPTOR' : _TESTRUNCOUNTMAPPING,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.TestRunCountMapping)
  })
_sym_db.RegisterMessage(TestRunCountMapping)

ProjectWriteMask = _reflection.GeneratedProtocolMessageType('ProjectWriteMask', (_message.Message,), {
  'DESCRIPTOR' : _PROJECTWRITEMASK,
  '__module__' : 'protos.project.project_pb2'
  # @@protoc_insertion_point(class_scope:rime.ProjectWriteMask)
  })
_sym_db.RegisterMessage(ProjectWriteMask)

_PROJECTMANAGER = DESCRIPTOR.services_by_name['ProjectManager']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\026ri/_gen/protos/project'
  _PROJECTMANAGER.methods_by_name['CreateProject']._options = None
  _PROJECTMANAGER.methods_by_name['CreateProject']._serialized_options = b'\202\323\344\223\002\021\"\014/v1/projects:\001*'
  _PROJECTMANAGER.methods_by_name['GetProject']._options = None
  _PROJECTMANAGER.methods_by_name['GetProject']._serialized_options = b'\202\323\344\223\002\033\022\031/v1/projects/{project_id}'
  _PROJECTMANAGER.methods_by_name['ListProjects']._options = None
  _PROJECTMANAGER.methods_by_name['ListProjects']._serialized_options = b'\202\323\344\223\002\016\022\014/v1/projects'
  _SAFEURL._serialized_start=152
  _SAFEURL._serialized_end=174
  _CREATEPROJECTREQUEST._serialized_start=176
  _CREATEPROJECTREQUEST._serialized_end=233
  _CREATEPROJECTRESPONSE._serialized_start=235
  _CREATEPROJECTRESPONSE._serialized_end=290
  _GETPROJECTREQUEST._serialized_start=292
  _GETPROJECTREQUEST._serialized_end=331
  _GETPROJECTRESPONSE._serialized_start=333
  _GETPROJECTRESPONSE._serialized_end=394
  _UPDATEPROJECTREQUEST._serialized_start=396
  _UPDATEPROJECTREQUEST._serialized_end=488
  _UPDATEPROJECTRESPONSE._serialized_start=490
  _UPDATEPROJECTRESPONSE._serialized_end=545
  _DELETEPROJECTREQUEST._serialized_start=547
  _DELETEPROJECTREQUEST._serialized_end=589
  _DELETEPROJECTRESPONSE._serialized_start=591
  _DELETEPROJECTRESPONSE._serialized_end=614
  _LISTPROJECTSREQUEST._serialized_start=616
  _LISTPROJECTSREQUEST._serialized_end=676
  _LISTPROJECTSRESPONSE._serialized_start=678
  _LISTPROJECTSRESPONSE._serialized_end=767
  _SERVEAVAILABLECOLUMNSFORPROJECTREQUEST._serialized_start=769
  _SERVEAVAILABLECOLUMNSFORPROJECTREQUEST._serialized_end=829
  _SERVEAVAILABLECOLUMNSFORPROJECTRESPONSE._serialized_start=831
  _SERVEAVAILABLECOLUMNSFORPROJECTRESPONSE._serialized_end=919
  _PROJECT._serialized_start=922
  _PROJECT._serialized_end=1106
  _SELECTEDCOLUMN._serialized_start=1108
  _SELECTEDCOLUMN._serialized_end=1161
  _ANNOTATEDPROJECT._serialized_start=1164
  _ANNOTATEDPROJECT._serialized_end=1389
  _TESTRUNCOUNTMAPPING._serialized_start=1391
  _TESTRUNCOUNTMAPPING._serialized_end=1471
  _PROJECTWRITEMASK._serialized_start=1473
  _PROJECTWRITEMASK._serialized_end=1582
  _PROJECTMANAGER._serialized_start=1585
  _PROJECTMANAGER._serialized_end=2169
# @@protoc_insertion_point(module_scope)
