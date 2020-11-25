#!/usr/bin/env python3
import os
from layers.buckets import BucketLayer
from aws_cdk import (
  core,
  aws_codebuild as b,
  aws_iam as iam,
  aws_s3 as s3,
  aws_kms as kms,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BuildJobLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, buckets:BucketLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.github_master_source = b.Source.git_hub(
      clone_depth=1,
      owner='dr-natetorious',
      repo='app-FinSurf',
      webhook=False
    )

    # self.github_private_source = b.Source.git_hub(
    #   owner='dr-natetorious',
    #   repo='app-FinSurf',
    #   webhook=True,
    #   webhook_filters=[
    #     b.FilterGroup.in_event_of(b.EventAction.PUSH)
    #     .and_branch_is_not('master')
    #   ]
    # )

    self.build_role = iam.Role(self,'CodeBuildRole',
      assumed_by= iam.ServicePrincipal(service="codebuild.amazonaws.com"),
      description='FinSurf code building account',
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess")])

    self.earnings_project = b.Project(self,'Earnings',
      project_name='Earnings-DataServices',
      source= self.github_master_source,
      environment= b.BuildEnvironment(
        build_image= b.LinuxBuildImage.from_docker_registry(name='python:3.8'),
        environment_variables={
          'APP_DIR', b.BuildEnvironmentVariable(value='/src/earnings')
        },
        compute_type=b.ComputeType.SMALL),
      role=self.build_role,
      encryption_key= buckets.artifacts_key,
      build_spec= b.BuildSpec.from_source_filename(filename='src/earnings/buildspec.yml'),
      artifacts= b.Artifacts.s3(
        identifier='Primary-Artifacts',
        bucket=buckets.artifacts_bucket,
        encryption=True,
        path='/artifacts',
        include_build_id=False,
        package_zip=True)
      )