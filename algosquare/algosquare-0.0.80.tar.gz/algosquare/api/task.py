"""AlgoSquare Task API."""
from .api import ApiObject, api_get, api_post, api_delete
from .model import Model

class Task(ApiObject):
    """Task class."""
    @classmethod
    def get(cls, task_id):
        """
        Gets specific task.
        
        Args:
            task_id: string.

        Returns:
            Task.
        """
        return cls(api_get(f'api/tasks/{task_id}'))

    def refresh(self):
        """reloads task."""
        self.update(api_get(f'api/tasks/{self.task_id}'))

    def start_automl(self, run_time = 60, max_algos = 10, server_cost = 0.2, max_algo_fee = 5):
        """
        Builds model for task.
        
        Args:
            run_time: time in minutes.
            max_algos: maximum number of algos to use.
            server_cost: maximum server cost per hour in USD.
            max_algo_fee: maximum hourly rate of deployment.

        Raises:
            RuntimeError, ValueError.
        """
        if self.status != 'inactive':
            raise RuntimeError('status must be inactive')

        run_time = int(run_time)
        if run_time < 5:
            raise ValueError('run_time must be minimum 5')

        max_algos = int(max_algos)
        if max_algos < 1:
            raise ValueError('max_algos must be minimum 1')

        server_cost = float(server_cost)
        if server_cost < 0.2:
            raise ValueError('server_cost must be a minimum of 0.2')

        max_algo_fee = float(max_algo_fee)
        if max_algo_fee < 0:
            raise ValueError('max_algo_fee must not be negative')

        self.update(api_post(f'api/tasks/{self.task_id}/automl', json=dict(run_time = run_time, max_algos = max_algos, server_cost = server_cost, max_algo_fee = max_algo_fee)))

    def stop_automl(self):
        """
        Stops model building.
        
        Raises:
            RuntimeError.
        """
        if self.status != 'inactive':
            raise RuntimeError('status is inactive')

        self.update(api_delete(f'api/tasks/{self.task_id}/automl'))

    def get_models(self):
        """
        Gets models for task.
        
        Returns:
            List of Models.
        """
        return [Model.load(x) for x in api_get(f'api/tasks/{self.task_id}/models')]