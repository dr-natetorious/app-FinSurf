#!/usr/bin/env python3
import os.path
from reusable.context import InfraContext
from aws_cdk.core import App, Stack, Environment
from layers.basenet import BaseNetworkingLayer
from layers.earnings_api import EarningsApiLayer
from layers.alexa import AlexaSkillLayer
from layers.k8s import KubernetesClusterLayer
from layers.friendlynamed import FriendlyNamedLayer
from layers.accountlinking import AccountLinkingLayer
from layers.secrets import SecretsLayer
from layers.portfoliolayer import PortfolioLayer
from layers.collectorlayer import CollectorLayer
from layers.marketgraphlayer import MarketGraphLayer
src_root_dir = os.path.join(os.path.dirname(__file__),"..")

default_env= Environment(region="us-west-2")

def create_infra_stack(infra_stack):
  context = InfraContext(env=default_env)
  context.secrets = SecretsLayer(infra_stack,'SecretsLayer')
  context.networking  = BaseNetworkingLayer(infra_stack, "BaseNetworkingLayer", context=context)
  context.earnings_api = EarningsApiLayer(infra_stack,'EarningsApiLayer', context=context)
  context.fnapi = FriendlyNamedLayer(infra_stack,'FriendlyNamed',context=context)
  AlexaSkillLayer(infra_stack,'AlexaSkills', context=context)
  AccountLinkingLayer(infra_stack, 'AccountLinking', context=context)
  context.collectors = CollectorLayer(infra_stack,'Collections', context=context)
  MarketGraphLayer(infra_stack,'MarketGraph', context=context)
  #PortfolioLayer(infra_stack,'PortfolioMgmt', context=context)
    
  #cluster = KubernetesClusterLayer(infra_stack, 'KubernetesClusterLayer',vpc=networking.vpc)

app = App()
infra_stack = Stack(app,'FinSurf', env=default_env)
create_infra_stack(infra_stack)

app.synth()
