#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from infra.reusable.proxyfrontend import LambdaProxyConstruct
from infra.reusable.pythonlambda import PythonLambda

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
  aws_apigateway as a,
  aws_route53 as dns,
  aws_route53_targets as dns_t,
  aws_certificatemanager as acm,
  core
)

class FriendlyNamedLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
      
    self.security_group = ec2.SecurityGroup(self,'FriendlyNamedSvc-SG',
      vpc=context.networking.vpc,
      allow_all_outbound=True,
      description='Security group for FriendlyNamed service components')

    self.security_group.add_ingress_rule(
      peer= ec2.Peer.any_ipv4(),
      connection=ec2.Port(
        protocol=ec2.Protocol.TCP,
        string_representation='RedisInbound',
        from_port=6379, to_port=6379))

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
      build_prefix='artifacts/FinSurf-Friendly-Named',
      handler='handler.app',
      subnet_group_name='FriendlyNamed',
      context=context,
      securityGroups= [self.security_group])

    self.python_lambda.function.add_environment(
      key='REDIS_HOST', value=self.cluster.attr_redis_endpoint_address)
    self.python_lambda.function.add_environment(
      key='REDIS_PORT', value=self.cluster.attr_redis_endpoint_port)

    self.frontend_proxy = LambdaProxyConstruct(self,'FriendlyNamedAPI',
      handler=self.python_lambda.function,
      context=context)

    self.url = self.frontend_proxy.rest_api.url
