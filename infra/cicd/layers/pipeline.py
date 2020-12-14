#!/usr/bin/env python3
import os
from infra.cicd.context import BuildContext
from infra.cicd.layers.buckets import BucketLayer
from infra.cicd.layers.buildjobs import BuildJobLayer
from aws_cdk import (
  core,
  aws_iam as iam,
  aws_s3 as s3,
  aws_codebuild as b,
  aws_codepipeline as p,
  aws_codepipeline_actions as actions,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class CodePipelineLayer(core.Construct):
  
  @property 
  def artifacts_bucket(self)-> s3.Bucket:
    return self.__bucket

  @property
  def buildjoblayer(self) -> BuildJobLayer:
    return self.__buildjoblayer
  
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:BuildContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__bucket = context.buckets.artifacts_bucket
    self.__buildjoblayer = context.build_projects

    role = iam.Role(self,'CodePipeline',
      assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
      description='Code deployment pipeline for app-FinSurf')

    self.core_pipeline = p.Pipeline(self, 'cicd-pipeline',
      pipeline_name='FinSurf-ContInt-ContDep',
      artifact_bucket= self.artifacts_bucket,
      role=role)

    # # Add trigger
    github_init_artifact = p.Artifact(artifact_name='github-init-artifact')

    self.core_pipeline.add_stage(
      stage_name='Trigger',
      actions=[
        # actions.S3SourceAction(
        #   action_name='Start-by-S3',
        #   bucket=self.core_pipeline.artifact_bucket,
        #   bucket_key='temp-does-not-exist',
        #   output=github_init_artifact)
        actions.GitHubSourceAction(
          action_name='Init-from-GitHub',
          owner='dr-natetorious',
          repo='app-FinSurf',
          # Note: The secret must be:
          #  1. formated non-json using the literal value from github.com/settings/tokens
          #     e.g., 1837422b*****26d31c
          #  2. referencing a token that includes scopes notifications, repo, workflow
          oauth_token=core.SecretValue.secrets_manager('GithubAccessToken.us-west-2'),
          output=github_init_artifact
        )
      ])

    # Add build steps for python jobs
    build_python_stage = self.core_pipeline.add_stage(stage_name='Build-Python-Projects')
    #binplace_stage = self.core_pipeline.add_stage(stage_name='BinPlace-Output')
    
    for projectName in self.buildjoblayer.python_projects.keys():
      build_project = self.buildjoblayer.python_projects[projectName].build_project
      project_artifact = p.Artifact(artifact_name=projectName)
      
      build_python_stage.add_action(actions.CodeBuildAction(
        input=github_init_artifact,
        project=build_project,
        action_name='Build_'+projectName,
        outputs=[project_artifact]
      ))

    # Prepare the infra deployment services
    build_infra_stage = self.core_pipeline.add_stage(stage_name='Deploy-Infra')
    build_infra_stage.add_action(actions.CodeBuildAction(
      input=github_init_artifact,
      project=self.buildjoblayer.cdk_infra_project.build_project,
      action_name='Build_Infra'
    ))
