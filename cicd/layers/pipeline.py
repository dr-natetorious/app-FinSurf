#!/usr/bin/env python3
import os
from layers.buckets import BucketLayer
from layers.buildjobs import BuildJobLayer
from aws_cdk import (
  core,
  aws_iam as iam,
  aws_s3 as s3,
  aws_codebuild as build,
  aws_codepipeline as p,
  aws_codepipeline_actions as actions,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class CodePipelineLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, build_jobs: BuildJobLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
   

    role = iam.Role(self,'CodePipeline',
      assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
      description='Code deployment pipeline for app-FinSurf')

    self.core_pipeline = p.Pipeline(self, 'CorePipeline',
      pipeline_name='FinSurf-CorePipeline',
      role=role)

    # # Add trigger
    github_init_artifact = p.Artifact(artifact_name='github-init-artifact')
    self.core_pipeline.add_stage(
      stage_name='Trigger',
      actions=[
        actions.GitHubSourceAction(
          action_name='Init-from-GitHub',
          owner='dr-natetorious',
          repo='app-FinSurf',
          oauth_token=core.SecretValue.secrets_manager('GithubPersonalAccessToken',json_field='GitHubPersonalAccessToken'),
          #oauth_token=core.SecretValue.ssm_secure(parameter_name='GithubPersonalAccessToken',version='2'),
          output=github_init_artifact
        )
      ])

    # Add build steps
    self.core_pipeline.add_stage(
      stage_name='Build-Python-Projects',
      actions =[ 
        actions.CodeBuildAction(
          input=github_init_artifact,
          project=build_jobs.python_projects[key].build_project,
          action_name='Build_'+key
        ) for key in build_jobs.python_projects.keys()
      ]
    )

