#!/usr/bin/env python3
import os.path
from context import InfraContext
from aws_cdk.core import App, Stack, Environment
from layers.basenet import BaseNetworkingLayer
from layers.api import EarningsApiLayer
from layers.k8s import KubernetesClusterLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-west-2")

def create_infra_stack(infra_stack):
    context = InfraContext(env=default_env)
    context.networking  = BaseNetworkingLayer(infra_stack, "BaseNetworkingLayer")
    context.earnings_api = EarningsApiLayer(infra_stack,'EarningsApiLayer', context=context)
    #cluster = KubernetesClusterLayer(infra_stack, 'KubernetesClusterLayer',vpc=networking.vpc)
    #datastores = DataStorageLayer(infra_stack, 'DataStores')
    #streaming = KinesisLayer(infra_stack, 'Streaming')
    #processors = LambdaLayer(infra_stack, 'Processors', stream=streaming.kinesis, auditTable=datastores.auditTable)
    

app = App()
infra_stack = Stack(app,'FinSurf', env=default_env)
create_infra_stack(infra_stack)

app.synth()
