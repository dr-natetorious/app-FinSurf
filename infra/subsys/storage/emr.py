import os.path as path
import jsii
from infra.reusable.context import InfraContext
from aws_cdk import (
  core,
  aws_ec2 as ec2,
  aws_emr as emr,
  aws_iam as iam,
  aws_glue as g,
)

src_root_dir = path.join(path.dirname(__file__),"../..")

class MapReduceLayer(core.Construct):
  """
  Configure the Graph management layer
  """
  def __init__(self, scope: core.Construct, id: str, context:InfraContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.security_group = ec2.SecurityGroup(self,'SecurityGroup',
      vpc=context.networking.vpc,
      allow_all_outbound=True,
      description='MapReduce Subsystem',
      security_group_name='finsurf-mapreduce-group')
 
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

    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    self.cluster = emr.CfnCluster(self,'MapRed',
      name='FinSurf-MapRed',
      job_flow_role='EMR_EC2_DefaultRole',#jobFlowRole.role_name,
      service_role=serviceRole.role_name,
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
      instances= emr.CfnCluster.JobFlowInstancesConfigProperty(
        hadoop_version='2.4.0',   
        termination_protected=False,
        master_instance_fleet= emr.CfnCluster.InstanceFleetConfigProperty(
          target_spot_capacity=1,
          instance_type_configs= [
            emr.CfnCluster.InstanceTypeConfigProperty(
              instance_type='m5.xlarge',
            )
        ]),
        core_instance_fleet= emr.CfnCluster.InstanceFleetConfigProperty(
          target_spot_capacity=2,
          instance_type_configs=[
            emr.CfnCluster.InstanceTypeConfigProperty(
              instance_type='m5.xlarge',
              # ebs_configuration=emr.CfnCluster.EbsConfigurationProperty(
              #   ebs_block_device_configs=emr.CfnCluster.EbsBlockDeviceConfigProperty(
              #     volume_specification=emr.CfnCluster.VolumeSpecificationProperty(
              #       size_in_gb=250,
              #       volume_type='gp3'))
              # )
          )
        ]),
        additional_master_security_groups=[self.security_group.security_group_id],
        additional_slave_security_groups=[self.security_group.security_group_id],
        ec2_subnet_ids=[net.subnet_id for net in context.networking.vpc._select_subnet_objects(subnet_group_name='MapReduce')],
      )
    )
