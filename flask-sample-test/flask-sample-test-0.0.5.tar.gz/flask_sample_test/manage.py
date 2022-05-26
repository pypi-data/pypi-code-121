import os
import pathlib

from flask import current_app
from jinja2 import Environment, PackageLoader
from sqlalchemy import Column

from flask_sample_test import SampleTest
from flask_sample_test.fields import TestColumn

try:
    from flask_script import Manager
except ImportError:
    Manager = None


if Manager is not None:
    SampleTestCommand = Manager(usage='Perform sample test')
else:
    class FakeCommand(object):
        def option(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    SampleTestCommand = FakeCommand()


@SampleTestCommand.option('-m', '--model', dest='model_name')
@SampleTestCommand.option('-q', '--quantity', dest='quantity', type=int)
def create_sample_data(model_name, quantity):
    flask_sample_test: SampleTest = current_app.extensions['flask_sample_test']
    test_data_path = current_app.config['TEST_DATA_PATH']

    env = Environment(loader=PackageLoader(pathlib.Path(__file__).resolve().parent.name))
    template = env.get_template('test_data.txt')

    model = flask_sample_test.models.get(model_name)
    if not model:
        raise Exception(f"unknown model, model_name: {model_name}")
    columns = model.__table__.columns
    test_file = os.path.join(os.getcwd(), test_data_path, f"{model_name}.py")
    with open(test_file, 'a+') as f:
        is_empty_file = True if not os.path.getsize(test_file) else False
        mock_data_list = []
        for i in range(quantity):
            random_data = {}
            for column in columns:
                column: Column
                if column.primary_key:
                    continue
                test_column = TestColumn.init_field(column)
                random_data[column.name] = test_column.random_value()
            mock_data_list.append(random_data)
        context = {
            "mock_data": mock_data_list,
            "import_model": f"from {model.__module__} import {model.__name__}",
            "model_name": model.__name__,
            "is_empty_file": is_empty_file,
        }
        content = template.render(**context)
        f.write(content)
