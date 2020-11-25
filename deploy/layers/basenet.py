#!/usr/bin/env python3
from aws_cdk import (
    aws_ec2 as ec2,
    aws_route53 as dns,
    core
)

class BaseNetworkingLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
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
        ec2.SubnetConfiguration(name='Kubes',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=21),
        ec2.SubnetConfiguration(name='EarningApi',subnet_type= ec2.SubnetType.PRIVATE, cidr_mask=24),
      ]
    )

    self.hostedZone = dns.PrivateHostedZone(self, 'PrivateFinSurfZone',
      vpc= self.vpc,
      zone_name='finsurf.internal',
      comment='Internal zone for FinSurf application'
    )

  @property
  def vpc(self) -> ec2.Vpc:
    return self.__vpc