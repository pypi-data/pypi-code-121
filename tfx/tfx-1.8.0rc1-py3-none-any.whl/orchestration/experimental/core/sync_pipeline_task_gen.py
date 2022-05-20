# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TaskGenerator implementation for sync pipelines."""

import collections
from typing import Callable, Dict, List, Mapping, Optional, Set

from absl import logging
from tfx.orchestration import data_types_utils
from tfx.orchestration import metadata
from tfx.orchestration.experimental.core import constants
from tfx.orchestration.experimental.core import mlmd_state
from tfx.orchestration.experimental.core import pipeline_state as pstate
from tfx.orchestration.experimental.core import service_jobs
from tfx.orchestration.experimental.core import task as task_lib
from tfx.orchestration.experimental.core import task_gen
from tfx.orchestration.experimental.core import task_gen_utils
from tfx.orchestration.portable import outputs_utils
from tfx.orchestration.portable.mlmd import execution_lib
from tfx.proto.orchestration import pipeline_pb2
from tfx.utils import status as status_lib
from tfx.utils import topsort
from ml_metadata.proto import metadata_store_pb2


class SyncPipelineTaskGenerator(task_gen.TaskGenerator):
  """Task generator for executing a sync pipeline.

  Calling `generate` is not thread-safe. Concurrent calls to `generate` should
  be explicitly serialized. Since MLMD may be updated upon call to `generate`,
  it's also not safe to call `generate` on different instances of this class
  where the instances refer to the same MLMD db and the same pipeline IR.
  """

  def __init__(self,
               mlmd_handle: metadata.Metadata,
               is_task_id_tracked_fn: Callable[[task_lib.TaskId], bool],
               service_job_manager: service_jobs.ServiceJobManager,
               fail_fast: bool = False):
    """Constructs `SyncPipelineTaskGenerator`.

    Args:
      mlmd_handle: A handle to the MLMD db.
      is_task_id_tracked_fn: A callable that returns `True` if a task_id is
        tracked by the task queue.
      service_job_manager: Used for handling service nodes in the pipeline.
      fail_fast: If `True`, pipeline run is aborted immediately if any node
        fails. If `False`, pipeline run is only aborted when no further progress
        can be made due to node failures.
    """
    self._mlmd_handle = mlmd_handle
    self._is_task_id_tracked_fn = is_task_id_tracked_fn
    self._service_job_manager = service_job_manager
    self._fail_fast = fail_fast

  def generate(self,
               pipeline_state: pstate.PipelineState) -> List[task_lib.Task]:
    """Generates tasks for executing the next executable nodes in the pipeline.

    The returned tasks must have `exec_task` populated. List may be empty if
    no nodes are ready for execution.

    Args:
      pipeline_state: The `PipelineState` object associated with the pipeline
        for which to generate tasks.

    Returns:
      A `list` of tasks to execute.
    """
    return _Generator(self._mlmd_handle, pipeline_state,
                      self._is_task_id_tracked_fn, self._service_job_manager,
                      self._fail_fast)()


class _Generator:
  """Generator implementation class for SyncPipelineTaskGenerator."""

  def __init__(self,
               mlmd_handle: metadata.Metadata,
               pipeline_state: pstate.PipelineState,
               is_task_id_tracked_fn: Callable[[task_lib.TaskId], bool],
               service_job_manager: service_jobs.ServiceJobManager,
               fail_fast: bool = False):
    self._mlmd_handle = mlmd_handle
    pipeline = pipeline_state.pipeline
    if pipeline.execution_mode != pipeline_pb2.Pipeline.ExecutionMode.SYNC:
      raise ValueError(
          'SyncPipelineTaskGenerator should be instantiated with a pipeline '
          'proto having execution_mode `SYNC`, not `{}`'.format(
              pipeline.execution_mode))
    for node in pipeline.nodes:
      which_node = node.WhichOneof('node')
      if which_node != 'pipeline_node':
        raise ValueError(
            'All sync pipeline nodes should be of type `PipelineNode`; found: '
            '`{}`'.format(which_node))
    self._pipeline_state = pipeline_state
    with self._pipeline_state:
      self._node_states_dict = self._pipeline_state.get_node_states_dict()
    self._pipeline_uid = self._pipeline_state.pipeline_uid
    self._pipeline = pipeline
    self._pipeline_run_id = (
        pipeline.runtime_spec.pipeline_run_id.field_value.string_value)
    self._is_task_id_tracked_fn = is_task_id_tracked_fn
    self._service_job_manager = service_job_manager
    self._fail_fast = fail_fast

  def __call__(self) -> List[task_lib.Task]:
    layers = _topsorted_layers(self._pipeline)
    skipped_node_ids = _skipped_node_ids(self._pipeline)
    terminal_node_ids = _terminal_node_ids(layers, skipped_node_ids)
    exec_node_tasks = []
    update_node_state_tasks = []
    successful_node_ids = set()
    failed_nodes_dict: Dict[str, status_lib.Status] = {}
    finalize_pipeline_task = None
    for layer_nodes in layers:
      for node in layer_nodes:
        node_id = node.node_info.id
        node_uid = task_lib.NodeUid.from_pipeline_node(self._pipeline, node)
        node_state = self._node_states_dict[node_uid]
        if node_state.is_success():
          successful_node_ids.add(node_id)
          continue
        if node_state.is_failure():
          failed_nodes_dict[node_id] = node_state.status
          continue
        if not self._upstream_nodes_successful(node, successful_node_ids):
          continue
        tasks = self._generate_tasks_for_node(node)
        for task in tasks:
          if isinstance(task, task_lib.UpdateNodeStateTask):
            if pstate.is_node_state_success(task.state):
              successful_node_ids.add(node_id)
            elif pstate.is_node_state_failure(task.state):
              failed_nodes_dict[node_id] = task.status
              if self._fail_fast:
                finalize_pipeline_task = self._abort_task(task.status.message)
            update_node_state_tasks.append(task)
          elif isinstance(task, task_lib.ExecNodeTask):
            exec_node_tasks.append(task)

        if finalize_pipeline_task:
          break

      if finalize_pipeline_task:
        break

    if not self._fail_fast and failed_nodes_dict:
      assert not finalize_pipeline_task
      node_by_id = _node_by_id(self._pipeline)
      # Collect nodes that cannot be run because they have a failed ancestor.
      unrunnable_node_ids = set()
      for node_id in failed_nodes_dict:
        unrunnable_node_ids |= _descendants(node_by_id, node_id)
      # Nodes that are still runnable have neither succeeded nor failed, and
      # don't have a failed ancestor.
      runnable_node_ids = node_by_id.keys() - (
          unrunnable_node_ids | successful_node_ids | failed_nodes_dict.keys())
      # If there are no runnable nodes, we can abort the pipeline.
      if not runnable_node_ids:
        finalize_pipeline_task = self._abort_task(
            f'Cannot make progress due to node failures: {failed_nodes_dict}')

    result = update_node_state_tasks
    if finalize_pipeline_task:
      result.append(finalize_pipeline_task)
    elif terminal_node_ids <= successful_node_ids:
      # If all terminal nodes are successful, the pipeline can be finalized.
      result.append(
          task_lib.FinalizePipelineTask(
              pipeline_uid=self._pipeline_uid,
              status=status_lib.Status(code=status_lib.Code.OK)))
    else:
      result.extend(exec_node_tasks)
    return result

  def _generate_tasks_for_node(
      self, node: pipeline_pb2.PipelineNode) -> List[task_lib.Task]:
    """Generates list of tasks for the given node."""
    node_uid = task_lib.NodeUid.from_pipeline_node(self._pipeline, node)
    node_id = node.node_info.id
    result = []

    node_state = self._node_states_dict[node_uid]
    if node_state.state in (pstate.NodeState.STOPPING, pstate.NodeState.STOPPED,
                            pstate.NodeState.PAUSING, pstate.NodeState.PAUSED):
      logging.info('Ignoring node in state \'%s\' for task generation: %s',
                   node_state.state, node_uid)
      return result

    # If this is a pure service node, there is no ExecNodeTask to generate
    # but we ensure node services and check service status.
    service_status = self._ensure_node_services_if_pure(node_id)
    if service_status is not None:
      if service_status == service_jobs.ServiceStatus.FAILED:
        # TODO(b/205642811): Mark all pending executions as either failed (if
        # active) or canceled (if new), and delete the the executions temporary
        # and output directories.
        error_msg = f'service job failed; node uid: {node_uid}'
        result.append(
            task_lib.UpdateNodeStateTask(
                node_uid=node_uid,
                state=pstate.NodeState.FAILED,
                status=status_lib.Status(
                    code=status_lib.Code.ABORTED, message=error_msg)))
      elif service_status == service_jobs.ServiceStatus.SUCCESS:
        logging.info('Service node successful: %s', node_uid)
        result.append(
            task_lib.UpdateNodeStateTask(
                node_uid=node_uid, state=pstate.NodeState.COMPLETE))
      elif service_status == service_jobs.ServiceStatus.RUNNING:
        result.append(
            task_lib.UpdateNodeStateTask(
                node_uid=node_uid, state=pstate.NodeState.RUNNING))
      return result

    # If a task for the node is already tracked by the task queue, it need
    # not be considered for generation again but we ensure node services
    # in case of a mixed service node.
    if self._is_task_id_tracked_fn(
        task_lib.exec_node_task_id_from_pipeline_node(self._pipeline, node)):
      service_status = self._ensure_node_services_if_mixed(node_id)
      if service_status == service_jobs.ServiceStatus.FAILED:
        error_msg = f'associated service job failed; node uid: {node_uid}'
        result.append(
            task_lib.UpdateNodeStateTask(
                node_uid=node_uid,
                state=pstate.NodeState.FAILED,
                status=status_lib.Status(
                    code=status_lib.Code.ABORTED, message=error_msg)))
      return result

    node_executions = task_gen_utils.get_executions(self._mlmd_handle, node)
    latest_executions_set = task_gen_utils.get_latest_executions_set(
        node_executions)

    # If all the executions in the set for the node are successful, we're done.
    if latest_executions_set and all(
        execution_lib.is_execution_successful(e)
        for e in latest_executions_set):
      logging.info('Node successful: %s', node_uid)
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid, state=pstate.NodeState.COMPLETE))
      return result

    # If one of the executions in the set for the node failed or cancelled, the
    # pipeline should be aborted if the node is not in state STARTING.
    # For nodes that are in state STARTING, new executions are created.
    # TODO (b/223627713) a node in a ForEach is not restartable, it is better
    # to prevent restarting for now.
    failed_executions = [
        e for e in latest_executions_set if execution_lib.is_execution_failed(e)
    ]
    if failed_executions and (len(latest_executions_set) > 1 or
                              node_state.state != pstate.NodeState.STARTING):
      error_msg = f'node {node_uid} failed; '
      for e in failed_executions:
        error_msg_value = e.custom_properties.get(
            constants.EXECUTION_ERROR_MSG_KEY)
        error_msg_value = data_types_utils.get_metadata_value(
            error_msg_value) if error_msg_value else ''
        error_msg += f'error: {error_msg_value}; '
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid,
              state=pstate.NodeState.FAILED,
              status=status_lib.Status(
                  code=status_lib.Code.ABORTED, message=error_msg)))
      return result

    latest_active_execution = task_gen_utils.get_latest_active_execution(
        latest_executions_set)
    if latest_active_execution:
      with mlmd_state.mlmd_execution_atomic_op(
          mlmd_handle=self._mlmd_handle,
          execution_id=latest_active_execution.id) as execution:
        execution.last_known_state = metadata_store_pb2.Execution.RUNNING
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid, state=pstate.NodeState.RUNNING))
      result.append(
          task_gen_utils.generate_task_from_execution(self._mlmd_handle,
                                                      self._pipeline, node,
                                                      execution))
      return result

    # Finally, we are ready to generate tasks for the node by resolving inputs.
    result.extend(self._resolve_inputs_and_generate_tasks_for_node(node))
    return result

  def _resolve_inputs_and_generate_tasks_for_node(
      self,
      node: pipeline_pb2.PipelineNode,
  ) -> List[task_lib.Task]:
    """Generates tasks for a node by freshly resolving inputs."""
    result = []
    node_uid = task_lib.NodeUid.from_pipeline_node(self._pipeline, node)
    resolved_info = task_gen_utils.generate_resolved_info(
        self._mlmd_handle, node)
    if resolved_info is None:
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid, state=pstate.NodeState.SKIPPED))
      return result

    if not resolved_info.input_artifacts:
      error_msg = f'failure to resolve inputs; node uid: {node_uid}'
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid,
              state=pstate.NodeState.FAILED,
              status=status_lib.Status(
                  code=status_lib.Code.ABORTED, message=error_msg)))
      return result

    executions = task_gen_utils.register_executions(
        metadata_handler=self._mlmd_handle,
        execution_type=node.node_info.type,
        contexts=resolved_info.contexts,
        input_dicts=resolved_info.input_artifacts,
        exec_properties=resolved_info.exec_properties)

    # Selects the first artifacts and create a exec task.
    input_artifacts = resolved_info.input_artifacts[0]
    # Selects the first execution and marks it as RUNNING.
    with mlmd_state.mlmd_execution_atomic_op(
        mlmd_handle=self._mlmd_handle,
        execution_id=executions[0].id) as execution:
      execution.last_known_state = metadata_store_pb2.Execution.RUNNING

    outputs_resolver = outputs_utils.OutputsResolver(
        node, self._pipeline.pipeline_info, self._pipeline.runtime_spec,
        self._pipeline.execution_mode)
    output_artifacts = outputs_resolver.generate_output_artifacts(execution.id)

    # For mixed service nodes, we ensure node services and check service
    # status; pipeline is aborted if the service jobs have failed.
    service_status = self._ensure_node_services_if_mixed(node.node_info.id)
    if service_status == service_jobs.ServiceStatus.FAILED:
      error_msg = f'associated service job failed; node uid: {node_uid}'
      result.append(
          task_lib.UpdateNodeStateTask(
              node_uid=node_uid,
              state=pstate.NodeState.FAILED,
              status=status_lib.Status(
                  code=status_lib.Code.ABORTED, message=error_msg)))
      return result

    outputs_utils.make_output_dirs(output_artifacts)
    result.append(
        task_lib.UpdateNodeStateTask(
            node_uid=node_uid, state=pstate.NodeState.RUNNING))
    result.append(
        task_lib.ExecNodeTask(
            node_uid=node_uid,
            execution_id=execution.id,
            contexts=resolved_info.contexts,
            input_artifacts=input_artifacts,
            exec_properties=resolved_info.exec_properties,
            output_artifacts=output_artifacts,
            executor_output_uri=outputs_resolver.get_executor_output_uri(
                execution.id),
            stateful_working_dir=outputs_resolver
            .get_stateful_working_directory(execution.id),
            tmp_dir=outputs_resolver.make_tmp_dir(execution.id),
            pipeline=self._pipeline))
    return result

  def _ensure_node_services_if_pure(
      self, node_id: str) -> Optional[service_jobs.ServiceStatus]:
    """Calls `ensure_node_services` and returns status if given node is pure service node."""
    if self._service_job_manager.is_pure_service_node(self._pipeline_state,
                                                      node_id):
      return self._service_job_manager.ensure_node_services(
          self._pipeline_state, node_id)
    return None

  def _ensure_node_services_if_mixed(
      self, node_id: str) -> Optional[service_jobs.ServiceStatus]:
    """Calls `ensure_node_services` and returns status if given node is mixed service node."""
    if self._service_job_manager.is_mixed_service_node(self._pipeline_state,
                                                       node_id):
      return self._service_job_manager.ensure_node_services(
          self._pipeline_state, node_id)
    return None

  def _upstream_nodes_successful(self, node: pipeline_pb2.PipelineNode,
                                 successful_node_ids: Set[str]) -> bool:
    """Returns `True` if all the upstream nodes have been successfully executed."""
    return set(node.upstream_nodes) <= successful_node_ids

  def _abort_task(self, error_msg: str) -> task_lib.FinalizePipelineTask:
    """Returns task to abort pipeline execution."""
    error_msg = (f'Aborting pipeline execution due to node execution failure; '
                 f'error: {error_msg}')
    logging.error(error_msg)
    return task_lib.FinalizePipelineTask(
        pipeline_uid=self._pipeline_uid,
        status=status_lib.Status(
            code=status_lib.Code.ABORTED, message=error_msg))


def _skipped_node_ids(pipeline: pipeline_pb2.Pipeline) -> Set[str]:
  """Returns the set of nodes that are marked as skipped in partial run."""
  skipped_node_ids = set()
  for node in pstate.get_all_pipeline_nodes(pipeline):
    if node.execution_options.HasField('skip'):
      skipped_node_ids.add(node.node_info.id)
  return skipped_node_ids


def _topsorted_layers(
    pipeline: pipeline_pb2.Pipeline) -> List[List[pipeline_pb2.PipelineNode]]:
  """Returns pipeline nodes in topologically sorted layers."""
  node_by_id = _node_by_id(pipeline)
  return topsort.topsorted_layers(
      [node.pipeline_node for node in pipeline.nodes],
      get_node_id_fn=lambda node: node.node_info.id,
      get_parent_nodes=(
          lambda node: [node_by_id[n] for n in node.upstream_nodes]),
      get_child_nodes=(
          lambda node: [node_by_id[n] for n in node.downstream_nodes]))


def _terminal_node_ids(layers: List[List[pipeline_pb2.PipelineNode]],
                       skipped_node_ids: Set[str]) -> Set[str]:
  """Returns nodes across all layers that have no downstream nodes to run."""
  terminal_node_ids: Set[str] = set()
  for layer_nodes in layers:
    for node in layer_nodes:
      # Ignore skipped nodes.
      if node.node_info.id in skipped_node_ids:
        continue
      if not node.downstream_nodes or all(
          downstream_node in skipped_node_ids
          for downstream_node in node.downstream_nodes):
        terminal_node_ids.add(node.node_info.id)
  return terminal_node_ids


def _node_by_id(
    pipeline: pipeline_pb2.Pipeline) -> Dict[str, pipeline_pb2.PipelineNode]:
  return {
      node.pipeline_node.node_info.id: node.pipeline_node
      for node in pipeline.nodes
  }


def _descendants(node_by_id: Mapping[str, pipeline_pb2.PipelineNode],
                 node_id: str) -> Set[str]:
  """Returns node_ids of all descendants of the given node_id."""
  queue = collections.deque()
  queue.extend(node_by_id[node_id].downstream_nodes)
  result = set()
  while queue:
    q_node_id = queue.popleft()
    if q_node_id not in result:
      queue.extend(node_by_id[q_node_id].downstream_nodes)
      result.add(q_node_id)
  return result
