from classiq.interface.chemistry import ground_state_problem, operator
from classiq.interface.chemistry.operator import PauliOperator

from classiq._internals import async_utils
from classiq._internals.api_wrapper import ApiWrapper
from classiq.exceptions import ClassiqGenerationError


def generate_hamiltonian(
    gs_problem: ground_state_problem.GroundStateProblem,
) -> PauliOperator:
    return async_utils.run(generate_hamiltonian_async(gs_problem))


async def generate_hamiltonian_async(
    gs_problem: ground_state_problem.GroundStateProblem,
) -> PauliOperator:
    result = await ApiWrapper.call_generate_hamiltonian_task(problem=gs_problem)

    if result.status != operator.OperatorStatus.SUCCESS:
        raise ClassiqGenerationError(f"Generate Hamiltonian failed: {result.details}")

    return result.details


ground_state_problem.GroundStateProblem.generate_hamiltonian = generate_hamiltonian  # type: ignore[attr-defined]
ground_state_problem.GroundStateProblem.generate_hamiltonian_async = generate_hamiltonian_async  # type: ignore[attr-defined]
