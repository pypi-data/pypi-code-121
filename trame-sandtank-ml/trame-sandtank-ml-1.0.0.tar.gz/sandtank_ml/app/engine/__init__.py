import asyncio
import multiprocessing
from functools import partial
from concurrent.futures import ProcessPoolExecutor

from trame.app import asynchronous

from .parflow.run import parflow_run
from .ai.run import ai_run
from .xai.run import xai_run

MULTI_PROCESS_MANAGER = None
PROCESS_EXECUTOR = None


def initialize(server):
    state, ctrl = server.state, server.controller

    # Get the executor pool setup
    global MULTI_PROCESS_MANAGER, PROCESS_EXECUTOR
    MULTI_PROCESS_MANAGER = multiprocessing.Manager()
    SPAWN = multiprocessing.get_context("spawn")
    PROCESS_EXECUTOR = ProcessPoolExecutor(1, mp_context=SPAWN)

    # ParFlow execution -------------------------------------------------------

    def exec_parflow(left=25, right=25, time=10):
        loop = asyncio.get_event_loop()
        queue = MULTI_PROCESS_MANAGER.Queue()

        asynchronous.decorate_task(
            loop.run_in_executor(
                PROCESS_EXECUTOR,
                partial(parflow_run, queue, left, right, time),
            )
        )
        asynchronous.create_state_queue_monitor_task(server, queue)

    def run_parflow(**kwargs):
        exec_parflow(left=state.pf_bc_left, right=state.pf_bc_right)

    # AI execution ------------------------------------------------------------

    async def run_ai():
        with state:
            state.ai_running = True

        await asyncio.sleep(0.1)

        with state:
            state.ai = ai_run(state.pf_bc_left, state.pf_bc_right)
            state.ai_running = False

    # XAI execution -----------------------------------------------------------

    async def run_xai():
        with state:
            state.xai_running = True

        await asyncio.sleep(0.1)

        with state:
            state.xai = await xai_run()
            state.xai_running = False

    # Controller registration -------------------------------------------------

    ctrl.parflow_run = run_parflow
    ctrl.ai_run = run_ai
    ctrl.xai_run = run_xai

    ctrl.on_server_ready.add(run_parflow)
