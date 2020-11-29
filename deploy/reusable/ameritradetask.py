#!/usr/bin/env python3
from reusable.context import InfraContext
from reusable.proxyfrontend import LambdaProxyConstruct
from reusable.pythonlambda import PythonLambda
import os.path as path
from aws_cdk import (
  core,
  aws_ecr_assets as assets,
  aws_ecs as ecs,
  aws_kinesis as k,
  aws_iam as iam,
  aws_apigateway as a,
  aws_ec2 as ec2,
  aws_lambda as lambda_,
  aws_lambda_event_sources as evt,
  aws_secretsmanager as sm,
  aws_ssm as ssm,
  aws_logs as logs,
  aws_neptune as n,
  aws_logs_destinations as dest,
  aws_ecs_patterns as ecsp,
  aws_applicationautoscaling as scale,
)

src_root_dir = path.join(path.dirname(__file__),"../..")

class AmeritradeTask(core.Construct):

  @property
  def vpc(self) -> ec2.Vpc:
    return self.__vpc

  @property
  def tda_secret(self) -> sm.Secret:
    return self.__tda_secret

  @property
  def context(self) -> InfraContext:
    return self.__context

  @property
  def tda_env_vars(self)->dict:
    return self.__tda_env_vars

  @property
  def task_definition(self) -> ecs.FargateTaskDefinition:
    return self.__task_definition

  def __init__(
    self, scope: core.Construct, id: str,
    directory:str,
    repository_name:str,
    context:InfraContext,
    log_group_name:str=None,
    **kwargs) -> None:
    """
    Creates the ameritrade container
    """
    super().__init__(scope, id, **kwargs)
    self.__context = context
    self.__vpc = context.networking.vpc
    self.__tda_secret = context.secrets.tda_secret
    self.__tda_env_vars = self.__get_tda_auth()

    self.__build_task(
      directory=directory,
      repository_name=repository_name,
      log_group_name=log_group_name)

  def __build_task(self,
    directory:str,
    repository_name:str,
    log_group_name:str=None):

    if log_group_name is None:
      log_group_name = '/finsurf/'+repository_name

    task_definition = ecs.FargateTaskDefinition(
      self,'FargateTaskDefinition')
    self.tda_secret.grant_read(task_definition.task_role)
    
    image = ecs.ContainerImage.from_docker_image_asset(
      asset=assets.DockerImageAsset(
        self,'DockerAsset',
        directory=path.join(src_root_dir,directory),
        repository_name=repository_name))

    self.log_group = logs.LogGroup(
      self,'LogGroup',
      log_group_name=log_group_name,
      removal_policy=core.RemovalPolicy.DESTROY,
      retention=logs.RetentionDays.TWO_WEEKS)
    
    self.env_vars = {}
    self.env_vars.update(self.tda_env_vars)
    task_definition.add_container('DefaultContainer',
      image=image,
      logging= ecs.AwsLogDriver(
        log_group=self.log_group,
        stream_prefix=repository_name,
      ),
      environment=self.env_vars,
      essential=True)

    self.__task_definition = task_definition

  def add_kinesis_subscription(self, stream:k.Stream, filter_pattern:logs.FilterPattern=None) -> None:
    if filter_pattern is None:
      filter_pattern=logs.FilterPattern.any_term('data')
    
    logs.SubscriptionFilter(
      self,'KinesisSubscription',
      log_group= self.log_group,
      filter_pattern=filter_pattern,
      destination=dest.KinesisDestination(stream = stream))

  def __get_tda_auth(self) -> None:    
    """
    Fetches the OAuth2 values from SSM
    """
    redirect_uri = ssm.StringParameter.from_string_parameter_name(self,'TDA-Redirect-Parameter',
      string_parameter_name='/app-FinSurf/tdameritrade/redirect_uri')    

    client_id = ssm.StringParameter.from_string_parameter_name(self, 'TDA_CLIENT_ID',
      string_parameter_name='/app-FinSurf/tdameritrade/client_id')

    return {
      'TDA_CLIENT_ID':client_id.string_value,
      'TDA_REDIRECT_URI':redirect_uri.string_value,
      'TDA_SECRET_ID':self.tda_secret.secret_arn
    }
