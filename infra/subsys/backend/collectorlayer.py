#!/usr/bin/env python3
from infra.reusable.context import InfraContext
from infra.reusable.proxyfrontend import LambdaProxyConstruct
from infra.reusable.pythonlambda import PythonLambda
from infra.reusable.ameritradetask import AmeritradeTask
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

src_root_dir = path.join(path.dirname(__file__),"../../..")

class CollectorLayer(core.Construct):
  """
  Configure the data collections layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__context = context
    self.__vpc = context.networking.vpc
    self.__tda_secret = context.secrets.tda_secret
    self.__tda_env_vars = self.__get_tda_auth()
    self.__configure_base()
    self.__configure_fundamentals()
    self.__configure_quote_collection()

  @property
  def quotes_stream(self) -> k.Stream:
    return self.__quotes_stream

  @property
  def fundamental_stream(self) -> k.Stream:
    return self.__fundamental_stream

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

  def __configure_base(self)->None:
    """
    Setup base dependencies
    """
    self.__quotes_stream = k.Stream(self,'QuoteStream',
      encryption=k.StreamEncryption.MANAGED,
      retention_period=core.Duration.days(7),
      shard_count=1,
      stream_name='finsurf-incoming-quotes')

    self.__fundamental_stream = k.Stream(self,'FundamentalStream',
      encryption=k.StreamEncryption.MANAGED,
      retention_period=core.Duration.days(7),
      shard_count=1,
      stream_name='finsurf-incoming-fundamentals')

    self.pm_compute_cluster = ecs.Cluster(self,'Cluster',vpc=self.vpc)
    self.security_group = ec2.SecurityGroup(self,'CollectorComponents',
      vpc=self.vpc,
      allow_all_outbound=True,
      description='Security Group for the CollectorLayer')

  def __configure_fundamentals(self) -> None:
    """
    Configure the daily check for fundamental data data.
    """    
    fundamental_definition = AmeritradeTask(
      self,'FundamentalTask',
      context=self.context,
      entry_point=[ "/usr/bin/python3", "/app/get_fundamentals.py" ],
      directory=path.join(src_root_dir,'src/collectors'),
      repository_name='finsurf-pm-fundamentals',
      env_vars={'STREAM_NAME':self.quotes_stream.stream_name})

    self.fundamental_stream.grant_write(fundamental_definition.task_definition.task_role)

    #fundamental_definition.add_kinesis_subscription(stream=self.fundamental_stream
   
    self.fundamental_svc = ecs.FargateService(
      self,'FundamentalSvc',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=0,
      security_group=self.security_group,
      service_name='finsurf-pm-fundamental',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='Collections'),
      task_definition=fundamental_definition.task_definition)

    sft = ecsp.ScheduledFargateTask(
      self,'FundamentalsTask',
      schedule= scale.Schedule.cron(hour="22", minute="0", week_day="6"),
      cluster=self.pm_compute_cluster,
      desired_task_count=1,
      scheduled_fargate_task_definition_options= ecsp.ScheduledFargateTaskDefinitionOptions(
        task_definition=fundamental_definition.task_definition),
      subnet_selection=ec2.SubnetSelection(subnet_group_name='Collections'),
      vpc=self.vpc)

  def __configure_quote_collection(self) -> None:
    """
    Configure the daily check for fundamental data data.
    """
    quote_task = AmeritradeTask(
      self,'QuoteCollectionTask',
      context=self.context,
      entry_point=[ "/usr/bin/python3", "/app/get_quotes.py" ],
      directory=path.join(src_root_dir,'src/collectors'),
      repository_name='finsurf-incoming-quotes',
      env_vars={'STREAM_NAME':self.quotes_stream.stream_name})
    
    #quote_task.add_kinesis_subscription(stream=self.quotes_stream)
    self.quotes_stream.grant_write(quote_task.task_definition.task_role)
   
    self.quotes_svc = ecs.FargateService(
      self,'QuoteSvc',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=1,
      security_group=self.security_group,
      service_name='finsurf-incoming-quotes',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='Collections'),
      task_definition=quote_task.task_definition)    

    sft = ecsp.ScheduledFargateTask(
      self,'QuoteScheduledTask',
      schedule= scale.Schedule.cron(hour="13-22/4", minute="30", week_day="6"), #week_day="2-6"),
      cluster=self.pm_compute_cluster,
      desired_task_count=1,      
      scheduled_fargate_task_definition_options= ecsp.ScheduledFargateTaskDefinitionOptions(
        task_definition=quote_task.task_definition),
      subnet_selection=ec2.SubnetSelection(subnet_group_name='Collections'),
      vpc=self.vpc)

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
  
