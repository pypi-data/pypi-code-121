import json
from typing import List, Union


class SampleTestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SimpleDataField):
            return str(o)
        return super().default(o)


class SampleTest(object):
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.models = {}
        self.config = {}
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app, db=None):
        self.db = db or self.db
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        self.models = {mapper.class_.__tablename__: mapper.class_ for mapper in db.Model.registry.mappers}
        app.extensions['flask_sample_test'] = self
        app.config.setdefault('TEST_DATA_PATH', 'sample_data')

    def create_env(self, sample_data_list):
        return SampleEnvironment(sample_data_list=sample_data_list, bind=self)

    def create_sample_data(self, model, data):
        return SampleData(model=model, data=data, bind=self)


class SampleData:
    def __init__(self, model, data, bind: SampleTest):
        self._model: callable = model
        self._data: dict = data
        self._instance = None
        self._bind = bind

    def create_instance(self):
        if self._instance:
            return self._instance.id
        self._instance = self._model()

        columns = self._model.__table__.columns
        for column in columns:
            column_name = column.get('name')
            column_nullable = column.get('nullable')
            column_type = column.get('type')
            column_default = column.get('default')
            if column_name == 'id':
                continue
            if column_name in self._data:
                data = self._data.get(column_name)
                if isinstance(column_type, self._db.Integer) and \
                        isinstance(data, SampleData):
                    fk = data.create_instance()
                    setattr(self._instance, column_name, fk)
                elif isinstance(data, (SimpleDataField, ComplexDataField)):
                    setattr(self._instance, column_name, str(data))
                else:
                    setattr(self._instance, column_name, data)
            assert column_name in self._data or column_nullable is True or column_default is not None, \
                f'{self._model.__name__.lower()} 的非空字段 {column_name} 不能为空'

        self._db.session.add(self._instance)
        self._db.session.flush()

        return self._instance.id

    def relation_model(self):
        result = [self]
        for key, value in self.data.items():
            if isinstance(value, SampleData):
                result.extend(value.relation_model())
        return result

    def init_instance(self):
        self._instance = None

    def load_instance(self):
        self._instance = self._db.session.merge(self._instance)

        return self._instance

    def __getattr__(self, item):
        self._instance = self.load_instance()
        return getattr(self._instance, item, None)

    def __setattr__(self, key, value):
        if key in ('_model', '_data', '_instance', '_db', '_inspector'):
            super(SampleData, self).__setattr__(key, value)
            return

        self._instance = self.load_instance()
        setattr(self._instance, key, value)


class SimpleDataField:
    def __init__(self, sample_data: SampleData, field: str):
        """
        :param sample_data: 样例数据
        :param field: 要取的字段
        """
        self._sample_data = sample_data
        self._field = field

    def __str__(self):

        self._sample_data.create_instance()
        return getattr(self._sample_data, self._field)

    def init_instance(self):
        self._sample_data.init_instance()


class ComplexDataField:
    def __init__(self, data: Union[dict, list, tuple, int, float, bool, str]):
        """
        :param data: 数据,
        """
        self.data = data
        self.relation: List[Union[SampleData, SimpleDataField]] = []

    def __str__(self):
        result = json.dumps(self.data, cls=SampleTestJSONEncoder)
        return json.loads(result)

    def _relation_simple_data(self, obj):
        if isinstance(obj, (str, float, int, bool)):
            return

        if isinstance(obj, SimpleDataField):
            self.relation.append(obj)

        if isinstance(obj, dict):
            for key, value in obj.items():
                self._relation_simple_data(key)
                self._relation_simple_data(value)
        if isinstance(obj, (list, tuple)):
            for item in obj:
                self._relation_simple_data(item)

    def init_instance(self):
        for item in self.relation:
            item.init_instance()


class SampleEnvironment(object):

    def __init__(self, sample_data_list, bind: SampleTest):
        self.bind = bind
        self.sample_data_list = sample_data_list

    def __enter__(self):
        for ins in self.sample_data_list:
            ins.create_instance()
        self.bind.db.session.commit()
        self.bind.db.session.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for ins in self.sample_data_list:
            ins.init_instance()
        for table in reversed(self.bind.db.metadata.sorted_tables):
            self.bind.db.session.query(table).delete()
            self.bind.db.session.commit()
            self.bind.db.session.close()
