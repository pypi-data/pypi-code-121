import json
import sys
import os
from jsonschema import Draft4Validator


def convert_report(report_file):
    with open(report_file, 'r') as json_file:
        report = json.load(json_file)

    # delete_tags params if delete_tags = True
    def common_processing(item, delete_tags):
        item['uri'], item['line'] = item.pop('location').split(':')
        item['line'] = int(item['line'])
        if delete_tags:
            item['tags'] = []
        else:
            item['tags'] = [{'name': '@' + tag} for tag in item.get('tags', [])]
        if 'id' not in item:
            item['id'] = item['name'].replace(' ', '-').lower()
        if 'description' in item:
            item['description'] = item['description'][0]
        else:
            item['description'] = ''

    for feature in report:
        common_processing(feature, True)
        for scenario in feature['elements']:
            common_processing(scenario, False)
            for step in scenario['steps']:
                step['uri'], step['line'] = step.pop('location').split(':')
                step['line'] = int(step['line'])
                if 'result' in step:
                    step['result']['duration'] = int(1000000000 * step['result']['duration'])
                else:
                    step['result'] = {'status': 'skipped', 'duration': 0}
                if 'table' in step:
                    step['rows'] = [{'cells': step['table']['headings']}] + \
                                   [{'cells': cells} for cells in step['table']['rows']]
                    del step['table']
                if 'match' in step:
                    if 'arguments' in step['match']:
                        step['match']['arguments'] = \
                            [{'val': '{}'.format(arg['value']), 'offset': 0} for arg in step['match']['arguments']]
                else:
                    step['match'] = {'arguments': [], 'location': 'UNKNOWN - SKIPPED'}
    return report


def validate_json(report_file):
    file_dir = os.path.dirname(__file__)
    file_path = f"{file_dir}/model/cucumber_report_schema.json"
    with open(file_path, 'r') as json_file:
        schema = json.load(json_file)
    errors = list(Draft4Validator(schema).iter_errors(report_file))
    for error in errors:
        print('#/' + '/'.join([str(path) for path in error.path]), error.message, file=sys.stderr)
    if errors:
        sys.exit(1)
