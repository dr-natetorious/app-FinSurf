#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from infra.reusable.proxyfrontend import LambdaProxyConstruct
from infra.reusable.containerlambda import ContainerLambda

from aws_cdk import (
  core,
  aws_iam as iam,
  aws_apigateway as a,
  aws_ec2 as ec2,
  aws_lambda as lambda_,
  aws_secretsmanager as sm,
  aws_ssm as ssm,
)

class AccountLinkingLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
      
    self.python_lambda = ContainerLambda(self,'AccountLinking',
      directory='src/account-linking',
      handler='handler.app',
      subnet_group_name='AccountLinking',
      context=context)

    self.frontend_proxy = LambdaProxyConstruct(self,'AccountLinkingAPI',
      handler=self.python_lambda.function,
      context=context)

    self.__configure_secrets(
      function=self.python_lambda.function,
      secret=context.secrets.tda_secret)

    self.__configure_tda_auth(
      function=self.python_lambda.function)

    self.url = self.frontend_proxy.rest_api.url

  def __configure_secrets(self, function:lambda_.Function, secret:sm.Secret) -> None:
    secret.grant_write(function.role)
    function.add_environment('TDA_SECRET_ID', secret.secret_full_arn)

  def __configure_tda_auth(self,function:lambda_.Function) -> None:    
    """
    Fetches the OAuth2 values from SSM
    """
    redirect_uri = ssm.StringParameter.from_string_parameter_name(self,'TDA-Redirect-Parameter',
      string_parameter_name='/app-FinSurf/tdameritrade/redirect_uri')
    function.add_environment(
      key='TDA_REDIRECT_URI', value=redirect_uri.string_value)

    client_id = ssm.StringParameter.from_string_parameter_name(self, 'TDA_CLIENT_ID',
      string_parameter_name='/app-FinSurf/tdameritrade/client_id')
    function.add_environment(key='TDA_CLIENT_ID', value=client_id.string_value)
  