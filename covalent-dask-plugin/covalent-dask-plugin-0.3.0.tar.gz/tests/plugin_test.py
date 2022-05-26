# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Tests for Covalent Dask executor."""

from sched import scheduler
import covalent as ct
from covalent._workflow.transport import TransportableObject
from covalent.executor import DaskExecutor
from dask.distributed import LocalCluster
import os
import uuid
import shutil

dispatch_id = str(uuid.uuid1())

def start_cluster():
    cluster = LocalCluster()
    return cluster

def test_init():
    """Test that initialization properly sets member variables."""

    executor = DaskExecutor(conda_env = "test", cache_dir = "/tmp/test", scheduler_address="tcp://0.0.0.0:8786")

    assert executor.scheduler_address == "tcp://0.0.0.0:8786"
    assert executor.log_stdout == "stdout.log"
    assert executor.log_stderr == "stderr.log"
    assert executor.conda_env == "test"
    assert executor.cache_dir == "/tmp/test"
    assert executor.current_env_on_conda_fail == False

def test_deserialization(mocker):
    """Test that the input function is deserialized."""

    cluster = start_cluster()

    executor = DaskExecutor(scheduler_address=cluster.scheduler_address)

    def simple_task(x):
        return x

    transport_function = TransportableObject(simple_task)
    deserizlized_mock = mocker.patch.object(
        transport_function,
        "get_deserialized",
        return_value = simple_task,
    )

    executor.execute(
        function = transport_function,
        args = [5],
        kwargs = {},
        node_id = 0,
        dispatch_id = dispatch_id,
        results_dir = "./",
    )

    deserizlized_mock.assert_called_once()
    cluster.close()
    shutil.rmtree(dispatch_id)

def test_function_call(mocker):
    """Test that the deserialized function is called with correct arguments."""
    cluster = start_cluster()
    executor = DaskExecutor(scheduler_address=cluster.scheduler_address)

    def simple_task(x):
        with open("simple_task_test", "w") as f:
            f.write(f"{x}")
        f.close()

    transport_function = TransportableObject(simple_task)

    # This mock is so that the call to execute uses the same simple_task object that we
    # want to make sure is called.
    mocker.patch.object(transport_function, "get_deserialized", return_value = simple_task)

    args = [5]
    kwargs = {}
    executor.execute(
        function = transport_function,
        args = args,
        kwargs = kwargs,
        node_id = 0,
        dispatch_id = dispatch_id,
        results_dir = "./",
    )

    assert os.path.exists("simple_task_test") == True
    with open("simple_task_test", "r") as f:
        data = f.readlines()
    f.close()
    assert len(data) == 1
    assert int(data[0]) == 5

    os.remove('simple_task_test')
    cluster.close()
    shutil.rmtree(dispatch_id)


def test_final_result():
    """Functional test to check that the result of the function execution is as expected."""

    cluster = start_cluster()
    executor = ct.executor.DaskExecutor(scheduler_address=cluster.scheduler_address)

    @ct.electron(executor = executor)
    def simple_task(x):
        return x

    @ct.lattice
    def sample_workflow(a):
        c = simple_task(a)
        return c

    dispatch_id_new = ct.dispatch(sample_workflow)(5)
    result = ct.get_result(dispatch_id=dispatch_id_new, wait=True)

    # The custom executor has a doubling of each electron's result, for illustrative purporses.
    assert result.result == 5
    cluster.close()
