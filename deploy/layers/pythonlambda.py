#!/usr/bin/env python3
import typing
from context import InfraContext
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
  core
)

class PythonLambda(core.Construct):
  """
  Represents a construct for a default Python repository.
  """
  def __init__(self, scope: core.Construct, id: str, 
    build_prefix:str,
    subnet_group_name:str,
    context:InfraContext,
    handler:str,
    securityGroups:typing.Optional[typing.List[ec2.SecurityGroup]]=None,
    **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    bucket_arn = ssm.StringParameter.from_string_parameter_name(self,'artifact_bucket',
      string_parameter_name='/app-FinSurf/artifacts/bucket_name')

    code_bucket = s3.Bucket.from_bucket_arn(self, 'code_bucket',
      bucket_arn=bucket_arn.string_value)

    deps_layer = lambda_.LayerVersion(self, 'Dependencies',
      code = lambda_.Code.from_bucket(
        bucket=code_bucket, 
        key= build_prefix+'/deps.zip'),
      compatible_runtimes= [ lambda_.Runtime.PYTHON_3_8],
      description='Runtime dependencies for Python Lambda '+id)

    self.function = lambda_.Function(self, 'Function',
      description='Python lambda function for '+id,
      handler=handler,
      code= lambda_.Code.from_bucket(bucket=code_bucket, key=build_prefix +'/app.zip'),
      timeout= core.Duration.minutes(1),
      layers=[ deps_layer ],
      tracing= lambda_.Tracing.ACTIVE,
      runtime = lambda_.Runtime.PYTHON_3_8,
      vpc= context.networking.vpc,
      vpc_subnets=ec2.SubnetSelection(subnet_group_name=subnet_group_name),
      security_groups=securityGroups)
