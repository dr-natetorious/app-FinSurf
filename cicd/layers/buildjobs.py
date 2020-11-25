#!/usr/bin/env python3
import os
from context import BuildContext
from layers.buckets import BucketLayer
from layers.images import BuildImagesLayer
from aws_cdk import (
  core,
  aws_codebuild as b,
  aws_iam as iam,
  aws_s3 as s3,
  aws_ecr_assets as assets,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BuildJobLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:BuildContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.build_role = iam.Role(self,'CodeBuildRole',
      assumed_by= iam.ServicePrincipal(service="codebuild.amazonaws.com"),
      description='FinSurf code building account',
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess")])

    # Create project for infrastructure
    self.cdk_infra_project = DeployInfraJob(self,'DeployInfra',
      build_image = context.build_images.cdk_deploy,
      build_role=self.build_role)

    # Configure all python build jobs here.
    self.python_projects = {
      'Earnings-DataServices':
        BuildPythonZip(self,'Earnings-DataServices',
          project_name='Earnings-DataServices',
          context=context,
          build_image = context.build_images.python_build,
          build_role=self.build_role,
          app_dir='src/earnings',
          output_name='earnings.zip'),
      'Alexa-Skill':
        BuildPythonZip(self,'Alexa-Skill',
          project_name='FinSurf-Alexa-Skill',
          context=context,
          build_image = context.build_images.python_build,
          build_role=self.build_role,
          app_dir='src/alexa-skill',
          output_name='finsurf-alexa-skill.zip')
    }    

class BuildPythonZip(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, 
    project_name:str,
    build_image:assets.DockerImageAsset, 
    context:BuildContext, 
    build_role:iam.Role,
    app_dir:str,output_name:str, **kwargs) -> None:

    super().__init__(scope, id, **kwargs)

    self.github_master_source = b.Source.git_hub(
      clone_depth=1,
      owner='dr-natetorious',
      repo='app-FinSurf',
      webhook=False
    )

    self.build_project = b.Project(self,'PythonProject',
      project_name=project_name,
      source= self.github_master_source,
      environment= b.BuildEnvironment(
        build_image= b.LinuxBuildImage.from_ecr_repository(
          repository=build_image.repository,
          tag=build_image.image_uri.split(':')[-1]),
        environment_variables={
          'APP_DIR':b.BuildEnvironmentVariable(value=app_dir)
        },
        compute_type=b.ComputeType.SMALL
      ),
      role=build_role,
      encryption_key= context.buckets.artifacts_key,
      build_spec= b.BuildSpec.from_source_filename(filename='cicd/configs/buildspec-python-zip.yml'),
      artifacts= b.Artifacts.s3(
        name=output_name,
        path="/artifacts",
        bucket=context.buckets.artifacts_bucket,
        encryption=True,
        include_build_id=False,
        package_zip=False)
      )

class DeployInfraJob(core.Construct):
  """
  Runs cdk automation
  """
  def __init__(self, scope: core.Construct, id: str, 
    build_image:assets.DockerImageAsset,
    build_role:iam.Role, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    self.github_master_source = b.Source.git_hub(
      clone_depth=1,
      owner='dr-natetorious',
      repo='app-FinSurf',
      webhook=False
    )

    self.build_project = b.Project(self, 'DeployInfra',
      project_name='Deploy-FinSurf-Infra',
      source= self.github_master_source,
      environment= b.BuildEnvironment(
        build_image= b.LinuxBuildImage.from_ecr_repository(
          repository=build_image.repository,
          tag=build_image.image_uri.split(':')[-1]),
        environment_variables={
        },
        compute_type=b.ComputeType.SMALL
      ),
      role=build_role,
      build_spec= b.BuildSpec.from_source_filename(filename='cicd/configs/buildspec-cdk-infra.yml'),
    )
