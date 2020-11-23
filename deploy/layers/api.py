#!/usr/bin/env python3
from aws_cdk import (
    aws_apigateway as api,
    aws_kinesis as ks,
    aws_iam as iam,
    core
)

class ApiLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, stream:ks.Stream, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.gateway = api.RestApi(self,'EmailServices')
    resource = self.gateway.root.add_resource('send-mail')

    role = iam.Role(self,'Apig-to-Kinesis',
      assumed_by= iam.ServicePrincipal('apigateway.amazonaws.com'),
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('AmazonKinesisFullAccess')])
    
    kinesisIntegration = api.AwsIntegration(
      service='kinesis',
      action='PutRecord',
      subdomain= stream.stream_name,
      options= api.IntegrationOptions(credentials_role=role))
      
    self.post_method = resource.add_method('POST', kinesisIntegration)

