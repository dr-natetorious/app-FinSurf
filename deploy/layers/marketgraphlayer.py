#!/usr/bin/env python3
from reusable.context import InfraContext
from reusable.proxyfrontend import LambdaProxyConstruct
from reusable.pythonlambda import PythonLambda
from reusable.ameritradetask import AmeritradeTask
from layers.collectorlayer import CollectorLayer
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

class MarketGraphLayer(core.Construct):
  """
  Configure the Graph management layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__context = context
    self.__vpc = context.networking.vpc
    self.__configure_neptune()
    #self.__configure_ingestion()

  @property
  def updates_handler(self) -> lambda_.Function:
    return self.__updates_handler

  @property
  def vpc(self) -> ec2.Vpc:
    return self.__vpc

  @property
  def context(self) -> InfraContext:
    return self.__context

  @property
  def collectorlayer(self) -> CollectorLayer:
    return self.__context.collectors

  @property
  def quotes_stream(self) -> k.Stream:
    return self.collectorlayer.quotes_stream

  @property
  def fundamental_stream(self) -> k.Stream:
    return self.collectorlayer.fundamental_stream

  def __configure_neptune(self)->None:
    self.subnet_group = n.CfnDBSubnetGroup(self,'SubnetGroup',
      db_subnet_group_description='MarketGraph Subnet',
      db_subnet_group_name='marketgraph-subnetgroup',
      subnet_ids= [net.subnet_id for net in self.vpc._select_subnet_objects(subnet_group_name='MarketGraph')])

    self.security_group = ec2.SecurityGroup(self,'SecGroup',
      vpc=self.vpc,
      allow_all_outbound=True,
      description='Security group for MarketGraph feature')
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
      db_cluster_identifier='marketgraph',
      vpc_security_group_ids=[self.security_group.security_group_id])

    counter=0
    for net in self.vpc._select_subnet_objects(subnet_group_name='MarketGraph'):
      az_name = net.availability_zone
      counter+=1
      neptune_instance = n.CfnDBInstance(
        self,'NeptuneInstance-'+str(counter),
        availability_zone=az_name,
        db_instance_identifier='marketgraph-instance-'+str(counter),
        db_instance_class='db.t3.medium',
        allow_major_version_upgrade=False,
        auto_minor_version_upgrade=True,
        db_cluster_identifier=self.neptune_cluster.db_cluster_identifier,
        db_subnet_group_name=self.subnet_group.db_subnet_group_name)
      
      neptune_instance.node.add_dependency(self.neptune_cluster)

    #n.CfnDBCluster.DBClusterRoleProperty(role_arn=cluster_role.role_arn)

  def __configure_ingestion(self)->None:
    self.__updates_handler = PythonLambda(
      self,'FinSurf-GraphBuilder',
      build_prefix='artifacts/FinSurf-GraphBuilder',
      handler='handlers.kinesis_event_handler',
      subnet_group_name='MarketGraph',
      context=self.context,
      securityGroups= [self.security_group]).function

    self.updates_handler.add_event_source(
      source=evt.KinesisEventSource(
        stream= self.quotes_stream,
        starting_position=lambda_.StartingPosition.TRIM_HORIZON))

    self.updates_handler.add_event_source(
      source=evt.KinesisEventSource(
        stream= self.fundamental_stream,
        starting_position=lambda_.StartingPosition.TRIM_HORIZON))

    # Configure writing to neptune
    self.updates_handler.add_environment(
      key='NEPTUNE_ENDPOINT', value=self.neptune_cluster.attr_endpoint)
