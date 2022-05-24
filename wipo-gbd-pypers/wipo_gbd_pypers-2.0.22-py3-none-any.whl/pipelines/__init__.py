import glob
import json
import os

# Create a dictionary of files and pipeline names
pipeline_names = {}
pipeline_specs = {}
pipelines = []

dir = os.path.dirname(os.path.realpath(__file__))


def raise_key_error(msg=''):
    raise KeyError(msg)


def load_pipelines():
    pipeline_names = {}
    pipeline_specs = {}
    pipelines = []
    for cursor_file in glob.glob('%s/*.json' % dir):
        with open(os.path.join(dir, cursor_file)) as fh:
            try:
                config = json.load(fh)
                name = config.get('name') or raise_key_error(
                    'name not found in %s' % cursor_file)
                label = config.get('label') or raise_key_error(
                    'label not found in %s' % cursor_file)

                pipelines.append({'name': name,
                                  'label': label})
                if name:
                    pipeline_names[name] = fh.name
                    pipeline_specs[name] = config

            except ValueError as e:
                print('*** Problem with file %s:' % cursor_file)
                raise e
    pipelines.sort(key=lambda x: x['name'])
    return pipeline_names, pipeline_specs, pipelines


pipeline_names, pipeline_specs, pipelines = load_pipelines()



