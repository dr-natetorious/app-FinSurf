#!/usr/bin/env python3
from context import InfraContext
from layers.earnings_api import EarningsApiLayer
from layers.pythonlambda import PythonLambda
from layers.basenet import NetworkingLayer
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_ec2 as ec2,
  aws_apigateway as a,
  aws_dynamodb as d,
  aws_lambda as lambda_,
  aws_iam as iam,
  aws_kms as kms,
  aws_ssm as ssm,
  aws_elasticache as ec,
  core
)

class FriendlyNameLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
  
    self.python_lambda = PythonLambda(self,'Friendly-Named',
      build_prefix='artifacts/FinSurf-Friendly-Name',
      handler='handler.lambda_handler',
      subnet_group_name='FriendlyNamed',
      context=context)

    self.security_group = ec2.SecurityGroup(self,'FriendlyNamed-SG',
      vpc=context.networking.vpc,
      description='Security group for FriendlyNamed service components')

    self.cluster = ec.CfnCacheCluster(self,'FriendlyNamedStore',
      cache_node_type= "cache.t2.micro",
      az_mode='cross-az',
      engine='redis',
      cluster_name='friendly-named',
      num_cache_nodes=1,
      auto_minor_version_upgrade=True,
      preferred_maintenance_window='sun',
      vpc_security_group_ids=[x.id for x in self.security_group])
  