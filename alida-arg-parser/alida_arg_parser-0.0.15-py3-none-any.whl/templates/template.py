{
    "name": "{{ name }}",
    "description": "{{ description }}",
    "mode": "{{mode.upper()}}",
    "area": "{{area.upper()}}",
    "url":  {{json.dumps(docker_image)}},
    "version": "1.0.0",
    "framework": {
        "id": 6,
        "name": "Python",
        "version": "3",
        "imageUrl": "https://cdn.alidalab.it/static/images/frameworks/python_logo.png"
    },
    "assets": { 
        "datasets": 
            {"input":[
                {% for input_dataset in input_datasets %}
                {   "name":{{json.dumps(input_dataset.name)}},
                    "description": {{json.dumps(input_dataset.description)}},
                    "type": "tabular",
                    "col_type": {{json.dumps(translation['column_types'][input_dataset.columns_type])}},
                    "order": {{loop.index-1}}
                },
                {% endfor %}
                ],
            "output": [
                {% for output_dataset in output_datasets %}
                {   "name":{{json.dumps(output_dataset.name)}},
                    "description": {{json.dumps(output_dataset.description)}},
                    "type": "tabular",
                    "order": {{loop.index-1}}
                },
                {% endfor %}
                ]
            },
        "models": 
            {"input":[
                {% for input_model in input_models %}
                {   "name":{{json.dumps(input_model.name)}},
                    "description": {{json.dumps(input_model.description)}},
                    "storage_type": "hdfs",
                    "order": {{loop.index-1}}
                },
                {% endfor %}
                ],
            "output": [
                {% for output_model in output_models %}
                {   "name":{{json.dumps(output_model.name)}},
                    "description": {{json.dumps(output_model.description)}},
                    "storage_type": "hdfs",
                    "order": {{loop.index-1}}
                },
                {% endfor %}
                ]
            }
    },
    "properties": [
        {% for property in properties %}
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.ApplicationProperty": {
                "description": {{json.dumps(property.description)}},
                "mandatory": {{json.dumps(property.required)}},
                "defaultValue": {{json.dumps(property.default)}},
                "value": null,
                "key": {{json.dumps(property.name)}},
                "type": {{json.dumps(translation['type'][property.type])}},
                "inputData": null,
                "outputData": null
            }
        },
        {% endfor %}
    ],
    "metrics": []
}

