#!/usr/bin/env python3
import os.path
from aws_cdk.core import App, Stack, Environment
from layers.images import BuildImagesLayer
from layers.buckets import BucketLayer
from layers.pipeline import CodePipelineLayer
from layers.buildjobs import BuildJobLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-east-1")

def create_infra_stack(infra_stack):
    build_images  = BuildImagesLayer(infra_stack, "BuildImages")
    buckets = BucketLayer(infra_stack, 'Buckets')
    build_jobs = BuildJobLayer(infra_stack, 'BuildJobs', buckets=buckets)
    #datastores = DataStorageLayer(infra_stack, 'DataStores')
    #streaming = KinesisLayer(infra_stack, 'Streaming')
    #processors = LambdaLayer(infra_stack, 'Processors', stream=streaming.kinesis, auditTable=datastores.auditTable)
    #api = ApiLayer(infra_stack,'Api',stream=streaming.kinesis)

app = App()
infra_stack = Stack(app,'FinSurfBuilder', env=default_env)
create_infra_stack(infra_stack)

app.synth()
