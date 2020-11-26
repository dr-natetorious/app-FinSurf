#!/usr/bin/env python3
from context import InfraContext
from layers.api import EarningsApiLayer
from layers.pythonlambda import PythonLambda
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

class AlexaSkillLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
  
    self.python_lambda = PythonLambda(self,'AlexaSkill',
      build_prefix='artifacts/FinSurf-Alexa-Skill',
      handler='handler.lambda_handler',
      subnet_group_name='Alexa',
      context=context)

    self.__build(self.python_lambda.function, context.earnings_api.rest_api)

  def __build(self,function:lambda_.Function, earnings_api:a.LambdaRestApi):
    function.add_environment('EARNINGS_API', earnings_api.url)

    function.add_permission(
      id='Alexa-Trigger',
      action='lambda:InvokeFunction',
      principal= iam.ServicePrincipal(
        service="alexa-appkit.amazon.com"),
      event_source_token='amzn1.ask.skill.9f4cb90e-4c57-41c2-a942-c2e6685888ba',
    )
