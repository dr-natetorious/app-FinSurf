#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from aws_cdk import (
  core,
  aws_apigateway as a,
  aws_lambda as lambda_,
  aws_apigateway as a,
  aws_route53 as dns,
  aws_route53_targets as dns_t,
  aws_certificatemanager as acm,
)

class LambdaProxyConstruct(core.Construct):
  """
  Configures a lambda behind APIGateway
  """
  def __init__(self, scope: core.Construct, id: str,
    handler:lambda_.Function,
    context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.rest_api = a.LambdaRestApi(self,id,
      options=a.RestApiProps(),
      handler=handler,
      proxy=True,
      description='Frontend proxy for '+handler.function_name)
