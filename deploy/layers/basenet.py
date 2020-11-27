#!/usr/bin/env python3
from reusable.context import InfraContext
from aws_cdk import (
    aws_ec2 as ec2,
    aws_route53 as dns,
    aws_certificatemanager as acm,
    core
)

class BaseNetworkingLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.__vpc = ec2.Vpc(self,'FinSurf', 
      cidr='10.50.0.0/16',
      nat_gateway_subnets= ec2.SubnetSelection(subnet_group_name='Egress'),
      enable_dns_hostnames=True,
      enable_dns_support=True,
      nat_gateways=2,
      max_azs=2,
      subnet_configuration= [
        ec2.SubnetConfiguration(name='Egress', subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=28),
        ec2.SubnetConfiguration(name='EarningApi',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=24),
        ec2.SubnetConfiguration(name='Alexa',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=24),
        ec2.SubnetConfiguration(name='FriendlyNamed',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=24),
        ec2.SubnetConfiguration(name='AccountLinking',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=24),
      ]
    )

    self.__hostedZone = dns.PrivateHostedZone(self, 'PrivateFinSurfZone',
      vpc= self.vpc,
      zone_name=context.environment.region+'.finsurf.internal',
      comment='Internal zone for FinSurf application'
    )

  @property
  def vpc(self) -> ec2.Vpc:
    return self.__vpc

  @property
  def dns_zone(self)->dns.PrivateHostedZone:
    return self.__hostedZone
