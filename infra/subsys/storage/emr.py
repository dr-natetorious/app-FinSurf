import os.path as path
import jsii
from infra.reusable.context import InfraContext
from aws_cdk import (
  core,
  aws_ec2 as ec2,
  aws_emr as emr,
  aws_iam as iam,
  aws_glue as g,
  aws_s3 as s3,
)

src_root_dir = path.join(path.dirname(__file__),"../..")
services = {
  9870: 'HDFS Name Name',
  18080: 'Spark History',
  8888: 'Hue',
  9443: 'JupyterHub',
  8088: 'Resource Manager',
  9864: 'HDFS DataNode',
  8042: 'Node Manager',
  443: 'Https',
  80: 'Http'
}

class MapReduceLayer(core.Construct):
  """
  Configure the Graph management layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    # Configure the security groups
    self.security_group = ec2.SecurityGroup(self,'SecurityGroup',
      vpc=context.networking.vpc,
      allow_all_outbound=True,
      description='MapReduce Subsystem',
      security_group_name='finsurf-mapreduce-group')

    for port in services.keys():
      self.security_group.add_ingress_rule(
        peer = ec2.Peer.any_ipv4(),
        connection= ec2.Port(
          protocol= ec2.Protocol.TCP,
          from_port=port, to_port=port,
          string_representation=services[port])
      )

    self.security_group.add_ingress_rule(
      peer = ec2.Peer.any_ipv4(),
      connection= ec2.Port(
        protocol= ec2.Protocol.UDP,
        from_port=0, to_port=65535,
        string_representation='Allow All UDP Traffic')
    )

    self.security_group.add_ingress_rule(
      peer = ec2.Peer.any_ipv4(),
      connection= ec2.Port(
        protocol= ec2.Protocol.TCP,
        from_port=0, to_port=65535,
        string_representation='Allow All TCP Traffic')
    )

    # Setup roles...
    jobFlowRole = iam.Role(self,'JobFlowRole', assumed_by=iam.ServicePrincipal(service='ec2.amazonaws.com'), 
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonElasticMapReduceforEC2Role')
      ]
    )

    serviceRole = iam.Role(self,'ServiceRole', assumed_by=iam.ServicePrincipal(service='elasticmapreduce.amazonaws.com'),
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonElasticMapReduceRole')
      ]
    )

    self.database = g.Database(self,'GlueStore',
      database_name='finsurf')

    self.bucket = s3.Bucket(self,'Bucket',
      removal_policy= core.RemovalPolicy.DESTROY)

    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    self.cluster = emr.CfnCluster(self,'MapRed',
      name='FinSurf-MapRed',
      job_flow_role='EMR_EC2_DefaultRole',#jobFlowRole.role_name,
      service_role=serviceRole.role_name,
      log_uri='s3://'+self.bucket.bucket_name+'/logs',
      release_label='emr-6.2.0',
      applications=[
        emr.CfnCluster.ApplicationProperty(name='Spark'),
        emr.CfnCluster.ApplicationProperty(name='Hue'),
        emr.CfnCluster.ApplicationProperty(name='Hive'),
        emr.CfnCluster.ApplicationProperty(name='JupyterHub'),
      ],
      configurations= [
        emr.CfnCluster.ConfigurationProperty(
          classification='spark-hive-site',
          configuration_properties={
            'hive.metastore.client.factory.class':'com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory'
          })
      ],
      managed_scaling_policy= emr.CfnCluster.ManagedScalingPolicyProperty(
        compute_limits=emr.CfnCluster.ComputeLimitsProperty(
          minimum_capacity_units=1,
          maximum_capacity_units=25,
          unit_type='InstanceFleetUnits'
        )
      ),
      instances= emr.CfnCluster.JobFlowInstancesConfigProperty(
        #hadoop_version='2.4.0',   
        termination_protected=False,
        master_instance_fleet= emr.CfnCluster.InstanceFleetConfigProperty(
          target_spot_capacity=1,
          instance_type_configs= [
            emr.CfnCluster.InstanceTypeConfigProperty(
              instance_type='r6g.2xlarge',
            )
        ]),
        core_instance_fleet= emr.CfnCluster.InstanceFleetConfigProperty(
          target_spot_capacity=1,
          instance_type_configs=[
            emr.CfnCluster.InstanceTypeConfigProperty(
              instance_type='r6g.2xlarge',
              ebs_configuration= emr.CfnCluster.EbsConfigurationProperty(
                ebs_block_device_configs=[
                  emr.CfnCluster.EbsBlockDeviceConfigProperty(
                  volume_specification=emr.CfnCluster.VolumeSpecificationProperty(
                    size_in_gb=250,
                    volume_type='gp2'))
                ]
              )
          )
        ]),
        additional_master_security_groups=[self.security_group.security_group_id],
        additional_slave_security_groups=[self.security_group.security_group_id],
        ec2_subnet_ids=[net.subnet_id for net in context.networking.vpc._select_subnet_objects(subnet_group_name='MapReduce')],
      )
    )
