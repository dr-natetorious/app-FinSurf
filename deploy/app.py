#!/usr/bin/env python3
import os.path
from context import InfraContext
from aws_cdk.core import App, Stack, Environment
from layers.basenet import BaseNetworkingLayer
from layers.earnings_api import EarningsApiLayer
from layers.alexa import AlexaSkillLayer
from layers.k8s import KubernetesClusterLayer
from layers.friendlynamed import FriendlyNamedLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-west-2")

def create_infra_stack(infra_stack):
    context = InfraContext(env=default_env)
    context.networking  = BaseNetworkingLayer(infra_stack, "BaseNetworkingLayer")
    context.earnings_api = EarningsApiLayer(infra_stack,'EarningsApiLayer', context=context)
    AlexaSkillLayer(infra_stack,'AlexaSkills', context=context)
    FriendlyNamedLayer(infra_stack,'FriendlyNamed',context=context)
    #cluster = KubernetesClusterLayer(infra_stack, 'KubernetesClusterLayer',vpc=networking.vpc)

app = App()
infra_stack = Stack(app,'FinSurf', env=default_env)
create_infra_stack(infra_stack)

app.synth()
