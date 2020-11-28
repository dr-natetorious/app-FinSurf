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
)

src_root_dir = path.join(path.dirname(__file__),"../..")

class PortfolioLayer(core.Construct):
  """
  Configure the portfolio management layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__configure_neptune(vpc=context.networking.vpc)
    self.__configure_ingestion(context=context)
    self.__configure_gateway(context)
    self.__configure_monitor(
      vpc=context.networking.vpc,
      secret=context.secrets.tda_secret)

  @property
  def updates_handler(self) -> lambda_.Function:
    return self.__updates_handler

  @property
  def updates_stream(self) -> k.Stream:
    return self.__updates_stream

  def __configure_neptune(self, vpc:ec2.Vpc)->None:
    self.subnet_group = n.CfnDBSubnetGroup(self,'SubnetGroup',
      db_subnet_group_description='Portfolio Management',
      db_subnet_group_name='portfoliomgmtsubnetgroup',
      subnet_ids= [net.subnet_id for net in vpc._select_subnet_objects(subnet_group_name='PortfolioMgmt')])

    self.security_group = ec2.SecurityGroup(self,'SecGroup',
      vpc=vpc,
      allow_all_outbound=True,
      description='Security group for PortfolioMgmt feature')
    self.security_group.add_ingress_rule(
      peer=ec2.Peer.any_ipv4(),
      connection=ec2.Port(
        protocol=ec2.Protocol.TCP,
        string_representation='Neptune',
        from_port=8182, to_port=8182))
    
    # cluster_role = iam.Role(self,'NeptuneClusterRole',
    #   assumed_by= iam.ServicePrincipal(service='neptune.amazonaws.com'))
    
    self.neptune_cluster = n.CfnDBCluster(
      self,'NeptuneCluster',
      db_subnet_group_name=self.subnet_group.db_subnet_group_name,
      deletion_protection=False,
      #associated_roles=[cluster_role],
      iam_auth_enabled=False,
      storage_encrypted=True,
      db_cluster_identifier='portfoliomgmt',
      vpc_security_group_ids=[self.security_group.security_group_id])

    counter=0
    for net in vpc._select_subnet_objects(subnet_group_name='PortfolioMgmt'):
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

  def __configure_ingestion(self, context:InfraContext)->None:
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
      context=context,
      securityGroups= [self.security_group]).function

    self.updates_handler.add_event_source(
      source=evt.KinesisEventSource(
        stream= self.updates_stream,
        starting_position=lambda_.StartingPosition.LATEST))
    
    # Configure writing to neptune
    self.updates_handler.role.add_managed_policy(
      policy=iam.ManagedPolicy.from_aws_managed_policy_name('NeptuneFullAccess'))
    self.updates_handler.add_environment(
      key='NEPTUNE_ENDPOINT', value=self.neptune_cluster.attr_endpoint)

  def __configure_gateway(self, context) ->None:
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
          context=context,
          securityGroups= [self.security_group]).function
      ))

  def __configure_monitor(self, vpc:ec2.Vpc, secret:sm.Secret):
    task_definition = ecs.FargateTaskDefinition(
      self,'TaskDefinition')
    
    image = ecs.ContainerImage.from_docker_image_asset(
      asset=assets.DockerImageAsset(
        self,'DockerAsset',
        directory=path.join(src_root_dir,'src/portfolio-mgmt/monitor'),
        repository_name='finsurf-pm-monitor'))

    log_group = logs.LogGroup(
      self,'MonitoringLogGroup',
      log_group_name='/finsurf/pm/monitoring',
      removal_policy=core.RemovalPolicy.DESTROY,
      retention=logs.RetentionDays.TWO_WEEKS)

    logs.SubscriptionFilter(
      self,'MonitoringFilter',
      log_group= log_group,
      filter_pattern=logs.FilterPattern.any_term('data'),
      destination=dest.KinesisDestination(
        stream = self.updates_stream))

    env_vars = {}
    env_vars.update(self.__get_tda_auth(secret))
    task_definition.add_container(
      'MonitoringContainer',
      image=image,
      logging= ecs.AwsLogDriver(        
        log_group=log_group,
        stream_prefix='pm-monitoring'
      ),
      environment=env_vars,
      essential=True)

    secret.grant_read(task_definition.task_role)
    
    self.pm_compute_cluster = ecs.Cluster(self,'Cluster',vpc=vpc)
    self.monitoring_svc = ecs.FargateService(
      self,'PortMgmt-Monitoring',
      cluster=self.pm_compute_cluster,
      assign_public_ip=False,
      desired_count=1,
      security_group=self.security_group,
      service_name='finsurf-pm-monitor',
      vpc_subnets=ec2.SubnetSelection(subnet_group_name='PortfolioMgmt'),
      task_definition=task_definition)

  def __get_tda_auth(self,secret:sm.Secret) -> None:    
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
      'TDA_SECRET_ID':secret.secret_arn
    }
  
