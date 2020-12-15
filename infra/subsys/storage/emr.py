import os.path as path
from infra.reusable.context import InfraContext
from aws_cdk import (
  core,
  aws_ec2 as ec2,
  aws_emr as emr,
  aws_iam as iam,
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

    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    # self.cluster = emr.CfnCluster(self,'MapRed',
    #   name='FinSurf-MapRed',
    #   job_flow_role=jobFlowRole.role_name,
    #   service_role=serviceRole.role_name,
    #   instances= emr.CfnCluster.JobFlowInstancesConfigProperty(
    #     master_instance_fleet= emr.CfnCluster.InstanceFleetConfigProperty(
    #       instance_type_configs= [
    #         emr.CfnCluster.InstanceTypeConfigProperty(
    #           instance_type='CORE')
    #     ]),
    #     ec2_subnet_ids=[net.subnet_id for net in context.networking.vpc._select_subnet_objects(subnet_group_name='MapReduce')],
    #   )
    # )