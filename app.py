#!/usr/bin/env python3
import os.path
from infra.reusable.context import InfraContext
from aws_cdk.core import App, Stack, Environment
from infra.layers.basenet import BaseNetworkingLayer
from infra.layers.earnings_api import EarningsApiLayer
from infra.layers.alexa import AlexaSkillLayer
from infra.layers.k8s import KubernetesClusterLayer
from infra.layers.friendlynamed import FriendlyNamedLayer
from infra.layers.accountlinking import AccountLinkingLayer
from infra.layers.secrets import SecretsLayer
from infra.layers.portfoliolayer import PortfolioLayer
from infra.layers.collectorlayer import CollectorLayer
from infra.layers.marketgraphlayer import MarketGraphLayer
src_root_dir = os.path.join(os.path.dirname(__file__))

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

app = App()
infra_stack = Stack(app,'FinSurf', env=default_env)
create_infra_stack(infra_stack)

from infra.cicd.app import create_cicd_stack
infra_stack = Stack(app,'FinSurfBuilder', env=default_env)
create_cicd_stack(infra_stack)

app.synth()
