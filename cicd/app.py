#!/usr/bin/env python3
import os.path
from context import BuildContext
from aws_cdk.core import App, Stack, Environment
from layers.images import BuildImagesLayer
from layers.buckets import BucketLayer
from layers.kms import KeyLayer
from layers.pipeline import CodePipelineLayer
from layers.buildjobs import BuildJobLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-west-2")

def create_infra_stack(infra_stack):
    context = BuildContext(env=default_env)
    context.encryption_keys = KeyLayer(infra_stack, 'EncryptionKeys')
    context.build_images = BuildImagesLayer(infra_stack, 'BuildImages')
    context.buckets = BucketLayer(infra_stack, 'Buckets', context=context)
    context.build_projects = BuildJobLayer(infra_stack, 'BuildJobs', context=context)
    context.pipelines = CodePipelineLayer(infra_stack,'CodePipelines', context=context)

app = App()
infra_stack = Stack(app,'FinSurfBuilder', env=default_env)
create_infra_stack(infra_stack)

app.synth()
