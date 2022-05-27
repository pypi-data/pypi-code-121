import os
from os.path import dirname, join
from django.conf import settings


class CrudSchema:
    PATH = ''
    MODEL_CLASS = None
    FIELDS = []
    ANNOTATIONS = {}
    SUB_CLASSES = {}
    ALWAYS_LIST = True

    def __init__(self, filters):
        # self.url_path = self.URL_PATH
        self.path = self.PATH
        self.model_class = self.MODEL_CLASS
        self.set_queryset(filters=filters)
        self.model_name = self.model_class.__name__
        if self.FIELDS:
            self.fields_data = [f for f in self.model_class._meta.fields if f.name in self.FIELDS]
        else:
            self.fields_data = self.model_class._meta.fields
        self.annotations = self.ANNOTATIONS
        self.required_fields = [f.name for f in self.fields_data if not f.blank]

    def set_queryset(self, filters):
        self.filters = filters if filters else {}
        self.queryset = self.model_class.objects.filter(**filters)

    def get(self):
        res = list(self.queryset.values(*self.FIELDS).annotate(**self.ANNOTATIONS))
        for relation_key, model_class in self.SUB_CLASSES.items():
            for item in res:
                if model_class.__name__ not in item:
                    item[model_class.__name__] = []
                item[model_class.__name__] = list(model_class.filter(id=item[relation_key]).values())

        if not self.ALWAYS_LIST and len(res) == 1:
            return res[0]
        return res

    def post(self, data):
        item = self.model_class(**data)
        item.full_clean()
        item.save()
        self.set_queryset(filters={'id': item.id})
        return self.get()

    def bulk_post(self, data, force=False):
        if not force:
            res = []
            ids = []
            for item in data:
                item = self.model_class(**item)
                item.full_clean()
                res.append(item)
            for item in res:
                item.save()
                ids.append(item.id)
        else:
            self.model_class.objects.bulk_create([self.model_class(**item) for item in data])
            ln = len(data)
            ids = list(self.model_class.objects.order_by('-id')[:ln].values_list('id', flat=True))
        self.set_queryset(filters={'id__in': ids})
        return self.get()

    def put(self, data):
        for item in self.queryset:
            for key, value in data.items():
                setattr(item, key, value)
            item.full_clean()
        self.queryset.update(**data)
        return self.get()

    def delete(self):
        self.queryset.delete()
        return True

    def _get_swaggar_query_parameters(self):
        return '\n'.join([
            '        - in: query\n'
            f'          name: {field.name}\n'
            f'          description: {field.help_text} '
            f'==> Available lookups {[str(a) for a in field.class_lookups]}\n'
            f'          required: false\n'
            '          schema: \n'
            f'            type: {field.description}'
            for field in self.fields_data])

    def swaggar_definition(self):
        rqs = '\n'.join(f'    - {field}' for field in self.required_fields)
        flds = '\n'.join([
            f'      {field.name}:\n'
            f'         type: {field.description}'
            # f'         format:{field}\n' \
            # f'         example:{field}\n' \
            for field in self.fields_data])
        return f'  {self.model_name}Item:\n' \
               '    type: object\n' \
               '    required:\n' \
               f'{rqs}\n' \
               '    properties:\n' \
               f'{flds}'

    def swagger_get(self):
        summary = f'Get a list of filtered {self.model_name}s'
        operation_id = f'search{self.model_name}'
        return '''
    get:
      tags:
        - developers
      summary: {summary}
      operationId: {operation_id}
      description: |
        By passing in the appropriate options, you can search for
        available {model_name} in the system
      parameters:\n{query_parameters}
      responses:
        '200':
          description: search results matching criteria
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/StoryItem'
      '400':
        description: bad input parameter
        '''.format(summary=summary, operation_id=operation_id, model_name=self.model_name,
                   query_parameters=self._get_swaggar_query_parameters())  # TODO

    def swagger_post(self):
        summary = f'Adds item to {self.model_name}s'
        operation_id = f'add{self.model_name}'
        return '''
    post:
      tags:
        - developers
      summary: {summary}
      operationId: {operation_id}
      description: Adds an item to system
      consumes:
      - application/json
      produces:
      - application/json
      parameters:\n{query_parameters}
        - in: body
          name: {model_name}Item
          description: {model_name} item to add
          schema:
            $ref: \'#/definitions/{model_name}Item\'
      responses:
        201:
          description: item created
        400:
          description: invalid input, object invalid
        409:
          description: an existing item already exists
        '''.format(summary=summary, operation_id=operation_id, model_name=self.model_name,
                   query_parameters=self._get_swaggar_query_parameters())

    def swagger_put(self):
        summary = f'Edits item in {self.model_name}s'
        operation_id = f'edit{self.model_name}'
        return '''
    put:
      tags:
        - developers
      summary: {summary}
      operationId: {operation_id}
      description: Edits item in system
      consumes:
      - application/json
      produces:
      - application/json
      parameters:
      - in: body
        name: {model_name}Item
        description: {model_name} item to add
        schema:
          $ref: \'#/definitions/{model_name}Item\'
      responses:
        201:
          description: item created
        400:
          description: invalid input, object invalid
        409:
          description: an existing item already exists
            '''.format(summary=summary, operation_id=operation_id, model_name=self.model_name)

    def swagger_delete(self):
        summary = f'Delete using filters {self.model_name}s'
        operation_id = f'delete{self.model_name}'
        return '''
    delete:
      tags:
        - developers
      summary: {summary}
      operationId: {operation_id}
      description: |
        By passing in the appropriate options, you can search for
        available {model_name} in the system
      parameters:
{parameters}
      responses:
        '204':
          description: search results matching criteria 
        '400':
          description: bad input parameter
        '''.format(summary=summary, operation_id=operation_id, model_name=self.model_name,
                   parameters=self._get_swaggar_query_parameters())  # TODO

    def swagger_doc(self):
        header = '''
openapi: 3.0.0
info:
  description: This is a simple CRUD API for {model_name}
  version: 1.0.0-oas3
  title: {model_name}
  license:
    name: AmeRepos
    url: https://github.com/amerepos

paths:
  /{url_path}:
'''.format(model_name=self.model_name, url_path=self.url_path)
        return f'{header} \n' \
               f'{self.swagger_get()}\n' \
               f'{self.swagger_post()}\n' \
               f'{self.swagger_put()}\n' \
               f'{self.swagger_delete()}\n' \
               f'definitions:\n' \
               f'{self.swaggar_definition()}'

    def _get_html_template(self):
        return '<html><head>' \
               '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.17.0/swagger-ui.css">' \
               '<script src="//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>' \
               '<script>function render() ' \
               '{{var ui = SwaggerUIBundle({{url:\'{model_name}.yaml\',dom_id: \'#swagger-ui\',' \
               'presets: [SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset]}});}}' \
               '</script></head><body onload="render()"><div id="swagger-ui"></div></body></html>'.format(
            model_name=self.model_name)

    @property
    def url_path(self):
        return '{base_app}/{path}'.format(base_app=self.__module__.split('.')[0], path=self.path)

    @property
    def docs_path(self):
        return join(self.__module__.split('.')[0], 'templates/swaggar', self.path, 'doc.html')
        return f'./templates/swaggar/{self.url_path}'

    @property
    def docs_path_to_yaml(self):
        return join(settings.STATIC_ROOT, 'swaggar', self.url_path, 'definition.yaml')
        return f'{self.docs_path}{self.model_name}.html'

    @property
    def docs_path_to_html(self):
        return join(self.__module__.split('.')[0], 'templates/swaggar', self.path, 'doc.html')
        return f'{self.docs_path}doc.html'

    @property
    def template_path(self):
        return f'swaggar/{self.url_path}doc.html'

    def generate_swagger_files(self):
        dr = dirname(self.docs_path_to_yaml)
        if not os.path.exists(dr):
            os.makedirs(dr)
        dr = dirname(self.docs_path_to_html)
        if not os.path.exists(dr):
            os.makedirs(dr)

        with open(self.docs_path_to_yaml, 'w') as f:
            f.write(self.swagger_doc())

        with open(self.docs_path_to_html, 'w') as f:
            f.write(self._get_html_template())
