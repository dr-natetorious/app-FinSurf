#!/usr/bin/env python3
from context import InfraContext
from layers.earnings_api import EarningsApiLayer
from layers.pythonlambda import PythonLambda
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

class FriendlyNamedLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
      
    self.security_group = ec2.SecurityGroup(self,'FriendlyNamed-SG',
      vpc=context.networking.vpc,
      description='Security group for FriendlyNamed service components')

    self.subnet_group = ec.CfnSubnetGroup(self,'CacheSubnets',
      cache_subnet_group_name='FriendlyNamed-Subnets',
      description='Subnet groups for FriendlyNamed service',
      subnet_ids= [net.subnet_id for net in context.networking.vpc._select_subnet_objects(subnet_group_name='FriendlyNamed')]
    )

    self.cluster = ec.CfnCacheCluster(self,'FriendlyNamedStore',
      cache_node_type= "cache.t2.micro",
      engine='redis',
      cluster_name='friendly-named',
      num_cache_nodes=1,
      auto_minor_version_upgrade=True,
      cache_subnet_group_name=self.subnet_group.cache_subnet_group_name,
      vpc_security_group_ids=[self.security_group.security_group_id])
  
    self.python_lambda = PythonLambda(self,'Friendly-Named',
      build_prefix='artifacts/FinSurf-Friendly-Name',
      handler='handler.lambda_handler',
      subnet_group_name='FriendlyNamed',
      context=context)
    self.python_lambda.function.add_environment(
      key='REDIS_HOST', value=self.cluster.attr_redis_endpoint_address)
    self.python_lambda.function.add_environment(
      key='REDIS_PORT', value=self.cluster.attr_redis_endpoint_port)
