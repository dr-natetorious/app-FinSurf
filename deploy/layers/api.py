#!/usr/bin/env python3
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_kms as kms,
  aws_apigateway as a,
  aws_dynamodb as d,
  aws_lambda as lambda_,
  aws_iam as iam,
  aws_ssm as ssm,
  core
)

class EarningsApiLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    bucket_name = ssm.StringParameter.from_string_parameter_name(self,'artifact_bucket',
      string_parameter_name='/app-FinSurf/artifacts/bucket_name')

    code_bucket = s3.Bucket.from_bucket_name(
      self, 'code_bucket',
      bucket_name=bucket_name)

    self.flask_lambda = lambda_.Function(self, 'FlaskFunction',
      handler='webapp.app',
      code= lambda_.Code.from_bucket(bucket=code_bucket, key='artifacts/earnings.zip'),
      timeout= core.Duration.minutes(1),
      tracing= lambda_.Tracing.ACTIVE,
      runtime = lambda_.Runtime.PYTHON_3_8,
      environment={})

    self.rest_api = a.LambdaRestApi(self,'EarningsApi',
      handler=self.flask_lambda,
      proxy=True,
      description='The FinSurf Earnings API')

    self.encryption_key = kms.Key(self,'EncryptionKey',
      alias='finsurf/earnings',
      description='Encryption key for Earnings feature',
      enable_key_rotation=True)

    self.cache_table = d.Table(self,'EarningCalendarCache',
      table_name='FinSurf-Earnings',
      billing_mode= d.BillingMode.PAY_PER_REQUEST,
      partition_key=d.Attribute(name='PartitionKey', type=d.AttributeType.STRING),
      sort_key= d.Attribute(name='SortKey', type=d.AttributeType.STRING),
      time_to_live_attribute= d.Attribute(name='Expiration', type= d.AttributeType.NUMBER),
      encryption_key=self.encryption_key
    )
