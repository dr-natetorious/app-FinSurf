#!/usr/bin/env python3
import typing
import os
from infra.reusable.context import InfraContext
from aws_cdk import (
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_iam as iam,
  aws_lambda as lambda_,
  aws_ecr_assets as assets,
  core
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")
class ContainerLambda(core.Construct):
  """
  Represents a construct for a default Python repository.
  """
  def __init__(self, scope: core.Construct, id: str, 
    repository_name:str,
    directory:str,
    subnet_group_name:str,
    context:InfraContext,
    securityGroups:typing.Optional[typing.List[ec2.SecurityGroup]]=None,
    **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.repo = assets.DockerImageAsset(self,'Repo',
      directory=os.path.join(src_root_dir,directory),
      repository_name=repository_name)

    self.function = lambda_.DockerImageFunction(self,'ContainerFunction',
      code = lambda_.DockerImageCode.from_ecr(
        repository=self.repo.repository,
        tag=self.repo.image_uri.split(':')[-1]), # lambda_.DockerImageCode.from_image_asset(directory=os.path.join(src_root_dir,directory)),
      description='Python container lambda function for '+repository_name,
      timeout= core.Duration.minutes(1),
      tracing= lambda_.Tracing.ACTIVE,
      vpc= context.networking.vpc,
      vpc_subnets=ec2.SubnetSelection(subnet_group_name=subnet_group_name),
      security_groups=securityGroups
    )
