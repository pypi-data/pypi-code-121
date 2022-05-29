from flex_optimization.stop_criteria.function_evaluation import StopFunctionEvaluation
from flex_optimization.stop_criteria.iteration import StopIterationEvaluation
from flex_optimization.stop_criteria.computation_time import StopComputationTime
from flex_optimization.stop_criteria.relative_change import StopRelativeChange
from flex_optimization.stop_criteria.absolute_change import StopAbsoluteChange
from flex_optimization.stop_criteria.rate import StopRate

stopping_criteria = {
    "StopFunctionEvaluation": StopFunctionEvaluation,
    "StopIterationEvaluation": StopIterationEvaluation,
    "StopComputationTime": StopComputationTime,
    "StopRelativeChange": StopRelativeChange,
    "StopAbsoluteChange": StopAbsoluteChange,
    "StopRate": StopRate
}
