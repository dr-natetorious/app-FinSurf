#!/usr/bin/env python3
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

class EarningsApiLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    bucket_arn = ssm.StringParameter.from_string_parameter_name(self,'artifact_bucket',
      string_parameter_name='/app-FinSurf/artifacts/bucket_name')

    code_bucket = s3.Bucket.from_bucket_arn(self, 'code_bucket',
      bucket_arn=bucket_arn.string_value)
    
    self.cache_table = d.Table(self,'EarningCalendarCache',
      billing_mode= d.BillingMode.PAY_PER_REQUEST,
      partition_key=d.Attribute(name='PartitionKey', type=d.AttributeType.STRING),
      sort_key= d.Attribute(name='SortKey', type=d.AttributeType.STRING),
      time_to_live_attribute= 'Expiration',
      server_side_encryption=True
    )

    self.flask_lambda = lambda_.Function(self, 'FlaskFunction',
      handler='webapp.app',
      code= lambda_.Code.from_bucket(bucket=code_bucket, key='artifacts/earnings.zip'),
      timeout= core.Duration.minutes(1),      
      tracing= lambda_.Tracing.ACTIVE,
      runtime = lambda_.Runtime.PYTHON_3_8,
      vpc= context.networking.vpc,
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='EarningApi'),
      environment={
        'CACHE_TABLE': self.cache_table.table_name
      })

    self.flask_lambda.add_to_role_policy(
      statement= iam.PolicyStatement(    
        actions=["dynamodb:*"],
        effect=iam.Effect.ALLOW,
        resources=[self.cache_table.table_arn]
      ))

    self.rest_api = a.LambdaRestApi(self,'EarningsApi',
      handler=self.flask_lambda,
      proxy=True,
      description='The FinSurf Earnings API')
