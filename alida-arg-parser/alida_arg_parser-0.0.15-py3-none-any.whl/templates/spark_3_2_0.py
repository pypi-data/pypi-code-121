{
    "name": "{{ name }}",
    "description": "{{ description }}",
    "mode": "{{mode.upper()}}",
    "metrics": [],
    "area": "{{area.upper()}}",
    "url": "docker://gitlab.alidalab.it:5000/alida/bd-management-services/spark-scdf:3.0.3",
    "version": "1.0.0",
    "framework": {
        "id": 5,
        "name": "Spark",
        "version": "3.2"
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
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.ApplicationProperty": {
                "description": "Dataset delimiter",
                "mandatory": false,
                "defaultValue": ",",
                "value": null,
                "key": "delimiter",
                "type": "STRING",
                "inputData": false,
                "outputData": false
            }
        },
        {
             "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                 "description": "Container image pull policy used when pulling images within Kubernetes. Valid values are Always, Never, and IfNotPresent.",
                 "mandatory": true,
                 "defaultValue": "Always",
                 "value": null,
                 "key": "spark.kubernetes.container.image.pullPolicy",
                 "type": "STRING",
                 "externalized": false,
                 "uri": null
             }
         },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Class to use for serializing objects that will be sent over the network or need to be cached in serialized form",
                "mandatory": false,
                "defaultValue": "0",
                "value": null,
                "key": "spark.serializer",
                "type": "INT",
                "minValue": "0",
                "maxValue": "1",
                "measure": "NONE",
                "mappings": [
                    {
                        "intValue": 0,
                        "name": "org.apache.spark.serializer.JavaSerializer"
                    },
                    {
                        "intValue": 1,
                        "name": "org.apache.spark.serializer.KryoSerializer"
                    }
                ],
                "category": true
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "The codec used to compress internal data such as RDD partitions, event log, broadcast variables and shuffle outputs",
                "mandatory": false,
                "defaultValue": "0",
                "value": null,
                "key": "spark.io.compression.codec",
                "type": "INT",
                "minValue": "0",
                "maxValue": "2",
                "measure": "NONE",
                "mappings": [
                    {
                        "intValue": 0,
                        "name": "lz4"
                    },
                    {
                        "intValue": 1,
                        "name": "lzf"
                    },
                    {
                        "intValue": 2,
                        "name": "snappy"
                    }
                ],
                "category": true
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Maximum size of map outputs to fetch simultaneously from each reduce task",
                "mandatory": false,
                "defaultValue": "50331648",
                "value": null,
                "key": "spark.reducer.maxSizeInFlight",
                "type": "INT",
                "minValue": "25165824",
                "maxValue": "100663296",
                "measure": "BYTES",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Default number of partitions in RDDs returned by transformations like join, reduceByKey, and parallelize when not set by user",
                "mandatory": false,
                "defaultValue": "1",
                "value": null,
                "key": "spark.default.parallelism",
                "type": "INT",
                "minValue": "1",
                "maxValue": "16",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Size of each piece of a block for TorrentBroadcastFactory",
                "mandatory": false,
                "defaultValue": "4194304",
                "value": null,
                "key": "spark.broadcast.blockSize",
                "type": "INT",
                "minValue": "2097152",
                "maxValue": "8388608",
                "measure": "BYTES",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Number of cores to allocate for each task",
                "mandatory": false,
                "defaultValue": "1",
                "value": null,
                "key": "spark.task.cpus",
                "type": "INT",
                "minValue": "1",
                "maxValue": "8",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "If set to true, performs speculative execution of tasks",
                "mandatory": false,
                "defaultValue": "0",
                "value": null,
                "key": "spark.speculation",
                "type": "BOOLEAN",
                "minValue": "0",
                "maxValue": "1",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "the spark master",
                "mandatory": true,
                "defaultValue": null,
                "value": null,
                "key": "spark.master",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "Spark app name",
                "mandatory": true,
                "defaultValue": "{{ name }}",
                "value": null,
                "key": "spark.name",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "Python module",
                "mandatory": true,
                "defaultValue": "main",
                "value": null,
                "key": "pythonModule",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "Number of executors",
                "mandatory": true,
                "defaultValue": 3,
                "value": null,
                "key": "spark.executor.instances",
                "type": "INT",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "Kubernetes secrets used to pull images from private image registries",
                "mandatory": true,
                "defaultValue": null,
                "value": null,
                "key": "spark.kubernetes.container.image.pullSecrets",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "Container image to use for the Spark application",
                "mandatory": true,
                "defaultValue": {{json.dumps(docker_image.replace("docker://", ""))}},
                "value": null,
                "key": "spark.kubernetes.container.image",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "The namespace that will be used for running the driver and executor pods",
                "mandatory": true,
                "defaultValue": null,
                "value": null,
                "key": "spark.kubernetes.namespace",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Whether to compress map output files",
                "mandatory": false,
                "defaultValue": "1",
                "value": null,
                "key": "spark.shuffle.compress",
                "type": "BOOLEAN",
                "minValue": "0",
                "maxValue": "1",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.StaticProperty": {
                "description": "The URL for HDFS service",
                "mandatory": true,
                "defaultValue": null,
                "value": null,
                "key": "hdfsUrl",
                "type": "STRING",
                "externalized": false,
                "uri": null
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Whether to compress broadcast variables before sending them",
                "mandatory": false,
                "defaultValue": "1",
                "value": null,
                "key": "spark.broadcast.compress",
                "type": "BOOLEAN",
                "minValue": "0",
                "maxValue": "1",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        },
        {
            "it.eng.alidalab.applicationcatalogue.domain.service.TuningProperty": {
                "description": "Whether to compress data spilled during shuffles",
                "mandatory": false,
                "defaultValue": "1",
                "value": null,
                "key": "spark.shuffle.spill.compress",
                "type": "BOOLEAN",
                "minValue": "0",
                "maxValue": "1",
                "measure": "NONE",
                "mappings": [],
                "category": false
            }
        }
    ],
    "metrics": []
}

