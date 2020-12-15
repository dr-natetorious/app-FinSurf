#!/usr/bin/env python3
import os.path
from infra.reusable.context import InfraContext
from aws_cdk.core import App, Stack, Environment
from infra.subsys.core.basenet import BaseNetworkingLayer
from infra.subsys.frontend.earnings_api import EarningsApiLayer
from infra.subsys.frontend.alexa import AlexaSkillLayer
from infra.subsys.core.k8s import KubernetesClusterLayer
from infra.subsys.frontend.friendlynamed import FriendlyNamedLayer
from infra.subsys.frontend.accountlinking import AccountLinkingLayer
from infra.subsys.core.secrets import SecretsLayer
from infra.subsys.backend.portfoliolayer import PortfolioLayer
from infra.subsys.backend.collectorlayer import CollectorLayer
from infra.subsys.core.marketgraphlayer import MarketGraphLayer
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
