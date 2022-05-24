import os
from mlflow.deployments import BaseDeploymentClient

infin_deployment_name = 'infinstor_deployment'


class PluginDeploymentClient(BaseDeploymentClient):
    def create_deployment(self, name, model_uri, flavor=None, config=None):
        print('create_deployment: Entered. model_uri=' + str(model_uri)
                + ', flavor=' + str(flavor) + ', config=' + str(config))
        if config and config.get('raiseError') == 'True':
            raise RuntimeError("Error requested")
        return {'name': infin_deployment_name, 'flavor': flavor}

    def delete_deployment(self, name):
        print('delete_deployment: Entered. name=' + str(name))
        return None

    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        print('update_deployment: Entered. model_uri=' + str(model_uri)
                + ', flavor=' + str(flavor) + ', config=' + str(config))
        return {'flavor': flavor}

    def list_deployments(self):
        print('list_deployment: Entered')
        if os.environ.get('raiseError') == 'True':
            raise RuntimeError('Error requested')
        return [infin_deployment_name]

    def get_deployment(self, name):
        print('get_deployment: Entered')
        return {'key1': 'val1', 'key2': 'val2'}

    def predict(self, deployment_name, df):
        print('predict: Entered. deployment_name=' + str(deployment_name)
                + ', df=' + str(df))
        return 1


def run_local(name, model_uri, flavor=None, config=None):
    print(f"Deployed locally at the key {name} using the model from {model_uri}. "
          f"It's flavor is {flavor} and config is {config}")


def target_help():
    print('target_help: Entered')
    return "Target help is called"
