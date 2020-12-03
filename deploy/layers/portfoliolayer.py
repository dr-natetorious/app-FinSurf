#!/usr/bin/env python3
from reusable.context import InfraContext
from reusable.proxyfrontend import LambdaProxyConstruct
from reusable.pythonlambda import PythonLambda
from reusable.ameritradetask import AmeritradeTask
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

class PortfolioLayer(core.Construct):
  """
  Configure the portfolio management layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__context = context
    self.__vpc = context.networking.vpc
    self.__tda_secret = context.secrets.tda_secret
    self.__tda_env_vars = self.__get_tda_auth()
    self.__configure_neptune()
    self.__configure_ingestion()
    self.__configure_gateway()
    self.__configure_monitor()
    self.__configure_fundamentals()
    self.__configure_quote_collection()

  @property
  def updates_handler(self) -> lambda_.Function:
    return self.__updates_handler

  @property
  def updates_stream(self) -> k.Stream:
    return self.__updates_stream

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

  def __configure_neptune(self)->None:
    self.subnet_group = n.CfnDBSubnetGroup(self,'SubnetGroup',
      db_subnet_group_description='Portfolio Management',
      db_subnet_group_name='portfoliomgmtsubnetgroup',
      subnet_ids= [net.subnet_id for net in self.vpc._select_subnet_objects(subnet_group_name='PortfolioMgmt')])

    self.security_group = ec2.SecurityGroup(self,'SecGroup',
      vpc=self.vpc,
      allow_all_outbound=True,
      description='Security group for PortfolioMgmt feature')
    self.security_group.add_ingress_rule(
      peer=ec2.Peer.any_ipv4(),
      connection=ec2.Port(
        protocol=ec2.Protocol.TCP,
        string_representation='Neptune',
        from_port=8182, to_port=8182))
    
    self.neptune_cluster = n.CfnDBCluster(
      self,'NeptuneCluster',
      db_subnet_group_name=self.subnet_group.db_subnet_group_name,
      deletion_protection=False,
      iam_auth_enabled=False,
      storage_encrypted=True,
      db_cluster_identifier='portfoliomgmt',
      vpc_security_group_ids=[self.security_group.security_group_id])

    counter=0
    for net in self.vpc._select_subnet_objects(subnet_group_name='PortfolioMgmt'):
      az_name = net.availability_zone
      counter+=1
      self.neptune_instance = n.CfnDBInstance(
        self,'NeptuneInstance-'+str(counter),
        availability_zone=az_name,
        db_instance_identifier='portmgmt-instance-'+str(counter),
        db_instance_class='db.t3.medium',
        allow_major_version_upgrade=False,
        auto_minor_version_upgrade=True,
        db_cluster_identifier=self.neptune_cluster.db_cluster_identifier,
        db_subnet_group_name=self.subnet_group.db_subnet_group_name)

    #n.CfnDBCluster.DBClusterRoleProperty(role_arn=cluster_role.role_arn)

  def __configure_ingestion(self)->None:
    self.__updates_stream = k.Stream(self,'PortfolioUpdates',
      encryption=k.StreamEncryption.MANAGED,
      retention_period=core.Duration.days(1),
      shard_count=1,
      stream_name='portfolio-updates')

    self.__updates_handler = PythonLambda(
      self,'UpdatesHandler',
      build_prefix='artifacts/FinSurf-PortfolioMgmt-UpdatesHandler',
      handler='updates_handler.lambda_handler',
      subnet_group_name='PortfolioMgmt',
      context=self.context,
      securityGroups= [self.security_group]).function

    self.updates_handler.add_event_source(
      source=evt.KinesisEventSource(
        stream= self.updates_stream,
        starting_position=lambda_.StartingPosition.LATEST))
    
    # Configure writing to neptune
    self.updates_handler.add_environment(
      key='NEPTUNE_ENDPOINT', value=self.neptune_cluster.attr_endpoint)

  def __configure_gateway(self) ->None:
    self.gateway = a.RestApi(self,'PortfolioMgmt')

    # Create kinesis integration
    integration_role = iam.Role(self,'KinesisIntegrationRole',
      assumed_by= iam.ServicePrincipal('apigateway.amazonaws.com'))
      
    self.updates_stream.grant_write(integration_role)

    updates = self.gateway.root.add_resource('updates')
    updates.add_method(
      http_method='POST',
      authorization_type= a.AuthorizationType.IAM,
      integration= a.AwsIntegration(
        service='kinesis',
        action='PutRecord',
        subdomain= self.updates_stream.stream_name,
        options= a.IntegrationOptions(credentials_role=integration_role)))

    pmapi = self.gateway.root.add_resource('pmapi')
    pmapi.add_proxy(
      any_method=True,
      default_integration=a.LambdaIntegration(
        handler= PythonLambda(self,'PortfolioMgmtAPI',
          build_prefix='artifacts/FinSurf-PortfolioMgmt-API',
          handler='handler.app',
          subnet_group_name='PortfolioMgmt',
          context=self.context,
          securityGroups= [self.security_group]).function))

  def __configure_monitor(self):
    monitoring_definition = AmeritradeTask(
      self,'MonitoringTask',
      context=self.context,
      directory=path.join(src_root_dir,'src/portfolio-mgmt/monitor'),
      repository_name='finsurf-pm-monitor')

    monitoring_definition.add_kinesis_subscription(stream=self.updates_stream)

    self.pm_compute_cluster = ecs.Cluster(self,'Cluster',vpc=self.vpc)
    self.monitoring_svc = ecs.FargateService(
      self,'PortMgmt-Monitoring',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=1,
      security_group=self.security_group,
      service_name='finsurf-pm-monitor',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
      task_definition=monitoring_definition.task_definition)

  def __configure_fundamentals(self) -> None:
    """
    Configure the daily check for fundamental data data.
    """    
    fundamental_definition = AmeritradeTask(
      self,'FundamentalTask',
      context=self.context,
      entry_point=[ "/usr/bin/python3", "/app/get_fundamentals.py" ],
      directory=path.join(src_root_dir,'src/portfolio-mgmt/fundamentals'),
      repository_name='finsurf-pm-fundamentals')

    fundamental_definition.add_kinesis_subscription(stream=self.updates_stream)
   
    self.fundamental_svc = ecs.FargateService(
      self,'FundamentalSvc',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=0,
      security_group=self.security_group,
      service_name='finsurf-pm-fundamental',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
      task_definition=fundamental_definition.task_definition)

    sft = ecsp.ScheduledFargateTask(
      self,'FundamentalsTask',
      schedule= scale.Schedule.cron(hour="22", minute="0", week_day="6"),
      cluster=self.pm_compute_cluster,
      desired_task_count=1,
      scheduled_fargate_task_definition_options= ecsp.ScheduledFargateTaskDefinitionOptions(
        task_definition=fundamental_definition.task_definition),
      subnet_selection=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
      vpc=self.vpc)

  def __configure_quote_collection(self) -> None:
    """
    Configure the daily check for fundamental data data.
    """    
    quote_task = AmeritradeTask(
      self,'QuoteCollectionTask',
      context=self.context,
      entry_point=[ "/usr/bin/python3", "/app/get_quotes.py" ],
      directory=path.join(src_root_dir,'src/portfolio-mgmt/fundamentals'),
      repository_name='finsurf-pm-quotes')

    quote_task.add_kinesis_subscription(stream=self.updates_stream)
   
    self.quotes_svc = ecs.FargateService(
      self,'QuoteSvc',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=0,
      security_group=self.security_group,
      service_name='finsurf-pm-quotes',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
      task_definition=quote_task.task_definition)

    sft = ecsp.ScheduledFargateTask(
      self,'QuoteScheduledTask',
      schedule= scale.Schedule.cron(hour="22", minute="0", week_day="2-6"),
      cluster=self.pm_compute_cluster,
      desired_task_count=1,      
      scheduled_fargate_task_definition_options= ecsp.ScheduledFargateTaskDefinitionOptions(
        task_definition=quote_task.task_definition),
      subnet_selection=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
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
  
