#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from infra.reusable.containerlambda import ContainerLambda
from infra.reusable.proxyfrontend import LambdaProxyConstruct
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

class EarningsApiLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    python_lambda = ContainerLambda(self,'EarningsFunction',
      directory='src/earnings',
      subnet_group_name='EarningApi',
      repository_name='finsurf-lambda-container_earnings',
      context=context)

    self.flask_lambda = python_lambda.function
    
    self.cache_table = d.Table(self,'EarningCalendarCache',
      billing_mode= d.BillingMode.PAY_PER_REQUEST,
      partition_key=d.Attribute(name='PartitionKey', type=d.AttributeType.STRING),
      sort_key= d.Attribute(name='SortKey', type=d.AttributeType.STRING),
      time_to_live_attribute= 'Expiration',
      server_side_encryption=True
    )

    self.flask_lambda.add_environment(
      key='CACHE_TABLE', value=self.cache_table.table_name)

    self.flask_lambda.add_to_role_policy(
      statement= iam.PolicyStatement(    
        actions=["dynamodb:*"],
        effect=iam.Effect.ALLOW,
        resources=[self.cache_table.table_arn]
      ))

    self.frontend_proxy = LambdaProxyConstruct(self,'EarningsApi',
      handler=self.flask_lambda,
      context=context)

    self.url = self.frontend_proxy.rest_api.url
