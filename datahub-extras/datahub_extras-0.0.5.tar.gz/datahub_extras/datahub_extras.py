import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.com.linkedin.pegasus2avro.datajob import (
    DataJobInputOutputClass
)
from datahub.metadata.com.linkedin.pegasus2avro.dataset import (
    DatasetPropertiesClass,
    DatasetLineageTypeClass,
    UpstreamClass,
    UpstreamLineage,
)
from datahub.metadata.schema_classes import (
    ChangeTypeClass, DataFlowInfoClass, DataJobInfoClass
)
import requests, json

def title_to_snake(s):
    splits = s.split(" ")
    return "_".join([sp[0].lower() + sp[1:] for sp in splits])

def split_and_strip(s, d):
    return list(map(lambda x: x.strip(), s.split(d)))

def extract(s):
    if not s.startswith("["):
        return [s]
    return split_and_strip(s.strip("[").strip("]"), ",")

class DatahubAgent:
    
    def __init__(self, rest_url, env):
        self.rest_url = rest_url
        self.emitter = DatahubRestEmitter(gms_server=rest_url, extra_headers={})
        self.env = env
    
    
    def create_task(self, platform, pipeline_id, task_id):
        urn = builder.make_data_job_urn(
            orchestrator=platform,
            flow_id=pipeline_id,
            job_id="{}.{}".format(pipeline_id, task_id),
            cluster=self.env
        )
        aspect = DataJobInfoClass(
            name="{}.{}".format(pipeline_id, task_id),
            type=platform
        )
        change = MetadataChangeProposalWrapper(
            entityType="dataJob",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=urn,
            aspectName="dataJobInfo",
            aspect=aspect,
        )
        self.emitter.emit_mcp(change)


    def create_task_lineage(self, platform, pipeline_id, task_id, inputs, outputs):
        dj_urn = lambda _id: builder.make_data_job_urn(
            orchestrator=platform,
            flow_id=pipeline_id,
            job_id="{}.{}".format(pipeline_id, _id),
            cluster=self.env
        )
        ds_urn = lambda _id, pfm: builder.make_dataset_urn(
            platform=pfm,
            name=_id,
            env=self.env
        )
        datajob_input_output = DataJobInputOutputClass(
            inputDatasets=[ds_urn(i["id"], i["platform"]) for i in inputs if i["type"] == "dataset"],
            outputDatasets=[ds_urn(o["id"], o["platform"]) for o in outputs if o["type"] == "dataset"],
            inputDatajobs=[dj_urn(i["id"], i["platform"]) for i in inputs if i["type"] == "task"]
        )
        urn = builder.make_data_job_urn(
            orchestrator=platform,
            flow_id=pipeline_id,
            job_id="{}.{}".format(pipeline_id, task_id),
            cluster=self.env
        )
        change = MetadataChangeProposalWrapper(
            entityType="dataJob",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=urn,
            aspectName="dataJobInputOutput",
            aspect=datajob_input_output,
        )
        self.emitter.emit_mcp(change)


    def create_dataset_lineage(self, platform, dataset_name, inputs):
        ds_urn = lambda _id, pfm: builder.make_dataset_urn(
            platform=pfm,
            name=_id,
            env=self.env
        )
        upstreams = []
        for inp_urn in [ds_urn(i["id"], i["platform"]) for i in inputs if i["type"] == "dataset"]:
            upstream = UpstreamClass(
                dataset=inp_urn,
                type=DatasetLineageTypeClass.TRANSFORMED,
            )
            upstreams.append(upstream)
        
        urn = builder.make_dataset_urn(
            platform=platform,
            name=dataset_name,
            env=self.env
        )
        change = MetadataChangeProposalWrapper(
            entityType="dataset",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=urn,
            aspectName="upstreamLineage",
            aspect=UpstreamLineage(upstreams=upstreams),
        )
        self.emitter.emit_mcp(change)


    def create_pipeline(self, platform, pipeline_name):
        pipeline_id = title_to_snake(pipeline_name)
        change = MetadataChangeProposalWrapper(
            entityType="dataflow",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=builder.make_data_flow_urn(
                orchestrator=platform, flow_id=pipeline_id, cluster=self.env),
            aspectName="dataFlowInfo",
            aspect=DataFlowInfoClass(name=pipeline_name),
        )
        self.emitter.emit_mcp(change)


    def create_dataset(self, platform, dataset_name):
        change = MetadataChangeProposalWrapper(
            entityType="dataset",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=builder.make_dataset_urn(
                platform=platform, name=dataset_name, env=self.env),
            aspectName="datasetProperties",
            aspect=DatasetPropertiesClass(name=dataset_name),
        )
        self.emitter.emit_mcp(change)
    
    
    def delete(self, **kwargs):
        if kwargs["type"] == "dataset":
            urn = builder.make_dataset_urn(
                platform=kwargs["platform"], name=kwargs["id"], env=self.env)
        elif kwargs["type"] == "task":
            urn = builder.make_data_job_urn(
                orchestrator=kwargs["platform"], flow_id=kwargs["pipeline_id"], 
                job_id="{}.{}".format(kwargs["pipeline_id"], kwargs["id"]), cluster=self.env)
        elif kwargs["type"] == "pipeline":
            urn = builder.make_data_flow_urn(
                orchestrator=kwargs["platform"], flow_id=kwargs["pipeline_id"], cluster=self.env)
        else:
            return "Incorrect entity type"
        url = self.rest_url+"/entities?action=delete"
        response = requests.post(url, data=json.dumps({"urn": urn}))
        return response.text


def emit_pipeline_metadata(platform, pipeline_name, agent, emit_string, clear=False):
    inputs, outputs = {}, {}
    entities = {}
    
    pipeline_id = title_to_snake(pipeline_name)
    if clear:
        agent.delete(platform=platform, type="pipeline", pipeline_id=pipeline_id)
    else:
        agent.create_pipeline(platform, pipeline_name)
    
    for line in emit_string.split("\n"):
        if line.strip() == "":
            continue
        sources, targets = list(map(extract, split_and_strip(line, ">>")))
        
        transform = lambda x: {
            "long_id": x,
            "platform": x.split("/")[0],
            "type": x.split("/")[1],
            "id": "/".join(x.split("/")[2:]),
        }

        sources = {s: transform(s) for s in sources}
        targets = {t: transform(t) for t in targets}
        entities = {**entities, **sources, **targets}
        
        for key, source in sources.items():
            outputs[key] = outputs.get(key, []) + list(targets.values())
        for key, target in targets.items():
            inputs[key] = inputs.get(key, []) + list(sources.values())

    for key, entity in entities.items():
        
        if clear:
            agent.delete(**{**entity, "pipeline_id": pipeline_id})
        else:
            if entity["type"] == "dataset":
                agent.create_dataset(entity["platform"], entity["id"])
                agent.create_dataset_lineage(entity["platform"], entity["id"], inputs.get(key, []))
                
            if entity["type"] == "task":
                inp, out = inputs.get(key, []), outputs.get(key, [])
                agent.create_task(entity["platform"], pipeline_id, entity["id"])
                agent.create_task_lineage(entity["platform"], pipeline_id, entity["id"], inp, out)
        