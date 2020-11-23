#!/usr/bin/env python3
import os.path
from aws_cdk.core import App, Stack, Environment
from layers.basenet import BaseNetworkingLayer
from layers.datastores import DataStorageLayer
from layers.kinesis import KinesisLayer
from layers.processors import LambdaLayer
from layers.api import ApiLayer
from layers.k8s import KubernetesClusterLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-east-1")

def create_infra_stack(infra_stack):
    networking  = BaseNetworkingLayer(infra_stack, "BaseNetworkingLayer")
    cluster = KubernetesClusterLayer(infra_stack, 'KubernetesClusterLayer',vpc=networking.vpc)
    #datastores = DataStorageLayer(infra_stack, 'DataStores')
    #streaming = KinesisLayer(infra_stack, 'Streaming')
    #processors = LambdaLayer(infra_stack, 'Processors', stream=streaming.kinesis, auditTable=datastores.auditTable)
    #api = ApiLayer(infra_stack,'Api',stream=streaming.kinesis)

app = App()
infra_stack = Stack(app,'FinSurf', env=default_env)
create_infra_stack(infra_stack)

app.synth()
