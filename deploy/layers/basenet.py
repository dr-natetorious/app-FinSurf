#!/usr/bin/env python3
from aws_cdk import (
    aws_ec2 as ec2,
    core
)

class BaseNetworkingLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.__vpc = ec2.Vpc(self,'FinSurf', cidr='10.10.0.0/16')

    self.__private_subnet_ids = []
    for net in self.__vpc.private_subnets:
      self.__private_subnet_ids.append(net.subnet_id)

  @property
  def vpc(self) -> ec2.Vpc:
    return self.__vpc

  @property
  def private_subnets_ids(self) -> list:
    return self.__private_subnet_ids