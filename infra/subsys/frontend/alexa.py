#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from infra.reusable.containerlambda import ContainerLambda
from infra.subsys.frontend.earnings_api import EarningsApiLayer
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
  Configure and deploy the Alexa Skill
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
  
    self.python_lambda = ContainerLambda(self,'FinSurf-Skill',
      repository_name='finsurf-lambda-container_alexaskill',
      directory='src/alexa-skill',
      subnet_group_name='Alexa',
      context=context)

    self.__build(self.python_lambda.function, context)

  def __build(self,function:lambda_.Function, context:InfraContext):
    function.add_environment('EARNINGS_API', context.earnings_api.url)
    function.add_environment('FRIENDLY_NAME_API', context.fnapi.url)

    function.add_permission(
      id='Alexa-Trigger',
      action='lambda:InvokeFunction',
      principal= iam.ServicePrincipal(
        service="alexa-appkit.amazon.com"),
      event_source_token='amzn1.ask.skill.9f4cb90e-4c57-41c2-a942-c2e6685888ba',
    )
