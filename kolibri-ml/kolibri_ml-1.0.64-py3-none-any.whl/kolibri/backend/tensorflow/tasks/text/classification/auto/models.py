from kolibri.data.ressources import Ressources
import json

resources = Ressources()

filename_job_functions = resources.get('models/kolibri/architectures/classification/neural_network_models.json').path

models = json.load(open(filename_job_functions))